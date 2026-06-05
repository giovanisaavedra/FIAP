"""
Cálculo do NDBI (Normalized Difference Built-up Index) e utilidades de
visualização e métricas derivadas.

NDBI = (B11 - B08) / (B11 + B08)
    B11 = SWIR1 (~1610 nm)
    B08 = NIR   (~842 nm)

Interpretação:
    NDBI > 0.1   → provável área construída
    NDBI ≈ 0     → solo nu / vegetação esparsa
    NDBI < 0     → vegetação densa ou água
"""

import numpy as np
from PIL import Image


def compute_ndbi(bands_array: np.ndarray) -> np.ndarray:
    """
    Calcula o NDBI a partir de um array de bandas Sentinel-2.

    Args:
        bands_array: array shape (H, W, 5) com ordem [R, G, B, NIR, SWIR1]

    Returns:
        Array shape (H, W) com valores NDBI no intervalo [-1, 1].
        Pixels onde NIR e SWIR1 são ambos zero retornam NaN.
    """
    if bands_array.ndim != 3 or bands_array.shape[2] < 5:
        raise ValueError(
            "bands_array precisa ter shape (H, W, 5) com as bandas "
            "[R, G, B, NIR, SWIR1]."
        )

    nir = bands_array[:, :, 3].astype(np.float32)
    swir1 = bands_array[:, :, 4].astype(np.float32)

    denom = swir1 + nir
    # Evita divisão por zero: onde o denominador é zero, retornamos NaN.
    ndbi = np.where(
        denom > 0,
        (swir1 - nir) / np.where(denom > 0, denom, 1.0),
        np.nan,
    )
    # Garante que valores fiquem no intervalo válido [-1, 1].
    ndbi = np.clip(ndbi, -1.0, 1.0)
    return ndbi.astype(np.float32)


def _ndbi_to_rgb(ndbi: np.ndarray) -> np.ndarray:
    """
    Mapeia valores NDBI [-1, 1] para uma colormap RGB ao estilo RdYlGn invertido:
        NDBI < 0       → verde (vegetação/água)
        NDBI 0 a 0.1   → amarelo/bege (solo nu / transição)
        NDBI > 0.1     → vermelho (área construída)

    Mapeamento manual (sem matplotlib) usando interpolação linear entre pontos
    de controle.
    """
    # Substitui NaN por 0 para o display.
    arr = np.nan_to_num(ndbi, nan=0.0)

    # Stops (NDBI value, RGB) — verde → amarelo → vermelho.
    stops = [
        (-1.0, (0, 100, 0)),       # verde escuro
        (-0.2, (60, 180, 60)),     # verde
        (0.0, (220, 220, 120)),    # bege/amarelo claro
        (0.1, (230, 160, 60)),     # laranja
        (0.4, (200, 40, 40)),      # vermelho
        (1.0, (120, 0, 0)),        # vermelho escuro
    ]

    values = np.array([s[0] for s in stops], dtype=np.float32)
    colors = np.array([s[1] for s in stops], dtype=np.float32)  # (N, 3)

    flat = arr.flatten()
    rgb_flat = np.empty((flat.size, 3), dtype=np.float32)
    for c in range(3):
        rgb_flat[:, c] = np.interp(flat, values, colors[:, c])

    rgb = rgb_flat.reshape(arr.shape + (3,)).astype(np.uint8)
    return rgb


def save_ndbi_visualization(ndbi_array: np.ndarray, output_path: str) -> None:
    """
    Salva uma visualização colorida do NDBI em PNG.

    Cores:
        - NDBI < 0    : tons de verde (vegetação/água)
        - NDBI 0–0.1  : tons de bege/amarelo (solo nu)
        - NDBI > 0.1  : tons de vermelho (áreas construídas)
    """
    rgb = _ndbi_to_rgb(ndbi_array)
    Image.fromarray(rgb).save(output_path)


def classify_built_up_level(pct_built_up: float) -> str:
    """
    Classifica o nível de área construída a partir do percentual de pixels
    acima do threshold de NDBI.

    Returns:
        'BAIXO' se < 10%
        'MÉDIO' se 10-30%
        'ALTO' se > 30%
    """
    if pct_built_up < 10.0:
        return "BAIXO"
    if pct_built_up <= 30.0:
        return "MÉDIO"
    return "ALTO"


def compute_built_up_metrics(
    ndbi_array: np.ndarray,
    threshold: float = 0.1,
) -> dict:
    """
    Calcula métricas resumidas de área construída a partir do NDBI.

    Args:
        ndbi_array: array (H, W) com valores NDBI
        threshold: valor de corte (default 0.1) acima do qual o pixel é
                   considerado "construído"

    Returns:
        dict com chaves:
            - 'pct_built_up': % de pixels com NDBI > threshold
            - 'mean_ndbi': NDBI médio (ignorando NaNs)
            - 'std_ndbi': desvio padrão do NDBI (ignorando NaNs)
            - 'threshold_used': threshold usado
            - 'built_up_level': classificação textual (BAIXO/MÉDIO/ALTO)
    """
    valid_mask = ~np.isnan(ndbi_array)
    n_valid = int(valid_mask.sum())
    if n_valid == 0:
        return {
            "pct_built_up": 0.0,
            "mean_ndbi": float("nan"),
            "std_ndbi": float("nan"),
            "threshold_used": threshold,
            "built_up_level": classify_built_up_level(0.0),
        }

    built_up_mask = (ndbi_array > threshold) & valid_mask
    pct_built_up = float(built_up_mask.sum()) / n_valid * 100.0

    return {
        "pct_built_up": float(pct_built_up),
        "mean_ndbi": float(np.nanmean(ndbi_array)),
        "std_ndbi": float(np.nanstd(ndbi_array)),
        "threshold_used": float(threshold),
        "built_up_level": classify_built_up_level(pct_built_up),
    }
