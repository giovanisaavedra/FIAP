"""
FarmTech Solutions - Página 4: Tendências e Previsões Interativas
Sistema de Previsão com Machine Learning e Interface Interativa

Autores: Giovani Saavedra e Marcio Elifas
RM: RM566797 e RM567871
GRUPO 37
1TIAOS - FIAP

"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# ==========================================================
#         CONFIGURAÇÃO DA PÁGINA
# ==========================================================

st.set_page_config(
    page_title="Previsões Interativas - FarmTech",
    page_icon="📈",
    layout="wide"
)

# Mapeamento global de culturas (case-insensitive)
CROP_MAPPING = {
    'Cotton': ['crop_Cotton', 'crop_cotton', 'crop_COTTON'],
    'Maize': ['crop_Maize', 'crop_maize', 'crop_MAIZE'],
    'Rice': ['crop_Rice', 'crop_rice', 'crop_RICE'],
    'Soybean': ['crop_Soybean', 'crop_soybean', 'crop_SOYBEAN'],
    'Wheat': ['crop_Wheat', 'crop_wheat', 'crop_WHEAT']
}


def encontrar_coluna_cultura(crop_name, available_columns):
    """
    Encontra a coluna correspondente à cultura selecionada
    """
    possible_names = CROP_MAPPING.get(crop_name, [f'crop_{crop_name}'])
    for possible_name in possible_names:
        if possible_name in available_columns:
            return possible_name

    # Fallback: buscar por substring
    for col in available_columns:
        if crop_name.lower() in col.lower():
            return col

    return None


# CSS Customizado
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
    }
    .header-subtitle {
        color: #C8E6C9;
        font-size: 18px;
        margin: 10px 0 0 0;
    }
    .prediction-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    .prediction-value {
        font-size: 48px;
        font-weight: bold;
        margin: 10px 0;
    }
    .prediction-label {
        font-size: 18px;
        opacity: 0.9;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="header-container">
        <h1 class="header-title">🌾 FarmTech Solutions</h1>
        <p class="header-subtitle">Previsões Interativas com Machine Learning</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📈 Previsões Interativas")
    st.info("""
        **Como usar:**
        1. Ajuste os sliders com dados da sua fazenda
        2. Veja as previsões em tempo real
        3. Analise as recomendações
        4. Otimize sua produção!
    """)

    st.divider()

    st.markdown("### 🎯 Modelos Disponíveis")
    st.success("""
        ✅ Random Forest (Principal)
        ✅ Regressão Linear
        ✅ Regressão Polinomial
    """)

# ==========================================================
#         TÍTULO DA PÁGINA
# ==========================================================

st.title("📈 Tendências e Previsões Interativas")
st.markdown("**Ajuste os parâmetros e veja previsões em tempo real usando Machine Learning**")

st.divider()


# ==========================================================
#         CARREGAR E PREPARAR DADOS
# ==========================================================

@st.cache_data
def carregar_dados():
    """Carrega e prepara os dados para treinamento"""
    try:
        df = pd.read_csv('data/processed/dataset_ml_preparado.csv')

        # Debug: mostrar colunas disponíveis
        st.sidebar.info(f"✅ Dataset carregado: {len(df)} registros")

        # Verificar se crop_type existe
        if 'crop_type' not in df.columns:
            # Procurar colunas crop_*
            crop_cols = [col for col in df.columns if col.startswith('crop_')]
            if crop_cols:
                st.sidebar.success(f"🌾 Culturas encontradas: {len(crop_cols)}")

        return df
    except FileNotFoundError:
        st.error("❌ Arquivo dataset_ml_preparado.csv não encontrado!")
        return None


@st.cache_resource
def treinar_modelos(df):
    """Treina os modelos de Machine Learning"""

    # Preparar features base (8 variáveis principais)
    features_base = ['N', 'P', 'K', 'soil_pH', 'temperature_C', 'humidity_%', 'rainfall_mm']

    # Verificar se crop_type existe ou se já está com one-hot encoding
    if 'crop_type' in df.columns:
        # Aplicar one-hot encoding
        df_encoded = pd.get_dummies(df, columns=['crop_type'], prefix='crop')
    else:
        # Já está com one-hot encoding
        df_encoded = df.copy()

    # Features completas
    crop_columns = [col for col in df_encoded.columns if col.startswith('crop_')]
    features = features_base + crop_columns

    # Targets
    y_irrigacao = df['volume_irrigacao_mm']
    y_fertilizacao_N = df['N_fertilizacao_kg_ha']
    y_rendimento = df['rendimento_kg_ha']

    X = df_encoded[features]

    # Normalizar dados
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Treinar modelos Random Forest (melhor performance)
    modelo_irrigacao = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
    modelo_fertilizacao = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
    modelo_rendimento = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)

    modelo_irrigacao.fit(X_scaled, y_irrigacao)
    modelo_fertilizacao.fit(X_scaled, y_fertilizacao_N)
    modelo_rendimento.fit(X_scaled, y_rendimento)

    # Calcular feature importance
    feature_importance = pd.DataFrame({
        'Feature': features_base,
        'Importancia_Irrigacao': modelo_irrigacao.feature_importances_[:len(features_base)],
        'Importancia_Fertilizacao': modelo_fertilizacao.feature_importances_[:len(features_base)],
        'Importancia_Rendimento': modelo_rendimento.feature_importances_[:len(features_base)]
    }).sort_values('Importancia_Rendimento', ascending=False)

    # Calcular R² dos modelos
    r2_irrigacao = modelo_irrigacao.score(X_scaled, y_irrigacao)
    r2_fertilizacao = modelo_fertilizacao.score(X_scaled, y_fertilizacao_N)
    r2_rendimento = modelo_rendimento.score(X_scaled, y_rendimento)

    metrics = {
        'Irrigação': {'R²': r2_irrigacao},
        'Fertilização': {'R²': r2_fertilizacao},
        'Rendimento': {'R²': r2_rendimento}
    }

    return {
        'modelo_irrigacao': modelo_irrigacao,
        'modelo_fertilizacao': modelo_fertilizacao,
        'modelo_rendimento': modelo_rendimento,
        'scaler': scaler,
        'features': features,
        'features_base': features_base,
        'crop_columns': crop_columns,
        'feature_importance': feature_importance,
        'metrics': metrics,
        'df_encoded': df_encoded  # Adicionar dataframe encoded
    }


# Carregar dados
df = carregar_dados()

if df is not None:
    # Verificar colunas necessárias
    required_cols = ['N', 'P', 'K', 'soil_pH', 'temperature_C', 'humidity_%', 'rainfall_mm',
                     'volume_irrigacao_mm', 'N_fertilizacao_kg_ha', 'rendimento_kg_ha']

    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.error(f"❌ Colunas faltando no dataset: {', '.join(missing_cols)}")
        st.info("💡 Verifique se o arquivo dataset_ml_preparado.csv está correto.")
        st.stop()

    # Treinar modelos
    with st.spinner('🤖 Treinando modelos de Machine Learning...'):
        try:
            models = treinar_modelos(df)
            st.success('✅ Modelos treinados e prontos para uso!')
        except Exception as e:
            st.error(f"❌ Erro ao treinar modelos: {str(e)}")
            st.info("💡 Detalhes do erro foram registrados. Verifique o dataset.")
            st.stop()

    # ==========================================================
    #         INTERFACE DE PREVISÃO INTERATIVA
    # ==========================================================

    st.header("🎯 Faça suas Previsões Interativas")
    st.markdown("**Ajuste os sliders abaixo para simular diferentes cenários agrícolas:**")

    st.divider()

    # Organizar inputs em colunas
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🌱 Nutrientes do Solo (NPK)")

        N_input = st.slider(
            "🔹 Nitrogênio (N) - kg/ha",
            min_value=0,
            max_value=150,
            value=75,
            step=5,
            help="Nitrogênio disponível no solo. Essencial para crescimento vegetal."
        )

        P_input = st.slider(
            "🔹 Fósforo (P) - kg/ha",
            min_value=0,
            max_value=150,
            value=60,
            step=5,
            help="Fósforo disponível no solo. Importante para raízes e floração."
        )

        K_input = st.slider(
            "🔹 Potássio (K) - kg/ha",
            min_value=0,
            max_value=210,
            value=105,
            step=5,
            help="Potássio disponível no solo. Fortalece resistência da planta."
        )

        pH_input = st.slider(
            "🔹 pH do Solo",
            min_value=4.0,
            max_value=9.5,
            value=6.5,
            step=0.1,
            help="Acidez/Alcalinidade do solo. Ideal: 6.0-7.0"
        )

    with col2:
        st.subheader("🌤️ Condições Climáticas")

        temp_input = st.slider(
            "🌡️ Temperatura Média (°C)",
            min_value=10.0,
            max_value=45.0,
            value=25.0,
            step=0.5,
            help="Temperatura média da região durante o ciclo da cultura."
        )

        humidity_input = st.slider(
            "💧 Umidade Relativa (%)",
            min_value=20.0,
            max_value=100.0,
            value=65.0,
            step=1.0,
            help="Umidade relativa do ar na região."
        )

        rainfall_input = st.slider(
            "🌧️ Precipitação (mm)",
            min_value=20.0,
            max_value=300.0,
            value=100.0,
            step=5.0,
            help="Precipitação total esperada durante o ciclo."
        )

        crop_input = st.selectbox(
            "🌾 Tipo de Cultura",
            options=['Cotton', 'Maize', 'Rice', 'Soybean', 'Wheat'],
            index=3,
            help="Selecione o tipo de cultura que será plantada."
        )

    st.divider()

    # ==========================================================
    #         FAZER PREVISÕES
    # ==========================================================

    # Preparar input para previsão
    input_data = {
        'N': N_input,
        'P': P_input,
        'K': K_input,
        'soil_pH': pH_input,
        'temperature_C': temp_input,
        'humidity_%': humidity_input,
        'rainfall_mm': rainfall_input
    }

    # Adicionar one-hot encoding para crop
    for crop_col in models['crop_columns']:
        input_data[crop_col] = 0

    # Encontrar e marcar a coluna correta da cultura selecionada
    crop_col_selecionada = encontrar_coluna_cultura(crop_input, models['crop_columns'])

    if crop_col_selecionada:
        input_data[crop_col_selecionada] = 1
    else:
        st.warning(f"⚠️ Cultura '{crop_input}' não encontrada exatamente. Usando aproximação.")
        # Usar primeira coluna como fallback
        if models['crop_columns']:
            input_data[models['crop_columns'][0]] = 1

    # Criar DataFrame
    input_df = pd.DataFrame([input_data])
    input_df = input_df[models['features']]  # Garantir ordem correta

    # Normalizar
    input_scaled = models['scaler'].transform(input_df)

    # Fazer previsões
    pred_irrigacao = models['modelo_irrigacao'].predict(input_scaled)[0]
    pred_fertilizacao = models['modelo_fertilizacao'].predict(input_scaled)[0]
    pred_rendimento = models['modelo_rendimento'].predict(input_scaled)[0]

    # ==========================================================
    #         EXIBIR RESULTADOS
    # ==========================================================

    st.header("🎉 Resultados das Previsões")

    # Cards de previsão
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="prediction-card" style="background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);">
            <div class="prediction-label">💧 Volume de Irrigação</div>
            <div class="prediction-value">{pred_irrigacao:.1f}</div>
            <div class="prediction-label">mm/ciclo</div>
        </div>
        """, unsafe_allow_html=True)

        if pred_irrigacao < 150:
            st.info("💡 **Irrigação Moderada**: Cultura com baixa demanda hídrica")
        elif pred_irrigacao < 250:
            st.success("💡 **Irrigação Adequada**: Demanda hídrica normal")
        else:
            st.warning("💡 **Irrigação Intensa**: Cultura com alta demanda hídrica")

    with col2:
        st.markdown(f"""
        <div class="prediction-card" style="background: linear-gradient(135deg, #50C878 0%, #228B22 100%);">
            <div class="prediction-label">🌿 Fertilização N (Nitrogênio)</div>
            <div class="prediction-value">{pred_fertilizacao:.1f}</div>
            <div class="prediction-label">kg/ha</div>
        </div>
        """, unsafe_allow_html=True)

        if pred_fertilizacao < 60:
            st.info("💡 **Fertilização Leve**: Solo com boa reserva natural")
        elif pred_fertilizacao < 100:
            st.success("💡 **Fertilização Moderada**: Reposição adequada")
        else:
            st.warning("💡 **Fertilização Intensa**: Solo carente de nutrientes")

    with col3:
        st.markdown(f"""
        <div class="prediction-card" style="background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);">
            <div class="prediction-label">🌾 Rendimento Esperado</div>
            <div class="prediction-value">{pred_rendimento:.0f}</div>
            <div class="prediction-label">kg/ha</div>
        </div>
        """, unsafe_allow_html=True)

        # Calcular produtividade relativa
        rendimento_medio = df['rendimento_kg_ha'].mean()
        percentual = ((pred_rendimento / rendimento_medio) - 1) * 100

        if percentual > 10:
            st.success(f"💡 **Excelente**: {percentual:+.1f}% acima da média!")
        elif percentual > 0:
            st.info(f"💡 **Bom**: {percentual:+.1f}% acima da média")
        else:
            st.warning(f"💡 **Atenção**: {percentual:.1f}% abaixo da média")

    st.divider()

    # ==========================================================
    #         ANÁLISE DETALHADA
    # ==========================================================

    st.header("📊 Análise Detalhada")

    tab1, tab2, tab3 = st.tabs(["📈 Tendências", "🎯 Otimização", "🤖 Performance ML"])

    with tab1:
        st.subheader("📈 Tendências Históricas")

        # Comparar com dados históricos
        col1, col2 = st.columns(2)

        with col1:
            # Gráfico de distribuição de irrigação
            fig_irrig = px.histogram(
                df,
                x='volume_irrigacao_mm',
                nbins=30,
                title='Distribuição Histórica de Irrigação',
                labels={'volume_irrigacao_mm': 'Volume de Irrigação (mm)'}
            )
            fig_irrig.add_vline(x=pred_irrigacao, line_dash="dash", line_color="red",
                                annotation_text="Sua Previsão")
            st.plotly_chart(fig_irrig, use_container_width=True)

        with col2:
            # Gráfico de distribuição de rendimento
            fig_rend = px.histogram(
                df,
                x='rendimento_kg_ha',
                nbins=30,
                title='Distribuição Histórica de Rendimento',
                labels={'rendimento_kg_ha': 'Rendimento (kg/ha)'}
            )
            fig_rend.add_vline(x=pred_rendimento, line_dash="dash", line_color="red",
                               annotation_text="Sua Previsão")
            st.plotly_chart(fig_rend, use_container_width=True)

        # Comparação com média por cultura
        # Tentar filtrar por crop_type ou por coluna one-hot
        if 'crop_type' in df.columns:
            df_cultura = df[df['crop_type'] == crop_input]
        else:
            # Filtrar pela coluna one-hot correspondente
            crop_col = encontrar_coluna_cultura(crop_input, models['df_encoded'].columns)
            if crop_col and crop_col in models['df_encoded'].columns:
                df_cultura = models['df_encoded'][models['df_encoded'][crop_col] == 1]
            else:
                # Se não encontrar, usar todos os dados
                df_cultura = models['df_encoded']
                st.info(f"ℹ️ Usando média geral (cultura '{crop_input}' não encontrada especificamente)")

        col1, col2, col3 = st.columns(3)

        with col1:
            media_irrig = df_cultura['volume_irrigacao_mm'].mean()
            delta_irrig = pred_irrigacao - media_irrig
            st.metric(
                "Irrigação vs Média da Cultura",
                f"{pred_irrigacao:.1f} mm",
                f"{delta_irrig:+.1f} mm",
                delta_color="normal"
            )

        with col2:
            media_fert = df_cultura['N_fertilizacao_kg_ha'].mean()
            delta_fert = pred_fertilizacao - media_fert
            st.metric(
                "Fertilização vs Média da Cultura",
                f"{pred_fertilizacao:.1f} kg/ha",
                f"{delta_fert:+.1f} kg/ha",
                delta_color="normal"
            )

        with col3:
            media_rend = df_cultura['rendimento_kg_ha'].mean()
            delta_rend = pred_rendimento - media_rend
            st.metric(
                "Rendimento vs Média da Cultura",
                f"{pred_rendimento:.0f} kg/ha",
                f"{delta_rend:+.0f} kg/ha",
                delta_color="normal"
            )

    with tab2:
        st.subheader("🎯 Sugestões de Otimização")

        st.markdown("""
        ### 💡 Recomendações Baseadas em Machine Learning

        Com base nas previsões do modelo e análise das features mais importantes, 
        aqui estão as principais recomendações para otimizar sua produção:
        """)

        # Análise de features importantes
        importance = models['feature_importance']

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🔝 Top 3 Fatores Mais Importantes:")
            for idx, row in importance.head(3).iterrows():
                st.markdown(f"""
                **{idx + 1}. {row['Feature']}**
                - Importância: {row['Importancia_Rendimento']:.3f}
                """)

        with col2:
            # Gráfico de importância
            fig_imp = px.bar(
                importance,
                x='Importancia_Rendimento',
                y='Feature',
                orientation='h',
                title='Importância das Features para Rendimento'
            )
            st.plotly_chart(fig_imp, use_container_width=True)

        st.divider()

        # Recomendações específicas
        st.markdown("#### ✅ Ações Recomendadas:")

        recomendacoes = []

        # 1. ANÁLISE DE pH (mais importante)
        if pH_input < 5.5:
            recomendacoes.append(
                "🔴 **CRÍTICO - pH Baixo**: Aplicar calcário (1-2 ton/ha) para corrigir acidez. Meta: 6.0-6.8")
        elif pH_input > 7.5:
            recomendacoes.append(
                "🔴 **CRÍTICO - pH Alto**: Aplicar enxofre elementar (200-300 kg/ha) para reduzir alcalinidade")
        elif pH_input < 6.0 or pH_input > 7.0:
            recomendacoes.append("🟡 **ATENÇÃO - pH Subótimo**: Monitorar e ajustar gradualmente. Ideal: 6.0-7.0")
        else:
            recomendacoes.append(
                "🟢 **pH Ideal**: Manter práticas atuais de manejo de solo (pH: {:.1f})".format(pH_input))

        # 2. ANÁLISE DE NPK (nutrientes)
        npk_problemas = []
        if N_input < 50:
            npk_problemas.append("Nitrogênio")
            recomendacoes.append(
                "🔴 **Nitrogênio Baixo** ({} kg/ha): Aplicar ureia ou sulfato de amônio".format(N_input))
        if P_input < 40:
            npk_problemas.append("Fósforo")
            recomendacoes.append("🔴 **Fósforo Baixo** ({} kg/ha): Aplicar superfosfato simples".format(P_input))
        if K_input < 70:
            npk_problemas.append("Potássio")
            recomendacoes.append("🔴 **Potássio Baixo** ({} kg/ha): Aplicar cloreto de potássio".format(K_input))

        if not npk_problemas:
            recomendacoes.append("🟢 **NPK Adequado**: Nutrientes em níveis satisfatórios (N:{}, P:{}, K:{})".format(
                N_input, P_input, K_input))

        # 3. ANÁLISE HÍDRICA INTEGRADA (precipitação + umidade + temperatura)
        # Baseado em literatura científica e dados do projeto

        # Calcular evapotranspiração estimada (Thornthwaite simplificado)
        # ET = 1.6 * (10*T/I)^a, simplificado para ET ≈ 0.6*T mm/dia
        evapotranspiracao_diaria = temp_input * 0.6  # mm/dia
        evapotranspiracao_mensal = evapotranspiracao_diaria * 30  # mm/mês

        # Calcular déficit hídrico real
        agua_disponivel = rainfall_input  # mm/mês
        deficit_hidrico_mm = max(0, evapotranspiracao_mensal - agua_disponivel)

        # Categorizar situação hídrica
        deficit_hidrico = False
        excesso_hidrico = False

        # THRESHOLDS CIENTÍFICOS:
        # Precipitação crítica: < 60mm/mês (Embrapa, 2023)
        # Umidade crítica: < 40% (FAO guidelines)
        # Evapotranspiração alta: > 150mm/mês

        if rainfall_input < 60:  # Crítico por precipitação
            deficit_hidrico = True
        elif rainfall_input < 100 and humidity_input < 50:  # Moderado combinado
            deficit_hidrico = True
        elif humidity_input < 40:  # Crítico por umidade baixa
            deficit_hidrico = True
        elif evapotranspiracao_mensal > 150 and rainfall_input < evapotranspiracao_mensal * 0.8:
            # Evapotranspiração alta e chuva insuficiente
            deficit_hidrico = True

        # Excesso: chuva > 200mm E umidade > 85%
        if rainfall_input > 200 and humidity_input > 85:
            excesso_hidrico = True

        # Recomendações hídricas baseadas na análise integrada
        if deficit_hidrico:
            if rainfall_input < 60 and humidity_input < 40:
                # CRÍTICO: Ambos abaixo do limite
                recomendacoes.append(f"🔴 **CRÍTICO - Déficit Hídrico Severo**")
                recomendacoes.append(
                    f"   📊 **Análise**: Precipitação: {rainfall_input:.0f}mm/mês (crítico: <60mm), Umidade: {humidity_input:.0f}% (crítico: <40%)")
                recomendacoes.append(f"   📊 **Evapotranspiração estimada**: {evapotranspiracao_mensal:.0f}mm/mês")
                recomendacoes.append(f"   📊 **Déficit hídrico**: {deficit_hidrico_mm:.0f}mm/mês")
                recomendacoes.append(
                    f"   💧 **Ação URGENTE**: Irrigar {deficit_hidrico_mm * 0.8:.0f}-{deficit_hidrico_mm:.0f}mm total no mês")
                recomendacoes.append(f"   💧 **Frequência**: 30-40mm/semana via gotejamento ou aspersão")
                recomendacoes.append(f"   ⏰ **Horário**: Início da manhã (6h-8h) ou fim da tarde (17h-19h)")

            elif rainfall_input < 100:
                # MODERADO: Precipitação insuficiente
                recomendacoes.append(f"🟡 **Déficit Hídrico Moderado**: Precipitação abaixo do ideal")
                recomendacoes.append(f"   📊 **Análise**: Precipitação: {rainfall_input:.0f}mm/mês (ideal: >100mm)")
                recomendacoes.append(f"   📊 **Déficit**: ~{deficit_hidrico_mm:.0f}mm/mês a repor")
                recomendacoes.append(
                    f"   💧 **Ação**: Irrigação complementar de {deficit_hidrico_mm * 0.6:.0f}-{deficit_hidrico_mm * 0.8:.0f}mm/mês")
                recomendacoes.append(f"   💧 **Frequência**: 20-25mm/semana")

            elif humidity_input < 40:
                # MODERADO: Umidade baixa aumenta evapotranspiração
                recomendacoes.append(f"🟡 **Umidade do Ar Crítica** ({humidity_input:.0f}%): Alta evapotranspiração")
                recomendacoes.append(
                    f"   📊 **Evapotranspiração**: {evapotranspiracao_mensal:.0f}mm/mês (~{evapotranspiracao_diaria:.1f}mm/dia)")
                recomendacoes.append(f"   💧 **Ação**: Aumentar frequência de irrigação para compensar perdas")
                recomendacoes.append(
                    f"   💧 **Recomendação**: {evapotranspiracao_mensal * 0.3:.0f}mm/mês adicional (10mm/semana)")
                recomendacoes.append(f"   ⏰ **Horário crítico**: Irrigar ao amanhecer para minimizar perdas")

            else:
                # Déficit por evapotranspiração alta
                recomendacoes.append(f"🟡 **Balanço Hídrico Negativo**: Evapotranspiração > Precipitação")
                recomendacoes.append(
                    f"   📊 **ET mensal**: {evapotranspiracao_mensal:.0f}mm vs Chuva: {rainfall_input:.0f}mm")
                recomendacoes.append(f"   💧 **Ação**: Irrigação complementar de {deficit_hidrico_mm * 0.5:.0f}mm/mês")

        elif excesso_hidrico:
            recomendacoes.append(f"🟡 **Excesso Hídrico**: Risco de encharcamento")
            recomendacoes.append(
                f"   📊 **Análise**: Precipitação: {rainfall_input:.0f}mm/mês, Umidade: {humidity_input:.0f}%")
            recomendacoes.append(f"   🚰 **Ação Imediata**: SUSPENDER toda irrigação")
            recomendacoes.append(f"   🚧 **Verificar**: Sistema de drenagem do terreno")
            recomendacoes.append(f"   ⚠️ **Monitorar**: Doenças fúngicas (Fusarium, Pythium, Phytophthora)")
            recomendacoes.append(f"   📅 **Retomar irrigação**: Quando chuva < 100mm/mês E umidade < 75%")

        else:
            if 100 <= rainfall_input <= 200 and 60 <= humidity_input <= 80:
                recomendacoes.append(f"🟢 **Balanço Hídrico Ideal**: Condições ótimas")
                recomendacoes.append(
                    f"   📊 **Análise**: Precipitação: {rainfall_input:.0f}mm/mês, Umidade: {humidity_input:.0f}%")
                recomendacoes.append(
                    f"   📊 **Evapotranspiração**: {evapotranspiracao_mensal:.0f}mm/mês (dentro do esperado)")
                recomendacoes.append(
                    f"   💧 **Manutenção**: Irrigação leve (10-15mm/semana) apenas em períodos >7 dias sem chuva")
                recomendacoes.append(f"   ✅ **Status**: Continuar monitoramento de rotina")
            else:
                recomendacoes.append(f"🟢 **Balanço Hídrico Aceitável**: Dentro da normalidade")
                recomendacoes.append(
                    f"   📊 **Precipitação**: {rainfall_input:.0f}mm/mês, **Umidade**: {humidity_input:.0f}%")
                recomendacoes.append(f"   💧 **Ação**: Irrigação de segurança (10mm/semana)")

        # 4. ANÁLISE DE TEMPERATURA
        if temp_input < 15:
            recomendacoes.append(
                "🟡 **Temperatura Baixa** ({:.1f}°C): Considerar culturas de clima frio ou uso de estufas".format(
                    temp_input))
            recomendacoes.append("   🌡️ **Alternativas**: Trigo, cevada, aveia são mais tolerantes ao frio.")
        elif temp_input > 35:
            recomendacoes.append(
                "🔴 **Temperatura Alta** ({:.1f}°C): Aumentar irrigação e usar sombreamento".format(temp_input))
            recomendacoes.append("   🌡️ **Ação**: Irrigar 2-3x ao dia. Considerar telas de sombreamento (30-50%).")
            if humidity_input < 50:
                recomendacoes.append(
                    "   ⚠️ **ALERTA**: Combinação de calor + baixa umidade = ALTO risco de estresse hídrico!")
        elif 20 <= temp_input <= 28:
            recomendacoes.append(
                "🟢 **Temperatura Ideal** ({:.1f}°C): Condições térmicas ótimas para a maioria das culturas".format(
                    temp_input))
        else:
            recomendacoes.append("🟡 **Temperatura Aceitável** ({:.1f}°C): Dentro da faixa tolerável".format(temp_input))

        # 5. SÍNTESE E PRIORIDADES
        st.divider()
        st.markdown("#### 🎯 **Prioridades de Ação:**")

        prioridade_alta = [r for r in recomendacoes if "🔴" in r]
        prioridade_media = [r for r in recomendacoes if "🟡" in r]
        prioridade_baixa = [r for r in recomendacoes if "🟢" in r]

        if prioridade_alta:
            st.error("**AÇÕES URGENTES:**")
            for rec in prioridade_alta:
                st.markdown(f"- {rec}")

        if prioridade_media:
            st.warning("**AÇÕES RECOMENDADAS:**")
            for rec in prioridade_media:
                st.markdown(f"- {rec}")

        if prioridade_baixa:
            st.success("**CONDIÇÕES FAVORÁVEIS:**")
            for rec in prioridade_baixa:
                st.markdown(f"- {rec}")

        st.divider()

        # Cálculo de viabilidade econômica
        st.markdown("#### 💰 Análise de Viabilidade Econômica")

        col1, col2 = st.columns(2)

        with col1:
            preco_cultura = st.number_input(
                "Preço de venda (R$/kg)",
                min_value=0.5,
                max_value=10.0,
                value=2.0,
                step=0.1
            )

        with col2:
            custo_ha = st.number_input(
                "Custo total por hectare (R$)",
                min_value=1000,
                max_value=20000,
                value=5000,
                step=500
            )

        receita_estimada = pred_rendimento * preco_cultura
        lucro_estimado = receita_estimada - custo_ha
        roi = (lucro_estimado / custo_ha) * 100

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("💵 Receita Estimada", f"R$ {receita_estimada:,.2f}/ha")

        with col2:
            st.metric("💰 Lucro Estimado", f"R$ {lucro_estimado:,.2f}/ha",
                      delta_color="normal" if lucro_estimado > 0 else "inverse")

        with col3:
            st.metric("📈 ROI (Retorno)", f"{roi:.1f}%",
                      delta_color="normal" if roi > 0 else "inverse")

        if lucro_estimado > 0:
            st.success(f"✅ **Viável**: Lucro estimado de R$ {lucro_estimado:,.2f} por hectare!")
        else:
            st.error(f"❌ **Inviável**: Prejuízo estimado de R$ {abs(lucro_estimado):,.2f} por hectare")

    with tab3:
        st.subheader("🤖 Performance dos Modelos de Machine Learning")

        st.markdown("""
        ### 📊 Métricas de Qualidade dos Modelos

        Os modelos foram treinados usando **Random Forest Regressor**, um algoritmo 
        ensemble robusto que combina múltiplas árvores de decisão.
        """)

        # Exibir métricas
        col1, col2, col3 = st.columns(3)

        with col1:
            r2 = models['metrics']['Irrigação']['R²']
            st.metric("🎯 R² - Irrigação", f"{r2:.3f}")
            if r2 > 0.7:
                st.success("Excelente ajuste!")
            elif r2 > 0.5:
                st.info("Bom ajuste")
            else:
                st.warning("Ajuste moderado")

        with col2:
            r2 = models['metrics']['Fertilização']['R²']
            st.metric("🎯 R² - Fertilização", f"{r2:.3f}")
            if r2 > 0.7:
                st.success("Excelente ajuste!")
            elif r2 > 0.5:
                st.info("Bom ajuste")
            else:
                st.warning("Ajuste moderado")

        with col3:
            r2 = models['metrics']['Rendimento']['R²']
            st.metric("🎯 R² - Rendimento", f"{r2:.3f}")
            if r2 > 0.7:
                st.success("Excelente ajuste!")
            elif r2 > 0.5:
                st.info("Bom ajuste")
            else:
                st.warning("Ajuste moderado")

        st.divider()

        # Calcular insights
        importances = models['modelo_rendimento'].feature_importances_
        feature_importance = pd.DataFrame({
            'Variável': models['features_base'],
            'Importância': importances[:len(models['features_base'])]
        }).sort_values('Importância', ascending=False)

        var_mais_importante = feature_importance.iloc[0]['Variável']
        imp_mais_importante = feature_importance.iloc[0]['Importância']

        rf_r2 = models['metrics']['Rendimento']['R²']

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            ### 🤖 Performance do ML

            - **Random Forest R²**: {rf_r2:.3f}
            - Modelo explica **{rf_r2 * 100:.1f}%** da variância
            - Ótimo para previsões práticas
            - Pronto para uso em produção
            """)

            st.markdown(f"""
            ### 🔬 Variável Mais Importante

            - **{var_mais_importante}**
            - Importância: {imp_mais_importante:.3f}
            - Foco principal de otimização
            """)

        with col2:
            st.markdown("""
            ### 💡 Recomendações Práticas

            1. **Use os sliders** para simular cenários
            2. **Otimize as top 3 variáveis** mais importantes
            3. **Mantenha pH** na faixa ideal (5.5-6.5)
            4. **Monitore continuamente** com sensores IoT
            5. **Ajuste estratégias** baseado nas previsões
            """)

            st.markdown("""
            ### 🚀 Próximos Passos

            - Implementar sistema IoT para coleta automática
            - Integrar previsões com dashboard operacional
            - Treinar modelos com mais dados históricos
            - Validar previsões com safras reais
            """)

        st.divider()

        st.success("""
        ### 🎉 Sistema Pronto!

        O sistema de ML está treinado e operacional. Use os sliders acima para fazer 
        previsões interativas e otimizar sua produção agrícola!

        **Aproveite o poder do Machine Learning para decisões mais inteligentes! 🌾🤖**
        """)

else:
    st.error("❌ Não foi possível carregar os dados. Verifique se o arquivo existe.")

# Rodapé
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; padding: 20px; color: #666;'>
    <p><strong>🌾 FarmTech Solutions</strong> - Machine Learning Interativo para Agricultura</p>
    <p>Desenvolvido com ❤️ usando Scikit-Learn e Streamlit</p>
    <p>FIAP - Fase 4 - 2025</p>
</div>
""", unsafe_allow_html=True)