"""
Download de imagens aéreas estáticas de alta resolução via Mapbox Static Images API.
"""

import requests

from src.config import MAPBOX_ACCESS_TOKEN


# Endpoint base da Static Images API do Mapbox (estilo "satellite-v9").
_MAPBOX_STATIC_URL = (
    "https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/"
    "{lon},{lat},{zoom}/{width}x{height}@2x"
)


def fetch_mapbox_aerial(
    latitude: float,
    longitude: float,
    output_path: str,
    zoom: int = 18,
    size: tuple = (512, 512),
) -> str:
    """
    Baixa imagem aérea de alta resolução centrada no ponto.

    Args:
        latitude: lat do centro
        longitude: lon do centro
        output_path: caminho onde salvar o PNG
        zoom: nível de zoom Mapbox (18 = ~0.5m/pixel)
        size: dimensões da imagem (width, height); max 1280x1280 no free tier

    Returns:
        Caminho do arquivo salvo.
    """
    width, height = size
    url = _MAPBOX_STATIC_URL.format(
        lon=longitude,
        lat=latitude,
        zoom=zoom,
        width=width,
        height=height,
    )

    response = requests.get(
        url,
        params={"access_token": MAPBOX_ACCESS_TOKEN},
        timeout=20,
    )
    if response.status_code != 200:
        raise ValueError(
            f"Falha ao baixar imagem do Mapbox (HTTP {response.status_code}): "
            f"{response.text[:200]}"
        )

    # Persiste os bytes direto em disco (PNG retornado pelo Mapbox).
    with open(output_path, "wb") as fh:
        fh.write(response.content)

    return output_path
