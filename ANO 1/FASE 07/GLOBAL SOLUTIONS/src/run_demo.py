"""
Demo de execução do pipeline SatVerify com narrativa de due diligence.

Roda 3 casos com perfis de negócio distintos (legítimo, questionável, fantasma),
imprime resumo por caso (incluindo score YOLO + NDBI) e, ao final, tabela
comparativa lado a lado com decisão e nível de risco.

Uso:
    python -m src.run_demo
"""

import textwrap

from src.pipeline import run_analysis


# Casos de teste — cada um com uma narrativa de due diligence diferente.
# Os endereços foram escolhidos para gerar contraste claro de NDBI entre eles.
TEST_ADDRESSES = [
    {
        "name": "Caso 1 — Fornecedor industrial legítimo",
        "address": "Av. Volkswagen, 100, São Bernardo do Campo, SP, Brasil",
        "business_context": (
            "Empresa declara ser fabricante industrial de autopeças com "
            "instalações de 5.000m². Análise satelital deve confirmar "
            "estrutura física compatível."
        ),
        "expected": "ALTO grau de área construída (>30%) — planta industrial consolidada",
        "expected_decision": "APROVADO - Estrutura industrial compatível detectada",
    },
    {
        "name": "Caso 2 — Comércio popular declarando porte de atacadista",
        "address": "Rua 25 de Março, 1000, São Paulo, SP, Brasil",
        "business_context": (
            "Empresa declara ser atacadista de eletrônicos com faturamento de "
            "R$ 200M/ano e instalações próprias compatíveis. Análise deve "
            "verificar se o tipo de estrutura física condiz com o porte declarado."
        ),
        "expected": "MUITO ALTO grau de área construída — comércio popular extremamente denso",
        "expected_decision": (
            "ATENÇÃO - Embora haja alta densidade construída, a região é "
            "predominantemente comércio popular de pequenos boxes, incompatível "
            "com operação de atacadista declarada"
        ),
    },
    {
        "name": "Caso 3 — Endereço fantasma (red flag)",
        "address": "Parque Estadual da Cantareira, São Paulo, SP, Brasil",
        "business_context": (
            "Empresa declara fábrica de R$ 50M/ano neste endereço. Análise "
            "deve detectar se há qualquer instalação física compatível."
        ),
        "expected": "MUITO BAIXO grau de área construída (<5%) — área verde preservada",
        "expected_decision": "REPROVADO - Sem evidência visual de instalação física",
    },
]


# Largura visual da caixa por caso (corresponde à linha "─" abaixo).
_CASE_BOX_WIDTH = 70
# Indentação usada para alinhar a continuação de linhas longas dentro da caixa.
# Layout do prefixo: "│ " (2) + label de 19 chars + ": " (2) = 23 chars.
_WRAP_INDENT = "│" + " " * 22
# Largura disponível para o texto após o prefixo de label.
_WRAP_WIDTH = _CASE_BOX_WIDTH - len(_WRAP_INDENT)


def wrap_text(
    text: str,
    width: int = _WRAP_WIDTH,
    indent: str = _WRAP_INDENT,
) -> str:
    """
    Quebra um texto longo em várias linhas para caber dentro da caixa visual.

    A primeira linha NÃO é prefixada (o caller já imprimiu o rótulo "│ campo : ").
    As linhas seguintes são prefixadas com `indent`, mantendo o alinhamento
    visual dentro da borda esquerda da caixa.
    """
    lines = textwrap.wrap(text, width=width)
    if not lines:
        return ""
    first, *rest = lines
    return "\n".join([first] + [f"{indent}{line}" for line in rest])


def _summarize_yolo(yolo_result: dict, is_sentinel: bool = False) -> str:
    """
    Resume um resultado de YOLO em uma linha legível.

    Para Sentinel (baixa resolução), o caso de 0 detecções recebe a nota
    'esperado para 10m/pixel' — alinhando o display com a justificativa
    do `scoring.py`.
    """
    total = int(yolo_result.get("total_detections", 0))
    counts = yolo_result.get("class_counts", {}) or {}
    if total == 0:
        if is_sentinel:
            return "0 objetos (esperado para 10m/pixel)"
        return "0 objetos"
    parts = ", ".join(
        f"{n} {cls}" for cls, n in sorted(counts.items(), key=lambda kv: -kv[1])
    )
    return f"{total} objetos ({parts})"


def _summarize_clip_dominant(clip_result: dict) -> str:
    """Resume o resultado do CLIP em 'categoria (XX%)'."""
    cat = clip_result.get("dominant_category", "?")
    prob = float(clip_result.get("dominant_score", 0.0))
    return f"{cat} ({prob * 100:.0f}%)"


def _summarize_clip_top3(clip_result: dict) -> str:
    """Resume o top-3 do CLIP em 'cat1 XX%, cat2 XX%, cat3 XX%'."""
    top3 = clip_result.get("top3", []) or []
    return ", ".join(f"{cat} {prob * 100:.0f}%" for cat, prob in top3)


def _print_report_preview(
    report_text: str,
    max_chars: int = 500,
    indent: str = "│   ",
) -> None:
    """
    Imprime os primeiros `max_chars` do relatório de DD, com cada linha
    prefixada por `indent` para ficar dentro da caixa visual do caso.
    """
    snippet = report_text[:max_chars]
    truncated = len(report_text) > max_chars
    for line in snippet.splitlines():
        print(f"{indent}{line}")
    if truncated:
        print(f"{indent}(...)")


def _print_summary(case: dict, result: dict) -> None:
    """Imprime o bloco visual de resumo de um caso bem-sucedido."""
    metrics = result["ndbi_metrics"]
    score = result["authenticity_score"]
    yolo_sentinel = result["yolo_sentinel"]
    yolo_mapbox = result["yolo_mapbox"]
    clip_result = result["clip_classification"]

    print()
    print("┌" + "─" * (_CASE_BOX_WIDTH - 1))
    print(f"│ {case['name']}")
    print("├" + "─" * (_CASE_BOX_WIDTH - 1))
    # Bloco de narrativa de negócio.
    print(f"│ {'contexto':<19}: {wrap_text(case['business_context'])}")
    print(f"│ {'expectativa':<19}: {wrap_text(case['expected'])}")
    print(f"│ {'decisão esperada':<19}: {wrap_text(case['expected_decision'])}")
    # Separador interno entre narrativa e dados técnicos.
    print("│ " + "─" * (_CASE_BOX_WIDTH - 3))
    # Bloco técnico.
    print(f"│ {'analysis_id':<19}: {result['analysis_id']}")
    print(f"│ {'endereço resolvido':<19}: {wrap_text(result['address_resolved'])}")
    print(
        f"│ {'lat / lon':<19}: "
        f"{result['latitude']:.6f}, {result['longitude']:.6f}"
    )
    print(f"│ {'Sentinel data':<19}: {result['sentinel_date']}")
    print(f"│ {'Sentinel nuvens':<19}: {result['sentinel_cloud_cover']:.1f}%")
    print(f"│ {'NDBI % construído':<19}: {metrics['pct_built_up']:.1f}%")
    print(f"│ {'NDBI médio':<19}: {metrics['mean_ndbi']:.3f}")
    print(f"│ {'classificação':<19}: {metrics['built_up_level']}")
    # Bloco de score + YOLO.
    print(f"│ {'score':<19}: {score['score']}/100")
    print(f"│ {'decisão':<19}: {score['decision']}")
    print(f"│ {'nível de risco':<19}: {score['risk_level']}")
    print(
        f"│ {'YOLO Mapbox':<19}: "
        f"{wrap_text(_summarize_yolo(yolo_mapbox))}"
    )
    print(
        f"│ {'YOLO Sentinel-2':<19}: "
        f"{wrap_text(_summarize_yolo(yolo_sentinel, is_sentinel=True))}"
    )
    print(
        f"│ {'CLIP categoria':<19}: "
        f"{wrap_text(_summarize_clip_dominant(clip_result))}"
    )
    print(
        f"│ {'CLIP top-3':<19}: "
        f"{wrap_text(_summarize_clip_top3(clip_result))}"
    )
    dd = result.get("dd_report") or {}
    dd_path = dd.get("report_path", "—")
    dd_secs = dd.get("generation_seconds")
    dd_suffix = (
        f" ({dd_secs}s)" if dd_secs is not None else " (falhou)"
    )
    print(f"│ {'relatório DD':<19}: {wrap_text(dd_path + dd_suffix)}")
    print(f"│ {'artefatos em':<19}: {result['output_dir']}")
    # Prévia dos primeiros caracteres do relatório, ainda dentro da caixa.
    report_text = result.get("dd_report_markdown") or ""
    if report_text.strip():
        print("│ " + "─" * (_CASE_BOX_WIDTH - 3))
        print("│ trecho do relatório:")
        _print_report_preview(report_text, max_chars=500, indent="│   ")
    print("└" + "─" * (_CASE_BOX_WIDTH - 1))


# ---------------------------------------------------------------------------
# Tabela comparativa final — todas as linhas têm exatamente 105 caracteres.
# Layout das colunas (entre as bordas │/║):
#     col1 (Caso)    = 54 chars  (acomoda nomes longos sem truncar muito)
#     col2 (NDBI%)   =  7 chars
#     col3 (Score)   =  7 chars
#     col4 (Risco)   =  8 chars
#     col5 (Decisão) = 13 chars
#     col6 (Status)  =  9 chars
# Total: 54 + 7 + 7 + 8 + 13 + 9 + 7 bordas verticais = 105
# ---------------------------------------------------------------------------
_COL_CASO = 54
_COL_NDBI = 7
_COL_SCORE = 7
_COL_RISCO = 8
_COL_DECISAO = 13
_COL_STATUS = 9
_TABLE_WIDTH = (
    _COL_CASO + _COL_NDBI + _COL_SCORE + _COL_RISCO + _COL_DECISAO + _COL_STATUS + 7
)


def _truncate_name(name: str, max_width: int) -> str:
    """
    Trunca o nome do caso se exceder `max_width`, adicionando '...' no final.

    Sempre retorna a string já left-aligned com padding até `max_width`,
    pronta para ser inserida numa coluna de largura fixa.
    """
    if len(name) <= max_width:
        return name.ljust(max_width)
    return (name[: max_width - 3] + "...").ljust(max_width)


def _row(
    label: str,
    ndbi: str,
    score: str,
    risco: str,
    decisao: str,
    status: str,
) -> str:
    """Monta uma linha de dados da tabela com larguras de coluna fixas."""
    # _COL_CASO - 2 para reservar 1 caractere de padding em cada lado do label.
    label_str = f" {_truncate_name(label, _COL_CASO - 2)} "
    ndbi_str = f"{ndbi:^{_COL_NDBI}}"
    score_str = f"{score:^{_COL_SCORE}}"
    risco_str = f"{risco:^{_COL_RISCO}}"
    decisao_str = f"{decisao:^{_COL_DECISAO}}"
    status_str = f"{status:^{_COL_STATUS}}"
    return (
        f"║{label_str}│{ndbi_str}│{score_str}│{risco_str}"
        f"│{decisao_str}│{status_str}║"
    )


def _print_comparative_report(rows: list) -> None:
    """Imprime a tabela comparativa dos casos."""
    top = "╔" + "═" * (_TABLE_WIDTH - 2) + "╗"
    title = "║" + "RELATÓRIO COMPARATIVO DOS CASOS".center(_TABLE_WIDTH - 2) + "║"
    head_sep = (
        "╠"
        + "═" * _COL_CASO + "╤"
        + "═" * _COL_NDBI + "╤"
        + "═" * _COL_SCORE + "╤"
        + "═" * _COL_RISCO + "╤"
        + "═" * _COL_DECISAO + "╤"
        + "═" * _COL_STATUS + "╣"
    )
    col_header = _row("Caso", "NDBI%", "Score", "Risco", "Decisão", "Status")
    mid_sep = (
        "╠"
        + "═" * _COL_CASO + "╪"
        + "═" * _COL_NDBI + "╪"
        + "═" * _COL_SCORE + "╪"
        + "═" * _COL_RISCO + "╪"
        + "═" * _COL_DECISAO + "╪"
        + "═" * _COL_STATUS + "╣"
    )
    bottom = (
        "╚"
        + "═" * _COL_CASO + "╧"
        + "═" * _COL_NDBI + "╧"
        + "═" * _COL_SCORE + "╧"
        + "═" * _COL_RISCO + "╧"
        + "═" * _COL_DECISAO + "╧"
        + "═" * _COL_STATUS + "╝"
    )

    # Validação: todas as bordas/headers têm exatamente _TABLE_WIDTH chars
    # (emojis ✅/❌ contam como 1 char em Python; o alinhamento visual em
    # alguns terminais pode variar por causa do double-width do emoji).
    for line in (top, title, head_sep, col_header, mid_sep, bottom):
        assert len(line) == _TABLE_WIDTH, (
            f"linha com {len(line)} chars (esperado {_TABLE_WIDTH}): {line!r}"
        )

    print()
    print(top)
    print(title)
    print(head_sep)
    print(col_header)
    print(mid_sep)
    for row in rows:
        if row["pct"] is None:
            ndbi_text = "--"
            score_text = "--"
            risco_text = "--"
            decisao_text = "--"
        else:
            ndbi_text = f"{row['pct']:.1f}%"
            score_text = f"{row['score']}"
            risco_text = row["risco"]
            decisao_text = row["decisao"]
        line = _row(
            row["label"],
            ndbi_text,
            score_text,
            risco_text,
            decisao_text,
            row["status"],
        )
        assert len(line) == _TABLE_WIDTH, (
            f"linha de dados com {len(line)} chars: {line!r}"
        )
        print(line)
    print(bottom)


def _short_label(case_name: str) -> str:
    """Extrai um rótulo curto a partir do `name` do caso (remove o 'Caso ')."""
    # Mantém o número + travessão + descrição, sem o prefixo "Caso ".
    if case_name.startswith("Caso "):
        return case_name[len("Caso "):].strip()
    return case_name.strip()


def main() -> int:
    successes = 0
    failures = 0
    report_rows = []

    for case in TEST_ADDRESSES:
        label = _short_label(case["name"])
        try:
            result = run_analysis(
                address=case["address"],
                business_context=case.get("business_context", ""),
            )
            _print_summary(case, result)
            metrics = result["ndbi_metrics"]
            score = result["authenticity_score"]
            report_rows.append({
                "label": label,
                "pct": metrics["pct_built_up"],
                "score": score["score"],
                "risco": score["risk_level"],
                "decisao": score["decision"],
                "status": "✅",
            })
            successes += 1
        except Exception as exc:  # noqa: BLE001
            print(f"\n❌ Falha em '{case['name']}': {exc}")
            report_rows.append({
                "label": label,
                "pct": None,
                "score": None,
                "risco": None,
                "decisao": None,
                "status": "❌",
            })
            failures += 1

    _print_comparative_report(report_rows)

    print()
    print("═══════════════════════════════")
    print(f"DEMO: {successes} ✅ | {failures} ❌")
    print("═══════════════════════════════")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
