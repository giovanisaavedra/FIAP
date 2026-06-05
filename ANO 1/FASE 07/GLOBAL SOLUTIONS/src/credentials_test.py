"""
Script standalone para validar todas as credenciais externas do SatVerify.

Uso:
    python -m src.credentials_test

Faz apenas chamadas mínimas — não consome créditos significativos.
"""

import sys

import requests

from src.config import (
    AWS_ACCESS_KEY_ID,
    AWS_REGION,
    AWS_S3_BUCKET,
    AWS_SECRET_ACCESS_KEY,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    MAPBOX_ACCESS_TOKEN,
    get_sentinelhub_config,
    validate_config,
)


def _print_test(service: str) -> None:
    print(f"🔍 Testando {service}...")


def _print_ok(service: str) -> None:
    print(f"✅ {service} OK")


def _print_fail(service: str, error: Exception) -> None:
    print(f"❌ {service} FALHOU: {error}")


def test_cdse() -> bool:
    """Testa autenticação no Copernicus Data Space Ecosystem via Catalog API."""
    _print_test("CDSE (Sentinel Hub)")
    try:
        from sentinelhub import BBox, CRS, DataCollection, SentinelHubCatalog

        config = get_sentinelhub_config()
        catalog = SentinelHubCatalog(config=config)
        # BBox pequeno sobre São Paulo (capital).
        bbox = BBox(bbox=[-46.65, -23.56, -46.63, -23.54], crs=CRS.WGS84)
        search = catalog.search(
            DataCollection.SENTINEL2_L2A,
            bbox=bbox,
            time=("2025-01-01", "2025-01-31"),
            filter="eo:cloud_cover < 30",
            limit=1,
        )
        # Materializa o iterador para forçar a chamada HTTP.
        list(search)
        _print_ok("CDSE (Sentinel Hub)")
        return True
    except Exception as exc:  # noqa: BLE001
        _print_fail("CDSE (Sentinel Hub)", exc)
        return False


def test_mapbox() -> bool:
    """Testa o token Mapbox via Static Images API."""
    _print_test("Mapbox")
    try:
        url = (
            "https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/"
            f"-46.6333,-23.5505,15/300x300?access_token={MAPBOX_ACCESS_TOKEN}"
        )
        response = requests.get(url, timeout=15)
        assert response.status_code == 200, (
            f"HTTP {response.status_code}: {response.text[:200]}"
        )
        _print_ok("Mapbox")
        return True
    except Exception as exc:  # noqa: BLE001
        _print_fail("Mapbox", exc)
        return False


def test_gemini() -> bool:
    """Testa a API Key do Google Gemini com uma geração mínima."""
    _print_test("Gemini")
    try:
        from google import genai

        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents="Diga olá em uma palavra.",
        )
        assert response.text, "Resposta vazia do Gemini"
        _print_ok("Gemini")
        return True
    except Exception as exc:  # noqa: BLE001
        _print_fail("Gemini", exc)
        return False


def test_aws_s3() -> bool:
    """Testa credenciais AWS listando 1 objeto do bucket configurado."""
    _print_test("AWS S3")
    try:
        import boto3

        s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
        )
        # MaxKeys=1 evita listar o bucket inteiro; sucesso = sem erro de permissão.
        s3.list_objects_v2(Bucket=AWS_S3_BUCKET, MaxKeys=1)
        _print_ok("AWS S3")
        return True
    except Exception as exc:  # noqa: BLE001
        _print_fail("AWS S3", exc)
        return False


def main() -> int:
    # Garante que o .env está completo antes de bater nas APIs.
    try:
        validate_config()
    except ValueError as exc:
        print(f"❌ Configuração inválida: {exc}")
        return 1

    results = [
        test_cdse(),
        test_mapbox(),
        test_gemini(),
        test_aws_s3(),
    ]

    passed = sum(1 for r in results if r)
    failed = len(results) - passed

    print()
    print("═══════════════════════════════")
    print(f"RESUMO: {passed} ✅ | {failed} ❌")
    print("═══════════════════════════════")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
