"""
FarmTech Solutions - Dashboard de Monitoramento IoT
Visualização em Tempo Real dos Dados dos Sensores

Autores: Grupo 37 - FIAP
Data: Novembro 2025
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from contextlib import contextmanager
from database_manager import FarmTechDatabase
from services.fase3_irrigacao import (
    ControladorIrrigacao,
    UMIDADE_MIN_PERCENT,
    UMIDADE_MAX_PERCENT,
    PH_MIN,
    PH_MAX,
)


# ============================================
# CONEXÃO CURTA AO BANCO (Fase 3)
# ============================================

@contextmanager
def _abrir_db_curta():
    """Abre/fecha uma conexão SQLite curta para operações de escrita.

    Usada pela seção de Irrigação Automatizada (Fase 3) para não
    manter o lock do banco enquanto o simulador IoT está gravando.
    """
    db_curta = FarmTechDatabase("farmtech_iot.db")
    try:
        yield db_curta
    finally:
        db_curta.fechar_conexao()


def _renderizar_lcd_16x2(linha1: str, linha2: str) -> str:
    """Formata duas strings em um bloco monoespaçado de 16x2 colunas."""
    l1 = (linha1[:16]).ljust(16)
    l2 = (linha2[:16]).ljust(16)
    moldura = "+" + "-" * 16 + "+"
    return f"{moldura}\n|{l1}|\n|{l2}|\n{moldura}"


def _icone_acao(acao: str) -> str:
    """Mapeia a ação do controlador para um emoji de status."""
    return {"LIGAR": "🟢", "DESLIGAR": "🔴", "BLOQUEADA": "🚫"}.get(acao, "⚪")


def renderizar_secao_irrigacao(df_leituras: pd.DataFrame) -> None:
    """Renderiza a seção '💧 Irrigação Automatizada (Fase 3)'.

    Lê a última leitura de cada sensor, passa pelo
    :class:`ControladorIrrigacao` e desenha cards de status, botão
    para registrar as decisões em ``historico_irrigacao``, tabela
    histórica, timeline Plotly e o display LCD 16x2 simulado.
    """
    st.header("💧 Irrigação Automatizada (Fase 3)")
    st.caption(
        f"Regra: umidade < {UMIDADE_MIN_PERCENT:.0f}% LIGA, "
        f"> {UMIDADE_MAX_PERCENT:.0f}% DESLIGA, "
        f"pH fora de {PH_MIN}–{PH_MAX} BLOQUEIA a bomba."
    )

    if df_leituras is None or df_leituras.empty:
        st.info("Sem leituras para avaliar.")
        return

    # Mantém o controlador na sessão para preservar a histerese.
    ctrl = st.session_state.setdefault("ctrl_irrigacao", ControladorIrrigacao())

    # Última leitura por sensor
    df_ult = (
        df_leituras.sort_values("timestamp", ascending=False)
        .drop_duplicates(subset=["sensor_id"], keep="first")
        .copy()
    )

    decisoes = []
    for _, linha in df_ult.iterrows():
        leitura = linha.to_dict()
        decisao = ctrl.avaliar(leitura)
        decisoes.append((leitura, decisao))

    # ---- Cards por sensor -----------------------------------
    colunas = st.columns(min(3, max(1, len(decisoes))))
    for idx, (leitura, decisao) in enumerate(decisoes):
        col = colunas[idx % len(colunas)]
        with col:
            icone = _icone_acao(decisao["acao"])
            st.markdown(
                f"### {icone} {leitura.get('sensor_id', '—')}"
            )
            st.caption(leitura.get("localizacao", "—"))
            if decisao["acao"] == "BLOQUEADA":
                st.error(f"Bomba **BLOQUEADA** — {decisao['motivo']}")
            elif decisao["acao"] == "LIGAR":
                st.success(f"Bomba **LIGADA** — {decisao['motivo']}")
            else:
                st.warning(f"Bomba **DESLIGADA** — {decisao['motivo']}")
            st.caption(f"🛠️ {decisao['recomendacao']}")

    # ---- Botão para registrar decisões ----------------------
    if st.button("⚙️ Avaliar e registrar agora", use_container_width=True):
        registradas = 0
        try:
            with _abrir_db_curta() as db_curta:
                for leitura, decisao in decisoes:
                    if db_curta.inserir_decisao_irrigacao(
                        sensor_id=leitura.get("sensor_id"),
                        acao=decisao["acao"],
                        motivo=decisao["motivo"],
                        umidade=leitura.get("soil_moisture"),
                        ph=leitura.get("soil_pH"),
                    ):
                        registradas += 1
            st.success(f"✅ {registradas} decisão(ões) registrada(s).")
            st.rerun()
        except Exception as exc:
            st.error(f"❌ Erro ao registrar: {exc}")

    # ---- Display LCD simulado -------------------------------
    if decisoes:
        opcoes_lcd = {
            f"{leitura.get('sensor_id')} ({leitura.get('localizacao', '—')})":
                (leitura, decisao)
            for leitura, decisao in decisoes
        }
        chave_lcd = st.selectbox(
            "📟 Display LCD 16x2 — selecione um sensor",
            list(opcoes_lcd.keys()),
        )
        leitura_lcd, decisao_lcd = opcoes_lcd[chave_lcd]
        umidade_v = leitura_lcd.get("soil_moisture", 0) or 0
        ph_v = leitura_lcd.get("soil_pH", 0) or 0
        if decisao_lcd["acao"] == "LIGAR":
            estado_bomba = "BOMBA: LIGADA"
        elif decisao_lcd["acao"] == "DESLIGAR":
            estado_bomba = "BOMBA: DESLIG."
        else:
            estado_bomba = "BOMBA: BLOQ."
        linha1 = f"U:{umidade_v:.0f}% pH:{ph_v:.1f}"
        st.code(_renderizar_lcd_16x2(linha1, estado_bomba), language="text")

    # ---- Histórico de decisões ------------------------------
    st.subheader("🗂️ Histórico de decisões")
    with _abrir_db_curta() as db_curta:
        df_hist = db_curta.obter_historico_irrigacao(limit=50)

    if df_hist.empty:
        st.info(
            "Nenhuma decisão registrada ainda. "
            "Clique em **Avaliar e registrar agora** para começar."
        )
    else:
        st.dataframe(df_hist, use_container_width=True, hide_index=True)

        df_plot = df_hist.copy()
        df_plot["timestamp"] = pd.to_datetime(df_plot["timestamp"])
        cores = {"LIGAR": "#2E7D32", "DESLIGAR": "#1565C0", "BLOQUEADA": "#C62828"}
        fig = px.scatter(
            df_plot,
            x="timestamp",
            y="umidade",
            color="acao",
            color_discrete_map=cores,
            hover_data=["sensor_id", "ph", "motivo"],
            title="Timeline das decisões de irrigação",
            labels={"timestamp": "Tempo", "umidade": "Umidade do solo (%)"},
        )
        fig.add_hline(
            y=UMIDADE_MIN_PERCENT,
            line_dash="dot",
            line_color="#EF6C00",
            annotation_text=f"Mín {UMIDADE_MIN_PERCENT:.0f}%",
        )
        fig.add_hline(
            y=UMIDADE_MAX_PERCENT,
            line_dash="dot",
            line_color="#1E88E5",
            annotation_text=f"Máx {UMIDADE_MAX_PERCENT:.0f}%",
        )
        fig.update_layout(height=420, legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

# Configuração da página
st.set_page_config(
    page_title="Monitoramento IoT - FarmTech",
    page_icon="📡",
    layout="wide"
)

# CSS customizado
st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)


def conectar_banco():
    """Conecta ao banco de dados."""
    try:
        db = FarmTechDatabase("farmtech_iot.db")
        return db
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None


def main():
    """Função principal do dashboard."""

    st.title("📡 Monitoramento de Sensores IoT em Tempo Real")
    st.markdown("---")

    # Conectar ao banco
    db = conectar_banco()

    if db is None:
        st.error("⚠️ Não foi possível conectar ao banco de dados!")
        st.info("Execute primeiro o simulador IoT: `python iot_simulator.py`")
        return

    # Sidebar com controles
    st.sidebar.title("⚙️ Configurações")

    auto_refresh = st.sidebar.checkbox("🔄 Atualização Automática", value=False)
    refresh_interval = st.sidebar.slider(
        "Intervalo (segundos)",
        min_value=5,
        max_value=60,
        value=10
    )

    # Botão de atualização manual
    if st.sidebar.button("🔃 Atualizar Dados"):
        st.rerun()

    st.sidebar.markdown("---")

    # Obter dados
    df_leituras = db.obter_ultimas_leituras(limit=500)
    df_alertas = db.obter_alertas_ativos()

    if len(df_leituras) == 0:
        st.warning("⚠️ Nenhuma leitura encontrada no banco de dados!")
        st.info("""
        ### Como começar:
        1. Execute o simulador IoT: `python iot_simulator.py`
        2. Aguarde alguns segundos para os dados serem coletados
        3. Atualize esta página
        """)
        return

    # ============================================
    # SEÇÃO 1: MÉTRICAS PRINCIPAIS
    # ============================================
    st.header("📊 Métricas Gerais do Sistema")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_sensores = df_leituras['sensor_id'].nunique()
        st.metric(
            label="🔌 Sensores Ativos",
            value=total_sensores,
            delta=None
        )

    with col2:
        total_leituras = len(df_leituras)
        st.metric(
            label="📈 Total de Leituras",
            value=f"{total_leituras:,}",
            delta=None
        )

    with col3:
        alertas_ativos = len(df_alertas)
        st.metric(
            label="⚠️ Alertas Ativos",
            value=alertas_ativos,
            delta=None
        )

    with col4:
        if len(df_leituras) > 0:
            ultima_leitura = pd.to_datetime(df_leituras['timestamp'].max())
            tempo_decorrido = (datetime.now() - ultima_leitura).total_seconds()
            st.metric(
                label="🕐 Última Atualização",
                value=f"{int(tempo_decorrido)}s atrás",
                delta=None
            )

    st.markdown("---")

    # ============================================
    # SEÇÃO 2: ALERTAS ATIVOS
    # ============================================
    if len(df_alertas) > 0:
        st.header("⚠️ Alertas Ativos")

        # Classificar alertas por severidade
        alertas_alta = df_alertas[df_alertas['severidade'] == 'alta']
        alertas_media = df_alertas[df_alertas['severidade'] == 'media']
        alertas_baixa = df_alertas[df_alertas['severidade'] == 'baixa']

        col1, col2, col3 = st.columns(3)

        with col1:
            st.error(f"🔴 Alta: {len(alertas_alta)}")
            if len(alertas_alta) > 0:
                for _, alerta in alertas_alta.iterrows():
                    st.write(f"• {alerta['mensagem']}")

        with col2:
            st.warning(f"🟡 Média: {len(alertas_media)}")
            if len(alertas_media) > 0:
                for _, alerta in alertas_media.iterrows():
                    st.write(f"• {alerta['mensagem']}")

        with col3:
            st.info(f"🟢 Baixa: {len(alertas_baixa)}")
            if len(alertas_baixa) > 0:
                for _, alerta in alertas_baixa.iterrows():
                    st.write(f"• {alerta['mensagem']}")

        st.markdown("---")

    # ============================================
    # SEÇÃO 2.5: IRRIGAÇÃO AUTOMATIZADA (Fase 3)
    # ============================================
    renderizar_secao_irrigacao(df_leituras)

    # ============================================
    # SEÇÃO 2.6: ALERTAS AWS AUTOMÁTICOS (Fase 5)
    # ============================================
    st.subheader("🔔 Alertas AWS")
    auto_alertas = st.toggle(
        "🔔 Alertas AWS automáticos",
        value=False,
        help=(
            "Quando ativo, a cada recarga da página o ServicoAlertas "
            "avalia o banco e publica novos alertas no tópico SNS "
            "(respeitando o cooldown)."
        ),
    )
    if auto_alertas:
        try:
            from services.alert_service import ServicoAlertas
            svc = st.session_state.setdefault("svc_alertas_iot", ServicoAlertas())
            resumo = svc.verificar_e_alertar()
            if resumo["enviados"] > 0:
                st.success(
                    f"✅ {resumo['enviados']} alerta(s) publicado(s); "
                    f"{resumo['ignorados_cooldown']} em cooldown."
                )
            else:
                st.caption(
                    f"Sem novos alertas — {resumo['avaliados']} candidato(s) avaliados, "
                    f"{resumo['ignorados_cooldown']} em cooldown."
                )
        except Exception as exc:  # pragma: no cover - nunca derrubar o dashboard
            st.warning(
                f"Não foi possível executar a varredura de alertas: "
                f"{type(exc).__name__}."
            )

    # ============================================
    # SEÇÃO 3: DADOS POR SENSOR
    # ============================================
    st.header("🔍 Análise por Sensor")

    # Seletor de sensor
    sensores_disponiveis = df_leituras['sensor_id'].unique()
    sensor_selecionado = st.selectbox(
        "Selecione um sensor:",
        options=sensores_disponiveis
    )

    # Filtrar dados do sensor
    df_sensor = df_leituras[df_leituras['sensor_id'] == sensor_selecionado].copy()
    df_sensor['timestamp'] = pd.to_datetime(df_sensor['timestamp'])
    df_sensor = df_sensor.sort_values('timestamp')

    # Informações do sensor
    if len(df_sensor) > 0:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.info(f"**Localização:** {df_sensor.iloc[0]['localizacao']}")
        with col2:
            st.info(f"**Farm ID:** {df_sensor.iloc[0]['farm_id']}")
        with col3:
            st.info(f"**Tipo:** {df_sensor.iloc[0]['tipo_sensor']}")

    # ============================================
    # GRÁFICOS DE SÉRIES TEMPORAIS
    # ============================================

    st.subheader("📈 Evolução Temporal dos Parâmetros")

    # Temperatura
    col1, col2 = st.columns(2)

    with col1:
        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(
            x=df_sensor['timestamp'],
            y=df_sensor['temperature_C'],
            mode='lines+markers',
            name='Temperatura',
            line=dict(color='#FF6B6B', width=2),
            marker=dict(size=6)
        ))
        fig_temp.update_layout(
            title="🌡️ Temperatura (°C)",
            xaxis_title="Tempo",
            yaxis_title="Temperatura (°C)",
            hovermode='x unified'
        )
        st.plotly_chart(fig_temp, use_container_width=True)

    with col2:
        fig_hum = go.Figure()
        fig_hum.add_trace(go.Scatter(
            x=df_sensor['timestamp'],
            y=df_sensor['humidity_percent'],
            mode='lines+markers',
            name='Umidade do Ar',
            line=dict(color='#4ECDC4', width=2),
            marker=dict(size=6)
        ))
        fig_hum.update_layout(
            title="💧 Umidade do Ar (%)",
            xaxis_title="Tempo",
            yaxis_title="Umidade (%)",
            hovermode='x unified'
        )
        st.plotly_chart(fig_hum, use_container_width=True)

    # pH e Umidade do Solo
    col1, col2 = st.columns(2)

    with col1:
        fig_ph = go.Figure()
        fig_ph.add_trace(go.Scatter(
            x=df_sensor['timestamp'],
            y=df_sensor['soil_pH'],
            mode='lines+markers',
            name='pH do Solo',
            line=dict(color='#95E1D3', width=2),
            marker=dict(size=6)
        ))
        # Adicionar linha de referência (pH ideal)
        fig_ph.add_hline(y=6.5, line_dash="dash", line_color="green",
                         annotation_text="pH Ideal")
        fig_ph.update_layout(
            title="🧪 pH do Solo",
            xaxis_title="Tempo",
            yaxis_title="pH",
            hovermode='x unified'
        )
        st.plotly_chart(fig_ph, use_container_width=True)

    with col2:
        fig_moisture = go.Figure()
        fig_moisture.add_trace(go.Scatter(
            x=df_sensor['timestamp'],
            y=df_sensor['soil_moisture'],
            mode='lines+markers',
            name='Umidade do Solo',
            line=dict(color='#A8E6CF', width=2),
            marker=dict(size=6),
            fill='tozeroy'
        ))
        # Adicionar zona crítica
        fig_moisture.add_hrect(
            y0=0, y1=20,
            line_width=0, fillcolor="red", opacity=0.2,
            annotation_text="Zona Crítica", annotation_position="top left"
        )
        fig_moisture.update_layout(
            title="💦 Umidade do Solo (%)",
            xaxis_title="Tempo",
            yaxis_title="Umidade (%)",
            hovermode='x unified'
        )
        st.plotly_chart(fig_moisture, use_container_width=True)

    # NPK
    st.subheader("🌿 Nutrientes do Solo (NPK)")

    fig_npk = go.Figure()
    fig_npk.add_trace(go.Scatter(
        x=df_sensor['timestamp'],
        y=df_sensor['N'],
        mode='lines+markers',
        name='Nitrogênio (N)',
        line=dict(color='#FFD93D', width=2)
    ))
    fig_npk.add_trace(go.Scatter(
        x=df_sensor['timestamp'],
        y=df_sensor['P'],
        mode='lines+markers',
        name='Fósforo (P)',
        line=dict(color='#6BCB77', width=2)
    ))
    fig_npk.add_trace(go.Scatter(
        x=df_sensor['timestamp'],
        y=df_sensor['K'],
        mode='lines+markers',
        name='Potássio (K)',
        line=dict(color='#4D96FF', width=2)
    ))
    fig_npk.update_layout(
        title="Evolução dos Nutrientes (mg/kg)",
        xaxis_title="Tempo",
        yaxis_title="Concentração (mg/kg)",
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_npk, use_container_width=True)

    st.markdown("---")

    # ============================================
    # SEÇÃO 4: ESTATÍSTICAS DO SENSOR
    # ============================================
    st.header("📊 Estatísticas do Sensor")

    # Obter estatísticas
    stats = db.obter_estatisticas_sensor(sensor_selecionado, dias=7)

    if stats:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("🌡️ Temp. Média", f"{stats.get('avg_temp', 0):.1f}°C")
            st.metric("🌡️ Temp. Mín", f"{stats.get('min_temp', 0):.1f}°C")

        with col2:
            st.metric("🌡️ Temp. Máx", f"{stats.get('max_temp', 0):.1f}°C")
            st.metric("💧 Umidade Média", f"{stats.get('avg_humidity', 0):.1f}%")

        with col3:
            st.metric("💦 Umidade Solo", f"{stats.get('avg_moisture', 0):.1f}%")
            st.metric("🧪 pH Médio", f"{stats.get('avg_pH', 0):.2f}")

        with col4:
            st.metric("🌧️ Chuva Total", f"{stats.get('total_rainfall', 0):.1f}mm")
            st.metric("📊 Total Leituras", f"{stats.get('total_leituras', 0):,}")

    st.markdown("---")

    # ============================================
    # SEÇÃO 5: TABELA DE DADOS BRUTOS
    # ============================================
    with st.expander("📋 Ver Dados Brutos (Últimas 50 leituras)"):
        df_display = df_sensor.head(50)[['timestamp', 'N', 'P', 'K', 'soil_pH',
                                         'temperature_C', 'humidity_percent',
                                         'soil_moisture', 'rainfall_mm']].copy()
        st.dataframe(df_display, use_container_width=True)

    # ============================================
    # AUTO-REFRESH
    # ============================================
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

    # Fechar conexão
    db.fechar_conexao()


if __name__ == "__main__":
    main()