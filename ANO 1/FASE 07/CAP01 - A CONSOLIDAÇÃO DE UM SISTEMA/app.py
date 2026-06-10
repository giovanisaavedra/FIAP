"""
FarmTech Solutions - Central de Comando (Fase 7)
Hub integrador dos serviços desenvolvidos nas Fases 1, 2, 3, 4, 5 e 6.

A página inicial deixou de ser apenas a home do dashboard de ML
(Fase 4) e passou a ser a Central de Comando do projeto: a partir
daqui o usuário acessa cada serviço integrado, dispara o simulador
IoT e acompanha o status operacional do sistema.

Autores: Giovani Saavedra e Marcio Elifas
RM: RM566797 e RM567871
GRUPO 37
1TIAOS - FIAP

FIAP - Fase 7 - 2026

Metodologia: CRISP-DM
Tecnologias: Python, Streamlit, Scikit-Learn, Plotly, YOLOv8, AWS
"""

# ==========================================================
#         IMPORTAÇÃO DE BIBLIOTECAS
# ==========================================================

import os
import sys
import subprocess
from pathlib import Path

import streamlit as st

from utils import render_header, render_sidebar

# ==========================================================
#         CONSTANTES E CAMINHOS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent
IOT_SIMULATOR_PATH = BASE_DIR / "iot_simulator.py"
DB_PATH = BASE_DIR / "farmtech_iot.db"

# Mapeamento (rótulo amigável -> caminho relativo) das páginas de destino.
PAGINA_FASE1 = "pages/1_🚜_Fase1_Calculos_e_Clima.py"
PAGINA_FASE2 = "pages/2_🗄️_Fase2_CRUD_Banco.py"
PAGINA_FASE3_IOT = "pages/3_📡_Fase3_Monitoramento_IoT.py"
PAGINA_FASE4_MODELAGEM = "pages/5_🤖_Fase4_Modelagem_Preditiva.py"
PAGINA_FASE4_PREVISOES = "pages/6_🔮_Fase4_Previsoes_Manual_IoT.py"
PAGINA_FASE4_INTERATIVA = "pages/7_🎛️_Fase4_Previsoes_Interativas.py"
PAGINA_FASE6 = "pages/9_📷_Fase6_Visao_Computacional.py"
PAGINA_FASE5 = "pages/10_🔔_Fase5_Alertas_AWS.py"

# ==========================================================
#         CONFIGURAÇÃO DA PÁGINA
# ==========================================================

st.set_page_config(
    page_title="FarmTech Solutions - Central Fase 7",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
#         CONTROLE DO SIMULADOR IoT (subprocess)
# ==========================================================

def _simulador_em_execucao() -> bool:
    """Retorna True se houver um processo do simulador ativo em sessão.

    O processo é guardado em ``st.session_state['iot_proc']`` quando
    iniciado. Quando o processo termina (poll() != None), o estado
    é considerado parado.
    """
    proc = st.session_state.get("iot_proc")
    if proc is None:
        return False
    return proc.poll() is None


def iniciar_simulador_iot() -> None:
    """Inicia o ``iot_simulator.py`` em subprocess não-bloqueante.

    Usa ``sys.executable`` para garantir o mesmo Python do Streamlit
    e armazena o objeto ``Popen`` em ``st.session_state`` para que
    o botão de parar possa encerrá-lo posteriormente.
    """
    if _simulador_em_execucao():
        st.toast("Simulador IoT já está em execução.", icon="ℹ️")
        return

    if not IOT_SIMULATOR_PATH.exists():
        st.error(f"Arquivo não encontrado: {IOT_SIMULATOR_PATH}")
        return

    try:
        creationflags = 0
        if os.name == "nt":
            # Em Windows, evita herdar o console do Streamlit.
            creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)

        proc = subprocess.Popen(
            [sys.executable, str(IOT_SIMULATOR_PATH)],
            cwd=str(BASE_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
        )
        st.session_state["iot_proc"] = proc
        st.session_state["iot_pid"] = proc.pid
        st.success(f"✅ Simulador IoT iniciado (PID {proc.pid}).")
    except Exception as exc:  # pragma: no cover - feedback visual
        st.error(f"❌ Falha ao iniciar o simulador: {exc}")


def parar_simulador_iot() -> None:
    """Encerra o subprocess do simulador IoT, se houver."""
    proc = st.session_state.get("iot_proc")
    if proc is None or proc.poll() is not None:
        st.info("Nenhum simulador em execução.")
        st.session_state.pop("iot_proc", None)
        st.session_state.pop("iot_pid", None)
        return

    try:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        st.success("🛑 Simulador IoT encerrado.")
    except Exception as exc:  # pragma: no cover - feedback visual
        st.error(f"❌ Erro ao parar o simulador: {exc}")
    finally:
        st.session_state.pop("iot_proc", None)
        st.session_state.pop("iot_pid", None)


# ==========================================================
#         CONSULTAS AO BANCO (status / alertas)
# ==========================================================

def carregar_status_banco() -> dict:
    """Lê o banco SQLite e devolve um resumo para o painel de status.

    Retorna sempre um dicionário com as chaves ``total_leituras``,
    ``alertas`` (DataFrame ou ``None``) e ``erro``. Falhas de leitura
    (banco vazio, sem tabela, arquivo inexistente) são capturadas e
    devolvidas no campo ``erro``.
    """
    resumo = {"total_leituras": 0, "alertas": None, "erro": None}

    try:
        # Import local para não pagar o custo se a página for trocada
        # antes do primeiro acesso ao banco.
        from database_manager import FarmTechDatabase

        db = FarmTechDatabase(str(DB_PATH))
        try:
            db.cursor.execute("SELECT COUNT(*) FROM leituras_sensores")
            resumo["total_leituras"] = int(db.cursor.fetchone()[0] or 0)

            import pandas as pd  # já é dependência do projeto

            resumo["alertas"] = pd.read_sql_query(
                """
                SELECT timestamp, sensor_id, tipo_alerta, severidade, mensagem
                FROM alertas
                ORDER BY timestamp DESC
                LIMIT 5
                """,
                db.conn,
            )
        finally:
            db.fechar_conexao()
    except Exception as exc:  # banco vazio, arquivo ausente, etc.
        resumo["erro"] = str(exc)

    return resumo


# ==========================================================
#         RENDERIZAÇÃO DA HOME
# ==========================================================

def _card_servico(titulo: str, descricao: str, cor: str) -> None:
    """Renderiza um pequeno cabeçalho colorido para cada card de serviço."""
    st.markdown(
        f"""
        <div style="background-color:{cor};padding:14px 18px;border-radius:8px;
                    margin-bottom:8px;color:white;">
            <div style="font-size:18px;font-weight:bold;">{titulo}</div>
            <div style="font-size:13px;opacity:0.95;">{descricao}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_painel_status() -> None:
    """Painel superior com status do simulador, total de leituras e alertas."""
    st.markdown("### 📊 Status do Sistema")

    status = carregar_status_banco()
    rodando = _simulador_em_execucao()
    pid = st.session_state.get("iot_pid")

    col1, col2, col3 = st.columns(3)

    with col1:
        if rodando:
            st.success(f"🟢 Simulador IoT em execução (PID {pid})")
        else:
            st.error("🔴 Simulador IoT parado")

    with col2:
        st.metric("📥 Leituras registradas", f"{status['total_leituras']:,}".replace(",", "."))

    with col3:
        alertas_df = status["alertas"]
        qtd_alertas = 0 if alertas_df is None else len(alertas_df)
        st.metric("🚨 Alertas recentes", qtd_alertas)

    with st.expander("Ver os 5 alertas mais recentes", expanded=False):
        if status["erro"]:
            st.warning(f"Banco indisponível ou vazio: {status['erro']}")
        elif alertas_df is None or alertas_df.empty:
            st.info("Sem alertas registrados no momento.")
        else:
            st.dataframe(alertas_df, use_container_width=True, hide_index=True)


def render_servicos_integrados() -> None:
    """Seção com os cards/botões dos serviços de cada Fase."""
    st.markdown("## 🚀 Serviços Integrados (Fases 1-6)")
    st.caption("Acesse cada serviço pelo botão correspondente.")

    # Linha 1 — Fases 1, 2 e 3
    col1, col2, col3 = st.columns(3)

    with col1:
        _card_servico(
            "🚜 Fase 1 — Cálculos e Clima",
            "Cálculo de área, insumos e consulta meteorológica.",
            "#2E7D32",
        )
        st.page_link(PAGINA_FASE1, label="Abrir Fase 1", icon="➡️")

    with col2:
        _card_servico(
            "🗄️ Fase 2 — Banco de Dados (CRUD)",
            "Gerenciar sensores, leituras, culturas e alertas.",
            "#1565C0",
        )
        st.page_link(PAGINA_FASE2, label="Abrir CRUD", icon="➡️")

    with col3:
        _card_servico(
            "📡 Fase 3 — IoT e Irrigação",
            "Simulador de sensores + Monitoramento em tempo real.",
            "#EF6C00",
        )

        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("▶ Iniciar Simulador IoT", use_container_width=True, key="btn_iot_start"):
                iniciar_simulador_iot()
                st.rerun()
        with btn_col2:
            if st.button("⏹ Parar Simulador", use_container_width=True, key="btn_iot_stop"):
                parar_simulador_iot()
                st.rerun()

        st.page_link(PAGINA_FASE3_IOT, label="Abrir Monitoramento IoT", icon="➡️")

    st.divider()

    # Linha 2 — Fases 4, 5 e 6
    col4, col5, col6 = st.columns(3)

    with col4:
        _card_servico(
            "🔮 Fase 4 — ML e Previsões",
            "Modelagem preditiva e previsões manuais/interativas.",
            "#6A1B9A",
        )
        st.page_link(PAGINA_FASE4_MODELAGEM, label="Modelagem Preditiva", icon="➡️")
        st.page_link(PAGINA_FASE4_PREVISOES, label="Previsões (Manual / IoT)", icon="➡️")
        st.page_link(PAGINA_FASE4_INTERATIVA, label="Previsões Interativas", icon="➡️")

    with col5:
        _card_servico(
            "🔔 Fase 5 — Alertas AWS",
            "Envio de notificações via SNS/Lambda na nuvem.",
            "#C62828",
        )
        st.page_link(PAGINA_FASE5, label="Abrir Alertas AWS", icon="➡️")

    with col6:
        _card_servico(
            "📷 Fase 6 — Visão Computacional",
            "Detecção de pragas e plantas com YOLOv8.",
            "#00838F",
        )
        st.page_link(PAGINA_FASE6, label="Abrir Visão Computacional", icon="➡️")


# ==========================================================
#         PÁGINA PRINCIPAL (HOME)
# ==========================================================

def main() -> None:
    """Renderiza a Central de Comando da Fase 7."""
    render_header()
    render_sidebar()

    st.title("🏠 Central de Comando — FarmTech Solutions (Fase 7)")
    st.markdown(
        """
        Esta é a **Central de Comando** do projeto FarmTech Solutions.
        A partir daqui, você acessa todos os serviços desenvolvidos ao
        longo das **Fases 1 a 6**, dispara o simulador IoT e acompanha
        o status operacional do sistema.

        👈 Use também o menu lateral para navegar livremente entre as páginas.
        """
    )

    st.divider()
    render_painel_status()

    st.divider()
    render_servicos_integrados()

    st.divider()

    st.markdown(
        """
        <div style='text-align: center; padding: 20px; color: #666;'>
            <p><strong>FarmTech Solutions</strong> - Agricultura de Precisão com IA</p>
            <p>FIAP - Fase 7 - 2026 | Integração das Fases 1 a 6</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================================
#         PONTO DE ENTRADA
# ==========================================================

if __name__ == "__main__":
    main()
