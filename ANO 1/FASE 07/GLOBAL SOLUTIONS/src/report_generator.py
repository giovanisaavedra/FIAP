"""
Gerador de relatório de Due Diligence via LLM (Google Gemini 2.5 Flash Lite).

Recebe o dicionário consolidado da análise (com NDBI, CLIP, YOLO, score) e
contexto de negócio (declaração da empresa) e produz:
  - resumo executivo (3-5 frases)
  - análise por evidência
  - lista de red flags
  - recomendação final fundamentada
  - limitações da análise

Hardware: roda em nuvem (Google AI Studio). Latência típica: 2-4 segundos.
"""

import time
from typing import Dict

from google import genai

from src.config import GEMINI_API_KEY, GEMINI_MODEL


# Template do prompt — inglês não usado de propósito; queremos PT-BR formal.
_PROMPT_TEMPLATE = """Você é um analista sênior de Due Diligence empresarial (KYB/AML), especializado em verificação de fornecedores via análise geoespacial e imagens de satélite. Sua tarefa é produzir um RELATÓRIO TÉCNICO DE DUE DILIGENCE em português brasileiro, com base nas evidências coletadas automaticamente pelo sistema SatVerify.

# CONTEXTO DA DECLARAÇÃO DA EMPRESA

{business_context}

**Endereço declarado:** {address_input}
**Endereço resolvido pelo geocoding:** {address_resolved}
**Coordenadas:** lat={latitude}, lon={longitude}

# EVIDÊNCIAS COLETADAS

## 1. Análise espectral (Sentinel-2 — satélite)
- Data da imagem: {sentinel_date}
- Cobertura de nuvens: {sentinel_cloud_cover}%
- Densidade de área construída (NDBI): {ndbi_pct:.1f}%
- NDBI médio: {ndbi_mean:.3f}
- Classificação NDBI: {ndbi_level}

## 2. Classificação semântica de cena (CLIP — modelo multimodal zero-shot)
- Categoria dominante: **{clip_dominant}** ({clip_dominant_prob:.0f}% de confiança)
- Top 3 categorias: {clip_top3}

## 3. Detecção de objetos (YOLOv8 OBB — modelo treinado em DOTA)
- Imagem aérea de alta resolução (Mapbox): {yolo_mapbox_count} objetos detectados ({yolo_mapbox_classes})
- Imagem de satélite Sentinel-2: {yolo_sentinel_count} objetos (limitação esperada de resolução)

## 4. Score consolidado do sistema
- **Score: {score}/100**
- **Decisão automatizada: {decision}**
- **Nível de risco: {risk_level}**
- Componentes do score: {score_components}

# INSTRUÇÕES PARA O RELATÓRIO

Produza um relatório em **markdown** com a seguinte estrutura, em português brasileiro formal:

## 📋 Resumo Executivo
3-5 frases sintetizando o achado principal e a recomendação. Tom profissional, evite jargão excessivo. Mencione score e decisão.

## 🔍 Análise das Evidências
Comente cada evidência de forma articulada:
- O que diz a análise espectral (NDBI)
- O que diz a classificação de cena (CLIP)
- O que dizem as detecções de objetos (YOLO)
- Onde há coerência entre os sinais e onde há divergência

## ⚠️ Red Flags Identificados
Liste em bullets os principais red flags (se houver). Se for caso APROVADO sem red flags, escrever "Nenhum red flag relevante identificado nesta análise."

## ✅ Recomendação Final
Recomendação acionável: aprovar, aprovar com diligência adicional, ou reprovar. Justifique com base nas evidências. Se aplicável, sugira próximos passos (ex: inspeção presencial, documentação adicional, validação por terceiros).

## 📌 Limitações desta análise
Mencione brevemente que esta é uma análise automatizada baseada em sinais geoespaciais (não substitui diligência humana completa) e que detecções dependem de qualidade da imagem disponível.

REGRAS IMPORTANTES:
1. Seja **honesto** sobre o que os dados mostram. Se houver incoerência, aponte.
2. Para o Caso "Volkswagen" (declarado como industrial mas CLIP indica residencial), explicite que o ENDEREÇO geocodificado pode corresponder a área administrativa, não operacional.
3. Para o Caso "Rua 25 de Março" (declarado como atacadista R$200M mas CLIP indica comércio popular denso), explicite a incompatibilidade entre porte declarado e tipo de zona detectada.
4. Para o Caso "Parque da Cantareira" (declarado como fábrica mas CLIP indica área verde), seja taxativo: não há evidência visual de instalação.
5. **NÃO invente dados.** Use apenas o que está em "Evidências Coletadas".
6. Mantenha o relatório com **300-500 palavras totais**.
"""


def _build_prompt(analysis_data: Dict, business_context: str) -> str:
    """Constrói o prompt completo, extraindo e formatando campos da análise."""
    ndbi = analysis_data["ndbi_metrics"]
    clip = analysis_data["clip_classification"]
    yolo_mapbox = analysis_data["yolo_mapbox"]
    yolo_sentinel = analysis_data["yolo_sentinel"]
    score_data = analysis_data["authenticity_score"]

    # Strings auxiliares (lidam com dicts vazios sem quebrar o format).
    clip_top3_str = ", ".join(
        f"{cat} {prob * 100:.0f}%" for cat, prob in (clip.get("top3") or [])
    ) or "indisponível"

    mapbox_classes = yolo_mapbox.get("class_counts") or {}
    yolo_mapbox_classes_str = (
        ", ".join(f"{cls}={n}" for cls, n in mapbox_classes.items())
        if mapbox_classes
        else "nenhum"
    )

    score_components = score_data.get("components") or {}
    score_components_str = (
        ", ".join(f"{k}={v}" for k, v in score_components.items())
        if score_components
        else "indisponível"
    )

    return _PROMPT_TEMPLATE.format(
        business_context=business_context,
        address_input=analysis_data["address_input"],
        address_resolved=analysis_data["address_resolved"],
        latitude=analysis_data["latitude"],
        longitude=analysis_data["longitude"],
        sentinel_date=analysis_data["sentinel_date"],
        sentinel_cloud_cover=analysis_data["sentinel_cloud_cover"],
        ndbi_pct=ndbi["pct_built_up"],
        ndbi_mean=ndbi["mean_ndbi"],
        ndbi_level=ndbi["built_up_level"],
        clip_dominant=clip["dominant_category"],
        clip_dominant_prob=float(clip["dominant_score"]) * 100,
        clip_top3=clip_top3_str,
        yolo_mapbox_count=yolo_mapbox["total_detections"],
        yolo_mapbox_classes=yolo_mapbox_classes_str,
        yolo_sentinel_count=yolo_sentinel["total_detections"],
        score=score_data["score"],
        decision=score_data["decision"],
        risk_level=score_data["risk_level"],
        score_components=score_components_str,
    )


def generate_dd_report(analysis_data: Dict, business_context: str) -> Dict:
    """
    Gera relatório de Due Diligence via Gemini com base nos dados da análise.

    Args:
        analysis_data: dicionário completo da análise (saída do pipeline.py),
            contendo `ndbi_metrics`, `clip_classification`, `yolo_mapbox`,
            `yolo_sentinel` e `authenticity_score`.
        business_context: contexto declarado pela empresa (string narrativa).

    Returns:
        dict com:
            - 'report_markdown': str (relatório completo em markdown)
            - 'model_used': str
            - 'prompt_tokens_estimated': int (estimativa rough; ~4 chars/token)
            - 'generation_seconds': float

    Raises:
        Exception: qualquer falha do SDK Gemini (rate limit, rede, auth, etc.)
            é propagada — o caller decide como tratar.
    """
    prompt = _build_prompt(analysis_data, business_context)

    start_time = time.time()
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    elapsed = time.time() - start_time

    report_text = response.text or ""

    return {
        "report_markdown": report_text,
        "model_used": GEMINI_MODEL,
        "prompt_tokens_estimated": len(prompt) // 4,
        "generation_seconds": round(elapsed, 2),
    }
