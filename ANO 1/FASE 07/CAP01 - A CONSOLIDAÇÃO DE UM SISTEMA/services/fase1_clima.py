"""
FarmTech Solutions - Serviço da Fase 1: API Meteorológica
Consulta a API pública Open-Meteo (sem chave) e devolve o clima
atual + previsão diária de 7 dias. Em caso de falha de rede ou
de resposta inválida, gera um conjunto de dados simulado realista
para que o dashboard continue funcionando.

Autores: Giovani Saavedra e Marcio Elifas
RM: RM566797 e RM567871
GRUPO 37
1TIAOS - FIAP

FIAP - Fase 7 - 2026
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Dict, List

import requests


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


# ==========================================================
#         CONSULTA REAL
# ==========================================================

def _construir_params(latitude: float, longitude: float) -> Dict[str, str]:
    """Monta o querystring para a chamada Open-Meteo."""
    return {
        "latitude": f"{latitude:.4f}",
        "longitude": f"{longitude:.4f}",
        "current": ",".join(
            [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation",
                "wind_speed_10m",
            ]
        ),
        "daily": ",".join(
            [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
            ]
        ),
        "timezone": "auto",
        "forecast_days": "7",
    }


def _parse_resposta(payload: dict) -> Dict:
    """Converte o JSON da Open-Meteo no formato padronizado do serviço."""
    atual = payload.get("current", {}) or {}
    diario = payload.get("daily", {}) or {}

    previsao = []
    datas = diario.get("time", []) or []
    tmax = diario.get("temperature_2m_max", []) or []
    tmin = diario.get("temperature_2m_min", []) or []
    chuva = diario.get("precipitation_sum", []) or []

    for i, data in enumerate(datas):
        previsao.append(
            {
                "data": data,
                "temp_max_C": float(tmax[i]) if i < len(tmax) and tmax[i] is not None else None,
                "temp_min_C": float(tmin[i]) if i < len(tmin) and tmin[i] is not None else None,
                "chuva_mm": float(chuva[i]) if i < len(chuva) and chuva[i] is not None else 0.0,
            }
        )

    return {
        "simulado": False,
        "fonte": "open-meteo.com",
        "latitude": payload.get("latitude"),
        "longitude": payload.get("longitude"),
        "timezone": payload.get("timezone"),
        "atual": {
            "temperatura_C": atual.get("temperature_2m"),
            "umidade_percent": atual.get("relative_humidity_2m"),
            "precipitacao_mm": atual.get("precipitation"),
            "vento_kmh": atual.get("wind_speed_10m"),
            "timestamp": atual.get("time"),
        },
        "previsao_7d": previsao,
    }


# ==========================================================
#         FALLBACK SIMULADO
# ==========================================================

def _simular_clima(latitude: float, longitude: float, motivo: str) -> Dict:
    """Gera um payload meteorológico simulado, com valores realistas."""
    hoje = datetime.now().date()
    previsao: List[Dict] = []
    for i in range(7):
        data = hoje + timedelta(days=i)
        tmax = round(random.uniform(22.0, 32.0), 1)
        tmin = round(tmax - random.uniform(6.0, 12.0), 1)
        chuva = round(max(0.0, random.gauss(3.5, 4.0)), 1)
        previsao.append(
            {
                "data": data.isoformat(),
                "temp_max_C": tmax,
                "temp_min_C": tmin,
                "chuva_mm": chuva,
            }
        )

    return {
        "simulado": True,
        "fonte": "simulado (fallback)",
        "motivo": motivo,
        "latitude": latitude,
        "longitude": longitude,
        "timezone": "local",
        "atual": {
            "temperatura_C": round(random.uniform(20.0, 30.0), 1),
            "umidade_percent": round(random.uniform(45.0, 85.0), 1),
            "precipitacao_mm": round(max(0.0, random.gauss(1.0, 2.0)), 1),
            "vento_kmh": round(random.uniform(5.0, 25.0), 1),
            "timestamp": datetime.now().isoformat(timespec="minutes"),
        },
        "previsao_7d": previsao,
    }


# ==========================================================
#         INTERFACE PÚBLICA
# ==========================================================

def obter_clima(latitude: float, longitude: float, timeout: float = 10.0) -> Dict:
    """Consulta o clima atual + previsão de 7 dias na Open-Meteo.

    Args:
        latitude: Latitude em graus decimais (ex.: ``-30.03``).
        longitude: Longitude em graus decimais (ex.: ``-51.23``).
        timeout: Timeout (segundos) para a chamada HTTP.

    Returns:
        Dicionário no formato:

        ``{
            "simulado": bool,
            "fonte": str,
            "atual": {"temperatura_C", "umidade_percent",
                      "precipitacao_mm", "vento_kmh", "timestamp"},
            "previsao_7d": [{"data", "temp_max_C",
                              "temp_min_C", "chuva_mm"}, ...]
        }``

        Em caso de erro de rede ou resposta inválida, devolve dados
        simulados com ``simulado=True`` para a UI sinalizar.
    """
    try:
        resp = requests.get(
            OPEN_METEO_URL,
            params=_construir_params(latitude, longitude),
            timeout=timeout,
        )
        resp.raise_for_status()
        payload = resp.json()
        if "current" not in payload or "daily" not in payload:
            return _simular_clima(latitude, longitude, motivo="resposta inesperada da API")
        return _parse_resposta(payload)
    except (requests.RequestException, ValueError) as exc:
        return _simular_clima(latitude, longitude, motivo=f"erro de rede: {exc}")


# ==========================================================
#         EXECUÇÃO DIRETA (auto-teste)
# ==========================================================

if __name__ == "__main__":
    dados = obter_clima(-30.03, -51.23)
    print("Simulado?", dados["simulado"])
    print("Atual:", dados["atual"])
    print("Previsão 7d:")
    for dia in dados["previsao_7d"]:
        print(" ", dia)
