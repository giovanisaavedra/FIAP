"""
Configuração central do SatVerify.

Carrega variáveis do `.env`, expõe constantes module-level e oferece
utilitários para validar credenciais e montar a config do Sentinel Hub
apontando para o Copernicus Data Space Ecosystem (CDSE).
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from sentinelhub import SHConfig

# Carrega o .env localizado na raiz do projeto (um nível acima de src/).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=_PROJECT_ROOT / ".env")


# ---------------------------------------------------------------------------
# Credenciais — Copernicus Data Space Ecosystem (CDSE)
# ---------------------------------------------------------------------------
CDSE_CLIENT_ID = os.getenv("CDSE_CLIENT_ID")
CDSE_CLIENT_SECRET = os.getenv("CDSE_CLIENT_SECRET")

# URLs fixas do CDSE (sucessor gratuito do Sentinel Hub clássico, mantido pela ESA).
CDSE_SH_BASE_URL = "https://sh.dataspace.copernicus.eu"
CDSE_SH_TOKEN_URL = (
    "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/"
    "protocol/openid-connect/token"
)


# ---------------------------------------------------------------------------
# Credenciais — Mapbox
# ---------------------------------------------------------------------------
MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN")


# ---------------------------------------------------------------------------
# Credenciais — Google Gemini
# ---------------------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")


# ---------------------------------------------------------------------------
# Credenciais — AWS S3
# ---------------------------------------------------------------------------
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")


# ---------------------------------------------------------------------------
# Configurações gerais da aplicação
# ---------------------------------------------------------------------------
APP_ENV = os.getenv("APP_ENV", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


# ---------------------------------------------------------------------------
# Parâmetros do Mapbox (imagens estáticas)
# ---------------------------------------------------------------------------
MAPBOX_IMAGE_SIZE = int(os.getenv("MAPBOX_IMAGE_SIZE", "1024"))
MAPBOX_ZOOM_LEVEL = int(os.getenv("MAPBOX_ZOOM_LEVEL", "18"))


# ---------------------------------------------------------------------------
# Parâmetros do Sentinel
# ---------------------------------------------------------------------------
SENTINEL_MAX_CLOUD_COVER = int(os.getenv("SENTINEL_MAX_CLOUD_COVER", "15"))
SENTINEL_LOOKBACK_DAYS = int(os.getenv("SENTINEL_LOOKBACK_DAYS", "120"))


# ---------------------------------------------------------------------------
# Diretórios locais
# ---------------------------------------------------------------------------
CACHE_DIR = os.getenv("CACHE_DIR", "./data/cache")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./outputs")


# Conjunto de variáveis obrigatórias (sem valor default).
_REQUIRED_VARS = {
    "CDSE_CLIENT_ID": CDSE_CLIENT_ID,
    "CDSE_CLIENT_SECRET": CDSE_CLIENT_SECRET,
    "MAPBOX_ACCESS_TOKEN": MAPBOX_ACCESS_TOKEN,
    "GEMINI_API_KEY": GEMINI_API_KEY,
    "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
    "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
    "AWS_S3_BUCKET": AWS_S3_BUCKET,
}


def validate_config() -> None:
    """
    Verifica se todas as variáveis obrigatórias estão preenchidas.

    Lança ValueError com a lista de variáveis faltantes, caso existam.
    """
    missing = [name for name, value in _REQUIRED_VARS.items() if not value]
    if missing:
        raise ValueError(
            "As seguintes variáveis de ambiente obrigatórias não estão "
            f"definidas no .env: {', '.join(missing)}"
        )


def get_sentinelhub_config() -> SHConfig:
    """
    Monta um SHConfig pronto para uso com o Copernicus Data Space Ecosystem.

    Importante: o pacote `sentinelhub` é o mesmo do Sentinel Hub clássico;
    só mudamos os endpoints para os do CDSE.
    """
    config = SHConfig()
    config.sh_client_id = CDSE_CLIENT_ID
    config.sh_client_secret = CDSE_CLIENT_SECRET
    config.sh_base_url = CDSE_SH_BASE_URL
    config.sh_token_url = CDSE_SH_TOKEN_URL
    return config
