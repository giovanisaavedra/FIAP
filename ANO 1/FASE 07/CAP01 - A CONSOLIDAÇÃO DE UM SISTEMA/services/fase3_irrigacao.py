"""
FarmTech Solutions - Serviço da Fase 3: Irrigação Automatizada
Implementa o ``ControladorIrrigacao``, regra de decisão que combina
umidade do solo, pH e nutrientes (NPK) para indicar se a bomba de
irrigação deve LIGAR, DESLIGAR ou ficar BLOQUEADA (com corretivo).

Esta lógica espelha o comportamento esperado do firmware Wokwi/ESP32
da Fase 3 do projeto, agora reutilizado pelo dashboard Streamlit.

Autores: Giovani Saavedra e Marcio Elifas
RM: RM566797 e RM567871
GRUPO 37
1TIAOS - FIAP

FIAP - Fase 7 - 2026
"""

from __future__ import annotations

from typing import Dict, Optional


# ==========================================================
#         LIMIARES DE DECISÃO (configuráveis)
# ==========================================================

# Limites de umidade do solo (%) — abaixo de UMIDADE_MIN_PERCENT
# liga a bomba; acima de UMIDADE_MAX_PERCENT desliga; no meio,
# mantém o estado anterior (histerese, evitando liga-desliga).
UMIDADE_MIN_PERCENT: float = 30.0
UMIDADE_MAX_PERCENT: float = 60.0

# Faixa de pH considerada apropriada para a maioria das culturas.
# Fora dela, irrigar não resolve — antes é preciso corrigir o solo.
PH_MIN: float = 5.5
PH_MAX: float = 7.5

# Limiares mínimos de NPK (mg/kg) — abaixo destes valores,
# recomendamos fertirrigação além (ou em vez) da irrigação simples.
NPK_LIMIARES: Dict[str, float] = {
    "N": 20.0,
    "P": 15.0,
    "K": 20.0,
}


# ==========================================================
#         CONTROLADOR
# ==========================================================

class ControladorIrrigacao:
    """Lógica de irrigação inteligente sobre as leituras dos sensores.

    Mantém o estado da bomba **por sensor** em memória, para implementar
    a regra de histerese (30%–60% mantém o estado anterior).

    Exemplo de uso::

        ctrl = ControladorIrrigacao()
        decisao = ctrl.avaliar({"sensor_id": "S1",
                                "soil_moisture": 25,
                                "soil_pH": 6.5,
                                "N": 45, "P": 30, "K": 40})
    """

    def __init__(self, estado_inicial: str = "DESLIGAR") -> None:
        """Cria o controlador, opcionalmente com um estado-base.

        Args:
            estado_inicial: estado da bomba assumido para sensores
                desconhecidos quando a umidade está na faixa adequada
                (``"LIGAR"`` ou ``"DESLIGAR"``).
        """
        if estado_inicial not in ("LIGAR", "DESLIGAR"):
            estado_inicial = "DESLIGAR"
        self._estado_inicial = estado_inicial
        self._estados_bomba: Dict[str, str] = {}

    # ------------------------------------------------------
    # Métodos auxiliares
    # ------------------------------------------------------

    @staticmethod
    def _get(leitura: Dict, *chaves, default: Optional[float] = None) -> Optional[float]:
        """Retorna o primeiro valor não-``None`` entre as chaves dadas."""
        for chave in chaves:
            valor = leitura.get(chave)
            if valor is not None:
                try:
                    return float(valor)
                except (TypeError, ValueError):
                    continue
        return default

    def estado_atual(self, sensor_id: str) -> str:
        """Devolve o estado vigente da bomba para o sensor informado."""
        return self._estados_bomba.get(sensor_id, self._estado_inicial)

    def _avaliar_npk(self, leitura: Dict) -> Optional[str]:
        """Gera string de recomendação de fertirrigação, se aplicável."""
        faltantes = []
        for nutriente, limiar in NPK_LIMIARES.items():
            valor = self._get(leitura, nutriente)
            if valor is not None and valor < limiar:
                faltantes.append(f"{nutriente} baixo ({valor:.0f} < {limiar:.0f})")
        if not faltantes:
            return None
        return "Recomenda-se fertirrigação — " + "; ".join(faltantes) + "."

    # ------------------------------------------------------
    # Regra principal
    # ------------------------------------------------------

    def avaliar(self, leitura: Dict) -> Dict:
        """Avalia uma leitura e devolve a decisão de irrigação.

        Args:
            leitura: Dicionário contendo no mínimo as chaves
                ``soil_moisture`` (ou ``umidade_solo``) e ``soil_pH``.
                Opcionalmente ``N``, ``P``, ``K`` e ``sensor_id``.

        Returns:
            Dicionário com:

            * ``acao``: ``"LIGAR"``, ``"DESLIGAR"`` ou ``"BLOQUEADA"``
            * ``motivo``: explicação curta da decisão
            * ``recomendacao``: ação recomendada ao operador
            * ``severidade``: ``"baixa"``, ``"media"`` ou ``"alta"``
        """
        sensor_id = str(leitura.get("sensor_id") or "DESCONHECIDO")
        umidade = self._get(leitura, "soil_moisture", "umidade_solo", default=50.0)
        ph = self._get(leitura, "soil_pH", "ph", default=7.0)

        rec_npk = self._avaliar_npk(leitura)

        # ---- Regra 1: pH fora da faixa BLOQUEIA a irrigação ----
        if ph < PH_MIN or ph > PH_MAX:
            corretivo = "calcário (subir pH)" if ph < PH_MIN else "enxofre (baixar pH)"
            recomendacao = (
                f"Aplicar {corretivo} antes de irrigar — "
                f"faixa ideal {PH_MIN}–{PH_MAX}."
            )
            if rec_npk:
                recomendacao += " " + rec_npk
            return {
                "acao": "BLOQUEADA",
                "motivo": (
                    f"pH {ph:.2f} fora da faixa ideal "
                    f"({PH_MIN}–{PH_MAX}); irrigar não corrige o solo."
                ),
                "recomendacao": recomendacao,
                "severidade": "alta",
            }

        # ---- Regra 2/3/4: histerese da umidade --------------
        if umidade < UMIDADE_MIN_PERCENT:
            acao = "LIGAR"
            motivo = (
                f"Umidade do solo {umidade:.1f}% abaixo do mínimo "
                f"({UMIDADE_MIN_PERCENT:.0f}%) — irrigação necessária."
            )
            severidade = "alta"
        elif umidade > UMIDADE_MAX_PERCENT:
            acao = "DESLIGAR"
            motivo = (
                f"Umidade do solo {umidade:.1f}% acima do máximo "
                f"({UMIDADE_MAX_PERCENT:.0f}%) — solo úmido, economizar água."
            )
            severidade = "baixa"
        else:
            anterior = self.estado_atual(sensor_id)
            acao = anterior
            motivo = (
                f"Umidade do solo {umidade:.1f}% na faixa adequada "
                f"({UMIDADE_MIN_PERCENT:.0f}%–{UMIDADE_MAX_PERCENT:.0f}%) — "
                f"mantendo estado anterior ({anterior})."
            )
            severidade = "baixa"

        # Atualiza estado interno apenas para ações reais.
        self._estados_bomba[sensor_id] = acao

        recomendacao = (
            rec_npk
            if rec_npk
            else "Sem ação corretiva adicional necessária."
        )

        return {
            "acao": acao,
            "motivo": motivo,
            "recomendacao": recomendacao,
            "severidade": severidade,
        }


# ==========================================================
#         EXECUÇÃO DIRETA (auto-teste)
# ==========================================================

if __name__ == "__main__":
    ctrl = ControladorIrrigacao()
    casos = [
        {"sensor_id": "S1", "soil_moisture": 25, "soil_pH": 6.5,
         "N": 45, "P": 30, "K": 40},
        {"sensor_id": "S2", "soil_moisture": 65, "soil_pH": 6.8,
         "N": 50, "P": 40, "K": 35},
        {"sensor_id": "S3", "soil_moisture": 45, "soil_pH": 6.5,
         "N": 10, "P": 5, "K": 10},
        {"sensor_id": "S4", "soil_moisture": 25, "soil_pH": 4.8,
         "N": 50, "P": 50, "K": 50},
    ]
    for c in casos:
        print(c["sensor_id"], "->", ctrl.avaliar(c))
