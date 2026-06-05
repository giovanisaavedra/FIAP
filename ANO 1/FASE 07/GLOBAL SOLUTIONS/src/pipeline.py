"""
Orquestração do pipeline de análise espacial do SatVerify.

Etapas:
    1. Geocoding do endereço
    2. Download da imagem Sentinel-2
    3. Cálculo do NDBI + métricas
    4. Download da imagem aérea Mapbox
    5. YOLO sobre o Sentinel-2 RGB
    6. YOLO sobre a imagem aérea Mapbox
    7. Classificação de cena com CLIP (zero-shot)
    8. Geração de relatório de DD via Gemini (LLM)
    9. Upload dos artefatos para AWS S3 (graceful degradation)
    --
    Score de autenticidade (NDBI + CLIP + YOLO) é calculado entre as
    etapas 7 e 8 — o relatório consome o resultado do score.
    --
    Persistência local em outputs/<analysis_id>/ + cópia remota no S3.
"""

import json
import os
import uuid
from datetime import datetime

from src.clip_classifier import classify_scene
from src.config import (
    AWS_S3_BUCKET,
    MAPBOX_IMAGE_SIZE,
    MAPBOX_ZOOM_LEVEL,
    OUTPUT_DIR,
    SENTINEL_LOOKBACK_DAYS,
    SENTINEL_MAX_CLOUD_COVER,
)
from src.geocoding import geocode_address
from src.mapbox_fetcher import fetch_mapbox_aerial
from src.ndbi import (
    compute_built_up_metrics,
    compute_ndbi,
    save_ndbi_visualization,
)
from src.report_generator import generate_dd_report
from src.s3_uploader import upload_analysis_artifacts
from src.scoring import compute_authenticity_score
from src.sentinel_fetcher import fetch_sentinel_image
from src.yolo_detector import detect_objects


_DEFAULT_BUSINESS_CONTEXT = (
    "Não foi fornecido contexto de declaração da empresa."
)


def _format_class_counts(class_counts: dict) -> str:
    """Formata `{'car': 8, 'truck': 3}` como 'car=8, truck=3' para log."""
    if not class_counts:
        return "(nenhuma classe)"
    items = sorted(class_counts.items(), key=lambda kv: -kv[1])
    return ", ".join(f"{cls}={cnt}" for cls, cnt in items)


def _format_clip_top3(top3: list) -> str:
    """Formata `[('industrial', 0.78), ...]` como 'industrial 78%, ...'."""
    return ", ".join(f"{cat} {prob * 100:.0f}%" for cat, prob in top3)


def _placeholder_report_markdown(error: Exception) -> str:
    """Conteúdo do relatório quando a chamada ao Gemini falha."""
    return (
        "# ⚠️ Relatório não disponível\n\n"
        "Não foi possível gerar o relatório de due diligence automaticamente.\n\n"
        f"Erro: {error}\n\n"
        "Análise técnica completa disponível em `metadata.json`.\n"
    )


def run_analysis(address: str, business_context: str = "") -> dict:
    """
    Executa o pipeline completo de análise espacial + scoring + relatório DD.

    Args:
        address: endereço textual.
        business_context: declaração de negócio da empresa (perfil, faturamento,
            tipo de operação). Usado pelo LLM para gerar o relatório. Se vazio,
            cai para um placeholder genérico.

    Returns:
        dict com todas as informações da análise, incluindo `yolo_sentinel`,
        `yolo_mapbox`, `clip_classification`, `authenticity_score` e `dd_report`.
    """
    analysis_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    analysis_dir = os.path.join(OUTPUT_DIR, analysis_id)
    os.makedirs(analysis_dir, exist_ok=True)

    effective_context = business_context.strip() or _DEFAULT_BUSINESS_CONTEXT

    print(f"\n▶ Iniciando análise {analysis_id}")
    print(f"  Endereço: {address}")
    print(f"  Pasta: {analysis_dir}")

    # ---------------------------------------------------------------- 1) Geocoding
    print("  [1/9] Geocoding do endereço...")
    geo = geocode_address(address)
    print(f"        → lat={geo['latitude']:.6f}, lon={geo['longitude']:.6f}")
    print(f"        → {geo['display_name']}")

    # ----------------------------------------------------- 2) Sentinel-2 download
    print("  [2/9] Buscando imagem Sentinel-2 mais recente...")
    sentinel = fetch_sentinel_image(
        bbox=geo["bbox"],
        output_dir=analysis_dir,
        max_cloud_cover=SENTINEL_MAX_CLOUD_COVER,
        lookback_days=SENTINEL_LOOKBACK_DAYS,
        size=(512, 512),
    )
    print(
        f"        → cena de {sentinel['date_acquired']} "
        f"(cloud cover = {sentinel['cloud_cover']:.1f}%)"
    )

    # -------------------------------------------------- 3) NDBI + métricas locais
    print("  [3/9] Calculando NDBI...")
    ndbi_array = compute_ndbi(sentinel["bands_array"])
    ndbi_viz_path = os.path.join(analysis_dir, "ndbi.png")
    save_ndbi_visualization(ndbi_array, ndbi_viz_path)
    ndbi_metrics = compute_built_up_metrics(ndbi_array)
    print(
        f"        → {ndbi_metrics['pct_built_up']:.1f}% de área construída "
        f"(NDBI médio = {ndbi_metrics['mean_ndbi']:.3f})"
    )

    # ----------------------------------------------------- 4) Imagem aérea Mapbox
    print(
        f"  [4/9] Baixando imagem aérea do Mapbox "
        f"(resolução {MAPBOX_IMAGE_SIZE}x{MAPBOX_IMAGE_SIZE}, "
        f"zoom {MAPBOX_ZOOM_LEVEL})..."
    )
    mapbox_path = os.path.join(analysis_dir, "mapbox_aerial.png")
    fetch_mapbox_aerial(
        latitude=geo["latitude"],
        longitude=geo["longitude"],
        output_path=mapbox_path,
        zoom=MAPBOX_ZOOM_LEVEL,
        size=(MAPBOX_IMAGE_SIZE, MAPBOX_IMAGE_SIZE),
    )

    # ----------------------------------------- 5) YOLO sobre o Sentinel-2 RGB
    print("  [5/9] Rodando YOLO em Sentinel-2 RGB...")
    yolo_sentinel_path = os.path.join(analysis_dir, "yolo_sentinel_annotated.png")
    yolo_sentinel = detect_objects(
        image_path=sentinel["rgb_path"],
        output_annotated_path=yolo_sentinel_path,
    )
    print(
        f"        → {yolo_sentinel['total_detections']} objetos detectados "
        f"({_format_class_counts(yolo_sentinel['class_counts'])})"
    )

    # ----------------------------------------- 6) YOLO sobre a imagem Mapbox
    print("  [6/9] Rodando YOLO em Mapbox aerial...")
    yolo_mapbox_path = os.path.join(analysis_dir, "yolo_mapbox_annotated.png")
    yolo_mapbox = detect_objects(
        image_path=mapbox_path,
        output_annotated_path=yolo_mapbox_path,
    )
    print(
        f"        → {yolo_mapbox['total_detections']} objetos detectados "
        f"({_format_class_counts(yolo_mapbox['class_counts'])})"
    )

    # ----------------------------------------- 7) CLIP sobre a imagem Mapbox
    print("  [7/9] Classificando cena com CLIP...")
    clip_classification = classify_scene(image_path=mapbox_path)
    print(
        f"        → categoria dominante: {clip_classification['dominant_category']} "
        f"({clip_classification['dominant_score'] * 100:.0f}%)"
    )
    print(
        f"        → top-3: {_format_clip_top3(clip_classification['top3'])}"
    )

    # ----------------------------------------------- Score de autenticidade
    print("  Calculando score de autenticidade...")
    authenticity_score = compute_authenticity_score(
        ndbi_metrics=ndbi_metrics,
        yolo_sentinel=yolo_sentinel,
        yolo_mapbox=yolo_mapbox,
        clip_classification=clip_classification,
    )
    print(
        f"        → score {authenticity_score['score']}/100 — "
        f"DECISÃO: {authenticity_score['decision']}"
    )

    # ----------------------------------------- 8) Relatório DD via Gemini
    # Dicionário "snapshot" da análise para o gerador de relatório. Não
    # incluímos arrays grandes (bands_array já não está aqui).
    analysis_for_report = {
        "address_input": address,
        "address_resolved": geo["display_name"],
        "latitude": geo["latitude"],
        "longitude": geo["longitude"],
        "sentinel_date": sentinel["date_acquired"],
        "sentinel_cloud_cover": sentinel["cloud_cover"],
        "ndbi_metrics": ndbi_metrics,
        "yolo_sentinel": yolo_sentinel,
        "yolo_mapbox": yolo_mapbox,
        "clip_classification": clip_classification,
        "authenticity_score": authenticity_score,
    }

    print("  [8/9] Gerando relatório de DD via Gemini...")
    report_path = os.path.join(analysis_dir, "dd_report.md")
    dd_report_meta: dict
    try:
        report_result = generate_dd_report(
            analysis_data=analysis_for_report,
            business_context=effective_context,
        )
        report_markdown = report_result["report_markdown"]
        word_count = len(report_markdown.split())
        elapsed = report_result["generation_seconds"]
        print(
            f"        → relatório gerado ({word_count} palavras, "
            f"{elapsed}s)"
        )
        dd_report_meta = {
            "report_path": report_path,
            "model_used": report_result["model_used"],
            "generation_seconds": elapsed,
            "prompt_tokens_estimated": report_result["prompt_tokens_estimated"],
            "word_count": word_count,
            "status": "ok",
        }
    except Exception as exc:  # noqa: BLE001
        # Falha em rede / rate limit / auth: não derruba o pipeline.
        print(f"  ⚠️  Falha ao gerar relatório DD: {exc}")
        report_markdown = _placeholder_report_markdown(exc)
        dd_report_meta = {
            "report_path": report_path,
            "model_used": None,
            "generation_seconds": None,
            "prompt_tokens_estimated": None,
            "word_count": len(report_markdown.split()),
            "status": "failed",
            "error": str(exc),
        }

    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write(report_markdown)

    # ----------------------------------------------------- Resultado consolidado
    result = {
        "analysis_id": analysis_id,
        "address_input": address,
        "business_context": effective_context,
        "address_resolved": geo["display_name"],
        "latitude": geo["latitude"],
        "longitude": geo["longitude"],
        "output_dir": analysis_dir,
        "sentinel_rgb_path": sentinel["rgb_path"],
        "sentinel_date": sentinel["date_acquired"],
        "sentinel_cloud_cover": sentinel["cloud_cover"],
        "mapbox_aerial_path": mapbox_path,
        "ndbi_visualization_path": ndbi_viz_path,
        "ndbi_metrics": ndbi_metrics,
        "yolo_sentinel": yolo_sentinel,
        "yolo_mapbox": yolo_mapbox,
        "clip_classification": clip_classification,
        "authenticity_score": authenticity_score,
        "dd_report": dd_report_meta,
        "dd_report_markdown": report_markdown,
        # Placeholder "pending" — substituído após [9/9] pelo resultado real.
        # A primeira versão do metadata.json (que vai junto no upload) carrega
        # esse placeholder; a versão final local (re-gravada após o upload)
        # contém o status verdadeiro.
        "s3_upload": {
            "status": "pending",
            "bucket": AWS_S3_BUCKET,
            "expected_prefix": f"analyses/{analysis_id}/",
        },
        "timestamp": timestamp,
    }

    # ------ Primeira gravação do metadata.json (com placeholder s3_upload)
    # O markdown completo NÃO entra no metadata para mantê-lo enxuto; já está
    # salvo em dd_report.md ao lado.
    def _persist_metadata() -> None:
        metadata_to_save = {
            k: v for k, v in result.items() if k != "dd_report_markdown"
        }
        with open(metadata_path, "w", encoding="utf-8") as fh:
            json.dump(metadata_to_save, fh, indent=2, ensure_ascii=False)

    metadata_path = os.path.join(analysis_dir, "metadata.json")
    _persist_metadata()

    # ----------------------------------------- 9) Upload para AWS S3
    print("  [9/9] Persistindo artefatos em AWS S3...")
    try:
        s3_result = upload_analysis_artifacts(
            analysis_dir=analysis_dir,
            analysis_id=analysis_id,
        )
        if s3_result["uploaded"]:
            print(
                f"        → {len(s3_result['files_uploaded'])} arquivo(s) "
                f"enviado(s) para {s3_result['s3_uri']}"
            )
            if s3_result["files_failed"]:
                print(
                    f"        ⚠️ {len(s3_result['files_failed'])} arquivo(s) "
                    "falharam"
                )
            result["s3_upload"] = {
                "status": "success",
                "bucket": s3_result["bucket"],
                "prefix": s3_result["prefix"],
                "s3_uri": s3_result["s3_uri"],
                "files_uploaded": s3_result["files_uploaded"],
                "files_failed": s3_result["files_failed"],
                "error": None,
            }
        else:
            err = s3_result.get("error") or "erro desconhecido"
            print(f"        ⚠️ Upload S3 falhou: {err}")
            print(
                f"        → Análise disponível apenas localmente em "
                f"{analysis_dir}"
            )
            result["s3_upload"] = {
                "status": "failed",
                "bucket": s3_result["bucket"],
                "prefix": s3_result["prefix"],
                "s3_uri": s3_result["s3_uri"],
                "files_uploaded": s3_result["files_uploaded"],
                "files_failed": s3_result["files_failed"],
                "error": err,
            }
    except Exception as exc:  # noqa: BLE001
        # Captura qualquer exceção inesperada (ex: import falhando) para
        # garantir graceful degradation.
        print(f"        ⚠️ Upload S3 falhou: {exc}")
        print(
            f"        → Análise disponível apenas localmente em {analysis_dir}"
        )
        result["s3_upload"] = {
            "status": "failed",
            "bucket": AWS_S3_BUCKET,
            "prefix": f"analyses/{analysis_id}/",
            "s3_uri": f"s3://{AWS_S3_BUCKET}/analyses/{analysis_id}/",
            "files_uploaded": [],
            "files_failed": [],
            "error": f"Exceção no upload S3: {exc}",
        }

    # ------ Segunda gravação do metadata.json (versão final consistente)
    _persist_metadata()

    # Bloco de fechamento com o resultado final.
    print("  ─ Análise concluída ─")
    print(f"  Score        : {authenticity_score['score']}/100")
    print(f"  Decisão      : {authenticity_score['decision']}")
    print(f"  Nível risco  : {authenticity_score['risk_level']}")
    print(f"  metadata em {metadata_path}")
    return result
