"""
FarmTech Solutions - Serviço da Fase 1: Cálculos Agrícolas
Funções utilitárias para cálculo de área de plantio em diferentes
geometrias e estimativa de insumos por cultura.

Autores: Giovani Saavedra e Marcio Elifas
RM: RM566797 e RM567871
GRUPO 37
1TIAOS - FIAP

FIAP - Fase 7 - 2026
"""

from __future__ import annotations

import math
from typing import Dict


# ==========================================================
#         CATÁLOGO DE INSUMOS POR CULTURA
# ==========================================================

# Dosagens de referência (valores didáticos, baseados em manuais
# agronômicos genéricos). Para uso em produção, recomenda-se
# atualizar com recomendação de engenheiro agrônomo local.
CATALOGO_INSUMOS: Dict[str, Dict] = {
    "milho": {
        "insumo_principal": "Adubo NPK 08-28-16",
        "dosagem": 350.0,
        "unidade": "kg/ha",
        "observacao": "Aplicação no plantio + cobertura nitrogenada.",
    },
    "soja": {
        "insumo_principal": "Adubo NPK 02-20-20",
        "dosagem": 250.0,
        "unidade": "kg/ha",
        "observacao": "Inoculação com Bradyrhizobium é obrigatória.",
    },
    "cafe": {
        "insumo_principal": "Adubo NPK 20-05-20",
        "dosagem": 400.0,
        "unidade": "kg/ha",
        "observacao": "Parcelar em 3 aplicações durante a safra.",
    },
    "cana": {
        "insumo_principal": "Adubo NPK 18-00-27",
        "dosagem": 500.0,
        "unidade": "kg/ha",
        "observacao": "Aplicar na soca, após o corte.",
    },
}


# ==========================================================
#         CÁLCULO DE ÁREA DE PLANTIO
# ==========================================================

def calcular_area_plantio(geometria: str, dimensoes: Dict[str, float]) -> Dict[str, float]:
    """Calcula a área de plantio para a geometria informada.

    Args:
        geometria: ``"retangulo"``, ``"triangulo"`` ou ``"circulo"``
            (pivô central). Aceita também variantes com acento.
        dimensoes: Dicionário com as medidas em **metros**, conforme
            a geometria escolhida:

            * ``retangulo``  -> ``{"largura": ..., "comprimento": ...}``
            * ``triangulo``  -> ``{"base": ..., "altura": ...}``
            * ``circulo``    -> ``{"raio": ...}``

    Returns:
        Dicionário com:

        * ``geometria``  – geometria normalizada
        * ``area_m2``    – área em metros quadrados
        * ``area_ha``    – área em hectares (1 ha = 10 000 m²)
        * ``perimetro_m`` – perímetro/contorno aproximado em metros

    Raises:
        ValueError: se a geometria for desconhecida ou se uma medida
            obrigatória estiver ausente ou não-positiva.
    """
    geom = geometria.strip().lower()
    # Normaliza acentos comuns vindos do form
    geom = (
        geom.replace("â", "a")
        .replace("ã", "a")
        .replace("á", "a")
        .replace("ê", "e")
        .replace("í", "i")
        .replace("ô", "o")
        .replace("ó", "o")
        .replace("ú", "u")
    )

    def _exigir(chave: str) -> float:
        valor = dimensoes.get(chave)
        if valor is None:
            raise ValueError(f"Dimensão obrigatória ausente: {chave!r}")
        valor = float(valor)
        if valor <= 0:
            raise ValueError(f"Dimensão {chave!r} deve ser positiva (recebido {valor}).")
        return valor

    if geom in {"retangulo", "rectangle"}:
        largura = _exigir("largura")
        comprimento = _exigir("comprimento")
        area = largura * comprimento
        perimetro = 2 * (largura + comprimento)

    elif geom in {"triangulo", "triangle"}:
        base = _exigir("base")
        altura = _exigir("altura")
        area = (base * altura) / 2.0
        # Aproximação de perímetro para triângulo isósceles equivalente.
        lado = math.sqrt((base / 2.0) ** 2 + altura ** 2)
        perimetro = base + 2 * lado

    elif geom in {"circulo", "circle", "pivo", "pivot"}:
        raio = _exigir("raio")
        area = math.pi * raio ** 2
        perimetro = 2 * math.pi * raio

    else:
        raise ValueError(
            f"Geometria desconhecida: {geometria!r}. "
            "Use 'retangulo', 'triangulo' ou 'circulo'."
        )

    return {
        "geometria": geom,
        "area_m2": round(area, 2),
        "area_ha": round(area / 10_000.0, 4),
        "perimetro_m": round(perimetro, 2),
    }


# ==========================================================
#         CÁLCULO DE INSUMOS
# ==========================================================

def calcular_insumos(cultura: str, area_ha: float) -> Dict[str, float]:
    """Calcula a quantidade total de insumo para uma cultura/área.

    Args:
        cultura: Nome da cultura (chave de :data:`CATALOGO_INSUMOS`).
            Aceita maiúsculas/minúsculas e acentos comuns
            (``"café"``, ``"Cana"`` etc.).
        area_ha: Área total em hectares.

    Returns:
        Dicionário com a cultura normalizada, o insumo principal,
        a dosagem por hectare e a quantidade total calculada.

    Raises:
        ValueError: se a cultura não existir no catálogo ou a área
            for não-positiva.
    """
    if area_ha is None or float(area_ha) <= 0:
        raise ValueError("Área (ha) deve ser um número positivo.")

    chave = (
        cultura.strip().lower()
        .replace("é", "e")
        .replace("ê", "e")
        .replace("á", "a")
        .replace("ã", "a")
    )
    if chave not in CATALOGO_INSUMOS:
        disponiveis = ", ".join(sorted(CATALOGO_INSUMOS.keys()))
        raise ValueError(
            f"Cultura {cultura!r} não consta no catálogo. "
            f"Disponíveis: {disponiveis}."
        )

    info = CATALOGO_INSUMOS[chave]
    dosagem = float(info["dosagem"])
    quantidade_total = dosagem * float(area_ha)

    return {
        "cultura": chave,
        "insumo_principal": info["insumo_principal"],
        "dosagem_por_ha": dosagem,
        "unidade": info["unidade"],
        "area_ha": round(float(area_ha), 4),
        "quantidade_total": round(quantidade_total, 2),
        "observacao": info["observacao"],
    }


# ==========================================================
#         EXECUÇÃO DIRETA (auto-teste)
# ==========================================================

if __name__ == "__main__":
    print("=== Teste rápido — Fase 1 / Cálculos ===")
    print(calcular_area_plantio("retangulo", {"largura": 100, "comprimento": 250}))
    print(calcular_area_plantio("circulo", {"raio": 75}))
    print(calcular_insumos("milho", 2.5))
    print(calcular_insumos("café", 1.0))
