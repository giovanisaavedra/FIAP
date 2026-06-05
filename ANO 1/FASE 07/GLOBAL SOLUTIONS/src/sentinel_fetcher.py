"""
Busca e download de imagens Sentinel-2 L2A no Copernicus Data Space Ecosystem.

Retorna 5 bandas em float32: [B04, B03, B02, B08, B11] → [R, G, B, NIR, SWIR1].
"""

import os
from datetime import datetime, timedelta

import numpy as np
from PIL import Image
from sentinelhub import (
    BBox,
    CRS,
    DataCollection,
    MimeType,
    SentinelHubCatalog,
    SentinelHubRequest,
)

from src.config import get_sentinelhub_config


def _parse_scene_datetime(scene: dict) -> datetime:
    """
    Faz parse do timestamp ISO retornado pelo catálogo do Sentinel Hub.

    Strings vêm em formato tipo '2025-01-15T13:42:31Z' — Python 3.10 não
    aceita o sufixo 'Z' direto em fromisoformat, então convertemos para
    '+00:00' antes.
    """
    raw = scene["properties"]["datetime"]
    return datetime.fromisoformat(raw.replace("Z", "+00:00"))


# Evalscript que retorna 5 bandas em float32, na ordem [R, G, B, NIR, SWIR1].
_EVALSCRIPT = """
//VERSION=3
function setup() {
    return {
        input: [{
            bands: ["B02", "B03", "B04", "B08", "B11"],
            units: "DN"
        }],
        output: { bands: 5, sampleType: "FLOAT32" }
    };
}
function evaluatePixel(sample) {
    return [sample.B04, sample.B03, sample.B02, sample.B08, sample.B11];
}
"""


def _normalize_rgb_for_display(rgb_float: np.ndarray) -> np.ndarray:
    """
    Normaliza um array RGB float (em DN do Sentinel) para uint8 [0, 255]
    usando percentis 2% e 98% para evitar outliers (nuvens muito brancas,
    pixels de sombra muito escuros).
    """
    out = np.zeros_like(rgb_float, dtype=np.uint8)
    for c in range(3):
        channel = rgb_float[:, :, c]
        p2, p98 = np.percentile(channel, (2, 98))
        if p98 - p2 < 1e-6:
            # Canal "plano" — evita divisão por zero.
            out[:, :, c] = 0
            continue
        clipped = np.clip(channel, p2, p98)
        scaled = (clipped - p2) / (p98 - p2) * 255.0
        out[:, :, c] = scaled.astype(np.uint8)
    return out


def fetch_sentinel_image(
    bbox: tuple,
    output_dir: str,
    max_cloud_cover: int = 30,
    lookback_days: int = 60,
    size: tuple = (512, 512),
) -> dict:
    """
    Baixa a imagem Sentinel-2 L2A mais recente da bbox especificada.

    Args:
        bbox: (lon_min, lat_min, lon_max, lat_max) em WGS84
        output_dir: pasta onde salvar os arquivos gerados
        max_cloud_cover: % máximo de nuvens aceito
        lookback_days: quantos dias para trás buscar
        size: dimensões da imagem em pixels (width, height)

    Returns:
        dict com chaves:
            - 'rgb_path': caminho do PNG da imagem RGB
            - 'bands_array': numpy array (H, W, 5) ordem [R, G, B, NIR, SWIR1]
            - 'date_acquired': data ISO da imagem
            - 'cloud_cover': % de nuvens da imagem
    """
    os.makedirs(output_dir, exist_ok=True)

    config = get_sentinelhub_config()
    sh_bbox = BBox(bbox=list(bbox), crs=CRS.WGS84)

    # Janela temporal: dos últimos `lookback_days` dias até hoje.
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=lookback_days)
    time_range = (start_date.isoformat(), end_date.isoformat())

    # Etapa 1 — buscar metadata no catálogo. Em vez de pegar a cena mais
    # recente, listamos todas as candidatas no período e escolhemos a com
    # MENOR cloud cover (desempate por recência). Isso evita o caso em que
    # a cena mais nova está parcialmente nublada exatamente sobre a bbox.
    catalog = SentinelHubCatalog(config=config)
    search = catalog.search(
        DataCollection.SENTINEL2_L2A,
        bbox=sh_bbox,
        time=time_range,
        filter=f"eo:cloud_cover < {max_cloud_cover}",
        fields={
            "include": [
                "id",
                "properties.datetime",
                "properties.eo:cloud_cover",
            ],
            "exclude": [],
        },
    )
    results = list(search)

    if not results:
        lon_min, lat_min, lon_max, lat_max = bbox
        center_lat = (lat_min + lat_max) / 2
        center_lon = (lon_min + lon_max) / 2
        raise ValueError(
            "Não foi encontrada cena Sentinel-2 com cloud_cover < "
            f"{max_cloud_cover}% nos últimos {lookback_days} dias para a "
            f"região (lat={center_lat:.4f}, lon={center_lon:.4f}).\n\n"
            "Sugestões:\n"
            f"  - Aumentar SENTINEL_MAX_CLOUD_COVER no .env (atual: {max_cloud_cover})\n"
            f"  - Aumentar SENTINEL_LOOKBACK_DAYS no .env (atual: {lookback_days})\n"
            "  - Verificar se a região tem cobertura Sentinel-2 frequente "
            "(regiões polares ou muito tropicais podem ter menos cenas)"
        )

    # Ordena por (cloud_cover crescente, datetime decrescente):
    #   - primeiro critério: a cena menos nublada vence
    #   - desempate: a mais recente vence
    results.sort(
        key=lambda s: (
            float(s["properties"]["eo:cloud_cover"]),
            -_parse_scene_datetime(s).timestamp(),
        )
    )

    best = results[0]
    date_acquired = best["properties"]["datetime"]
    cloud_cover = float(best["properties"]["eo:cloud_cover"])

    print(
        f"        → cena selecionada: {date_acquired} "
        f"(cloud cover = {cloud_cover:.1f}%) — "
        f"{len(results)} cenas candidatas no período"
    )

    # Etapa 2 — solicitar as bandas via Process API, restringindo a janela
    # temporal ao DIA exato da cena escolhida. Isso garante que o Process
    # baixe exatamente a cena com menor cloud cover que identificamos no
    # catálogo (e não uma cena mais recente porém mais nublada que cairia
    # no time_range amplo se usássemos mosaicking_order="mostRecent").
    best_day = _parse_scene_datetime(best).date()
    narrow_time = (
        best_day.isoformat(),
        (best_day + timedelta(days=1)).isoformat(),
    )

    request = SentinelHubRequest(
        evalscript=_EVALSCRIPT,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A.define_from(
                    "s2l2a_cdse", service_url=config.sh_base_url
                ),
                time_interval=narrow_time,
                mosaicking_order="leastCC",
                maxcc=max_cloud_cover / 100.0,
            )
        ],
        responses=[
            SentinelHubRequest.output_response("default", MimeType.TIFF),
        ],
        bbox=sh_bbox,
        size=size,
        config=config,
    )

    data = request.get_data()
    if not data:
        raise ValueError(
            "A Process API do CDSE retornou vazio mesmo após encontrar "
            "resultados no catálogo. Tente novamente em alguns minutos."
        )

    bands_array = data[0].astype(np.float32)  # shape (H, W, 5)

    # Salva o array completo em .npy para reuso posterior (NDBI, etc.).
    npy_path = os.path.join(output_dir, "sentinel_bands.npy")
    np.save(npy_path, bands_array)

    # Salva uma visualização RGB em PNG (canais 0, 1, 2 = R, G, B).
    rgb = _normalize_rgb_for_display(bands_array[:, :, :3])
    rgb_path = os.path.join(output_dir, "sentinel_rgb.png")
    Image.fromarray(rgb).save(rgb_path)

    return {
        "rgb_path": rgb_path,
        "bands_array": bands_array,
        "date_acquired": date_acquired,
        "cloud_cover": cloud_cover,
    }
