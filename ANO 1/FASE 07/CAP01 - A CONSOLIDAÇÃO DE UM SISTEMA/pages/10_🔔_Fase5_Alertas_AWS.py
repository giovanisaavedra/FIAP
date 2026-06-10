"""
FarmTech Solutions - Fase 5: Alertas em Nuvem (AWS SNS)
Operação manual e automática do tópico SNS ``farmtech-alertas``:
testar conexão, enviar mensagem de teste, varrer o banco e
publicar alertas, consultar o histórico de envios.

Atenção: credenciais ficam EXCLUSIVAMENTE em ``.env`` e nunca são
exibidas na UI — o ARN aparece mascarado (somente os 12 últimos
caracteres).

Autores: Giovani Saavedra e Marcio Elifas
RM: RM566797 e RM567871
GRUPO 37
1TIAOS - FIAP

FIAP - Fase 7 - 2026
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from services.alert_service import ServicoAlertas
from utils import render_header, render_sidebar


# ==========================================================
#         CONFIGURAÇÃO DA PÁGINA
# ==========================================================

st.set_page_config(
    page_title="Alertas AWS",
    page_icon="🔔",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent.parent


# ==========================================================
#         SERVIÇO (cache em sessão)
# ==========================================================

def get_servico() -> ServicoAlertas:
    """Reaproveita uma instância do ``ServicoAlertas`` na sessão."""
    if "servico_alertas" not in st.session_state:
        st.session_state["servico_alertas"] = ServicoAlertas()
    return st.session_state["servico_alertas"]


# ==========================================================
#         PAINEL DE STATUS
# ==========================================================

def painel_status(svc: ServicoAlertas) -> None:
    """Cards com região, ARN mascarado e diagnóstico do SNS."""
    st.subheader("📡 Status da integração SNS")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Região", svc.region or "—")
    with col2:
        st.metric("Tópico (ARN mascarado)", svc.mascarar_arn())
    with col3:
        st.metric(
            "Cooldown",
            f"{int(svc.limiares['ALERTA_COOLDOWN_MINUTOS'])} min",
        )

    diag = svc.testar_conexao()
    if diag["ok"] and diag["modo"] == "sns":
        st.success(f"✅ {diag['mensagem']}")
    elif diag["ok"] and diag["modo"] == "simulado":
        st.warning(f"⚠️ Modo simulado — {diag['mensagem']}")
    else:
        st.error(f"❌ {diag['mensagem']}")

    with st.expander("Limiares configurados", expanded=False):
        df_lim = pd.DataFrame(
            [{"parametro": k, "valor": v} for k, v in svc.limiares.items()]
        )
        st.dataframe(df_lim, use_container_width=True, hide_index=True)


# ==========================================================
#         AÇÕES MANUAIS
# ==========================================================

def acoes_manuais(svc: ServicoAlertas) -> None:
    """Botões: teste manual e varredura de regras."""
    st.subheader("⚙️ Ações")

    col1, col2 = st.columns(2)

    # --- Teste ---------------------------------------------
    with col1:
        if st.button(
            "✉️ Enviar alerta de teste",
            use_container_width=True,
            key="btn_alerta_teste",
        ):
            assunto = "[FarmTech] 🧪 Teste manual"
            corpo = (
                "🧪 TESTE\n"
                "--------------------------------\n"
                "Esta é uma mensagem de teste disparada manualmente pela "
                "Central de Comando — Fase 7.\n\n"
                f"Origem: dashboard Streamlit\n"
                f"Timestamp: {datetime.now().isoformat(timespec='seconds')}\n"
            )
            resultado = svc.enviar_alerta(assunto, corpo, severidade="ALTO")
            if resultado["ok"]:
                if resultado["modo"] == "sns":
                    st.success(
                        f"✅ Publicado no SNS — MessageId "
                        f"`{resultado['message_id']}`"
                    )
                else:
                    st.info(f"💾 {resultado['mensagem']}")
            else:
                st.error(f"❌ {resultado['mensagem']}")

    # --- Varredura -----------------------------------------
    with col2:
        if st.button(
            "🔍 Verificar sensores e enviar alertas",
            use_container_width=True,
            key="btn_varredura",
        ):
            with st.spinner("Avaliando regras e publicando alertas..."):
                resumo = svc.verificar_e_alertar()
            st.success(
                f"✅ {resumo['enviados']} enviado(s), "
                f"{resumo['ignorados_cooldown']} ignorado(s) (cooldown), "
                f"{resumo['erros']} erro(s) sobre {resumo['avaliados']} candidato(s)."
            )
            if resumo["detalhes"]:
                df = pd.DataFrame(
                    [
                        {
                            "sensor_id": d["sensor_id"],
                            "tipo_alerta": d["tipo_alerta"],
                            "severidade": d["severidade"],
                            "status": d.get("status"),
                            "contexto": d["contexto"],
                        }
                        for d in resumo["detalhes"]
                    ]
                )
                st.dataframe(df, use_container_width=True, hide_index=True)


# ==========================================================
#         HISTÓRICO
# ==========================================================

def secao_historico(svc: ServicoAlertas) -> None:
    """Tabela com os alertas já publicados (``enviado_sns=1``)."""
    st.subheader("🗂️ Histórico de alertas enviados")
    enviados = svc.listar_alertas_enviados(limit=50)
    if not enviados:
        st.info(
            "Nenhum alerta foi enviado ainda. "
            "Use **✉️ Enviar alerta de teste** ou **🔍 Verificar sensores**."
        )
        return
    df = pd.DataFrame(enviados)
    st.dataframe(df, use_container_width=True, hide_index=True)


# ==========================================================
#         EXPLICAÇÃO ARQUITETURAL
# ==========================================================

def explicacao_arquitetura() -> None:
    """Expander que documenta o fluxo — ponto de apoio para o vídeo."""
    with st.expander("ℹ️ Como funciona (arquitetura ponta a ponta)"):
        st.markdown(
            """
            ### Pipeline de alertas FarmTech

            ```
            [Sensor IoT]
                │  insere leitura (SQLite)
                ▼
            [farmtech_iot.db / leituras_sensores ou analises_visuais]
                │  ServicoAlertas.verificar_e_alertar()
                ▼
            [Regras de negócio (.env / DEFAULTS)]
                │  formata mensagem com severidade + ação corretiva
                ▼
            [Antideduplicação (alertas.enviado_sns + cooldown)]
                │  ainda não enviado nesse intervalo?
                ▼
            [AWS SNS — tópico farmtech-alertas]
                │  push para todas as assinaturas confirmadas
                ▼
            [E-mail / SMS / Lambda]  ← chega no(s) destinatário(s)
            ```

            **Regras implementadas**

            | Origem | Condição | Severidade | Ação corretiva |
            |---|---|---|---|
            | `leituras_sensores` | `soil_moisture < ALERTA_UMIDADE_CRITICA` | 🔴 CRÍTICO | Acionar irrigação imediatamente |
            | `leituras_sensores` | `soil_pH < ALERTA_PH_MIN` ou `> ALERTA_PH_MAX` | 🟠 ALTO | Aplicar calcário (ácido) ou enxofre (alcalino) |
            | `leituras_sensores` | `temperature_C > ALERTA_TEMP_MAX` | 🟠 ALTO | Antecipar irrigação para evitar estresse térmico |
            | `analises_visuais` | `status` contém "praga" | 🔴 CRÍTICO | Inspecionar talhão e avaliar defensivo |

            **Antideduplicação** — cada (sensor, tipo) só é reenviado após
            `ALERTA_COOLDOWN_MINUTOS` (default 30). Os envios ficam em
            `alertas.enviado_sns = 1`.

            **Segurança** — todas as credenciais AWS ficam no `.env`
            (ignorado pelo Git). O ARN aparece sempre mascarado.
            """
        )


# ==========================================================
#         PÁGINA PRINCIPAL
# ==========================================================

def main() -> None:
    """Ponto de entrada da página Alertas AWS."""
    render_header()
    render_sidebar()

    st.title("🔔 Fase 5 — Alertas em Nuvem (AWS SNS)")
    st.caption(
        "Painel de operação do tópico SNS `farmtech-alertas`. "
        "Regras avaliam o banco SQLite e publicam alertas com "
        "severidade e ação corretiva."
    )

    svc = get_servico()
    painel_status(svc)
    st.divider()
    acoes_manuais(svc)
    st.divider()
    secao_historico(svc)
    st.divider()
    explicacao_arquitetura()


if __name__ == "__main__":
    main()
