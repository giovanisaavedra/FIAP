"""
FarmTech Solutions - Serviço de Alertas SNS (Fase 5/7)
Avalia o banco SQLite, formata mensagens e publica no tópico AWS
SNS configurado em ``.env``. Em modo simulado (sem ``SNS_TOPIC_ARN``)
grava em ``data/alertas_simulados.log``.

Boas práticas:
* Credenciais vêm exclusivamente do ``.env`` carregado por
  ``python-dotenv`` — **não** são logadas em hipótese alguma.
* Conexões SQLite curtas com ``timeout=10`` para conviver com o
  simulador IoT escrevendo em paralelo.
* Antideduplicação via tabela ``alertas`` + coluna ``enviado_sns``
  (preserva o histórico mesmo se o cooldown for excedido depois).

Autores: Giovani Saavedra e Marcio Elifas
RM: RM566797 e RM567871
GRUPO 37
1TIAOS - FIAP

FIAP - Fase 7 - 2026
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv


# ==========================================================
#         CONSTANTES E DEFAULTS
# ==========================================================

# Defaults usados quando o ``.env`` não traz a variável.
DEFAULTS: Dict[str, float] = {
    "ALERTA_UMIDADE_CRITICA": 20.0,
    "ALERTA_PH_MIN": 5.0,
    "ALERTA_PH_MAX": 8.0,
    "ALERTA_TEMP_MAX": 40.0,
    "ALERTA_COOLDOWN_MINUTOS": 30.0,
}

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_SIMULADO = BASE_DIR / "data" / "alertas_simulados.log"


# ==========================================================
#         SERVIÇO
# ==========================================================

class ServicoAlertas:
    """Frente sobre o AWS SNS com regras de negócio FarmTech."""

    # ------------------------------------------------------
    # Inicialização e configuração
    # ------------------------------------------------------

    def __init__(self, env_path: Optional[str] = None) -> None:
        """Carrega ``.env`` e prepara o cliente SNS (lazy).

        Args:
            env_path: Caminho explícito do ``.env``. ``None`` deixa
                o ``python-dotenv`` resolver automaticamente.
        """
        # ``override=False`` para respeitar variáveis já no ambiente
        # (úteis em CI ou ao testar com valores temporários).
        load_dotenv(dotenv_path=env_path, override=False)

        self.region = os.getenv("AWS_REGION") or "us-east-1"
        self.topic_arn = os.getenv("SNS_TOPIC_ARN") or ""
        self.db_path = os.getenv("DB_PATH") or "farmtech_iot.db"

        self.limiares: Dict[str, float] = {
            chave: float(os.getenv(chave, DEFAULTS[chave]))
            for chave in DEFAULTS
        }

        self._sns_client = None  # cache do boto3.client('sns')

        # Garante a coluna enviado_sns o quanto antes (idempotente).
        self._garantir_coluna_enviado_sns()

    # ------------------------------------------------------
    # Acesso ao boto3 (lazy + sem logar credencial)
    # ------------------------------------------------------

    @property
    def modo_simulado(self) -> bool:
        """``True`` quando não há SNS_TOPIC_ARN ou boto3 indisponível."""
        return not self.topic_arn

    def _client(self):
        """Retorna o cliente SNS (cria-o na 1ª chamada)."""
        if self._sns_client is None:
            import boto3  # import local — evita custo se modo simulado

            self._sns_client = boto3.client("sns", region_name=self.region)
        return self._sns_client

    def mascarar_arn(self) -> str:
        """ARN com apenas os últimos 12 caracteres visíveis."""
        if not self.topic_arn:
            return "(simulado)"
        if len(self.topic_arn) <= 12:
            return self.topic_arn
        return "•" * 12 + self.topic_arn[-12:]

    # ------------------------------------------------------
    # Diagnóstico do SNS
    # ------------------------------------------------------

    def testar_conexao(self) -> Dict:
        """Valida a configuração consultando ``get_topic_attributes``.

        Returns:
            Dict ``{"ok": bool, "modo": str, "mensagem": str}``.
            Nunca devolve credenciais nem o ARN completo.
        """
        if self.modo_simulado:
            return {
                "ok": True,
                "modo": "simulado",
                "mensagem": (
                    "SNS_TOPIC_ARN não definido — alertas serão gravados em "
                    f"{LOG_SIMULADO.relative_to(BASE_DIR)}."
                ),
            }
        try:
            attrs = self._client().get_topic_attributes(TopicArn=self.topic_arn)
            n_subs = attrs.get("Attributes", {}).get(
                "SubscriptionsConfirmed", "?"
            )
            return {
                "ok": True,
                "modo": "sns",
                "mensagem": (
                    f"Conectado ao tópico SNS (assinaturas confirmadas: {n_subs})."
                ),
            }
        except Exception as exc:
            # NÃO incluir a stacktrace inteira — pode vazar nomes de keys.
            return {
                "ok": False,
                "modo": "erro",
                "mensagem": f"Falha ao acessar o tópico SNS: {type(exc).__name__}.",
            }

    # ------------------------------------------------------
    # Persistência (conexão curta)
    # ------------------------------------------------------

    def _conn(self) -> sqlite3.Connection:
        """Abre uma conexão SQLite curta, ``timeout=10`` p/ conviver com o IoT."""
        return sqlite3.connect(self.db_path, timeout=10, check_same_thread=False)

    def _garantir_coluna_enviado_sns(self) -> None:
        """Aplica a migration ``enviado_sns`` se o banco ainda não a tiver."""
        try:
            with self._conn() as cn:
                try:
                    cn.execute(
                        "ALTER TABLE alertas ADD COLUMN enviado_sns INTEGER DEFAULT 0"
                    )
                    cn.commit()
                except sqlite3.OperationalError:
                    pass  # coluna já existe
        except Exception:
            pass  # banco inacessível agora — verificações posteriores tratam

    def _ja_alertado_no_cooldown(
        self,
        sensor_id: Optional[str],
        tipo_alerta: str,
    ) -> bool:
        """True se houver alerta do mesmo (sensor, tipo) dentro do cooldown."""
        minutos = self.limiares["ALERTA_COOLDOWN_MINUTOS"]
        limite = (
            datetime.now() - timedelta(minutes=minutos)
        ).strftime("%Y-%m-%d %H:%M:%S")
        try:
            with self._conn() as cn:
                cur = cn.execute(
                    """
                    SELECT COUNT(*) FROM alertas
                    WHERE tipo_alerta = ?
                      AND (sensor_id = ? OR (? IS NULL AND sensor_id IS NULL))
                      AND timestamp >= ?
                      AND enviado_sns = 1
                    """,
                    (tipo_alerta, sensor_id, sensor_id, limite),
                )
                return int(cur.fetchone()[0]) > 0
        except Exception:
            return False

    def _registrar_envio(
        self,
        sensor_id: Optional[str],
        tipo_alerta: str,
        severidade: str,
        mensagem: str,
    ) -> None:
        """Grava o envio em ``alertas`` com ``enviado_sns=1``."""
        try:
            with self._conn() as cn:
                cn.execute(
                    """
                    INSERT INTO alertas
                        (sensor_id, tipo_alerta, severidade, mensagem, enviado_sns)
                    VALUES (?, ?, ?, ?, 1)
                    """,
                    (sensor_id, tipo_alerta, severidade, mensagem),
                )
                cn.commit()
        except Exception:
            pass  # falha aqui não deve impedir o envio em si

    def listar_alertas_enviados(self, limit: int = 50) -> List[Dict]:
        """Retorna os alertas já publicados (``enviado_sns=1``)."""
        try:
            with self._conn() as cn:
                cur = cn.execute(
                    """
                    SELECT alerta_id, timestamp, sensor_id, tipo_alerta,
                           severidade, mensagem
                    FROM alertas
                    WHERE enviado_sns = 1
                    ORDER BY timestamp DESC, alerta_id DESC
                    LIMIT ?
                    """,
                    (int(limit),),
                )
                colunas = [c[0] for c in cur.description]
                return [dict(zip(colunas, row)) for row in cur.fetchall()]
        except Exception:
            return []

    # ------------------------------------------------------
    # Envio
    # ------------------------------------------------------

    def _formatar_mensagem(
        self,
        severidade: str,
        contexto: str,
        acao: str,
    ) -> Tuple[str, str]:
        """Monta (assunto, corpo) com cabeçalho e timestamp padronizados."""
        icone = "🔴 CRÍTICO" if severidade.upper() == "CRITICO" else "🟠 ALTO"
        assunto = f"[FarmTech] {icone} — Alerta automático"
        corpo = (
            f"{icone}\n"
            f"{'-' * 32}\n"
            f"{contexto}\n\n"
            f"AÇÃO CORRETIVA:\n  {acao}\n\n"
            f"Timestamp: {datetime.now().isoformat(timespec='seconds')}\n"
        )
        return assunto, corpo

    def enviar_alerta(
        self,
        assunto: str,
        mensagem: str,
        severidade: str = "ALTO",
    ) -> Dict:
        """Publica uma mensagem no SNS (ou no log de simulação).

        Args:
            assunto:    Subject do e-mail (será encurtado se > 100 chars).
            mensagem:   Corpo completo.
            severidade: ``"CRITICO"`` ou ``"ALTO"``.

        Returns:
            ``{"ok": bool, "modo": "sns"|"simulado", "message_id": str|None,
               "mensagem": str}``.
            Não inclui credenciais.
        """
        assunto = (assunto or "Alerta FarmTech")[:100]

        if self.modo_simulado:
            try:
                LOG_SIMULADO.parent.mkdir(parents=True, exist_ok=True)
                with LOG_SIMULADO.open("a", encoding="utf-8") as fh:
                    fh.write(
                        f"\n=== {datetime.now().isoformat(timespec='seconds')} "
                        f"[{severidade}] ===\n"
                        f"Subject: {assunto}\n{mensagem}\n"
                    )
                return {
                    "ok": True,
                    "modo": "simulado",
                    "message_id": None,
                    "mensagem": "Alerta gravado no log (modo simulado).",
                }
            except Exception as exc:
                return {
                    "ok": False,
                    "modo": "simulado",
                    "message_id": None,
                    "mensagem": f"Falha ao gravar no log: {type(exc).__name__}.",
                }

        try:
            resp = self._client().publish(
                TopicArn=self.topic_arn,
                Subject=assunto,
                Message=mensagem,
            )
            return {
                "ok": True,
                "modo": "sns",
                "message_id": resp.get("MessageId"),
                "mensagem": "Mensagem publicada no SNS.",
            }
        except Exception as exc:
            return {
                "ok": False,
                "modo": "sns",
                "message_id": None,
                "mensagem": f"Falha no publish: {type(exc).__name__}.",
            }

    # ------------------------------------------------------
    # Coleta de gatilhos no banco
    # ------------------------------------------------------

    def _coletar_leituras_recentes(self) -> List[Dict]:
        """Última leitura de cada sensor (para avaliar regra)."""
        try:
            with self._conn() as cn:
                cur = cn.execute(
                    """
                    SELECT l.*
                    FROM leituras_sensores l
                    JOIN (
                        SELECT sensor_id, MAX(timestamp) AS ts
                        FROM leituras_sensores
                        GROUP BY sensor_id
                    ) u ON l.sensor_id = u.sensor_id AND l.timestamp = u.ts
                    """
                )
                cols = [c[0] for c in cur.description]
                return [dict(zip(cols, row)) for row in cur.fetchall()]
        except Exception:
            return []

    def _coletar_analises_visuais_recentes(self, limit: int = 10) -> List[Dict]:
        """Últimas N análises visuais (Fase 6)."""
        try:
            with self._conn() as cn:
                cur = cn.execute(
                    """
                    SELECT id, timestamp, imagem, status, num_deteccoes
                    FROM analises_visuais
                    ORDER BY id DESC LIMIT ?
                    """,
                    (int(limit),),
                )
                cols = [c[0] for c in cur.description]
                return [dict(zip(cols, row)) for row in cur.fetchall()]
        except Exception:
            return []

    # ------------------------------------------------------
    # REGRAS DE NEGÓCIO
    # ------------------------------------------------------

    def _regras_leitura(self, leitura: Dict) -> List[Dict]:
        """Lista de alertas (não enviados ainda) gerados por uma leitura."""
        sid = leitura.get("sensor_id")
        alertas: List[Dict] = []

        umidade = leitura.get("soil_moisture")
        if umidade is not None and umidade < self.limiares["ALERTA_UMIDADE_CRITICA"]:
            alertas.append({
                "sensor_id": sid,
                "tipo_alerta": "UMIDADE_CRITICA",
                "severidade": "CRITICO",
                "contexto": (
                    f"Sensor {sid} — umidade do solo {umidade:.1f}% "
                    f"abaixo do crítico ({self.limiares['ALERTA_UMIDADE_CRITICA']:.0f}%)."
                ),
                "acao": f"Acionar irrigação imediatamente no setor do sensor {sid}.",
            })

        ph = leitura.get("soil_pH")
        if ph is not None and (
            ph < self.limiares["ALERTA_PH_MIN"]
            or ph > self.limiares["ALERTA_PH_MAX"]
        ):
            corretivo = (
                "calcário (subir pH)"
                if ph < self.limiares["ALERTA_PH_MIN"]
                else "enxofre (baixar pH)"
            )
            alertas.append({
                "sensor_id": sid,
                "tipo_alerta": "PH_FORA_FAIXA",
                "severidade": "ALTO",
                "contexto": (
                    f"Sensor {sid} — pH do solo {ph:.2f} fora da faixa "
                    f"{self.limiares['ALERTA_PH_MIN']:.1f}–"
                    f"{self.limiares['ALERTA_PH_MAX']:.1f}."
                ),
                "acao": (
                    f"Aplicar corretivo de solo: {corretivo} antes da próxima irrigação."
                ),
            })

        temp = leitura.get("temperature_C")
        if temp is not None and temp > self.limiares["ALERTA_TEMP_MAX"]:
            alertas.append({
                "sensor_id": sid,
                "tipo_alerta": "TEMPERATURA_ALTA",
                "severidade": "ALTO",
                "contexto": (
                    f"Sensor {sid} — temperatura {temp:.1f}°C acima do limite "
                    f"({self.limiares['ALERTA_TEMP_MAX']:.0f}°C)."
                ),
                "acao": "Risco de estresse térmico — antecipar irrigação.",
            })

        return alertas

    def _regras_visao(self, analise: Dict) -> List[Dict]:
        """Alertas gerados a partir de uma análise visual (Fase 6)."""
        status = (analise.get("status") or "").lower()
        # status agrícola textual da Fase 6: praga, saudavel, pessoa, objetos
        # OBS: status no banco é a mensagem (com emoji). Detectamos pela palavra-chave.
        if "praga" in status or "⚠️" in (analise.get("status") or ""):
            return [{
                "sensor_id": f"VIS_{analise.get('id')}",
                "tipo_alerta": "PRAGA_VISUAL",
                "severidade": "CRITICO",
                "contexto": (
                    f"Análise visual #{analise.get('id')} "
                    f"({analise.get('imagem')}) — {analise.get('status')} "
                    f"({analise.get('num_deteccoes')} detecções)."
                ),
                "acao": (
                    "Inspecionar o talhão e avaliar aplicação de defensivo "
                    "ou medidas de manejo integrado de pragas."
                ),
            }]
        return []

    # ------------------------------------------------------
    # Orquestração
    # ------------------------------------------------------

    def verificar_e_alertar(self) -> Dict:
        """Varre o banco e envia alertas pendentes (respeitando cooldown).

        Returns:
            ``{"avaliados": int, "enviados": int, "ignorados_cooldown": int,
               "erros": int, "detalhes": [...]}``.
        """
        self._garantir_coluna_enviado_sns()

        candidatos: List[Dict] = []
        for leitura in self._coletar_leituras_recentes():
            candidatos.extend(self._regras_leitura(leitura))
        for analise in self._coletar_analises_visuais_recentes():
            candidatos.extend(self._regras_visao(analise))

        enviados = 0
        ignorados = 0
        erros = 0
        detalhes: List[Dict] = []

        for c in candidatos:
            if self._ja_alertado_no_cooldown(c["sensor_id"], c["tipo_alerta"]):
                ignorados += 1
                detalhes.append({**c, "status": "cooldown"})
                continue
            assunto, corpo = self._formatar_mensagem(
                c["severidade"], c["contexto"], c["acao"]
            )
            resultado = self.enviar_alerta(assunto, corpo, severidade=c["severidade"])
            if resultado["ok"]:
                self._registrar_envio(
                    c["sensor_id"], c["tipo_alerta"],
                    c["severidade"], c["contexto"],
                )
                enviados += 1
                detalhes.append({**c, "status": "enviado",
                                 "modo": resultado["modo"]})
            else:
                erros += 1
                detalhes.append({**c, "status": "erro"})

        return {
            "avaliados": len(candidatos),
            "enviados": enviados,
            "ignorados_cooldown": ignorados,
            "erros": erros,
            "detalhes": detalhes,
        }


# ==========================================================
#         EXECUÇÃO DIRETA (smoke-test, sem expor credenciais)
# ==========================================================

if __name__ == "__main__":
    svc = ServicoAlertas()
    print("ARN mascarado:", svc.mascarar_arn())
    print("Região:", svc.region)
    print("Limiares:", svc.limiares)
    print("Modo simulado?", svc.modo_simulado)
    print("Teste de conexão:", svc.testar_conexao())
