# ==========================================================
#         IMPORTAÇÃO DE BIBLIOTECAS
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
import os

# Adicionar path do database_manager
sys.path.append(os.path.dirname(__file__))

# Importar módulo do banco de dados
try:
    from database_manager import FarmTechDatabase

    IOT_DISPONIVEL = True
except ImportError:
    IOT_DISPONIVEL = False
    st.warning("⚠️ Módulo IoT não encontrado. Modo manual apenas.")

# ==========================================================
#         CONFIGURAÇÃO DA PÁGINA
# ==========================================================

st.set_page_config(
    page_title="Previsões - FarmTech",
    page_icon="🔮",
    layout="wide"
)

# Header
st.markdown("""
    <style>
    .header-container {
        background-color: #2E7D32;
        padding: 30px 50px;
        margin-bottom: 30px;
        margin-top: -50px;
        margin-left: -50px;
        margin-right: -50px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .header-title {
        color: white !important;
        font-size: 38px;
        font-weight: bold;
        margin: 0;
        padding: 0;
    }

    .header-subtitle {
        color: #C8E6C9;
        font-size: 18px;
        margin: 10px 0 0 0;
        padding: 0;
    }

    .prediction-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        margin: 10px 0;
    }

    .prediction-title {
        color: white;
        font-size: 18px;
        margin: 0;
    }

    .prediction-value {
        color: #FFD700;
        font-size: 36px;
        font-weight: bold;
        margin: 10px 0;
    }

    .prediction-unit {
        color: #E0E0E0;
        font-size: 14px;
    }

    .mode-selector {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    </style>

    <div class="header-container">
        <h1 class="header-title">🌾 FarmTech Solutions</h1>
        <p class="header-subtitle">Sistema de Previsão Agrícola com Machine Learning + IoT</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================================
#   🆕 NOVO: SELETOR DE MODO (IoT vs Manual)
# ==========================================================

st.markdown("### 🎛️ Selecione o Modo de Previsão")

col1, col2 = st.columns(2)

with col1:
    if st.button("📝 MODO MANUAL", use_container_width=True, type="secondary"):
        st.session_state['modo_previsao'] = 'manual'

with col2:
    if IOT_DISPONIVEL:
        if st.button("📡 MODO IoT (Dados de Sensores)", use_container_width=True, type="primary"):
            st.session_state['modo_previsao'] = 'iot'
    else:
        st.button("📡 MODO IoT (Indisponível)", use_container_width=True, disabled=True)

# Inicializar modo se não existir
if 'modo_previsao' not in st.session_state:
    st.session_state['modo_previsao'] = 'manual'

st.divider()

# Indicador visual do modo atual
if st.session_state['modo_previsao'] == 'manual':
    st.info("📝 **Modo Atual:** MANUAL - Insira os dados manualmente")
else:
    st.success("📡 **Modo Atual:** IoT - Usando dados dos sensores em tempo real")

st.divider()

# Sidebar
with st.sidebar:
    st.markdown("### 🔮 Previsões Disponíveis")
    st.info("""
        **3 Modelos Preditivos:**
        - 💧 Volume de Irrigação
        - 🌿 Fertilização NPK
        - 🌾 Rendimento
    """)

    st.divider()

    st.markdown("### 📋 Status dos Modelos")

    # Status Irrigação
    if 'modelo_irrigacao' in st.session_state:
        algoritmo = st.session_state['modelo_irrigacao'].get('algoritmo', 'N/A')
        st.success(f"✅ Irrigação: {algoritmo}")
    else:
        st.warning("⚠️ Modelo de Irrigação não carregado")

    # Status Fertilização
    if 'modelo_fertilizacao' in st.session_state:
        algoritmo = st.session_state['modelo_fertilizacao'].get('algoritmo', 'N/A')
        st.success(f"✅ Fertilização: {algoritmo}")
    else:
        st.warning("⚠️ Modelo de Fertilização não carregado")

    # Status Rendimento
    if 'modelo_rendimento' in st.session_state:
        algoritmo = st.session_state['modelo_rendimento'].get('algoritmo', 'N/A')
        st.success(f"✅ Rendimento: {algoritmo}")
    else:
        st.warning("⚠️ Modelo de Rendimento não carregado")

    st.divider()

    st.markdown("### 🔄 Modo Ativo")
    if st.session_state['modo_previsao'] == 'manual':
        st.info("📝 Entrada Manual")
    else:
        st.success("📡 Sensores IoT")


# ==========================================================
#         FUNÇÕES AUXILIARES (mantidas do código original)
# ==========================================================

def calcular_features_derivadas(inputs, cultura):
    """
    Calcula features derivadas necessárias para os modelos
    """
    features = {}

    # Mapas de demanda
    demanda_agua_map = {
        'Maize': 600, 'Rice': 1200, 'Soybean': 500,
        'Wheat': 450, 'Cotton': 800
    }

    rendimento_map = {
        'Maize': 6000, 'Rice': 7000, 'Soybean': 3500,
        'Wheat': 4500, 'Cotton': 2500
    }

    preco_map = {
        'Maize': 0.20, 'Rice': 0.30, 'Soybean': 0.35,
        'Wheat': 0.25, 'Cotton': 1.50
    }

    # Água
    features['agua_total_mm'] = inputs['rainfall_mm'] + inputs['volume_irrigacao_mm']
    features['NPK_total'] = inputs['N'] + inputs['P'] + inputs['K']
    features['NPK_fertilizacao_total'] = (inputs['N_fertilizacao_kg_ha'] +
                                          inputs['P_fertilizacao_kg_ha'] +
                                          inputs['K_fertilizacao_kg_ha'])

    features['evapotranspiracao_estimada'] = inputs['temperature_C'] * 0.16 * (
            (100 - inputs['humidity_%']) / 100)
    features['deficit_hidrico_mm'] = max(0, features['evapotranspiracao_estimada'] - inputs['rainfall_mm'])

    features['demanda_agua_cultura'] = demanda_agua_map.get(cultura, 600)
    features['balanco_hidrico'] = features['agua_total_mm'] - features['demanda_agua_cultura']
    features['necessidade_irrigacao_teorica'] = max(0, features['evapotranspiracao_estimada'] -
                                                    inputs['rainfall_mm'])
    features['indice_aridez'] = inputs['rainfall_mm'] / (inputs['temperature_C'] + 10)
    features['agua_adequacao'] = features['agua_total_mm'] / features['demanda_agua_cultura']

    # Fertilização
    disponibilidade = 1.0 if 5.5 <= inputs['soil_pH'] <= 7.0 else 0.6
    features['disponibilidade_nutrientes'] = disponibilidade
    features['N_disponivel'] = inputs['N'] * disponibilidade
    features['P_disponivel'] = inputs['P'] * disponibilidade
    features['K_disponivel'] = inputs['K'] * disponibilidade

    features['razao_NP'] = inputs['N'] / (inputs['P'] + 0.1)
    features['razao_NK'] = inputs['N'] / (inputs['K'] + 0.1)
    features['razao_PK'] = inputs['P'] / (inputs['K'] + 0.1)

    features['desvio_NPK_ideal'] = abs((inputs['N'] / 4) - (inputs['P'] / 2) - (inputs['K'] / 1))

    features['eficiencia_N'] = 50.0
    features['eficiencia_P'] = 60.0
    features['eficiencia_K'] = 55.0

    # Rendimento
    features['estresse_termico'] = 1 if (inputs['temperature_C'] > 35 or
                                         inputs['temperature_C'] < 15) else 0
    features['estresse_hidrico'] = 1 if features['agua_total_mm'] < features['demanda_agua_cultura'] * 0.6 else 0
    features['estresse_total'] = features['estresse_termico'] + features['estresse_hidrico']

    features['condicoes_ideais'] = (
            (1 if 20 <= inputs['temperature_C'] <= 30 else 0) * 0.3 +
            (1 if 60 <= inputs['humidity_%'] <= 80 else 0) * 0.3 +
            (1 if 5.5 <= inputs['soil_pH'] <= 7.0 else 0) * 0.4
    )

    features['NPK_agua_interacao'] = features['NPK_total'] * features['agua_adequacao']

    features['adequacao_insumos'] = (
            (features['NPK_total'] / 150) * 0.4 +
            features['agua_adequacao'] * 0.4 +
            features['condicoes_ideais'] * 0.2
    )

    # Econômicas
    features['custo_agua_m3'] = demanda_agua_map.get(cultura, 0.1) * 0.0002
    features['custo_irrigacao'] = inputs['volume_irrigacao_mm'] * 0.1 * 10
    features['custo_fertilizacao'] = (inputs['N_fertilizacao_kg_ha'] * 3.5 +
                                      inputs['P_fertilizacao_kg_ha'] * 4.2 +
                                      inputs['K_fertilizacao_kg_ha'] * 2.8)

    features['rendimento_potencial'] = rendimento_map.get(cultura, 5000)
    features['taxa_realizacao'] = min(1.0, features['adequacao_insumos'])
    features['preco_produto'] = preco_map.get(cultura, 0.25)
    features['receita_bruta'] = features['rendimento_potencial'] * features['taxa_realizacao'] * features[
        'preco_produto']
    features['margem_bruta'] = features['receita_bruta'] - features['custo_irrigacao'] - features['custo_fertilizacao']

    return features


def fazer_previsao(inputs_base, features_derivadas, cultura, modelo_info, features_list):
    """
    Faz previsão usando o modelo especificado
    """
    # Combinar inputs base com features derivadas
    all_features = {**inputs_base, **features_derivadas}

    # Adicionar one-hot encoding
    culturas_disponiveis = ['Maize', 'Rice', 'Soybean', 'Wheat', 'Cotton']
    for cult in culturas_disponiveis:
        if cult == 'Cotton':  # drop_first=True
            continue
        coluna = f'crop_type_{cult}'
        all_features[coluna] = 1 if cultura == cult else 0

    # Criar DataFrame
    df_input = pd.DataFrame([all_features])

    # Garantir ordem das colunas
    df_input = df_input[features_list]

    # Normalizar
    scaler = modelo_info['scaler']
    input_scaled = scaler.transform(df_input)

    # Aplicar transformação polinomial se necessário
    if modelo_info.get('poly') is not None:
        poly = modelo_info['poly']
        input_scaled = poly.transform(input_scaled)

    # Fazer previsão
    modelo = modelo_info['modelo']
    previsao = modelo.predict(input_scaled)[0]

    return previsao


# ==========================================================
#   🆕 FUNÇÃO PARA OBTER DADOS DOS SENSORES IoT
# ==========================================================

def obter_dados_sensores_iot():
    """
    Obtém os dados mais recentes dos sensores IoT
    """
    if not IOT_DISPONIVEL:
        st.error("❌ Módulo IoT não disponível")
        return None

    try:
        # Conectar ao banco de dados
        db = FarmTechDatabase("farmtech_iot.db")

        # Obter últimas leituras
        df_leituras = db.obter_ultimas_leituras(limit=10)

        db.fechar_conexao()

        if len(df_leituras) == 0:
            st.warning("⚠️ Nenhuma leitura encontrada. Execute o simulador IoT primeiro!")
            return None

        return df_leituras

    except Exception as e:
        st.error(f"❌ Erro ao acessar banco IoT: {e}")
        return None


# ==========================================================
#         INTERFACE - MODO IoT
# ==========================================================

if st.session_state['modo_previsao'] == 'iot':

    st.subheader("📡 Dados dos Sensores IoT")

    # Obter dados dos sensores
    df_sensores = obter_dados_sensores_iot()

    if df_sensores is not None and len(df_sensores) > 0:

        # Seletor de sensor
        sensores_disponiveis = df_sensores['sensor_id'].unique().tolist()
        sensor_selecionado = st.selectbox(
            "🔌 Selecione o Sensor:",
            sensores_disponiveis
        )

        # Filtrar dados do sensor selecionado
        df_sensor = df_sensores[df_sensores['sensor_id'] == sensor_selecionado]

        # Pegar a leitura mais recente
        leitura_recente = df_sensor.iloc[0]

        # Mostrar dados do sensor
        st.success(f"✅ Última leitura: {leitura_recente['timestamp']}")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("🌡️ Temperatura", f"{leitura_recente['temperature_C']:.1f}°C")
            st.metric("💧 Umidade Ar", f"{leitura_recente['humidity_percent']:.1f}%")

        with col2:
            st.metric("💦 Umidade Solo", f"{leitura_recente.get('soil_moisture', 0):.1f}%")
            st.metric("🧪 pH", f"{leitura_recente['soil_pH']:.2f}")

        with col3:
            st.metric("🌿 N", f"{leitura_recente['N']:.1f} mg/kg")
            st.metric("🌿 P", f"{leitura_recente['P']:.1f} mg/kg")

        with col4:
            st.metric("🌿 K", f"{leitura_recente['K']:.1f} mg/kg")
            st.metric("🌧️ Chuva", f"{leitura_recente['rainfall_mm']:.1f} mm")

        st.divider()

        # Formulário simplificado para dados adicionais
        with st.form("form_iot"):
            st.markdown("**🌾 Informações Adicionais**")

            col1, col2 = st.columns(2)

            with col1:
                culturas_disponiveis = ['Maize', 'Rice', 'Soybean', 'Wheat', 'Cotton']
                input_cultura = st.selectbox("Tipo de Cultura", culturas_disponiveis)

            with col2:
                st.info("💡 Os demais dados virão do sensor")

            botao_prever_iot = st.form_submit_button(
                "🔮 GERAR PREVISÕES COM DADOS IoT",
                use_container_width=True,
                type="primary"
            )

        # Processar previsão com dados IoT
        if botao_prever_iot:

            # Preparar inputs a partir dos dados do sensor
            inputs_iot = {
                'N': float(leitura_recente['N']),
                'P': float(leitura_recente['P']),
                'K': float(leitura_recente['K']),
                'soil_pH': float(leitura_recente['soil_pH']),
                'temperature_C': float(leitura_recente['temperature_C']),
                'humidity_%': float(leitura_recente['humidity_percent']),
                'rainfall_mm': float(leitura_recente['rainfall_mm']),
                'volume_irrigacao_mm': float(leitura_recente.get('irrigation_volume_mm', 0)),
                'N_fertilizacao_kg_ha': 0.0,
                'P_fertilizacao_kg_ha': 0.0,
                'K_fertilizacao_kg_ha': 0.0,
            }

            st.divider()
            st.header("📊 Resultados das Previsões (Dados IoT)")

            with st.spinner("🤖 Processando previsões com dados dos sensores..."):

                resultados = {}

                # PREVISÃO 1: IRRIGAÇÃO
                if 'modelo_irrigacao' in st.session_state:
                    features = calcular_features_derivadas(inputs_iot, input_cultura)

                    previsao_irrigacao = fazer_previsao(
                        inputs_iot,
                        features,
                        input_cultura,
                        st.session_state['modelo_irrigacao'],
                        st.session_state['features_irrigacao']
                    )

                    resultados['irrigacao'] = max(0, previsao_irrigacao)
                    inputs_iot['volume_irrigacao_mm'] = resultados['irrigacao']

                # PREVISÃO 2: FERTILIZAÇÃO
                if 'modelo_fertilizacao' in st.session_state:
                    features = calcular_features_derivadas(inputs_iot, input_cultura)

                    target_fert = st.session_state.get('target_fertilizacao', 'N_fertilizacao_kg_ha')

                    previsao_fert = fazer_previsao(
                        inputs_iot,
                        features,
                        input_cultura,
                        st.session_state['modelo_fertilizacao'],
                        st.session_state['features_fertilizacao']
                    )

                    resultados['fertilizacao'] = max(0, previsao_fert)

                    if 'N' in target_fert:
                        inputs_iot['N_fertilizacao_kg_ha'] = resultados['fertilizacao']
                    elif 'P' in target_fert:
                        inputs_iot['P_fertilizacao_kg_ha'] = resultados['fertilizacao']
                    else:
                        inputs_iot['K_fertilizacao_kg_ha'] = resultados['fertilizacao']

                # PREVISÃO 3: RENDIMENTO
                if 'modelo_rendimento' in st.session_state:
                    features = calcular_features_derivadas(inputs_iot, input_cultura)

                    previsao_rendimento = fazer_previsao(
                        inputs_iot,
                        features,
                        input_cultura,
                        st.session_state['modelo_rendimento'],
                        st.session_state['features_rendimento']
                    )

                    resultados['rendimento'] = max(0, previsao_rendimento)

                # Exibir resultados (mesmo formato do modo manual)
                col1, col2, col3 = st.columns(3)

                with col1:
                    if 'irrigacao' in resultados:
                        st.markdown(f"""
                        <div class="prediction-card">
                            <p class="prediction-title">💧 Volume de Irrigação</p>
                            <p class="prediction-value">{resultados['irrigacao']:.2f}</p>
                            <p class="prediction-unit">mm</p>
                        </div>
                        """, unsafe_allow_html=True)

                with col2:
                    if 'fertilizacao' in resultados:
                        nutriente = st.session_state.get('target_fertilizacao', 'N_fertilizacao_kg_ha')
                        nutriente_nome = nutriente.split('_')[0]

                        st.markdown(f"""
                        <div class="prediction-card">
                            <p class="prediction-title">🌿 Fertilização {nutriente_nome}</p>
                            <p class="prediction-value">{resultados['fertilizacao']:.2f}</p>
                            <p class="prediction-unit">kg/ha</p>
                        </div>
                        """, unsafe_allow_html=True)

                with col3:
                    if 'rendimento' in resultados:
                        st.markdown(f"""
                        <div class="prediction-card">
                            <p class="prediction-title">🌾 Rendimento Esperado</p>
                            <p class="prediction-value">{resultados['rendimento']:.0f}</p>
                            <p class="prediction-unit">kg/ha</p>
                        </div>
                        """, unsafe_allow_html=True)

                st.success("✅ Previsões geradas com sucesso usando dados dos sensores IoT!")

                # Salvar previsão no banco (opcional)
                try:
                    db = FarmTechDatabase("farmtech_iot.db")

                    previsao_data = {
                        'cultura_id': None,
                        'input_N': inputs_iot['N'],
                        'input_P': inputs_iot['P'],
                        'input_K': inputs_iot['K'],
                        'input_soil_pH': inputs_iot['soil_pH'],
                        'input_temperature': inputs_iot['temperature_C'],
                        'input_humidity': inputs_iot['humidity_%'],
                        'input_rainfall': inputs_iot['rainfall_mm'],
                        'previsao_irrigacao_mm': resultados.get('irrigacao', 0),
                        'previsao_N_fertilizacao': resultados.get('fertilizacao', 0),
                        'previsao_P_fertilizacao': 0,
                        'previsao_K_fertilizacao': 0,
                        'previsao_rendimento_kg_ha': resultados.get('rendimento', 0),
                        'modelo_usado': 'ML Pipeline',
                        'confianca_previsao': 0.85
                    }

                    previsao_id = db.inserir_previsao_ml(previsao_data)

                    if previsao_id > 0:
                        st.info(f"💾 Previsão salva no banco com ID: {previsao_id}")

                    db.fechar_conexao()

                except Exception as e:
                    st.warning(f"⚠️ Não foi possível salvar previsão no banco: {e}")

    else:
        st.warning("""
        ⚠️ **Nenhum dado de sensor disponível!**

        Para usar o Modo IoT:
        1. Execute o simulador IoT: `python iot_simulator.py`
        2. Aguarde alguns segundos para dados serem coletados
        3. Volte aqui e clique em "🔮 GERAR PREVISÕES COM DADOS IoT"
        """)

# ==========================================================
#         INTERFACE - MODO MANUAL (código original)
# ==========================================================

elif st.session_state['modo_previsao'] == 'manual':

    st.subheader("📝 Preencha os Dados da Fazenda")

    with st.form("form_previsao"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**🌱 Nutrientes no Solo**")
            input_N = st.number_input("Nitrogênio (N) kg/ha", 0.0, 150.0, 60.0, key="input_n")
            input_P = st.number_input("Fósforo (P) kg/ha", 0.0, 150.0, 50.0, key="input_p")
            input_K = st.number_input("Potássio (K) kg/ha", 0.0, 200.0, 45.0, key="input_k")
            input_pH = st.number_input("pH do Solo", 3.0, 10.0, 6.5, 0.1, key="input_ph")

        with col2:
            st.markdown("**☁️ Condições Climáticas**")
            input_temp = st.number_input("Temperatura (°C)", 0.0, 45.0, 25.0, key="input_temp")
            input_humid = st.number_input("Umidade (%)", 0.0, 100.0, 70.0, key="input_humid")
            input_rain = st.number_input("Precipitação (mm)", 0.0, 500.0, 80.0, key="input_rain")

        with col3:
            st.markdown("**🌿 Manejo e Cultura**")
            input_irrig = st.number_input("Irrigação Atual (mm)", 0.0, 300.0, 0.0,
                                          help="Deixe 0 para prever", key="input_irrig")

            input_N_fert = st.number_input("Fertilização N (kg/ha)", 0.0, 150.0, 0.0,
                                           help="Deixe 0 para prever", key="input_n_fert")
            input_P_fert = st.number_input("Fertilização P (kg/ha)", 0.0, 150.0, 0.0,
                                           help="Deixe 0 para prever", key="input_p_fert")
            input_K_fert = st.number_input("Fertilização K (kg/ha)", 0.0, 150.0, 0.0,
                                           help="Deixe 0 para prever", key="input_k_fert")

            culturas_disponiveis = ['Maize', 'Rice', 'Soybean', 'Wheat', 'Cotton']
            input_cultura = st.selectbox("Tipo de Cultura", culturas_disponiveis, key="input_cultura")

        st.divider()

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            botao_prever = st.form_submit_button("🔮 GERAR TODAS AS PREVISÕES",
                                                 use_container_width=True,
                                                 type="primary")

    # Processar previsões no modo manual (código original)
    if botao_prever:

        st.divider()
        st.header("📊 Resultados das Previsões")

        with st.spinner("🤖 Processando previsões..."):

            inputs_iniciais = {
                'N': input_N,
                'P': input_P,
                'K': input_K,
                'soil_pH': input_pH,
                'temperature_C': input_temp,
                'humidity_%': input_humid,
                'rainfall_mm': input_rain,
                'volume_irrigacao_mm': input_irrig,
                'N_fertilizacao_kg_ha': input_N_fert,
                'P_fertilizacao_kg_ha': input_P_fert,
                'K_fertilizacao_kg_ha': input_K_fert,
            }

            resultados = {}

            # PREVISÃO 1: IRRIGAÇÃO
            if 'modelo_irrigacao' in st.session_state:
                features = calcular_features_derivadas(inputs_iniciais, input_cultura)

                previsao_irrigacao = fazer_previsao(
                    inputs_iniciais,
                    features,
                    input_cultura,
                    st.session_state['modelo_irrigacao'],
                    st.session_state['features_irrigacao']
                )

                resultados['irrigacao'] = max(0, previsao_irrigacao)
                inputs_iniciais['volume_irrigacao_mm'] = resultados['irrigacao']

            # PREVISÃO 2: FERTILIZAÇÃO
            if 'modelo_fertilizacao' in st.session_state:
                features = calcular_features_derivadas(inputs_iniciais, input_cultura)

                target_fert = st.session_state.get('target_fertilizacao', 'N_fertilizacao_kg_ha')

                previsao_fert = fazer_previsao(
                    inputs_iniciais,
                    features,
                    input_cultura,
                    st.session_state['modelo_fertilizacao'],
                    st.session_state['features_fertilizacao']
                )

                resultados['fertilizacao'] = max(0, previsao_fert)

                if 'N' in target_fert:
                    inputs_iniciais['N_fertilizacao_kg_ha'] = resultados['fertilizacao']
                elif 'P' in target_fert:
                    inputs_iniciais['P_fertilizacao_kg_ha'] = resultados['fertilizacao']
                else:
                    inputs_iniciais['K_fertilizacao_kg_ha'] = resultados['fertilizacao']

            # PREVISÃO 3: RENDIMENTO
            if 'modelo_rendimento' in st.session_state:
                features = calcular_features_derivadas(inputs_iniciais, input_cultura)

                previsao_rendimento = fazer_previsao(
                    inputs_iniciais,
                    features,
                    input_cultura,
                    st.session_state['modelo_rendimento'],
                    st.session_state['features_rendimento']
                )

                resultados['rendimento'] = max(0, previsao_rendimento)

            # Exibir resultados
            col1, col2, col3 = st.columns(3)

            with col1:
                if 'irrigacao' in resultados:
                    st.markdown(f"""
                    <div class="prediction-card">
                        <p class="prediction-title">💧 Volume de Irrigação</p>
                        <p class="prediction-value">{resultados['irrigacao']:.2f}</p>
                        <p class="prediction-unit">mm</p>
                    </div>
                    """, unsafe_allow_html=True)

            with col2:
                if 'fertilizacao' in resultados:
                    nutriente = st.session_state.get('target_fertilizacao', 'N_fertilizacao_kg_ha')
                    nutriente_nome = nutriente.split('_')[0]

                    st.markdown(f"""
                    <div class="prediction-card">
                        <p class="prediction-title">🌿 Fertilização {nutriente_nome}</p>
                        <p class="prediction-value">{resultados['fertilizacao']:.2f}</p>
                        <p class="prediction-unit">kg/ha</p>
                    </div>
                    """, unsafe_allow_html=True)

            with col3:
                if 'rendimento' in resultados:
                    st.markdown(f"""
                    <div class="prediction-card">
                        <p class="prediction-title">🌾 Rendimento Esperado</p>
                        <p class="prediction-value">{resultados['rendimento']:.0f}</p>
                        <p class="prediction-unit">kg/ha</p>
                    </div>
                    """, unsafe_allow_html=True)

            st.success("✅ Previsões geradas com sucesso!")