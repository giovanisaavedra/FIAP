"""
Gerador de PDF de entrega acadêmica — SatVerify GS 2026.1.

Uso:
    python -m src.build_pdf

Saída:
    docs/SatVerify_GS_2026.pdf
"""

from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak,
    Table, TableStyle,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PDF = PROJECT_ROOT / "docs" / "SatVerify_GS_2026.pdf"
SCREENSHOTS_DIR = PROJECT_ROOT / "docs" / "screenshots"

# Cores institucionais
COLOR_PRIMARY = colors.HexColor("#1E3A8A")      # azul profundo
COLOR_SECONDARY = colors.HexColor("#FF9900")    # laranja AWS
COLOR_ACCENT = colors.HexColor("#10B981")       # verde aprovado
COLOR_WARN = colors.HexColor("#F59E0B")         # amarelo atenção
COLOR_DANGER = colors.HexColor("#EF4444")       # vermelho reprovado
COLOR_TEXT = colors.HexColor("#1F2937")
COLOR_MUTED = colors.HexColor("#6B7280")
COLOR_BG_TABLE = colors.HexColor("#F3F4F6")


def _build_styles():
    """Constrói folha de estilos customizada."""
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="CoverTitle",
        parent=styles["Heading1"],
        fontSize=28,
        textColor=COLOR_PRIMARY,
        alignment=TA_CENTER,
        spaceAfter=20,
        leading=34,
    ))
    styles.add(ParagraphStyle(
        name="CoverSubtitle",
        parent=styles["Heading2"],
        fontSize=16,
        textColor=COLOR_TEXT,
        alignment=TA_CENTER,
        spaceAfter=12,
        leading=20,
        keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="CoverCaption",
        parent=styles["Normal"],
        fontSize=11,
        textColor=COLOR_MUTED,
        alignment=TA_CENTER,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="H1Custom",
        parent=styles["Heading1"],
        fontSize=20,
        textColor=COLOR_PRIMARY,
        spaceBefore=24,
        spaceAfter=14,
        leading=24,
        keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="H2Custom",
        parent=styles["Heading2"],
        fontSize=15,
        textColor=COLOR_TEXT,
        spaceBefore=16,
        spaceAfter=8,
        leading=20,
        keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="H3Custom",
        parent=styles["Heading3"],
        fontSize=12,
        textColor=COLOR_TEXT,
        spaceBefore=12,
        spaceAfter=6,
        leading=16,
        keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="BodyJustified",
        parent=styles["Normal"],
        fontSize=10.5,
        textColor=COLOR_TEXT,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        leading=15,
    ))
    styles.add(ParagraphStyle(
        name="BulletItem",
        parent=styles["Normal"],
        fontSize=10.5,
        textColor=COLOR_TEXT,
        alignment=TA_LEFT,
        leftIndent=18,
        bulletIndent=8,
        spaceAfter=4,
        leading=15,
    ))
    styles.add(ParagraphStyle(
        name="Callout",
        parent=styles["Normal"],
        fontSize=10,
        textColor=COLOR_PRIMARY,
        alignment=TA_JUSTIFY,
        leftIndent=20,
        rightIndent=20,
        spaceBefore=8,
        spaceAfter=8,
        leading=14,
    ))
    styles.add(ParagraphStyle(
        name="FigCaption",
        parent=styles["Normal"],
        fontSize=9,
        textColor=COLOR_MUTED,
        alignment=TA_CENTER,
        spaceAfter=14,
        leading=12,
    ))
    styles.add(ParagraphStyle(
        name="QueroConcorrer",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=16,
        textColor=colors.HexColor("#1F4E79"),
        alignment=TA_CENTER,
        spaceBefore=24,
        spaceAfter=24,
        borderWidth=2,
        borderColor=colors.HexColor("#1F4E79"),
        borderPadding=12,
        borderRadius=4,
    ))
    return styles


def _add_image_if_exists(story, image_path: Path, caption: str, width_cm: float = 15):
    """
    Adiciona imagem ao story preservando o aspect ratio.

    Se o arquivo não existir, mostra placeholder textual.

    Args:
        story: lista da reportlab Platypus story
        image_path: caminho do arquivo PNG/JPG
        caption: legenda da figura (vai abaixo da imagem)
        width_cm: largura desejada em cm (a altura é calculada proporcionalmente)
    """
    from PIL import Image as PILImage  # import local para evitar quebrar se PIL faltar

    styles = _build_styles()

    if image_path.exists():
        try:
            # Lê dimensões reais com Pillow antes de passar para reportlab.
            with PILImage.open(image_path) as pil_img:
                original_width, original_height = pil_img.size

            # Calcula altura proporcional baseada na largura desejada.
            target_width = width_cm * cm
            aspect_ratio = original_height / original_width
            target_height = target_width * aspect_ratio

            # Limita altura máxima para não estourar a página A4 (~25cm úteis).
            max_height = 20 * cm
            if target_height > max_height:
                target_height = max_height
                target_width = target_height / aspect_ratio

            # Cria imagem com width E height explícitos — reportlab respeita
            # a proporção em vez de tentar deduzir e achatar lateralmente.
            img = Image(
                str(image_path),
                width=target_width,
                height=target_height,
                hAlign="CENTER",
            )
            story.append(img)
        except Exception as e:
            story.append(Paragraph(
                f"[Imagem indisponível: {image_path.name} — {e}]",
                styles["FigCaption"]
            ))
    else:
        story.append(Paragraph(
            f"[PLACEHOLDER — adicionar imagem em "
            f"<i>{image_path.relative_to(PROJECT_ROOT)}</i>]",
            styles["FigCaption"]
        ))

    story.append(Paragraph(caption, styles["FigCaption"]))


def _make_table(data, col_widths=None, header_color=None):
    """Cria tabela estilizada."""
    header_color = header_color or COLOR_PRIMARY
    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), header_color),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_BG_TABLE]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D1D5DB")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return tbl


def _format_month_pt(dt: datetime) -> str:
    """Formata data em português."""
    months_pt = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
    }
    return f"{months_pt[dt.month]} de {dt.year}"


def _add_page_number(canvas, doc):
    """Desenha o número da página no rodapé centralizado (exceto capa)."""
    if doc.page == 1:
        return
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#666666"))
    page_width = canvas._pagesize[0]
    canvas.drawCentredString(page_width / 2.0, 1.2 * cm, str(doc.page))
    canvas.restoreState()


def build_pdf():
    """Função principal: monta o PDF inteiro e salva."""
    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
        title="SatVerify — FIAP GS 2026.1",
        author="Giovani Saavedra & Marcio Elifas",
    )

    styles = _build_styles()
    story = []

    # ===========================================================
    # CAPA
    # ===========================================================
    story.append(Spacer(1, 4 * cm))
    story.append(Paragraph("🛰️ SatVerify", styles["CoverTitle"]))
    story.append(Paragraph(
        "Plataforma de Due Diligence Empresarial<br/>via Inteligência Espacial",
        styles["CoverSubtitle"]
    ))
    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph(
        "<i>Validação automatizada de existência e atividade de empresas<br/>"
        "em endereços declarados, combinando imagens de satélite,<br/>"
        "visão computacional e IA cognitiva.</i>",
        styles["CoverCaption"]
    ))
    story.append(Spacer(1, 3.5 * cm))
    story.append(Paragraph(
        "<b>FIAP — Faculdade de Informática e Administração Paulista</b>",
        styles["CoverCaption"]
    ))
    story.append(Paragraph(
        "Global Solution 2026.1 — Inteligência Artificial (1º Ano)",
        styles["CoverCaption"]
    ))
    story.append(Spacer(1, 1.2 * cm))
    story.append(Paragraph("<b>Equipe</b>", styles["CoverCaption"]))
    story.append(Paragraph(
        "Giovani Saavedra — RM566797<br/>"
        "Marcio Elifas — RM567871",
        styles["CoverCaption"]
    ))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        "<b>Tutora:</b> Sabrina Otoni<br/>"
        "<b>Coordenador:</b> André Godoi Chiovatto",
        styles["CoverCaption"]
    ))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("QUERO CONCORRER", styles["QueroConcorrer"]))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        _format_month_pt(datetime.now()),
        styles["CoverCaption"]
    ))
    story.append(PageBreak())

    # ===========================================================
    # SUMÁRIO
    # ===========================================================
    story.append(Paragraph("Sumário", styles["H1Custom"]))
    toc_items = [
        ("1.", "Introdução", "3"),
        ("1.1", "O problema da fraude empresarial", "3"),
        ("1.2", "A oportunidade da inteligência espacial", "3"),
        ("1.3", "Objetivo e escopo da POC", "4"),
        ("2.", "Desenvolvimento", "5"),
        ("2.1", "Arquitetura técnica e stack tecnológico", "5"),
        ("2.2", "Pipeline de processamento (9 etapas)", "7"),
        ("2.3", "Decisões arquiteturais críticas", "9"),
        ("2.4", "Integração com AWS S3", "12"),
        ("2.5", "Integração com as disciplinas do curso", "13"),
        ("3.", "Resultados", "14"),
        ("3.1", "Casos de demonstração validados", "14"),
        ("3.2", "Métricas comparativas", "16"),
        ("3.3", "Padrões de fraude detectados", "17"),
        ("4.", "Conclusões", "19"),
        ("4.1", "Lições aprendidas", "19"),
        ("4.2", "Limitações conhecidas", "20"),
        ("4.3", "Trabalho futuro", "21"),
        ("5.", "Referências", "22"),
    ]
    toc_data = [["#", "Seção", "Página"]] + toc_items
    story.append(_make_table(
        toc_data,
        col_widths=[1.2 * cm, 12 * cm, 2.5 * cm],
    ))
    story.append(PageBreak())

    # ===========================================================
    # 1. INTRODUÇÃO
    # ===========================================================
    story.append(Paragraph("1. Introdução", styles["H1Custom"]))

    story.append(Paragraph("1.1 O problema da fraude empresarial", styles["H2Custom"]))
    story.append(Paragraph(
        "Segundo o Escritório das Nações Unidas sobre Drogas e Crime (UNODC) [8], a "
        "lavagem de dinheiro movimenta entre US$ 800 bilhões e US$ 2 trilhões anualmente "
        "em escala global — o equivalente a 2-5% do PIB mundial. Um vetor recorrente "
        "atividade é a declaração de endereços empresariais incompatíveis com a operação "
        "real: fábricas que são apenas escritórios, atacadistas que operam de boxes de "
        "comércio popular, empresas com endereço em áreas de preservação ambiental.",
        styles["BodyJustified"]
    ))
    story.append(Paragraph(
        "Due Diligence empresarial — tradicionalmente associada à compliance bancária "
        "(KYB — <i>Know Your Business</i>) e ao combate à lavagem de dinheiro (AML — "
        "<i>Anti-Money Laundering</i>) — depende historicamente de visitas presenciais, "
        "validação manual de documentos e cruzamento com bases públicas. É um processo "
        "caro, lento, e que não escala diante do volume de empresas a verificar em uma "
        "economia globalizada.",
        styles["BodyJustified"]
    ))

    story.append(Paragraph("1.2 A oportunidade da inteligência espacial", styles["H2Custom"]))
    story.append(Paragraph(
        "Imagens de satélite tornaram-se um recurso de qualidade comercial nos últimos "
        "anos. A constelação Sentinel-2, da Agência Espacial Europeia (ESA), oferece "
        "imagens multiespectrais gratuitas com resolução de 10 metros por pixel e "
        "revisita global de 5 dias. Provedores comerciais como Mapbox e Maxar oferecem "
        "imagens aéreas com resolução submetro acessíveis via APIs.",
        styles["BodyJustified"]
    ))
    story.append(Paragraph(
        "Paralelamente, modelos de visão computacional (YOLO, CLIP, SAM) e modelos de "
        "linguagem (Gemini, GPT) democratizaram acesso a capacidades de inferência que "
        "há cinco anos exigiriam equipes especializadas. Combinar essas duas tendências "
        "— dados geoespaciais acessíveis e inferência cognitiva via IA — abre espaço "
        "para uma nova geração de produtos de compliance.",
        styles["BodyJustified"]
    ))

    story.append(Paragraph("1.3 Objetivo e escopo da POC", styles["H2Custom"]))
    story.append(Paragraph(
        "Este projeto desenvolve uma Prova de Conceito (POC) chamada <b>SatVerify</b>, "
        "que automatiza a verificação inicial de endereços empresariais combinando:",
        styles["BodyJustified"]
    ))
    bullets = [
        "<b>Geocoding</b> do endereço declarado (Nominatim / OpenStreetMap)",
        "<b>Análise espectral</b> via Sentinel-2 (NDBI — densidade construída)",
        "<b>Detecção de objetos</b> via YOLOv8-OBB (DOTA) em imagem aérea",
        "<b>Classificação semântica</b> via CLIP zero-shot",
        "<b>Síntese cognitiva</b> via Google Gemini 2.5 Flash Lite",
        "<b>Persistência auditável</b> em AWS S3 com presigned URLs",
        "<b>Dashboard interativo</b> via Streamlit para demonstração",
    ]
    for b in bullets:
        story.append(Paragraph(f"• {b}", styles["BulletItem"]))

    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        "A POC produz uma decisão estruturada (APROVADO / ATENÇÃO / REPROVADO) com "
        "score 0-100 e relatório textual interpretável pelo analista humano. O escopo "
        "deliberadamente exclui validação documental, integração CNPJ e visita "
        "presencial — esses ficam como atribuições do analista que receberá o output.",
        styles["BodyJustified"]
    ))
    story.append(PageBreak())

    # ===========================================================
    # 2. DESENVOLVIMENTO
    # ===========================================================
    story.append(Paragraph("2. Desenvolvimento", styles["H1Custom"]))

    story.append(Paragraph("2.1 Arquitetura técnica e stack tecnológico", styles["H2Custom"]))
    story.append(Paragraph(
        "O sistema foi construído em Python 3.11 com arquitetura modular em torno de "
        "um pipeline sequencial. Cada etapa é um módulo independente em <i>src/</i>, "
        "permitindo substituição de provedores ou modelos sem alterar a orquestração.",
        styles["BodyJustified"]
    ))

    stack_data = [
        ["Camada", "Tecnologia", "Função"],
        ["Linguagem", "Python 3.11", "Backend e pipeline"],
        ["Geocoding", "Nominatim (OSM)", "Endereço → lat/lon"],
        ["Satélite", "Sentinel-2 L2A via CDSE", "Bandas espectrais"],
        ["Aerial", "Mapbox Static Images API", "Imagem 1024×1024 zoom 18"],
        ["Visão (objetos)", "YOLOv8n-OBB / DOTA", "Detecção em imagem aérea"],
        ["Visão (cena)", "CLIP ViT-B/32 (HuggingFace)", "Classificação zero-shot"],
        ["LLM", "Google Gemini 2.5 Flash Lite", "Relatório DD textual"],
        ["Storage", "AWS S3 (us-east-1)", "Persistência auditável"],
        ["Frontend", "Streamlit", "Dashboard interativo"],
        ["ML Framework", "PyTorch + Transformers", "Inferência CLIP"],
    ]
    story.append(_make_table(stack_data, col_widths=[3.5 * cm, 5.5 * cm, 6.5 * cm]))
    story.append(Spacer(1, 0.4 * cm))

    _add_image_if_exists(
        story,
        SCREENSHOTS_DIR / "01_dashboard_home.png",
        "Figura 1 — Tela inicial do dashboard Streamlit, com sidebar de controle "
        "(3 botões de casos de demonstração + entrada para nova análise) e área principal "
        "explicando o produto e os 4 passos do pipeline.",
        width_cm=15,
    )

    story.append(Paragraph("2.2 Pipeline de processamento (9 etapas)", styles["H2Custom"]))
    story.append(Paragraph(
        "Cada análise SatVerify percorre 9 etapas sequenciais, totalizando entre 15 "
        "e 30 segundos por execução em hardware CPU comum (MacBook Air Apple Silicon).",
        styles["BodyJustified"]
    ))

    pipeline_data = [
        ["#", "Etapa", "Tempo médio", "Tecnologia"],
        ["1", "Geocoding (endereço → coord)", "~0.5s", "Nominatim"],
        ["2", "Sentinel-2 (cena mais limpa)", "~3-5s", "CDSE OData + Process"],
        ["3", "NDBI (densidade construída)", "~0.3s", "NumPy"],
        ["4", "Mapbox aerial 1024×1024", "~1-2s", "Mapbox Static"],
        ["5", "YOLO em Sentinel-2", "~0.5s", "Ultralytics"],
        ["6", "YOLO em Mapbox", "~0.5s", "Ultralytics"],
        ["7", "CLIP zero-shot", "~1-2s", "HuggingFace"],
        ["8", "Gemini relatório DD", "~3-5s", "google-genai SDK"],
        ["9", "Upload AWS S3", "~2-3s", "boto3"],
    ]
    story.append(_make_table(pipeline_data, col_widths=[1 * cm, 6.5 * cm, 3 * cm, 4 * cm]))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("2.3 Decisões arquiteturais críticas", styles["H2Custom"]))
    story.append(Paragraph(
        "Durante o desenvolvimento, várias decisões foram tomadas com base em testes "
        "empíricos. Cada uma delas foi documentada em <i>docs/PROJECT_DECISIONS.md</i>. "
        "Aqui sintetizamos as cinco mais impactantes.",
        styles["BodyJustified"]
    ))

    story.append(Paragraph("Descoberta 1 — NDBI sozinho não basta", styles["H3Custom"]))
    story.append(Paragraph(
        "O índice NDBI (<i>Normalized Difference Built-up Index</i>), calculado a "
        "partir das bandas SWIR e NIR do Sentinel-2, mede densidade de área construída. "
        "É um excelente proxy para presença de infraestrutura, mas <b>não distingue tipos "
        "de uso</b>. O Caso 2 da nossa demonstração (comércio popular na Rua 25 de Março) "
        "apresentou NDBI de 77,7% — maior que o Caso 1 (Volkswagen, 45,1%). Isso "
        "demonstrou que NDBI sozinho confundiria casos opostos. A decisão foi adicionar "
        "uma camada semântica complementar.",
        styles["BodyJustified"]
    ))

    story.append(Paragraph("Descoberta 2 — YOLO COCO falha em imagens aéreas", styles["H3Custom"]))
    story.append(Paragraph(
        "YOLOv8 padrão é treinado no dataset COCO (objetos do cotidiano em ângulo "
        "horizontal). Em imagens aéreas (top-down), o modelo detecta zero objetos em "
        "pátios industriais. A migração para YOLOv8n-OBB treinado em DOTA (<i>Dataset "
        "of Object detection in Aerial Images</i>) resolveu parcialmente — mas o "
        "viés geográfico do DOTA (treinado em imagens chinesas) ainda limita "
        "detecções em zonas brasileiras.",
        styles["BodyJustified"]
    ))

    story.append(Paragraph("Descoberta 3 — CLIP como solução pivote", styles["H3Custom"]))
    story.append(Paragraph(
        "Após três iterações sem sucesso no YOLO, adotamos CLIP (<i>Contrastive "
        "Language-Image Pre-training</i>) da OpenAI como camada complementar. CLIP "
        "é um modelo multimodal que permite <b>classificação zero-shot</b>: definimos "
        "categorias semânticas em linguagem natural (\"a planta industrial vista de "
        "cima\", \"uma área comercial densa com pequenos boxes\", \"uma área verde "
        "com vegetação\") e CLIP retorna probabilidades. Resolução em 30 linhas de "
        "código Python, rodando em CPU em segundos.",
        styles["BodyJustified"]
    ))
    story.append(Paragraph(
        "<i>Quando uma técnica entra em rendimento decrescente, vale mais pivotar "
        "para abordagem complementar do que insistir. Adicionamos CLIP não para "
        "'substituir' o YOLO, mas para complementá-lo com um sinal diferente: "
        "classificação semântica da cena em vez de detecção de objetos pontuais. "
        "Resultado: dois sinais independentes que se validam mutuamente.</i>",
        styles["Callout"]
    ))

    story.append(Paragraph("Descoberta 4 — Geocoding administrativo ≠ operacional", styles["H3Custom"]))
    story.append(Paragraph(
        "Ao testar com o endereço \"Av. Volkswagen, 100, São Bernardo do Campo\", "
        "o Nominatim resolveu para uma área administrativa da Volkswagen (escritório "
        "ou portaria), não para a planta industrial em si. A imagem Mapbox revelou "
        "zona residencial mista. <b>Isso não é bug — é exatamente o tipo de fraude "
        "que due diligence deve detectar.</b> Uma empresa pode declarar um endereço "
        "tecnicamente correto (com nome industrial conhecido) sabendo que ali está "
        "apenas a recepção, enquanto a operação real está em outro lugar — ou não "
        "existe.",
        styles["BodyJustified"]
    ))

    story.append(Paragraph("Descoberta 5 — Graceful degradation", styles["H3Custom"]))
    story.append(Paragraph(
        "O pipeline depende de 6 integrações externas (Nominatim, CDSE, Mapbox, "
        "Gemini, AWS, modelos ML). Cada uma é um ponto potencial de falha. "
        "Implementamos <i>graceful degradation</i>: se o upload S3 falhar, a análise "
        "local continua. Se o Gemini estiver indisponível, o sistema entrega os "
        "sinais técnicos sem relatório textual. Esse princípio reflete maturidade "
        "arquitetural — produtos enterprise raramente quebram inteiros porque um "
        "componente externo falhou.",
        styles["BodyJustified"]
    ))

    story.append(PageBreak())

    story.append(Paragraph("2.4 Integração com AWS S3", styles["H2Custom"]))
    story.append(Paragraph(
        "A persistência auditável em nuvem foi implementada usando AWS S3 (região "
        "us-east-1). O bucket dedicado <i>fiap-gs-satverify-2026</i> recebe todos os "
        "artefatos de cada análise, organizados sob o prefixo <i>analyses/&lt;uuid&gt;/</i>:",
        styles["BodyJustified"]
    ))
    s3_bullets = [
        "<i>metadata.json</i> — dicionário consolidado com todos os sinais técnicos",
        "<i>sentinel_rgb.png</i> — imagem RGB do satélite",
        "<i>ndbi.png</i> — visualização do índice NDBI",
        "<i>mapbox_aerial.png</i> — imagem aérea de alta resolução",
        "<i>yolo_*_annotated.png</i> — imagens com bounding boxes YOLO",
        "<i>dd_report.md</i> — relatório textual gerado pelo Gemini",
    ]
    for b in s3_bullets:
        story.append(Paragraph(f"• {b}", styles["BulletItem"]))

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "Além do upload, o dashboard implementa três funcionalidades enterprise: "
        "(1) <b>URLs pré-assinadas</b> com expiração de 1 hora para download seguro "
        "sem expor credenciais; (2) <b>link direto para o console AWS</b> permitindo "
        "auditoria via interface oficial; (3) <b>painel de estatísticas de uso</b> "
        "mostrando storage consumido, percentual do Free Tier e custo estimado.",
        styles["BodyJustified"]
    ))

    _add_image_if_exists(
        story,
        SCREENSHOTS_DIR / "03a_painel_aws_s3.png",
        "Figura 2 — Painel AWS S3 no dashboard (parte 1): informações do bucket, "
        "botão para acesso direto ao console AWS e seção de Downloads Diretos com "
        "URLs pré-assinadas válidas por 1 hora.",
        width_cm=15,
    )

    _add_image_if_exists(
        story,
        SCREENSHOTS_DIR / "03b_painel_aws_s3.png",
        "Figura 3 — Painel AWS S3 no dashboard (parte 2): estatísticas de uso "
        "(total de arquivos, storage usado, % do Free Tier, custo estimado) e "
        "checklist de boas práticas aplicadas (bucket privado, IAM dedicado, "
        "budget alarm).",
        width_cm=15,
    )

    _add_image_if_exists(
        story,
        SCREENSHOTS_DIR / "07_aws_console_bucket.png",
        "Figura 4 — Console AWS S3 mostrando as análises persistidas (uma pasta "
        "por analysis_id), demonstrando integração efetiva com a nuvem.",
        width_cm=15,
    )

    # ===========================================================
    # 2.5 — Integração com as disciplinas do curso
    # ===========================================================
    story.append(Paragraph(
        "2.5 Integração com as disciplinas do curso",
        styles["H2Custom"]
    ))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(
        "O SatVerify foi concebido como aplicação prática integrada das nove "
        "disciplinas que compõem o primeiro ano do curso de Inteligência "
        "Artificial da FIAP. A seguir, descrevemos como cada disciplina se "
        "manifesta no projeto.",
        styles["BodyJustified"]
    ))
    story.append(Spacer(1, 0.3 * cm))

    # Disciplina 1 — AI Challenges
    story.append(Paragraph(
        "<b>AI Challenges.</b> O projeto inteiro é um exercício de identificação "
        "e resolução de um desafio real de IA. Partimos de um problema concreto "
        "— a fraude empresarial, que movimenta entre US$ 800 bilhões e US$ 2 "
        "trilhões anuais segundo o UNODC — e construímos uma POC que demonstra "
        "viabilidade técnica e econômica. Decisões pragmáticas documentadas na "
        "seção 2.3, como pivotar de YOLO para CLIP após três iterações sem "
        "sucesso (Descoberta 3) e implementar graceful degradation diante de "
        "seis integrações externas (Descoberta 5), refletem a maturidade "
        "exigida pela disciplina ao lidar com problemas reais e suas restrições.",
        styles["BodyJustified"]
    ))
    story.append(Spacer(1, 0.2 * cm))

    # Disciplina 2 — AI Computer Systems & Sensors
    story.append(Paragraph(
        "<b>AI Computer Systems &amp; Sensors.</b> Embora o projeto não utilize "
        "ESP32 ou sensores embarcados — o escopo é cloud-native — ele trabalha "
        "extensivamente com sensores remotos: o instrumento multiespectral MSI "
        "da constelação Sentinel-2 da ESA, que capta seis bandas espectrais "
        "relevantes a 10 metros de resolução, e os sensores aéreos "
        "fotogramétricos que alimentam o Mapbox a 0,5 metro por pixel. Os "
        "dados desses sensores são processados em hardware CPU comum (MacBook "
        "Air com Apple Silicon), demonstrando que computação espacial avançada "
        "é viável fora de centros de processamento dedicados.",
        styles["BodyJustified"]
    ))
    story.append(Spacer(1, 0.2 * cm))

    # Disciplina 3 — Cognitive Cybersecurity
    story.append(Paragraph(
        "<b>Cognitive Cybersecurity.</b> O SatVerify aplica diretamente "
        "cibersegurança cognitiva ao domínio de Anti-Money Laundering (AML) e "
        "Know Your Business (KYB). Implementamos segurança em camadas: bucket "
        "S3 privado com Block-All-Public-Access, usuário IAM dedicado não-root "
        "com política mínima, credenciais via variáveis de ambiente (nunca "
        "commitadas no repositório), URLs pré-assinadas com expiração de uma "
        "hora, e auditabilidade completa via persistência em nuvem. Cada "
        "análise é registrada com UUID próprio e timestamp, criando trilha "
        "auditável compatível com requisitos regulatórios de compliance "
        "bancário.",
        styles["BodyJustified"]
    ))
    story.append(Spacer(1, 0.2 * cm))

    # Disciplina 4 — Cognitive Data Science
    story.append(Paragraph(
        "<b>Cognitive Data Science.</b> Quase todos os pilares de Ciência de "
        "Dados Cognitiva do curso encontram aplicação no projeto. O dashboard "
        "interativo foi construído em Streamlit, com sidebar de controle, "
        "painéis de evidências visuais, downloads diretos e estatísticas de "
        "uso. A busca de cenas Sentinel-2 implementa análise temporal com "
        "lookback de 120 dias para encontrar a cena mais limpa disponível. "
        "Dados espaciais estão presentes em toda etapa — geocoding, bounding "
        "boxes orientados, raster multibandas georreferenciado. A persistência "
        "de metadados em formato JSON estruturado no S3 ecoa princípios de "
        "modelagem orientada a documentos. E a síntese cognitiva final é "
        "executada pelo Gemini 2.5 Flash Lite, que transforma sinais numéricos "
        "heterogêneos em narrativa interpretável pelo analista humano.",
        styles["BodyJustified"]
    ))
    story.append(Spacer(1, 0.2 * cm))

    # Disciplina 5 — Computational Thinking with Python
    story.append(Paragraph(
        "<b>Computational Thinking with Python.</b> A POC é integralmente "
        "desenvolvida em Python 3.11, aplicando princípios fundamentais do "
        "pensamento computacional: decomposição (cada uma das 9 etapas do "
        "pipeline é um módulo independente em src/), abstração (provedores "
        "externos podem ser substituídos sem alterar a orquestração), "
        "reutilização (componentes compartilhados entre os três casos de "
        "demonstração e novas análises) e tratamento sistemático de exceções "
        "(graceful degradation diante de falhas externas). O projeto inclui "
        "gerenciamento adequado de dependências via requirements.txt, "
        "ambiente virtualizado isolado, e versionamento estruturado em "
        "Git/GitHub seguindo boas práticas de engenharia de software.",
        styles["BodyJustified"]
    ))
    story.append(Spacer(1, 0.2 * cm))

    # Disciplina 6 — Formação Social e Sustentabilidade
    story.append(Paragraph(
        "<b>Formação Social e Sustentabilidade.</b> O SatVerify ataca um "
        "problema com forte impacto social — a lavagem de dinheiro compromete "
        "2 a 5% do PIB mundial e financia atividades criminais que afetam "
        "diretamente comunidades vulneráveis. A POC democratiza o acesso a "
        "ferramentas de compliance, tradicionalmente caras e restritas a "
        "grandes instituições financeiras, viabilizando-as via APIs públicas "
        "e dados abertos (Sentinel-2 gratuito por política de dados da ESA). "
        "No eixo de sustentabilidade ambiental, o Caso 3 (Parque Estadual da "
        "Cantareira) demonstra capacidade direta de detectar empresas-fantasma "
        "declaradas em unidades de conservação — aplicação imediata de "
        "tecnologia espacial para defesa de patrimônio ecológico nacional.",
        styles["BodyJustified"]
    ))
    story.append(Spacer(1, 0.2 * cm))

    # Disciplina 7 — Machine Learning & Modelling
    story.append(Paragraph(
        "<b>Machine Learning &amp; Modelling.</b> Múltiplas técnicas de ML são "
        "empregadas em complementariedade. O CLIP zero-shot (OpenAI, 2021) "
        "exemplifica aprendizado não supervisionado aplicado a classificação "
        "semântica de cenas, sem necessidade de fine-tuning ou rotulação "
        "manual. O YOLOv8-OBB treinado no dataset DOTA aplica transfer "
        "learning: utilizamos um modelo pré-treinado em imagens aéreas "
        "chinesas e o aplicamos a um novo domínio (Brasil) sem retreinamento. "
        "A modelagem da decisão final combina múltiplos sinais via score "
        "ponderado, decomposto de forma transparente (Figura 14) para que o "
        "analista compreenda como cada componente contribui — princípio de "
        "interpretabilidade central à disciplina.",
        styles["BodyJustified"]
    ))
    story.append(Spacer(1, 0.2 * cm))

    # Disciplina 8 — Plataformas, Serviços Cognitivos & Cloud Computing
    story.append(Paragraph(
        "<b>Plataformas, Serviços Cognitivos &amp; Cloud Computing.</b> O "
        "SatVerify integra seis plataformas externas em um único pipeline "
        "coerente: Nominatim/OSM (geocoding), Copernicus Data Space Ecosystem "
        "(busca e download Sentinel-2), Mapbox Static Images (imagem aérea de "
        "alta resolução), Google Gemini 2.5 Flash Lite (LLM para síntese "
        "cognitiva), AWS S3 (persistência auditável), e Ultralytics/Hugging "
        "Face (modelos de visão computacional). A camada AWS aplica práticas "
        "enterprise: IAM com política mínima, budget alarm em US$ 0,01, "
        "monitoramento contínuo de Free Tier, presigned URLs e organização "
        "hierárquica por UUID. Embora a POC atual rode localmente, a "
        "arquitetura modular permite migração imediata para deploy serverless "
        "(Lambda + S3 backend + Streamlit Cloud), conforme detalhado na "
        "seção 4.3.",
        styles["BodyJustified"]
    ))
    story.append(Spacer(1, 0.2 * cm))

    # Disciplina 9 — Redes Neurais Artificiais, Deep Learning e Algoritmos Genéticos
    story.append(Paragraph(
        "<b>Redes Neurais Artificiais, Deep Learning e Algoritmos "
        "Genéticos.</b> Duas arquiteturas de deep learning compõem o coração "
        "da inteligência visual do SatVerify. O YOLOv8 utiliza uma CNN "
        "profunda como backbone para detecção de objetos com bounding boxes "
        "orientados, capaz de identificar veículos, piscinas e estruturas em "
        "imagens aéreas top-down. O CLIP ViT-B/32 combina um Vision "
        "Transformer com encoder de texto, criando embeddings multimodais que "
        "permitem classificação semântica zero-shot a partir de descrições em "
        "linguagem natural. Ambos rodam sobre PyTorch e Hugging Face "
        "Transformers, demonstrando o estado da arte em redes neurais "
        "aplicado a um problema prático de inferência em CPU. Algoritmos "
        "genéticos não foram empregados na POC atual, mas estão previstos "
        "como evolução futura para otimização automática dos pesos do scoring "
        "com base em dataset rotulado por especialistas de compliance.",
        styles["BodyJustified"]
    ))
    story.append(Spacer(1, 0.3 * cm))

    # Parágrafo de fechamento
    story.append(Paragraph(
        "A integração das nove disciplinas no SatVerify não é mera "
        "justaposição de tecnologias — cada componente do projeto reflete "
        "conceitos específicos absorvidos ao longo do primeiro ano. A "
        "combinação dessas competências em uma POC coesa, auditável e "
        "tecnicamente sólida demonstra a aplicabilidade prática do currículo "
        "de IA da FIAP em problemas reais de impacto socioeconômico.",
        styles["BodyJustified"]
    ))
    story.append(Spacer(1, 0.5 * cm))

    story.append(PageBreak())

    # ===========================================================
    # 3. RESULTADOS
    # ===========================================================
    story.append(Paragraph("3. Resultados", styles["H1Custom"]))

    story.append(Paragraph("3.1 Casos de demonstração validados", styles["H2Custom"]))
    story.append(Paragraph(
        "O sistema foi validado com 3 casos representativos de padrões distintos de "
        "fraude empresarial. Cada caso ilustra um tipo diferente de incoerência que o "
        "sistema é capaz de detectar.",
        styles["BodyJustified"]
    ))

    # === CASO 1 ===
    story.append(Paragraph("Caso 1 — Fornecedor industrial declarado", styles["H3Custom"]))
    story.append(Paragraph(
        "<b>Endereço declarado:</b> Av. Volkswagen, 100, São Bernardo do Campo, SP<br/>"
        "<b>Contexto declarado:</b> Empresa declara ser fabricante industrial de "
        "autopeças com instalações de 5.000m²<br/>"
        "<b>Resultado:</b> Score 50/100 — Decisão ATENÇÃO — Risco MÉDIO",
        styles["BodyJustified"]
    ))
    story.append(Paragraph(
        "O Nominatim resolveu para uma área administrativa da Volkswagen ("
        "\"Parque Terra Nova I, Jardim Andréa Demarchi\"). NDBI de 45,1% indica "
        "alta densidade construída, mas o CLIP classificou a cena como predominantemente "
        "residencial (60%), com industrial em apenas 10%. Conclusão: o endereço "
        "geocodificado pode corresponder a anexo administrativo, não às instalações "
        "fabris.",
        styles["BodyJustified"]
    ))

    _add_image_if_exists(
        story,
        SCREENSHOTS_DIR / "02a_caso1_header_evidencias.png",
        "Figura 5 — Caso 1 (Volkswagen): cabeçalho da análise com decisão "
        "ATENÇÃO, score 50/100, risco MÉDIO e endereço resolvido pelo geocoding.",
        width_cm=15,
    )

    _add_image_if_exists(
        story,
        SCREENSHOTS_DIR / "02b_caso1_header_evidencias.png",
        "Figura 6 — Caso 1 (Volkswagen): quatro evidências visuais lado a lado — "
        "Sentinel-2 (10m/pixel), NDBI colorido, imagem aérea Mapbox (0,5m/pixel) "
        "e detecções YOLO sobre a imagem aérea.",
        width_cm=15,
    )

    # === CASO 2 ===
    story.append(Paragraph("Caso 2 — Atacadista declarado em comércio popular", styles["H3Custom"]))
    story.append(Paragraph(
        "<b>Endereço declarado:</b> Rua 25 de Março, 1000, São Paulo, SP<br/>"
        "<b>Contexto declarado:</b> Atacadista de eletrônicos com faturamento de "
        "R$ 200M/ano e instalações próprias compatíveis<br/>"
        "<b>Resultado:</b> Score 65/100 — Decisão ATENÇÃO — Risco MÉDIO",
        styles["BodyJustified"]
    ))
    story.append(Paragraph(
        "NDBI de 77,7% (maior do que o Caso 1!) sugere zona urbana extremamente "
        "densa. CLIP confirmou: <i>commercial_dense</i> com 74% de confiança. "
        "Esse caso é particularmente interessante: NDBI elevadíssimo poderia "
        "sugerir aprovação isolada, mas o tipo de zona detectada (comércio popular "
        "de pequenos boxes) é incompatível com porte declarado de R$ 200M anuais. "
        "Demonstra a necessidade de combinar múltiplas camadas.",
        styles["BodyJustified"]
    ))

    _add_image_if_exists(
        story,
        SCREENSHOTS_DIR / "02c_caso2_header.png",
        "Figura 7 — Caso 2 (Rua 25 de Março): cabeçalho da análise com decisão "
        "ATENÇÃO, score 65/100, risco MÉDIO. Apesar do NDBI elevado (77,7%), "
        "o tipo de zona observado é incompatível com porte declarado.",
        width_cm=15,
    )

    _add_image_if_exists(
        story,
        SCREENSHOTS_DIR / "02d_caso2_evidencias.png",
        "Figura 8 — Caso 2 (Rua 25 de Março): evidências visuais. Sentinel-2 e "
        "Mapbox revelam densidade urbana extrema típica de comércio popular, "
        "confirmada pela classificação CLIP como commercial_dense (74%).",
        width_cm=15,
    )

    # === CASO 3 ===
    story.append(Paragraph("Caso 3 — Endereço fantasma", styles["H3Custom"]))
    story.append(Paragraph(
        "<b>Endereço declarado:</b> Parque Estadual da Cantareira, São Paulo, SP<br/>"
        "<b>Contexto declarado:</b> Fábrica de R$ 50M/ano<br/>"
        "<b>Resultado:</b> Score 0/100 — Decisão REPROVADO — Risco ALTO",
        styles["BodyJustified"]
    ))
    story.append(Paragraph(
        "NDBI de 0,0% (área completamente verde), CLIP classifica como "
        "<i>green_area</i> com 100% de confiança, YOLO não detecta nenhum objeto. "
        "Red flag inequívoco: o endereço declarado corresponde a uma unidade de "
        "conservação ambiental. Decisão automatizada REPROVADO sem necessidade "
        "de diligência adicional.",
        styles["BodyJustified"]
    ))

    _add_image_if_exists(
        story,
        SCREENSHOTS_DIR / "06a_caso3_reprovado.png",
        "Figura 9 — Caso 3 (Cantareira): cabeçalho da análise com decisão "
        "REPROVADO, score 0/100, risco ALTO. Endereço corresponde a unidade de "
        "conservação ambiental.",
        width_cm=15,
    )

    _add_image_if_exists(
        story,
        SCREENSHOTS_DIR / "06b_caso3_reprovado.png",
        "Figura 10 — Caso 3 (Cantareira): evidências visuais confirmam "
        "predominância de mata atlântica nativa, sem infraestrutura compatível "
        "com a operação fabril declarada. NDBI zero, CLIP green_area 100%, YOLO "
        "sem detecções.",
        width_cm=15,
    )

    story.append(Paragraph("3.2 Métricas comparativas", styles["H2Custom"]))

    metrics_data = [
        ["Métrica", "Caso 1\n(VW)", "Caso 2\n(25 de Março)", "Caso 3\n(Cantareira)"],
        ["NDBI (% construído)", "45,1%", "77,7%", "0,0%"],
        ["NDBI médio", "0,059", "0,209", "−0,316"],
        ["YOLO Sentinel-2", "0 obj", "0 obj", "0 obj"],
        ["YOLO Mapbox", "2 obj", "2 obj", "0 obj"],
        ["CLIP categoria", "residential", "commercial_dense", "green_area"],
        ["CLIP confiança", "60%", "74%", "100%"],
        ["Score final", "50/100", "65/100", "0/100"],
        ["Decisão", "ATENÇÃO", "ATENÇÃO", "REPROVADO"],
        ["Risco", "MÉDIO", "MÉDIO", "ALTO"],
        ["Gemini palavras", "~570", "~563", "~434"],
        ["Tempo total", "~25s", "~22s", "~18s"],
    ]
    story.append(_make_table(metrics_data, col_widths=[4 * cm, 3.5 * cm, 4 * cm, 3.5 * cm]))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("3.3 Padrões de fraude detectados", styles["H2Custom"]))
    story.append(Paragraph(
        "Os três casos demonstram três padrões diferentes de fraude potencial, cada "
        "um detectado por uma combinação distinta de sinais:",
        styles["BodyJustified"]
    ))

    cell_style = ParagraphStyle(
        name="TableCell",
        parent=styles["Normal"],
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#1a1a1a"),
    )
    patterns_data = [
        ["Caso", "Padrão de fraude", "Sinal principal"],
        [
            Paragraph("1 — VW", cell_style),
            Paragraph("Endereço administrativo travestido de operacional", cell_style),
            Paragraph("CLIP detecta zona residencial onde se declara indústria", cell_style),
        ],
        [
            Paragraph("2 — 25 de Março", cell_style),
            Paragraph("Tipo de operação incompatível com porte declarado", cell_style),
            Paragraph("CLIP detecta comércio popular onde se declara atacadista", cell_style),
        ],
        [
            Paragraph("3 — Cantareira", cell_style),
            Paragraph("Endereço completamente fantasma", cell_style),
            Paragraph("NDBI zero, CLIP detecta área verde", cell_style),
        ],
    ]
    story.append(_make_table(patterns_data, col_widths=[3 * cm, 6.5 * cm, 7 * cm]))
    story.append(Spacer(1, 0.4 * cm))

    _add_image_if_exists(
        story,
        SCREENSHOTS_DIR / "04a_relatorio_gemini.png",
        "Figura 11 — Relatório Gemini (parte 1): cabeçalho com identificação da "
        "empresa e endereço, Resumo Executivo sintetizando o achado principal "
        "e a recomendação, e início da Análise das Evidências.",
        width_cm=15,
    )

    _add_image_if_exists(
        story,
        SCREENSHOTS_DIR / "04b_relatorio_gemini.png",
        "Figura 12 — Relatório Gemini (parte 2): continuação da Análise das "
        "Evidências (NDBI, CLIP, YOLO), seção de Red Flags Identificados e "
        "início da Recomendação Final.",
        width_cm=15,
    )

    _add_image_if_exists(
        story,
        SCREENSHOTS_DIR / "04c_relatorio_gemini.png",
        "Figura 13 — Relatório Gemini (parte 3): conclusão da Recomendação "
        "Final com próximos passos sugeridos e seção de Limitações da análise "
        "automatizada.",
        width_cm=15,
    )

    _add_image_if_exists(
        story,
        SCREENSHOTS_DIR / "05_decomposicao_score.png",
        "Figura 14 — Decomposição transparente do score: cada componente (NDBI, "
        "CLIP, YOLO Mapbox, YOLO Sentinel) contribui com pontuação ponderada. "
        "Permite ao analista entender por que o sistema chegou à decisão final.",
        width_cm=15,
    )

    _add_image_if_exists(
        story,
        SCREENSHOTS_DIR / "08a_yolo_detection_zoom.png",
        "Figura 15 — Detecção YOLO em zoom (parte 1): bounding boxes orientados "
        "sobre imagem Mapbox de alta resolução, mostrando objetos identificados "
        "pelo modelo YOLOv8-OBB treinado em DOTA.",
        width_cm=15,
    )

    _add_image_if_exists(
        story,
        SCREENSHOTS_DIR / "08b_yolo_detection_zoom.png",
        "Figura 16 — Detecção YOLO em zoom (parte 2): outro exemplo de "
        "detecção do mesmo modelo, demonstrando capacidade de identificar "
        "veículos e estruturas mesmo em ângulo aéreo top-down vertical.",
        width_cm=15,
    )

    story.append(PageBreak())

    # ===========================================================
    # 4. CONCLUSÕES
    # ===========================================================
    story.append(Paragraph("4. Conclusões", styles["H1Custom"]))

    story.append(Paragraph("4.1 Lições aprendidas", styles["H2Custom"]))
    story.append(Paragraph(
        "O desenvolvimento do SatVerify produziu cinco lições principais, "
        "documentadas em detalhe em <i>docs/PROJECT_DECISIONS.md</i>:",
        styles["BodyJustified"]
    ))
    lessons = [
        "<b>Sinais isolados são insuficientes.</b> Nenhum dos 4 sinais técnicos "
        "(NDBI, YOLO Sentinel, YOLO Mapbox, CLIP) sozinho é capaz de classificar "
        "corretamente os 3 casos. Apenas a combinação ponderada produz decisões "
        "coerentes.",

        "<b>Iteração com critério de parada é virtude.</b> Após 3 tentativas no "
        "YOLO sem sucesso satisfatório, pivotar para CLIP foi mais valioso do que "
        "continuar otimizando. Saber quando parar de iterar é parte do método.",

        "<b>IA cognitiva moderna substitui pipelines complexos.</b> CLIP zero-shot "
        "resolveu em 30 linhas de código um problema que exigiria semanas de "
        "fine-tuning de uma CNN customizada. Discurso de produto: usar modelos "
        "fundacionais quando suficientes.",

        "<b>Fraudes reais começam em pequenas incoerências.</b> O Caso 1 "
        "(Volkswagen) demonstrou o tipo mais sutil — endereço tecnicamente correto, "
        "mas geográfica e operacionalmente incompatível. Um sistema que detecta isso "
        "automaticamente é genuinamente útil.",

        "<b>Graceful degradation é decisão de produto.</b> Em arquiteturas com "
        "múltiplas integrações externas, robustez vs falhas é tão importante quanto "
        "performance no caminho feliz.",
    ]
    for l in lessons:
        story.append(Paragraph(f"• {l}", styles["BulletItem"]))

    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("4.2 Limitações conhecidas", styles["H2Custom"]))
    limits = [
        "<b>Cobertura de nuvens:</b> Sentinel-2 raramente tem cobertura zero. "
        "Implementamos lookback de 120 dias para encontrar a melhor cena disponível.",

        "<b>Geocoding ambíguo:</b> Endereços imprecisos ou em zonas rurais podem "
        "resolver para pontos inesperados (que pode ser red flag legítimo).",

        "<b>YOLO em imagens aéreas brasileiras:</b> Modelo DOTA tem viés geográfico "
        "(treinado em imagens chinesas). Detecções podem ser inconsistentes.",

        "<b>CLIP em vocabulário fixo:</b> Categorias semânticas são pré-definidas. "
        "Cenas atípicas (porto, aeroporto, mineração) podem não se encaixar bem.",

        "<b>Custos AWS S3:</b> Free tier de 5GB cobre POC, mas produção exige "
        "monitoramento contínuo de uso.",
    ]
    for l in limits:
        story.append(Paragraph(f"• {l}", styles["BulletItem"]))

    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("4.3 Trabalho futuro", styles["H2Custom"]))
    future = [
        "Fine-tuning de YOLO ou CLIP com dataset brasileiro anotado",
        "Análise temporal de NDBI (detectar construção/demolição recente "
        "que indique fraude de \"empresa nova\" em estrutura antiga)",
        "Detecção de anomalias com autoencoders sobre embeddings CLIP",
        "Cross-referencing com bases públicas (CNPJ, alvarás municipais, ICMS)",
        "Deploy em nuvem (Streamlit Cloud + S3 backend + Lambda para "
        "execução assíncrona em batch)",
        "Integração com AWS CloudTrail para auditoria completa de acessos",
        "Refinamento dos pesos de scoring com dataset rotulado por especialistas "
        "humanos (compliance officers)",
    ]
    for f in future:
        story.append(Paragraph(f"• {f}", styles["BulletItem"]))

    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        "<i>SatVerify demonstra que due diligence empresarial moderna pode ser "
        "substancialmente automatizada combinando dados geoespaciais públicos, "
        "modelos de visão computacional open-source e LLMs de baixo custo. O "
        "produto, em sua forma atual, já é capaz de pré-classificar empresas em "
        "três níveis de risco com base em sinais físicos verificáveis, oferecendo "
        "ao analista humano um ponto de partida estruturado e auditável.</i>",
        styles["Callout"]
    ))

    story.append(PageBreak())

    # ===========================================================
    # 5. REFERÊNCIAS
    # ===========================================================
    story.append(Paragraph("5. Referências", styles["H1Custom"]))

    refs = [
        "ESA — European Space Agency. <i>Sentinel-2 Mission</i>. Disponível em "
        "https://sentinel.esa.int/web/sentinel/missions/sentinel-2",

        "Copernicus Data Space Ecosystem. <i>Sentinel Hub APIs</i>. "
        "https://dataspace.copernicus.eu/",

        "Mapbox. <i>Static Images API Documentation</i>. "
        "https://docs.mapbox.com/api/maps/static-images/",

        "Ultralytics. <i>YOLOv8 Documentation — Oriented Bounding Boxes</i>. "
        "https://docs.ultralytics.com/models/yolov8/",

        "Xia et al. <i>DOTA: A Large-scale Dataset for Object Detection in Aerial "
        "Images</i>. CVPR 2018. https://captain-whu.github.io/DOTA/",

        "Radford et al. <i>Learning Transferable Visual Models From Natural "
        "Language Supervision (CLIP)</i>. OpenAI, 2021. "
        "https://arxiv.org/abs/2103.00020",

        "Google AI. <i>Gemini 2.5 Flash Lite — Model Card</i>. "
        "https://ai.google.dev/gemini-api/docs/models",

        "UNODC — United Nations Office on Drugs and Crime. <i>Money-Laundering "
        "Overview</i>. Disponível em: "
        "https://www.unodc.org/unodc/en/money-laundering/overview.html",

        "Zha, Y.; Gao, J.; Ni, S. <i>Use of normalized difference built-up index "
        "in automatically mapping urban areas from TM imagery</i>. International "
        "Journal of Remote Sensing, vol. 24, n. 3, pp. 583-594, 2003. "
        "DOI: 10.1080/01431160304987",

        "AWS — Amazon Web Services. <i>S3 Best Practices and Pricing</i>. "
        "https://aws.amazon.com/s3/",

        "FIAP — Faculdade de Informática e Administração Paulista. <i>Material "
        "didático do 1º Ano de IA (Fases 3 a 7)</i>. 2026.",
    ]
    for i, r in enumerate(refs, 1):
        story.append(Paragraph(f"[{i}] {r}", styles["BulletItem"]))

    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        "<i>Repositório GitHub e documentação técnica completa disponíveis em:</i>",
        styles["BodyJustified"]
    ))
    story.append(Paragraph(
        "<i>https://github.com/giovanisaavedra/FIAP/tree/main/ANO%201/FASE%2007/GLOBAL%20SOLUTIONS</i>",
        styles["FigCaption"]
    ))

    # ===========================================================
    # GERA O ARQUIVO
    # ===========================================================
    doc.build(story, onFirstPage=_add_page_number, onLaterPages=_add_page_number)
    print(f"✅ PDF gerado: {OUTPUT_PDF}")
    print(f"   Tamanho: {OUTPUT_PDF.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    build_pdf()
