"""
Cálculo do score de autenticidade da empresa a partir das evidências
espaciais: NDBI (densidade espectral) + YOLO (objetos pontuais) +
CLIP (classificação semântica da cena).

Pesos atuais (totalizam 100):
    NDBI         : 40
    CLIP         : 40
    YOLO Mapbox  : 15
    YOLO Sentinel:  5

CLIP foi adicionado para complementar o YOLO em imagens aéreas, onde a
detecção pontual mostrou rendimento decrescente mesmo com modelo
especializado (DOTA). A combinação de sinais independentes (densidade,
semântica, objetos) produz scores mais discriminativos entre os casos.

Regras determinísticas e explicáveis — cada componente contribui com
pontos, e a soma define a decisão final (APROVADO / ATENÇÃO / REPROVADO).
"""


# Classes do dataset DOTA (modelo yolov8n-obb.pt) consideradas evidência
# de atividade empresarial visível em imagens aéreas verticais.
# Mantivemos também os nomes equivalentes do COCO ("car", "truck", "bus",
# "person", "motorcycle") como fallback para quem usar o modelo antigo.
_RELEVANT_CLASSES_MAPBOX = {
    # ----- DOTA (modelo aéreo, atual) -----
    "small-vehicle",   # carros vistos de cima
    "large-vehicle",   # caminhões e ônibus — sinal de logística pesada
    "storage-tank",    # tanques — forte indicador industrial
    "plane",           # aeroportos / hangares privados
    "ship",            # operações marítimas
    "helicopter",      # heliporto — sinal de operação executiva
    "harbor",          # cais / operações portuárias
    # ----- COCO (fallback, modelo retangular antigo) -----
    "car",
    "truck",
    "bus",
    "person",
    "motorcycle",
}


# Categorias CLIP agrupadas por "perfil de evidência empresarial".
_CLIP_STRONG = {"industrial", "parking_or_storage"}
_CLIP_COMMERCIAL = {"commercial_dense"}
_CLIP_NEUTRAL = {"residential"}
# Tudo o resto (green_area, agricultural, etc.) cai em "negativo".


def compute_authenticity_score(
    ndbi_metrics: dict,
    yolo_sentinel: dict,
    yolo_mapbox: dict,
    clip_classification: dict,
) -> dict:
    """
    Combina NDBI + YOLO (Sentinel e Mapbox) + CLIP em um score 0-100 com
    decisão e justificativa textual.

    Args:
        ndbi_metrics: resultado de `compute_built_up_metrics`
        yolo_sentinel: resultado de `detect_objects` sobre o Sentinel-2 RGB
                       (baixa resolução, usado apenas como confirmação macro)
        yolo_mapbox: resultado de `detect_objects` sobre a imagem aérea Mapbox
                     (alta resolução, evidência adicional de atividade)
        clip_classification: resultado de `classify_scene` (CLIP zero-shot)
                             sobre a imagem aérea Mapbox

    Returns:
        dict com:
            - 'score': int 0-100
            - 'decision': 'APROVADO' | 'ATENÇÃO' | 'REPROVADO'
            - 'risk_level': 'BAIXO' | 'MÉDIO' | 'ALTO'
            - 'reasoning': list[str] (passos da decisão, em PT-BR)
            - 'components': dict (decomposição do score)
    """
    reasoning: list = []
    components: dict = {}

    # ----------------------------------------------------------------------
    # Componente 1 — NDBI (peso 40): área construída via banda SWIR.
    # ----------------------------------------------------------------------
    pct_built = float(ndbi_metrics["pct_built_up"])
    if pct_built >= 30:
        ndbi_score = 40
        reasoning.append(
            f"NDBI: {pct_built:.1f}% de área construída — densidade alta "
            "compatível com instalação empresarial (+40 pontos)"
        )
    elif pct_built >= 10:
        ndbi_score = 25
        reasoning.append(
            f"NDBI: {pct_built:.1f}% de área construída — densidade "
            "moderada (+25 pontos)"
        )
    elif pct_built >= 3:
        ndbi_score = 10
        reasoning.append(
            f"NDBI: {pct_built:.1f}% de área construída — densidade "
            "baixa (+10 pontos)"
        )
    else:
        ndbi_score = 0
        reasoning.append(
            f"NDBI: {pct_built:.1f}% de área construída — praticamente sem "
            "evidência espectral de instalação (+0 pontos)"
        )
    components["ndbi_score"] = ndbi_score

    # ----------------------------------------------------------------------
    # Componente 2 — CLIP (peso 40): classificação semântica da cena.
    # ----------------------------------------------------------------------
    dominant_cat = clip_classification["dominant_category"]
    dominant_prob = float(clip_classification["dominant_score"])
    dominant_pct = dominant_prob * 100.0

    if dominant_cat in _CLIP_STRONG:
        if dominant_prob >= 0.5:
            clip_score = 40
            clip_msg = (
                f"CLIP: cena classificada como '{dominant_cat}' com "
                f"{dominant_pct:.0f}% de confiança — forte evidência de "
                "operação empresarial (+40 pontos)"
            )
        elif dominant_prob >= 0.3:
            clip_score = 25
            clip_msg = (
                f"CLIP: cena classificada como '{dominant_cat}' com "
                f"{dominant_pct:.0f}% de confiança — evidência moderada "
                "(+25 pontos)"
            )
        else:
            clip_score = 15
            clip_msg = (
                f"CLIP: cena classificada como '{dominant_cat}' com baixa "
                f"confiança ({dominant_pct:.0f}%) (+15 pontos)"
            )
    elif dominant_cat in _CLIP_COMMERCIAL:
        if dominant_prob >= 0.5:
            # Comércio denso não é red flag, mas merece atenção quando a
            # empresa se declara industrial ou atacadista.
            clip_score = 25
            clip_msg = (
                f"CLIP: cena classificada como '{dominant_cat}' "
                f"({dominant_pct:.0f}%) — área comercial, verificar "
                "compatibilidade com declaração (+25 pontos)"
            )
        else:
            clip_score = 15
            clip_msg = (
                f"CLIP: classificação ambígua tendendo a "
                f"'{dominant_cat}' (+15 pontos)"
            )
    elif dominant_cat in _CLIP_NEUTRAL:
        clip_score = 10
        clip_msg = (
            f"CLIP: cena classificada como '{dominant_cat}' "
            f"({dominant_pct:.0f}%) — incompatível com operação empresarial "
            "declarada (+10 pontos)"
        )
    else:
        # green_area, agricultural, etc. — red flag direto.
        clip_score = 0
        clip_msg = (
            f"CLIP: cena classificada como '{dominant_cat}' "
            f"({dominant_pct:.0f}%) — sem evidência de instalação "
            "empresarial (+0 pontos)"
        )
    reasoning.append(clip_msg)
    components["clip_score"] = clip_score

    # ----------------------------------------------------------------------
    # Componente 3 — YOLO Mapbox (peso 15): evidência visual de atividade
    # na imagem aérea de alta resolução. Peso reduzido porque o YOLO aéreo
    # mostrou rendimento decrescente em imagens brasileiras.
    # ----------------------------------------------------------------------
    relevant_count_mapbox = sum(
        count
        for cls, count in yolo_mapbox["class_counts"].items()
        if cls in _RELEVANT_CLASSES_MAPBOX
    )

    if relevant_count_mapbox >= 10:
        mapbox_score = 15
        reasoning.append(
            f"YOLO Mapbox: {relevant_count_mapbox} objetos relevantes "
            "(veículos, tanques, infraestrutura industrial) — alta "
            "atividade visível (+15 pontos)"
        )
    elif relevant_count_mapbox >= 3:
        mapbox_score = 10
        reasoning.append(
            f"YOLO Mapbox: {relevant_count_mapbox} objetos relevantes — "
            "atividade moderada (+10 pontos)"
        )
    elif relevant_count_mapbox >= 1:
        mapbox_score = 5
        reasoning.append(
            f"YOLO Mapbox: {relevant_count_mapbox} objeto(s) relevante(s) — "
            "pouca atividade detectada (+5 pontos)"
        )
    else:
        mapbox_score = 0
        reasoning.append(
            "YOLO Mapbox: nenhum objeto relevante detectado — sem evidência "
            "visual de atividade (+0 pontos)"
        )
    components["mapbox_score"] = mapbox_score

    # ----------------------------------------------------------------------
    # Componente 4 — YOLO Sentinel-2 (peso 5): confirmação macro.
    # Esperado detectar pouco (10m/pixel é insuficiente para COCO/DOTA);
    # qualquer detecção é bônus.
    # ----------------------------------------------------------------------
    sentinel_detections = int(yolo_sentinel["total_detections"])
    if sentinel_detections > 0:
        sentinel_score = 5
        reasoning.append(
            f"YOLO Sentinel-2: {sentinel_detections} detecção(ões) — "
            "confirmação adicional em baixa resolução (+5 pontos)"
        )
    else:
        sentinel_score = 0
        reasoning.append(
            "YOLO Sentinel-2: nenhuma detecção (esperado — resolução de "
            "10m/pixel limita detecção de objetos)"
        )
    components["sentinel_score"] = sentinel_score

    # ----------------------------------------------------------------------
    # Score final e decisão.
    # ----------------------------------------------------------------------
    total_score = ndbi_score + clip_score + mapbox_score + sentinel_score
    components["total"] = total_score

    if total_score >= 70:
        decision = "APROVADO"
        risk_level = "BAIXO"
        reasoning.append(
            f"\n🎯 DECISÃO: APROVADO (score {total_score}/100) — evidência "
            "espacial sólida de instalação empresarial real"
        )
    elif total_score >= 40:
        decision = "ATENÇÃO"
        risk_level = "MÉDIO"
        reasoning.append(
            f"\n🎯 DECISÃO: ATENÇÃO (score {total_score}/100) — há "
            "evidências, mas porte ou tipo da estrutura pode não condizer "
            "com declaração. Recomenda-se diligência adicional."
        )
    else:
        decision = "REPROVADO"
        risk_level = "ALTO"
        reasoning.append(
            f"\n🎯 DECISÃO: REPROVADO (score {total_score}/100) — sem "
            "evidência espacial suficiente de instalação física compatível"
        )

    return {
        "score": total_score,
        "decision": decision,
        "risk_level": risk_level,
        "reasoning": reasoning,
        "components": components,
    }
