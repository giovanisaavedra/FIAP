"""
SatVerify — Dashboard Interativo Streamlit

Roda via:
    streamlit run src/dashboard.py

Funcionalidades:
- 3 casos pré-validados (carregamento instantâneo de outputs/)
- Análise nova ao vivo (formulário expansível)
- Visualização das 4 imagens-chave + métricas + relatório Gemini
"""

import json
import os
import re
import sys
from pathlib import Path

# Quando rodado via `streamlit run src/dashboard.py`, a raiz do projeto NÃO
# entra automaticamente no sys.path (diferente de `python -m src.dashboard`).
# Inserimos a raiz manualmente para que `from src.pipeline import ...` funcione
# nos dois modos de execução. Precisa vir ANTES do import de `src.*`.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st

# Import do pipeline apenas se o usuário rodar nova análise (a importação
# é leve; YOLO/CLIP só carregam quando `run_analysis` é chamado).
from src.pipeline import run_analysis


# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="SatVerify — Due Diligence Espacial",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Casos pré-definidos da demo (correspondem aos endereços rodados em run_demo)
# ---------------------------------------------------------------------------
DEMO_CASES = [
    {
        "label": "🏭 Caso 1 — Fornecedor industrial",
        "address": "Av. Volkswagen, 100, São Bernardo do Campo, SP, Brasil",
        "business_context": (
            "Empresa declara ser fabricante industrial de autopeças com "
            "instalações de 5.000m²."
        ),
        "description": "Endereço industrial declarado em zona consagrada",
        "expected_decision": "ATENÇÃO",
    },
    {
        "label": "🏪 Caso 2 — Comércio popular como atacadista",
        "address": "Rua 25 de Março, 1000, São Paulo, SP, Brasil",
        "business_context": (
            "Empresa declara ser atacadista de eletrônicos com faturamento "
            "de R$ 200M/ano e instalações próprias compatíveis."
        ),
        "description": "Porte declarado vs porte observado",
        "expected_decision": "ATENÇÃO",
    },
    {
        "label": "🌳 Caso 3 — Endereço fantasma",
        "address": "Parque Estadual da Cantareira, São Paulo, SP, Brasil",
        "business_context": (
            "Empresa declara fábrica de R$ 50M/ano neste endereço."
        ),
        "description": "Red flag clássico — sem instalação física",
        "expected_decision": "REPROVADO",
    },
]


# ---------------------------------------------------------------------------
# Carregamento de análises a partir de outputs/
# ---------------------------------------------------------------------------
def load_analysis_from_disk(analysis_dir: str) -> dict | None:
    """
    Lê metadata.json + relatório .md de uma pasta de análise.
    Retorna dict completo pronto para renderizar, ou None se não existir.
    """
    metadata_path = os.path.join(analysis_dir, "metadata.json")
    if not os.path.exists(metadata_path):
        return None
    with open(metadata_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    # Carrega o relatório de DD (markdown gerado pelo Gemini).
    report_path = os.path.join(analysis_dir, "dd_report.md")
    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as fh:
            data["dd_report_text"] = fh.read()
    else:
        data["dd_report_text"] = "Relatório não disponível."

    return data


def _normalize(s: str) -> str:
    """
    Normaliza string para comparação tolerante: lowercase, espaços
    colapsados e trim nas pontas. Cobre variações sutis que quebrariam
    o matching exato (espaço duplo, espaço final, capitalização).
    """
    if not s:
        return ""
    return re.sub(r"\s+", " ", s.strip().lower())


def find_analysis_for_case(case_address: str, analyses: list) -> dict | None:
    """
    Procura uma análise existente em `outputs/` cujo `address_input` case
    com o endereço do caso demo. Usa matching normalizado para tolerar
    variações sutis (espaçamento, capitalização).

    `analyses` já vem ordenado por timestamp decrescente; em caso de
    múltiplos matches, devolve o mais recente.
    """
    target = _normalize(case_address)
    for analysis in analyses:
        if _normalize(analysis.get("address", "")) == target:
            return analysis
    return None


def list_available_analyses() -> list:
    """
    Lista todas as análises com `metadata.json` em `outputs/`, ordenadas
    por timestamp decrescente (mais recentes primeiro).
    """
    outputs_dir = Path("outputs")
    analyses: list = []
    if not outputs_dir.exists():
        return analyses

    for subdir in outputs_dir.iterdir():
        if not subdir.is_dir():
            continue
        metadata_path = subdir / "metadata.json"
        if not metadata_path.exists():
            continue
        try:
            with open(metadata_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            analyses.append({
                "id": data.get("analysis_id", subdir.name),
                "address": data.get("address_input", "—"),
                "decision": (
                    data.get("authenticity_score", {}).get("decision", "—")
                ),
                "score": data.get("authenticity_score", {}).get("score", 0),
                "dir": str(subdir),
                "timestamp": data.get("timestamp", ""),
            })
        except Exception:
            # Análise corrompida — ignora silenciosamente.
            continue

    analyses.sort(key=lambda x: x["timestamp"], reverse=True)
    return analyses


# ---------------------------------------------------------------------------
# Sidebar de controle
# ---------------------------------------------------------------------------
def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("# 🛰️ SatVerify")
        st.markdown("**Due Diligence Espacial via IA**")
        st.markdown("---")

        st.markdown("### 📋 Casos de Demonstração")
        st.caption("Análises pré-validadas para demonstração instantânea.")

        for i, case in enumerate(DEMO_CASES):
            if st.button(
                case["label"],
                key=f"demo_{i}",
                use_container_width=True,
            ):
                st.session_state["selected_demo"] = case
                st.session_state["mode"] = "demo"

        st.markdown("---")

        st.markdown("### 🔍 Nova Análise")
        with st.expander("Analisar novo endereço", expanded=False):
            new_address = st.text_input(
                "Endereço",
                placeholder="ex: Av. Paulista, 1578, São Paulo, SP, Brasil",
            )
            new_context = st.text_area(
                "Contexto declarado",
                placeholder=(
                    "Ex: Empresa declara ser distribuidora atacadista..."
                ),
            )
            if st.button(
                "▶️ Rodar Análise",
                type="primary",
                use_container_width=True,
            ):
                if new_address.strip():
                    st.session_state["new_analysis"] = {
                        "address": new_address,
                        "context": new_context or "Não fornecido.",
                    }
                    st.session_state["mode"] = "new"
                else:
                    st.error("Endereço é obrigatório.")

        st.markdown("---")

        st.markdown("### 📁 Histórico")
        analyses = list_available_analyses()
        if analyses:
            st.caption(f"{len(analyses)} análise(s) já executada(s)")
            with st.expander("Ver histórico"):
                # Mostra só as 10 mais recentes para não inundar a sidebar.
                for a in analyses[:10]:
                    if st.button(
                        f"{a['decision']} — {a['address'][:40]}",
                        key=f"hist_{a['id']}",
                        use_container_width=True,
                    ):
                        st.session_state["selected_hist"] = a
                        st.session_state["mode"] = "hist"

        # ---- Card AWS Status (estatísticas globais do bucket) ----
        # Falha silenciosa — se AWS estiver indisponível, o sidebar segue
        # funcionando sem essa caixa (graceful degradation).
        try:
            from src.s3_uploader import get_bucket_stats

            stats = get_bucket_stats()
            if not stats.get("error"):
                st.markdown("---")
                st.markdown("### ☁️ AWS S3 Status")
                st.caption(f"**Bucket:** `{stats['bucket']}`")
                # Cada análise produz ~7 artefatos; dividindo por 7 dá uma
                # aproximação de "quantas análises estão persistidas".
                analyses_count = (
                    stats["total_files"] // 7
                    if stats["total_files"] > 0
                    else 0
                )
                st.metric("Análises persistidas", analyses_count)
                st.caption(
                    f"Storage: {stats['total_mb']:.2f} MB / 5 GB"
                )
                st.progress(
                    min(stats["free_tier_used_pct"] / 100, 1.0)
                )
        except Exception:  # noqa: BLE001
            pass

        st.markdown("---")
        st.caption(
            "**FIAP Global Solution 2026.1**  \n"
            "Stack: Python • Streamlit • Sentinel-2 • "
            "Mapbox • YOLO • CLIP • Gemini • AWS S3"
        )


# ---------------------------------------------------------------------------
# Painel AWS S3 — auditoria, download seguro e governança financeira
# ---------------------------------------------------------------------------
# Ícones por nome de arquivo, para deixar a lista de downloads mais legível.
_FILE_EMOJI = {
    "metadata.json": "📊",
    "sentinel_rgb.png": "🛰️",
    "ndbi.png": "📈",
    "mapbox_aerial.png": "🚁",
    "yolo_sentinel_annotated.png": "🎯",
    "yolo_mapbox_annotated.png": "🎯",
    "dd_report.md": "📝",
}


def render_aws_panel(data: dict) -> None:
    """
    Renderiza o painel de visibilidade AWS S3 para uma análise específica.

    Inclui: bucket info + link para console AWS, downloads diretos via
    presigned URLs, estatísticas de uso do bucket e checklist de boas
    práticas. Só aparece quando o upload S3 da análise teve sucesso.
    """
    # Import local para evitar travar o dashboard se boto3 não estiver
    # disponível por algum motivo (graceful degradation).
    from src.s3_uploader import (
        generate_presigned_urls,
        get_bucket_stats,
        get_console_url,
    )

    s3_info = data.get("s3_upload", {}) or {}
    if s3_info.get("status") != "success":
        return  # Sem painel quando o upload não rolou.

    files_uploaded = s3_info.get("files_uploaded", []) or []
    analysis_id = data.get("analysis_id", "")

    with st.expander(
        "☁️ **AWS S3 — Auditoria & Persistência**",
        expanded=True,
    ):
        # ---- Linha 1: bucket info + botão para o console AWS ----
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(
                f"**Bucket:** `{s3_info.get('bucket', '—')}`  \n"
                f"**Região:** `us-east-1`  \n"
                f"**Prefix da análise:** `{s3_info.get('prefix', '—')}`"
            )
        with col2:
            console_url = get_console_url(analysis_id)
            st.markdown(
                f'<a href="{console_url}" target="_blank">'
                f'<button style="background-color:#FF9900;color:white;'
                f'padding:8px 16px;border:none;border-radius:4px;'
                f'cursor:pointer;width:100%;">'
                f'🔗 Ver no Console AWS</button></a>',
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # ---- Linha 2: downloads diretos via presigned URLs ----
        st.markdown("### 📥 Downloads Diretos")
        st.caption(
            "URLs pré-assinadas válidas por 1 hora. Padrão de segurança "
            "bancário — permite compartilhamento sem expor credenciais."
        )

        with st.spinner("Gerando URLs seguras..."):
            urls = generate_presigned_urls(
                files_uploaded, expires_in_seconds=3600
            )

        if not urls:
            st.warning("Não foi possível gerar URLs de download.")
        else:
            files_list = list(urls.items())
            col_a, col_b = st.columns(2)
            for i, (key, url) in enumerate(files_list):
                filename = key.split("/")[-1]
                emoji = _FILE_EMOJI.get(filename, "📄")
                target_col = col_a if i % 2 == 0 else col_b
                with target_col:
                    st.markdown(
                        f'<a href="{url}" target="_blank">'
                        f'<button style="background-color:#1E88E5;color:white;'
                        f'padding:6px 12px;border:none;border-radius:4px;'
                        f'cursor:pointer;width:100%;margin:2px 0;'
                        f'text-align:left;font-size:13px;">'
                        f"{emoji} {filename}</button></a>",
                        unsafe_allow_html=True,
                    )

        st.markdown("---")

        # ---- Linha 3: estatísticas de uso do bucket ----
        st.markdown("### 📊 Estatísticas de Uso do Bucket")

        with st.spinner("Consultando AWS..."):
            stats = get_bucket_stats()

        if stats.get("error"):
            st.warning(
                f"Não foi possível obter estatísticas: {stats['error']}"
            )
        else:
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Total de Arquivos", stats["total_files"])
            with m2:
                st.metric("Storage Usado", f"{stats['total_mb']:.2f} MB")
            with m3:
                st.metric(
                    "Free Tier (5GB)",
                    f"{stats['free_tier_used_pct']:.4f}%",
                    help=(
                        "Percentual do Free Tier AWS S3 utilizado "
                        "(5GB gratuitos)"
                    ),
                )
            with m4:
                cost = stats["estimated_monthly_cost_usd"]
                st.metric(
                    "Custo Estimado/Mês",
                    f"${cost:.4f}",
                    help="Estimativa baseada em ~$0.023/GB acima de 5GB",
                )

            if stats.get("last_modified"):
                st.caption(
                    "📅 Última modificação no bucket: "
                    f"{stats['last_modified'][:19]}"
                )

        st.markdown("---")

        # ---- Linha 4: checklist de boas práticas (storytelling) ----
        st.markdown("### 🔒 Boas Práticas Aplicadas")
        col_x, col_y = st.columns(2)
        with col_x:
            st.markdown(
                "- ✅ Bucket privado (Block all public access)\n"
                "- ✅ Usuário IAM dedicado (não-root)\n"
                "- ✅ Política mínima (`AmazonS3FullAccess`)"
            )
        with col_y:
            st.markdown(
                "- ✅ Budget alarm em US$ 0.01\n"
                "- ✅ Conta AWS dedicada ao projeto\n"
                "- ✅ Credenciais via `.env` (nunca commitadas)"
            )


# ---------------------------------------------------------------------------
# Renderização do resultado completo (corpo principal)
# ---------------------------------------------------------------------------
def render_analysis_result(data: dict | None) -> None:
    """Renderiza uma análise completa no main panel."""
    if not data:
        st.warning("Análise não encontrada ou metadata.json ausente.")
        return

    # === HEADER ===
    score_data = data.get("authenticity_score", {}) or {}
    decision = score_data.get("decision", "—")
    score = score_data.get("score", 0)
    risk = score_data.get("risk_level", "—")

    decision_emoji = {
        "APROVADO": "✅",
        "ATENÇÃO": "⚠️",
        "REPROVADO": "🚨",
    }.get(decision, "❓")

    risk_emoji = {
        "BAIXO": "🟢",
        "MÉDIO": "🟡",
        "ALTO": "🔴",
    }.get(risk, "⚪")

    st.markdown(f"# {decision_emoji} Resultado: {decision}")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"**📍 Endereço analisado:**  \n`{data['address_input']}`")
        st.caption(f"Resolvido: {data.get('address_resolved', '—')}")
        st.caption(
            f"Coordenadas: {data.get('latitude', 0):.4f}, "
            f"{data.get('longitude', 0):.4f}"
        )
    with col2:
        st.metric("Score", f"{score}/100")
    with col3:
        st.metric("Risco", f"{risk_emoji} {risk}")

    # === BADGE DE S3 (logo abaixo do header) ===
    s3_info = data.get("s3_upload", {}) or {}
    s3_status = s3_info.get("status", "not_attempted")

    if s3_status == "success":
        files_count = len(s3_info.get("files_uploaded", []))
        st.success(
            f"☁️ **Persistido em AWS S3**: {files_count} arquivo(s) em "
            f"`{s3_info.get('s3_uri', '—')}`"
        )
    elif s3_status == "failed":
        st.warning(
            f"⚠️ Upload S3 falhou: "
            f"{s3_info.get('error', 'erro desconhecido')}. "
            "Análise disponível localmente."
        )
    elif s3_status == "pending":
        st.info("⏳ Upload S3 pendente")
    # else: not_attempted → não mostra nada (compatibilidade com análises antigas)

    # === PAINEL AWS DETALHADO (presigned URLs, console, stats) ===
    render_aws_panel(data)

    st.markdown("---")

    # === EVIDÊNCIAS VISUAIS (4 colunas) ===
    st.markdown("## 🖼️ Evidências Visuais")

    col_a, col_b, col_c, col_d = st.columns(4)

    with col_a:
        st.markdown("**🛰️ Sentinel-2**")
        rgb_path = data.get("sentinel_rgb_path", "")
        if rgb_path and os.path.exists(rgb_path):
            st.image(rgb_path, use_container_width=True)
        else:
            st.caption("_imagem indisponível_")
        sentinel_date = (data.get("sentinel_date") or "—")[:10]
        st.caption(f"Cena: {sentinel_date}")
        st.caption(f"Nuvens: {data.get('sentinel_cloud_cover', 0):.1f}%")

    with col_b:
        st.markdown("**📊 NDBI**")
        ndbi_path = data.get("ndbi_visualization_path", "")
        if ndbi_path and os.path.exists(ndbi_path):
            st.image(ndbi_path, use_container_width=True)
        else:
            st.caption("_imagem indisponível_")
        ndbi_pct = data.get("ndbi_metrics", {}).get("pct_built_up", 0)
        st.caption(f"{ndbi_pct:.1f}% construído")

    with col_c:
        st.markdown("**🚁 Mapbox Aerial**")
        mapbox_path = data.get("mapbox_aerial_path", "")
        if mapbox_path and os.path.exists(mapbox_path):
            st.image(mapbox_path, use_container_width=True)
        else:
            st.caption("_imagem indisponível_")
        st.caption("0.5m/pixel @ zoom 18")

    with col_d:
        st.markdown("**🎯 YOLO Detecções**")
        yolo_annot_path = (
            data.get("yolo_mapbox", {}).get("annotated_image_path", "")
        )
        if yolo_annot_path and os.path.exists(yolo_annot_path):
            st.image(yolo_annot_path, use_container_width=True)
        else:
            st.caption("_imagem indisponível_")
        yolo_total = data.get("yolo_mapbox", {}).get("total_detections", 0)
        st.caption(f"{yolo_total} objeto(s) detectado(s)")

    st.markdown("---")

    # === MÉTRICAS DETALHADAS ===
    st.markdown("## 📊 Métricas Detalhadas")

    m1, m2, m3 = st.columns(3)

    with m1:
        ndbi = data.get("ndbi_metrics", {}) or {}
        st.markdown("**NDBI (Área Construída)**")
        st.markdown(f"- % construído: **{ndbi.get('pct_built_up', 0):.1f}%**")
        st.markdown(f"- NDBI médio: {ndbi.get('mean_ndbi', 0):.3f}")
        st.markdown(f"- Classificação: **{ndbi.get('built_up_level', '—')}**")

    with m2:
        clip = data.get("clip_classification", {}) or {}
        st.markdown("**CLIP (Classificação de Cena)**")
        st.markdown(f"- Dominante: **{clip.get('dominant_category', '—')}**")
        st.markdown(
            f"- Confiança: {clip.get('dominant_score', 0) * 100:.0f}%"
        )
        st.markdown("- Top 3:")
        for cat, prob in clip.get("top3", []) or []:
            st.markdown(f"  - {cat}: {prob * 100:.0f}%")

    with m3:
        yolo_m = data.get("yolo_mapbox", {}) or {}
        st.markdown("**YOLO (Detecção de Objetos)**")
        st.markdown(f"- Total: **{yolo_m.get('total_detections', 0)}**")
        classes = yolo_m.get("class_counts", {}) or {}
        if classes:
            for cls, count in classes.items():
                st.markdown(f"  - {cls}: {count}")
        else:
            st.markdown("- Nenhuma detecção")
        st.caption(f"Modelo: {yolo_m.get('model_used', '—')}")

    st.markdown("---")

    # === RELATÓRIO DD (GEMINI) ===
    st.markdown("## 🤖 Relatório de Due Diligence")
    st.caption(
        f"Gerado por Gemini "
        f"({data.get('dd_report', {}).get('model_used', '—')})"
    )

    report_text = data.get("dd_report_text", "Relatório não disponível.")
    st.markdown(report_text)

    st.markdown("---")

    # === DECOMPOSIÇÃO DO SCORE ===
    with st.expander("🧮 Decomposição do Score (transparência algorítmica)"):
        components = score_data.get("components", {}) or {}

        st.markdown("**Componentes do score:**")
        st.markdown(
            f"- NDBI: **{components.get('ndbi_score', 0)}** pontos (peso 40)"
        )
        st.markdown(
            f"- CLIP: **{components.get('clip_score', 0)}** pontos (peso 40)"
        )
        st.markdown(
            f"- YOLO Mapbox: **{components.get('mapbox_score', 0)}** "
            "pontos (peso 15)"
        )
        st.markdown(
            f"- YOLO Sentinel-2: **{components.get('sentinel_score', 0)}** "
            "pontos (peso 5)"
        )
        st.markdown(f"- **Total: {components.get('total', 0)}/100**")

        st.markdown("**Raciocínio:**")
        for line in score_data.get("reasoning", []) or []:
            st.markdown(f"> {line}")

    # === METADATA TÉCNICA ===
    with st.expander("🔧 Metadata técnica (JSON)"):
        st.json(data)


# ---------------------------------------------------------------------------
# Tela de boas-vindas (antes de qualquer interação)
# ---------------------------------------------------------------------------
def render_welcome() -> None:
    st.markdown("# 🛰️ SatVerify")
    st.markdown(
        "### Plataforma de Due Diligence Empresarial via Inteligência Espacial"
    )
    st.markdown(
        "Validação automatizada de existência e atividade de empresas em "
        "endereços declarados, usando imagens de satélite, visão computacional "
        "e IA cognitiva."
    )
    st.markdown("---")

    st.info(
        "👈 **Selecione um caso de demonstração** na barra lateral, ou "
        "execute uma nova análise inserindo um endereço."
    )

    st.markdown("### 🧪 Como o sistema funciona")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**1️⃣ Geocoding**")
        st.caption("Converte endereço em coordenadas via Nominatim/OSM")
    with col2:
        st.markdown("**2️⃣ Análise Espectral**")
        st.caption("NDBI sobre Sentinel-2 (ESA) para densidade construída")
    with col3:
        st.markdown("**3️⃣ Visão Computacional**")
        st.caption("YOLOv8 (DOTA) + CLIP zero-shot sobre imagem aérea")
    with col4:
        st.markdown("**4️⃣ Relatório Cognitivo**")
        st.caption("Gemini 2.5 sintetiza evidências em recomendação")


# ---------------------------------------------------------------------------
# Orquestrador principal
# ---------------------------------------------------------------------------
def main() -> None:
    render_sidebar()

    # Painel de debug na sidebar mostrando o que está em outputs/ — ajuda
    # o usuário a entender por que um caso pode não estar sendo encontrado
    # (matching falha quando endereços antigos divergem dos atuais).
    analyses_available = list_available_analyses()
    if analyses_available:
        with st.sidebar:
            with st.expander(
                f"🔧 Debug ({len(analyses_available)} análises em outputs/)",
                expanded=False,
            ):
                for a in analyses_available:
                    st.caption(
                        f"• `{a['address'][:50]}...` → "
                        f"{a['decision']} ({a['score']}/100)"
                    )

    # Sem interação ainda → tela de boas-vindas.
    if "mode" not in st.session_state:
        render_welcome()
        return

    mode = st.session_state["mode"]

    # === MODO: DEMO PRÉ-VALIDADO ===
    if mode == "demo":
        case = st.session_state["selected_demo"]
        analyses = list_available_analyses()
        match = find_analysis_for_case(case["address"], analyses)

        st.markdown(f"## {case['label']}")
        st.info(f"**Contexto declarado:** {case['business_context']}")
        st.markdown("---")

        if not match:
            st.warning(
                "⚠️ Não há análise pré-validada para o endereço:\n\n"
                f"`{case['address']}`\n\n"
                "Você pode:"
            )

            col1, col2 = st.columns(2)
            with col1:
                # Permite rodar o pipeline ao vivo direto da tela do caso.
                if st.button(
                    "▶️ Executar agora (15-30s)",
                    type="primary",
                    use_container_width=True,
                    key=f"run_now_{case['address']}",
                ):
                    with st.spinner("Executando pipeline completo..."):
                        try:
                            run_analysis(
                                address=case["address"],
                                business_context=case["business_context"],
                            )
                            st.success("✅ Análise concluída!")
                            st.rerun()
                        except Exception as exc:  # noqa: BLE001
                            st.error(f"Erro na análise: {exc}")
            with col2:
                st.markdown("**Ou rode no terminal:**")
                st.code("python -m src.run_demo", language="bash")

            # Lista o que está disponível no histórico para o usuário se
            # localizar (matching falhou — talvez tenha algo parecido).
            if analyses:
                st.markdown("---")
                st.markdown("**📁 Análises disponíveis no histórico:**")
                for a in analyses[:5]:
                    st.caption(f"- {a['address'][:70]} ({a['decision']})")
            return

        data = load_analysis_from_disk(match["dir"])
        render_analysis_result(data)

    # === MODO: NOVA ANÁLISE AO VIVO ===
    elif mode == "new":
        new = st.session_state.get("new_analysis")
        if not new:
            render_welcome()
            return

        st.markdown("## 🔍 Análise Nova — Em Execução")
        st.info(
            f"**Endereço:** {new['address']}  \n"
            f"**Contexto:** {new['context']}"
        )

        with st.spinner("Executando pipeline completo (15-30s)..."):
            try:
                result = run_analysis(
                    address=new["address"],
                    business_context=new["context"],
                )
                # Recarrega do disco para garantir consistência (e pegar o
                # dd_report.md gravado pelo pipeline).
                data = load_analysis_from_disk(result["output_dir"])
                st.success("✅ Análise concluída!")
                st.markdown("---")
                render_analysis_result(data)
                # Limpa o trigger para evitar re-execução em rerun.
                del st.session_state["new_analysis"]
                st.session_state["mode"] = "viewing"
            except Exception as exc:  # noqa: BLE001
                st.error(f"Erro na análise: {exc}")
                if "new_analysis" in st.session_state:
                    del st.session_state["new_analysis"]

    # === MODO: HISTÓRICO ===
    elif mode == "hist":
        hist = st.session_state["selected_hist"]
        data = load_analysis_from_disk(hist["dir"])
        st.markdown("## 📁 Análise do Histórico")
        st.markdown("---")
        render_analysis_result(data)

    # === MODO: VIEWING (após nova análise — não re-roda nada) ===
    else:
        render_welcome()


if __name__ == "__main__":
    main()
