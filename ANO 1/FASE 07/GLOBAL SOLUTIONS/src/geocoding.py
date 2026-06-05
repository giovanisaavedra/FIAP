"""
Geocoding de endereços textuais usando Nominatim (OpenStreetMap).
"""

from geopy.geocoders import Nominatim


# Aproximação para gerar uma bbox de ~500m x 500m em latitudes médias.
# 1 grau de latitude ≈ 111 km, então 0.0025 graus ≈ 277 m. Usamos ±0.0025
# em ambos os eixos, gerando um quadrado de ~500m x 500m centrado no ponto.
# Para precisão maior, seria necessário corrigir a longitude por cos(lat),
# mas a aproximação é suficiente para o PoC.
_HALF_BBOX_DEG = 0.0025


def geocode_address(address: str) -> dict:
    """
    Converte um endereço em coordenadas geográficas usando Nominatim.

    Args:
        address: endereço textual (ex: "Av. Paulista 1578, São Paulo")

    Returns:
        dict com chaves:
            - 'latitude': float
            - 'longitude': float
            - 'display_name': str (endereço formatado retornado pelo Nominatim)
            - 'bbox': tuple (lon_min, lat_min, lon_max, lat_max)

    Raises:
        ValueError: se o endereço não puder ser geocodificado.
    """
    # Nominatim exige um user-agent identificável (boas práticas / ToS).
    geolocator = Nominatim(
        user_agent="satverify-poc/1.0 (contato: dev@satverify.local)",
        timeout=10,
    )

    location = geolocator.geocode(address)
    if location is None:
        raise ValueError(
            f"Não foi possível geocodificar o endereço: '{address}'.\n\n"
            "Formatos recomendados:\n"
            "  - 'Rua/Avenida + Número, Cidade, Estado, País'\n"
            "  - Exemplo: 'Av. Paulista, 1578, São Paulo, SP, Brasil'\n"
            "  - Ou nome de ponto turístico/empresa conhecida: "
            "'Refinaria de Paulínia, SP'\n\n"
            "Evite endereços genéricos como 'Estrada Municipal' ou "
            "'Zona Rural' sem coordenadas específicas."
        )

    lat = float(location.latitude)
    lon = float(location.longitude)

    bbox = (
        lon - _HALF_BBOX_DEG,  # lon_min
        lat - _HALF_BBOX_DEG,  # lat_min
        lon + _HALF_BBOX_DEG,  # lon_max
        lat + _HALF_BBOX_DEG,  # lat_max
    )

    return {
        "latitude": lat,
        "longitude": lon,
        "display_name": location.address,
        "bbox": bbox,
    }
