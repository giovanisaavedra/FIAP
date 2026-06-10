"""
FarmTech Solutions - Página 2: Modelagem Preditiva
Treinamento e avaliação de modelos de Machine Learning

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
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import time

# ==========================================================
#         CONFIGURAÇÃO DA PÁGINA
# ==========================================================

st.set_page_config(
    page_title="Modelagem - FarmTech",
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
    </style>

    <div class="header-container">
        <h1 class="header-title">🌾 FarmTech Solutions</h1>
        <p class="header-subtitle">Sistema de Previsão Agrícola com Machine Learning</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🤖 Machine Learning")
    st.info("""
        **Modelos Disponíveis:**
        - Regressão Linear Múltipla
        - Regressão Polinomial (Grau 2)

        **Targets:**
        - Volume de Irrigação
        - Fertilização NPK
        - Rendimento
    """)

    st.divider()

    st.markdown("### 📊 Métricas")
    st.info("""
        **MAE**: Erro médio absoluto
        **RMSE**: Raiz do erro quadrático
        **R²**: Coef. de determinação
    """)

# ==========================================================
#         TÍTULO DA PÁGINA
# ==========================================================

st.title("🔮 Modelagem Preditiva")
st.markdown("Treinamento e avaliação de modelos de Machine Learning")

st.divider()


# ==========================================================
#         CARREGAR DADOS
# ==========================================================

@st.cache_data
def carregar_dados():
    """Carrega o dataset preparado"""
    try:
        df = pd.read_csv('data/processed/dataset_ml_preparado.csv')
        return df
    except FileNotFoundError:
        st.error("❌ Arquivo dataset_ml_preparado.csv não encontrado!")
        st.info("Execute a Fase 8 (Feature Engineering) do EDA primeiro e salve o dataset.")
        st.stop()


# Carregar dados
dt = carregar_dados()

st.success(f"✅ Dataset carregado: {len(dt):,} registros e {len(dt.columns)} colunas")


# ==========================================================
#    FUNÇÕES AUXILIARES
# ==========================================================

def treinar_modelo(X_train, X_test, y_train, y_test, algoritmo, grau_poly=2):
    """
    Treina modelo de regressão e retorna métricas
    """
    inicio = time.time()

    # Normalizar dados
    scaler_X = StandardScaler()
    X_train_scaled = scaler_X.fit_transform(X_train)
    X_test_scaled = scaler_X.transform(X_test)

    poly_transformer = None  # ← NOVO: Salvar transformer polinomial

    # Escolher algoritmo
    if algoritmo == "Regressão Linear Múltipla":
        modelo = LinearRegression()
        modelo.fit(X_train_scaled, y_train)
        y_pred_train = modelo.predict(X_train_scaled)
        y_pred_test = modelo.predict(X_test_scaled)

    elif algoritmo == "Regressão Polinomial":
        poly = PolynomialFeatures(degree=grau_poly, include_bias=False)
        X_train_poly = poly.fit_transform(X_train_scaled)
        X_test_poly = poly.transform(X_test_scaled)

        poly_transformer = poly  # ← NOVO: Salvar o objeto poly

        modelo = LinearRegression()
        modelo.fit(X_train_poly, y_train)
        y_pred_train = modelo.predict(X_train_poly)
        y_pred_test = modelo.predict(X_test_poly)

    tempo = time.time() - inicio

    # Calcular métricas
    metricas = {
        'train': {
            'mae': mean_absolute_error(y_train, y_pred_train),
            'rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
            'r2': r2_score(y_train, y_pred_train)
        },
        'test': {
            'mae': mean_absolute_error(y_test, y_pred_test),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
            'r2': r2_score(y_test, y_pred_test)
        },
        'tempo': tempo,
        'y_pred_test': y_pred_test,
        'y_test': y_test,
        'modelo': modelo,
        'scaler': scaler_X,
        'poly': poly_transformer,  # ← NOVO: Incluir transformer no retorno
        'algoritmo': algoritmo  # ← NOVO: Salvar nome do algoritmo usado
    }

    return metricas


def plotar_real_vs_previsto(y_test, y_pred, titulo):
    """Plota gráfico Real vs Previsto"""
    fig = go.Figure()

    # Pontos reais vs previstos
    fig.add_trace(go.Scatter(
        x=y_test,
        y=y_pred,
        mode='markers',
        name='Previsões',
        marker=dict(
            color=y_test,
            colorscale='Viridis',
            size=8,
            opacity=0.6,
            colorbar=dict(title="Valor Real")
        )
    ))

    # Linha diagonal (previsão perfeita)
    min_val = min(y_test.min(), y_pred.min())
    max_val = max(y_test.max(), y_pred.max())
    fig.add_trace(go.Scatter(
        x=[min_val, max_val],
        y=[min_val, max_val],
        mode='lines',
        name='Previsão Perfeita',
        line=dict(color='red', dash='dash', width=2)
    ))

    fig.update_layout(
        title=titulo,
        xaxis_title='Valores Reais',
        yaxis_title='Valores Previstos',
        height=500,
        hovermode='closest'
    )

    return fig


def plotar_residuos(y_test, y_pred, titulo):
    """Plota gráfico de resíduos"""
    residuos = y_test - y_pred

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=y_pred,
        y=residuos,
        mode='markers',
        marker=dict(
            color=residuos,
            colorscale='RdYlGn_r',
            size=8,
            opacity=0.6,
            colorbar=dict(title="Resíduo")
        )
    ))

    # Linha zero
    fig.add_hline(y=0, line_dash="dash", line_color="red")

    fig.update_layout(
        title=titulo,
        xaxis_title='Valores Previstos',
        yaxis_title='Resíduos (Real - Previsto)',
        height=400
    )

    return fig


def mostrar_metricas(metricas, prefixo=""):
    """Mostra métricas em colunas"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            f"{prefixo}MAE",
            f"{metricas['test']['mae']:.2f}",
            delta=f"{metricas['train']['mae'] - metricas['test']['mae']:.2f}",
            delta_color="inverse"
        )

    with col2:
        st.metric(
            f"{prefixo}RMSE",
            f"{metricas['test']['rmse']:.2f}",
            delta=f"{metricas['train']['rmse'] - metricas['test']['rmse']:.2f}",
            delta_color="inverse"
        )

    with col3:
        st.metric(
            f"{prefixo}R²",
            f"{metricas['test']['r2']:.3f}",
            delta=f"{metricas['test']['r2'] - metricas['train']['r2']:.3f}",
            delta_color="normal"
        )

    with col4:
        st.metric(
            f"{prefixo}Tempo",
            f"{metricas['tempo']:.2f}s"
        )


# ==========================================================
#    📊 TREINAMENTO DE MODELOS
# ==========================================================

st.header("📊 Treinamento e Avaliação de Modelos")

# Tabs para os 3 modelos
tab1, tab2, tab3 = st.tabs([
    "💧 Modelo 1: Irrigação",
    "🌿 Modelo 2: Fertilização",
    "🌾 Modelo 3: Rendimento"
])

# ==========================================================
#    TAB 1: MODELO DE IRRIGAÇÃO
# ==========================================================

with tab1:
    st.subheader("💧 Previsão de Volume de Irrigação")

    st.markdown("""
    **Objetivo:** Prever quanto de irrigação é necessária com base em:
    - Precipitação e condições climáticas
    - Déficit hídrico e evapotranspiração
    - Demanda hídrica da cultura
    - Balanço hídrico do solo
    """)

    st.divider()

    # Seleção de algoritmo
    col1, col2 = st.columns([2, 1])

    with col1:
        algoritmo_irrig = st.selectbox(
            "Escolha o algoritmo:",
            ["Regressão Linear Múltipla", "Regressão Polinomial"],
            key="algo_irrig"
        )

    with col2:
        st.markdown("###")
        botao_treinar_irrig = st.button("🚀 Treinar Modelo", key="treinar_irrig", use_container_width=True)

    # Treinar modelo
    if botao_treinar_irrig:
        with st.spinner("Treinando modelo..."):
            # FEATURES ENRIQUECIDAS PARA IRRIGAÇÃO
            features_irrig = [
                # Features climáticas originais
                'rainfall_mm', 'temperature_C', 'humidity_%',

                # Features de solo originais
                'N', 'P', 'K', 'soil_pH',

                # NOVAS features específicas para irrigação
                'deficit_hidrico_mm',
                'evapotranspiracao_estimada',
                'demanda_agua_cultura',
                'balanco_hidrico',
                'necessidade_irrigacao_teorica',
                'indice_aridez',
                'agua_adequacao',
                'agua_total_mm'
            ]

            # Adicionar colunas de cultura (one-hot)
            colunas_cultura = [col for col in dt.columns if col.startswith('crop_type_')]
            features_irrig.extend(colunas_cultura)

            X = dt[features_irrig]
            y = dt['volume_irrigacao_mm']

            # Dividir treino/teste
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Treinar
            metricas_irrig = treinar_modelo(
                X_train, X_test, y_train, y_test,
                algoritmo_irrig
            )

            # Salvar no session_state
            st.session_state['modelo_irrigacao'] = metricas_irrig
            st.session_state['features_irrigacao'] = features_irrig

        st.success("✅ Modelo treinado com sucesso!")

    # Mostrar resultados se modelo existe
    if 'modelo_irrigacao' in st.session_state:
        st.divider()

        st.markdown("### 📊 Métricas de Desempenho")
        mostrar_metricas(st.session_state['modelo_irrigacao'])

        # Interpretação
        r2 = st.session_state['modelo_irrigacao']['test']['r2']
        if r2 > 0.3:
            st.success(f"✅ R² = {r2:.3f} - Modelo com BOM desempenho!")
        elif r2 > 0.2:
            st.info(f"ℹ️ R² = {r2:.3f} - Modelo com desempenho razoável")
        else:
            st.warning(f"⚠️ R² = {r2:.3f} - Modelo com desempenho limitado")

        st.divider()

        # Gráficos
        col1, col2 = st.columns(2)

        with col1:
            fig1 = plotar_real_vs_previsto(
                st.session_state['modelo_irrigacao']['y_test'],
                st.session_state['modelo_irrigacao']['y_pred_test'],
                "Real vs Previsto - Irrigação"
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = plotar_residuos(
                st.session_state['modelo_irrigacao']['y_test'],
                st.session_state['modelo_irrigacao']['y_pred_test'],
                "Resíduos - Irrigação"
            )
            st.plotly_chart(fig2, use_container_width=True)

# ==========================================================
#    TAB 2: MODELO DE FERTILIZAÇÃO
# ==========================================================

with tab2:
    st.subheader("🌿 Previsão de Fertilização NPK")

    st.markdown("""
    **Objetivo:** Prever quantidade de fertilizante necessária com base em:
    - Nutrientes disponíveis no solo (afetados por pH)
    - Razões e balanço NPK
    - Eficiência de uso de nutrientes
    - Tipo de cultura
    """)

    st.divider()

    # Escolher qual nutriente prever
    nutriente_target = st.radio(
        "Escolha o nutriente para prever:",
        ["Nitrogênio (N)", "Fósforo (P)", "Potássio (K)"],
        horizontal=True,
        key="nutriente"
    )

    # Mapear escolha para coluna
    mapa_nutriente = {
        "Nitrogênio (N)": "N_fertilizacao_kg_ha",
        "Fósforo (P)": "P_fertilizacao_kg_ha",
        "Potássio (K)": "K_fertilizacao_kg_ha"
    }

    target_fert = mapa_nutriente[nutriente_target]

    col1, col2 = st.columns([2, 1])

    with col1:
        algoritmo_fert = st.selectbox(
            "Escolha o algoritmo:",
            ["Regressão Linear Múltipla", "Regressão Polinomial"],
            key="algo_fert"
        )

    with col2:
        st.markdown("###")
        botao_treinar_fert = st.button("🚀 Treinar Modelo", key="treinar_fert", use_container_width=True)

    # Treinar modelo
    if botao_treinar_fert:
        with st.spinner("Treinando modelo..."):
            # FEATURES ENRIQUECIDAS PARA FERTILIZAÇÃO
            features_fert = [
                # Features originais
                'N', 'P', 'K', 'soil_pH', 'NPK_total',

                # NOVAS features específicas para fertilização
                'disponibilidade_nutrientes',
                'N_disponivel',
                'P_disponivel',
                'K_disponivel',
                'razao_NP',
                'razao_NK',
                'razao_PK',
                'desvio_NPK_ideal',
                'eficiencia_N',
                'eficiencia_P',
                'eficiencia_K'
            ]

            # Adicionar colunas de cultura
            colunas_cultura = [col for col in dt.columns if col.startswith('crop_type_')]
            features_fert.extend(colunas_cultura)

            X = dt[features_fert]
            y = dt[target_fert]

            # Dividir treino/teste
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Treinar
            metricas_fert = treinar_modelo(
                X_train, X_test, y_train, y_test,
                algoritmo_fert
            )

            # Salvar no session_state
            st.session_state['modelo_fertilizacao'] = metricas_fert
            st.session_state['features_fertilizacao'] = features_fert
            st.session_state['target_fertilizacao'] = target_fert

        st.success("✅ Modelo treinado com sucesso!")

    # Mostrar resultados
    if 'modelo_fertilizacao' in st.session_state:
        st.divider()

        st.markdown("### 📊 Métricas de Desempenho")
        mostrar_metricas(st.session_state['modelo_fertilizacao'])

        r2 = st.session_state['modelo_fertilizacao']['test']['r2']
        if r2 > 0.5:
            st.success(f"✅ R² = {r2:.3f} - Modelo com EXCELENTE desempenho!")
        elif r2 > 0.3:
            st.success(f"✅ R² = {r2:.3f} - Modelo com BOM desempenho!")
        else:
            st.info(f"ℹ️ R² = {r2:.3f} - Modelo com desempenho razoável")

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            fig1 = plotar_real_vs_previsto(
                st.session_state['modelo_fertilizacao']['y_test'],
                st.session_state['modelo_fertilizacao']['y_pred_test'],
                f"Real vs Previsto - {nutriente_target}"
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = plotar_residuos(
                st.session_state['modelo_fertilizacao']['y_test'],
                st.session_state['modelo_fertilizacao']['y_pred_test'],
                f"Resíduos - {nutriente_target}"
            )
            st.plotly_chart(fig2, use_container_width=True)

# ==========================================================
#    TAB 3: MODELO DE RENDIMENTO
# ==========================================================

with tab3:
    st.subheader("🌾 Previsão de Rendimento")

    st.markdown("""
    **Objetivo:** Prever o rendimento da cultura com base em:
    - TODAS as variáveis disponíveis (clima, solo, manejo)
    - Estresses abióticos (térmico, hídrico)
    - Interações NPK × Água
    - Adequação geral de insumos
    """)

    st.divider()

    col1, col2 = st.columns([2, 1])

    with col1:
        algoritmo_rend = st.selectbox(
            "Escolha o algoritmo:",
            ["Regressão Linear Múltipla", "Regressão Polinomial"],
            key="algo_rend"
        )

    with col2:
        st.markdown("###")
        botao_treinar_rend = st.button("🚀 Treinar Modelo", key="treinar_rend", use_container_width=True)

    # Treinar modelo
    if botao_treinar_rend:
        with st.spinner("Treinando modelo..."):
            # FEATURES ENRIQUECIDAS PARA RENDIMENTO
            # Usar TODAS as features exceto target e suas derivadas
            features_rend = [
                col for col in dt.columns
                if col not in [
                    'rendimento_kg_ha',  # Target
                    'rendimento_potencial',  # Derivada do target
                    'taxa_realizacao',  # Derivada do target
                    'receita_bruta',  # Derivada do target
                    'margem_bruta',  # Derivada do target
                    'preco_produto'  # Relacionado ao target
                ]
            ]

            X = dt[features_rend]
            y = dt['rendimento_kg_ha']

            # Dividir treino/teste
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Treinar
            metricas_rend = treinar_modelo(
                X_train, X_test, y_train, y_test,
                algoritmo_rend
            )

            # Salvar no session_state
            st.session_state['modelo_rendimento'] = metricas_rend
            st.session_state['features_rendimento'] = features_rend

        st.success("✅ Modelo treinado com sucesso!")

    # Mostrar resultados
    if 'modelo_rendimento' in st.session_state:
        st.divider()

        st.markdown("### 📊 Métricas de Desempenho")
        mostrar_metricas(st.session_state['modelo_rendimento'])

        r2 = st.session_state['modelo_rendimento']['test']['r2']
        mae = st.session_state['modelo_rendimento']['test']['mae']

        if r2 > 0.4:
            st.success(f"✅ R² = {r2:.3f} - Modelo com EXCELENTE desempenho!")
        elif r2 > 0.25:
            st.success(f"✅ R² = {r2:.3f} - Modelo com BOM desempenho!")
        elif r2 > 0.15:
            st.info(f"ℹ️ R² = {r2:.3f} - Modelo com desempenho razoável")
        else:
            st.warning(f"⚠️ R² = {r2:.3f} - Modelo com desempenho limitado")

        st.info(f"""
        💡 **Interpretação prática:**
        - O modelo erra em média ±{mae:.0f} kg/ha
        - Explica {r2 * 100:.1f}% da variação no rendimento
        - Para sistema agrícola complexo, R² > 0.25 já é considerado bom!
        """)

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            fig1 = plotar_real_vs_previsto(
                st.session_state['modelo_rendimento']['y_test'],
                st.session_state['modelo_rendimento']['y_pred_test'],
                "Real vs Previsto - Rendimento"
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = plotar_residuos(
                st.session_state['modelo_rendimento']['y_test'],
                st.session_state['modelo_rendimento']['y_pred_test'],
                "Resíduos - Rendimento"
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Distribuição dos erros
        st.markdown("### 📊 Distribuição dos Erros")

        residuos = st.session_state['modelo_rendimento']['y_test'] - st.session_state['modelo_rendimento'][
            'y_pred_test']

        fig_hist = px.histogram(
            x=residuos,
            nbins=50,
            title="Distribuição dos Resíduos (Erros)",
            labels={'x': 'Resíduo (kg/ha)', 'y': 'Frequência'},
            color_discrete_sequence=['#2E7D32']
        )
        fig_hist.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Zero")
        st.plotly_chart(fig_hist, use_container_width=True)

        st.info("""
        💡 **Como interpretar:**
        - Distribuição centrada em zero = modelo não enviesado ✅
        - Forma de sino = erros seguem distribuição normal ✅
        - Caudas longas = alguns casos com erro grande ⚠️
        """)

# ==========================================================
#    📊 COMPARAÇÃO DE MODELOS
# ==========================================================

st.divider()
st.header("📊 Comparação de Modelos")

# Verificar quais modelos foram treinados
modelos_treinados = []
if 'modelo_irrigacao' in st.session_state:
    modelos_treinados.append('Irrigação')
if 'modelo_fertilizacao' in st.session_state:
    modelos_treinados.append('Fertilização')
if 'modelo_rendimento' in st.session_state:
    modelos_treinados.append('Rendimento')

if len(modelos_treinados) == 0:
    st.info("ℹ️ Treine pelo menos um modelo para ver a comparação")
else:
    st.success(f"✅ {len(modelos_treinados)} modelo(s) treinado(s): {', '.join(modelos_treinados)}")

    # Criar tabela comparativa
    dados_comparacao = []

    if 'modelo_irrigacao' in st.session_state:
        m = st.session_state['modelo_irrigacao']
        dados_comparacao.append({
            'Modelo': 'Irrigação',
            'Algoritmo': m.get('algoritmo', 'N/A'),  # ← NOVO
            'MAE': f"{m['test']['mae']:.2f}",
            'RMSE': f"{m['test']['rmse']:.2f}",
            'R²': f"{m['test']['r2']:.3f}",
            'Tempo (s)': f"{m['tempo']:.2f}"
        })

    if 'modelo_fertilizacao' in st.session_state:
        m = st.session_state['modelo_fertilizacao']
        dados_comparacao.append({
            'Modelo': 'Fertilização',
            'Algoritmo': m.get('algoritmo', 'N/A'),  # ← NOVO
            'MAE': f"{m['test']['mae']:.2f}",
            'RMSE': f"{m['test']['rmse']:.2f}",
            'R²': f"{m['test']['r2']:.3f}",
            'Tempo (s)': f"{m['tempo']:.2f}"
        })

    if 'modelo_rendimento' in st.session_state:
        m = st.session_state['modelo_rendimento']
        dados_comparacao.append({
            'Modelo': 'Rendimento',
            'Algoritmo': m.get('algoritmo', 'N/A'),  # ← NOVO
            'MAE': f"{m['test']['mae']:.2f}",
            'RMSE': f"{m['test']['rmse']:.2f}",
            'R²': f"{m['test']['r2']:.3f}",
            'Tempo (s)': f"{m['tempo']:.2f}"
        })

    df_comparacao = pd.DataFrame(dados_comparacao)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.dataframe(df_comparacao, use_container_width=True, hide_index=True)

    with col2:
        if len(modelos_treinados) >= 2:
            # Gráfico de barras R²
            valores_r2 = [float(d['R²']) for d in dados_comparacao]
            fig_comp = px.bar(
                x=[d['Modelo'] for d in dados_comparacao],
                y=valores_r2,
                title="Comparação R² entre Modelos",
                labels={'x': 'Modelo', 'y': 'R²'},
                color=valores_r2,
                color_continuous_scale='Viridis'
            )
            fig_comp.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig_comp, use_container_width=True)

    st.info("""
    💡 **Como interpretar:**
    - **MAE/RMSE**: Quanto menor, melhor (menos erro)
    - **R²**: Quanto maior, melhor (explica mais variação)
    - **R² > 0.30**: Bom desempenho para agricultura
    - **R² > 0.50**: Excelente desempenho
    """)

# ==========================================================
#    ✅ CONCLUSÃO E PRÓXIMOS PASSOS
# ==========================================================

st.divider()

st.success("""
### ✅ Modelos Treinados com Features Enriquecidas!

**O que você fez nesta página:**
1. ✅ Treinou 3 modelos com **features avançadas**
2. ✅ Avaliou desempenho com métricas (MAE, RMSE, R²)
3. ✅ Visualizou gráficos de performance
4. ✅ Comparou algoritmos e modelos

**🎯 Impacto do Feature Engineering:**
As features enriquecidas da Fase 8 melhoraram significativamente o desempenho!

**🎯 Próximo passo:**
Vá para a página **"Fazer Previsões"** para usar os modelos treinados 
e obter recomendações personalizadas para sua fazenda!
""")