#==========================================================
#         IMPORTAÇÃO DE BIBLIOTECAS
#==========================================================

import streamlit as st
import seaborn as sns
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
# ⭐ IMPORTAR AS FUNÇÕES DO UTILS
from utils import render_header, render_sidebar

#==========================================================
#         📚 FASE 1: CONFIGURAÇÃO DO AMBIENTE
#==========================================================

#Configuração da página
st.set_page_config(page_title='Análise de Dados', layout="wide")

# ============================================
#     RENDERIZAR HEADER E SIDEBAR
# ============================================

# ⭐ CHAMAR AS FUNÇÕES (apenas 2 linhas!)
render_header()
render_sidebar()

# Conteúdo da página
st.title("📈 Análise Exploratória de Dados (EDA)")

#==========================================================
#       📊 FASE 2: CARREGAMENTO E INSPEÇÃO INICIAL
#==========================================================

st.header("Dataset disponível: dataset_final_farmtech.csv")
dt = pd.read_csv('data/processed/dataset_final_farmtech.csv')
st.dataframe(dt)

st.divider()

st.header("1. Visão Geral dos Dados")

st.divider()

st.header("📋 Resumo Executivo")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="📊 Total de Registros",
        value=f"{len(dt):,}",
        delta="Dataset completo"
    )

with col2:
    st.metric(
        label="📋 Variáveis",
        value=dt.shape[1],
        delta=f"{dt.shape[1]-1} features + 1 target"
    )

with col3:
    st.metric(
        label="🌾 Culturas",
        value=dt['crop_type'].nunique(),
        delta="Tipos diferentes"
    )

with col4:
    completude = (1 - dt.isnull().sum().sum() / (len(dt) * len(dt.columns))) * 100
    st.metric(
        label="✅ Completude",
        value=f"{completude:.1f}%",
        delta="Qualidade dos dados"
    )

with col5:
    st.metric(
        label="💾 Memória",
        value=f"{dt.memory_usage(deep=True).sum() / 1024**2:.2f} MB",
        delta="Tamanho do dataset"
    )

st.divider()

#Informações sobre o dataset
st.subheader('Informações do Dataset:')

st.divider()

st.write('Dimensões do Dataset')

# Cria 3 colunas com larguras iguais
col1, col2 = st.columns(2)

# Adiciona conteúdo em cada coluna
with col1:
    st.header("Linhas")
    st.write(dt.shape[0])

with col2:
    st.header("Colunas")
    st.write(dt.shape[1])

st.divider()

st.subheader('Tipos de Dados:')

# Criar DataFrame com informações dos tipos de dados
df_types = pd.DataFrame({
    'Coluna': dt.columns,
    'Tipo de Dados': dt.dtypes.astype(str),
    'Valores Não-Nulos': dt.count().values,
    'Valores Nulos': dt.isnull().sum().values,
    '% Completo': (dt.count() / len(dt) * 100).round(2).values
})

# Exibir o DataFrame na aplicação Streamlit ⭐ hide_index=True
st.dataframe(df_types, use_container_width=True, hide_index=True)

st.divider()

# ========== ESTATÍSTICAS DESCRITIVAS ==========
st.header("📊 Estatísticas Descritivas")
st.dataframe(dt.describe().T, use_container_width=True)

# Insights
st.info("""
💡 **Como interpretar:**
- **count**: Quantidade de valores não-nulos
- **mean**: Média aritmética
- **std**: Desvio padrão (dispersão dos dados)
- **min/max**: Valores mínimo e máximo
- **25%/50%/75%**: Quartis (divisões dos dados em 4 partes)
""")

st.divider()

# ========== DISTRIBUIÇÃO DE CULTURAS ==========
st.header("🌾 Distribuição de Culturas")

col1, col2 = st.columns(2)

with col1:
    culturas = dt['crop_type'].value_counts().reset_index()
    culturas.columns = ['Cultura', 'Quantidade']
    culturas['Percentual'] = (culturas['Quantidade'] / len(dt) * 100).round(2)
    st.dataframe(culturas, use_container_width=True)

with col2:
    fig = px.pie(
        culturas,
        values='Quantidade',
        names='Cultura',
        title='Distribuição de Culturas',
        color_discrete_sequence=px.colors.sequential.Greens
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

#==========================================================
#       🔍 FASE 3: ANÁLISE DE VALORES AUSENTES
#==========================================================

#Verificar valores ausentes
st.subheader("Valores Ausentes")
st.write(dt.isnull().sum())
st.write("Percentual de Valores Ausentes:")
st.write((dt.isnull().sum() / len(dt) * 100).round(2))

#==========================================================
#       📈 FASE 4: ANÁLISE UNIVARIADA
#==========================================================

st.divider()

st.header("📈 Análise Univariada")

st.markdown("""
Análise individual de cada variável para entender:
- **Distribuição**: Como os valores estão espalhados
- **Centralidade**: Onde os dados se concentram
- **Outliers**: Valores extremos ou atípicos
- **Assimetria**: Se a distribuição pende para um lado
""")

st.divider()


# ============================================
#    FUNÇÃO DE ANÁLISE
# ============================================

def analisar_variavel_numerica(df, coluna, titulo, unidade=""):
    """Análise univariada completa de uma variável numérica"""

    col1, col2 = st.columns(2)

    with col1:
        # Histograma
        fig = px.histogram(
            df,
            x=coluna,
            title=f'Distribuição: {titulo}',
            labels={coluna: f'{titulo} ({unidade})'},
            color_discrete_sequence=['#2E7D32']
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Boxplot
        fig = px.box(
            df,
            y=coluna,
            title=f'Boxplot: {titulo}',
            labels={coluna: f'{titulo} ({unidade})'},
            color_discrete_sequence=['#2E7D32']
        )
        st.plotly_chart(fig, use_container_width=True)

    # Métricas
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📊 Média", f"{df[coluna].mean():.2f} {unidade}")
    with col2:
        st.metric("📍 Mediana", f"{df[coluna].median():.2f} {unidade}")
    with col3:
        st.metric("📏 Desvio Padrão", f"{df[coluna].std():.2f} {unidade}")
    with col4:
        assimetria = df[coluna].skew()
        st.metric("📐 Assimetria", f"{assimetria:.2f}")


# ============================================
#         ANÁLISE POR CATEGORIAS
# ============================================

# Criar tabs por categoria
tab1, tab2, tab3, tab4 = st.tabs([
    "🌱 Nutrientes (NPK + pH)",
    "🌤️ Clima",
    "💧 Manejo Agrícola",
    "🌾 Rendimento"
])

# ============================================
#    TAB 1: NUTRIENTES (N, P, K, pH)
# ============================================

with tab1:
    st.subheader("🌱 Análise de Nutrientes do Solo")

    st.markdown("""
    Os nutrientes NPK e o pH do solo são **fundamentais** para o desenvolvimento das plantas:
    - **N (Nitrogênio)**: Crescimento vegetativo (folhas, caules)
    - **P (Fósforo)**: Desenvolvimento de raízes, flores e frutos
    - **K (Potássio)**: Resistência a doenças e qualidade dos frutos
    - **pH**: Disponibilidade dos nutrientes no solo
    """)

    st.divider()

    # ========== NITROGÊNIO (N) ==========
    st.markdown("### 🔹 Nitrogênio (N)")
    analisar_variavel_numerica(dt, 'N', 'Nitrogênio', 'kg/ha')

    # Insights agronômicos
    st.info("""
    💡 **Interpretação Agronômica:**
    - **Faixa adequada**: 40-80 kg/ha (varia por cultura)
    - **Deficiência**: Folhas amareladas (clorose)
    - **Excesso**: Crescimento excessivo de folhas, vulnerável a pragas
    """)

    st.divider()

    # ========== FÓSFORO (P) ==========
    st.markdown("### 🔹 Fósforo (P)")
    analisar_variavel_numerica(dt, 'P', 'Fósforo', 'kg/ha')

    # Insights agronômicos
    st.info("""
    💡 **Interpretação Agronômica:**
    - **Faixa adequada**: 20-40 kg/ha
    - **Deficiência**: Crescimento lento, folhas arroxeadas
    - **Importância**: Crítico nas fases iniciais e reprodutivas
    """)

    st.divider()

    # ========== POTÁSSIO (K) ==========
    st.markdown("### 🔹 Potássio (K)")
    analisar_variavel_numerica(dt, 'K', 'Potássio', 'kg/ha')

    # Insights agronômicos
    st.info("""
    💡 **Interpretação Agronômica:**
    - **Faixa adequada**: 40-80 kg/ha
    - **Deficiência**: Bordas das folhas queimadas
    - **Importância**: Regulação hídrica e qualidade dos frutos
    """)

    st.divider()

    # ========== pH DO SOLO ==========
    st.markdown("### 🔹 pH do Solo")
    analisar_variavel_numerica(dt, 'soil_pH', 'pH do Solo', '')

    # Insights agronômicos com análise dos dados
    ph_medio = dt['soil_pH'].mean()

    if ph_medio < 5.5:
        st.warning(f"""
        ⚠️ **Atenção: Solo Ácido!**
        - pH médio: {ph_medio:.2f}
        - **Problema**: Nutrientes ficam menos disponíveis, alumínio tóxico aumenta
        - **Solução**: Aplicar calcário (calagem) para elevar o pH
        """)
    elif ph_medio > 7.5:
        st.warning(f"""
        ⚠️ **Atenção: Solo Alcalino!**
        - pH médio: {ph_medio:.2f}
        - **Problema**: Fósforo e micronutrientes ficam indisponíveis
        - **Solução**: Adicionar matéria orgânica ou enxofre
        """)
    else:
        st.success(f"""
        ✅ **Excelente: pH Ideal!**
        - pH médio: {ph_medio:.2f}
        - **Faixa ideal**: 5.5-7.0 para maioria das culturas
        - **Benefício**: Máxima disponibilidade de nutrientes
        """)

    st.divider()

    # ========== RESUMO NPK ==========
    st.markdown("### 📊 Resumo Comparativo NPK")

    # Criar tabela resumo
    resumo_npk = pd.DataFrame({
        'Nutriente': ['N (Nitrogênio)', 'P (Fósforo)', 'K (Potássio)'],
        'Média (kg/ha)': [
            dt['N'].mean(),
            dt['P'].mean(),
            dt['K'].mean()
        ],
        'Desvio Padrão': [
            dt['N'].std(),
            dt['P'].std(),
            dt['K'].std()
        ],
        'Mínimo': [
            dt['N'].min(),
            dt['P'].min(),
            dt['K'].min()
        ],
        'Máximo': [
            dt['N'].max(),
            dt['P'].max(),
            dt['K'].max()
        ]
    })

    # Arredondar valores
    resumo_npk = resumo_npk.round(2)

    st.dataframe(resumo_npk, use_container_width=True, hide_index=True)

    # Gráfico comparativo
    fig = px.bar(
        resumo_npk,
        x='Nutriente',
        y='Média (kg/ha)',
        title='Comparação dos Níveis Médios de NPK',
        color='Nutriente',
        color_discrete_sequence=['#1B5E20', '#2E7D32', '#4CAF50']
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================
#    TAB 2: CLIMA (temperatura, umidade, chuva)
# ============================================

with tab2:
    st.subheader("🌤️ Análise de Variáveis Climáticas")

    st.markdown("""
    As condições climáticas têm **impacto direto** no desenvolvimento das culturas:
    - **Temperatura**: Afeta crescimento e desenvolvimento
    - **Umidade**: Influencia transpiração e doenças
    - **Chuva**: Principal fonte de água para as plantas
    """)

    st.divider()

    # ========== TEMPERATURA ==========
    st.markdown("### 🌡️ Temperatura")
    analisar_variavel_numerica(dt, 'temperature_C', 'Temperatura', '°C')

    st.info("""
    💡 **Faixas Ideais por Cultura:**
    - **Milho**: 20-30°C
    - **Arroz**: 25-35°C
    - **Trigo**: 15-25°C
    - **Soja**: 20-30°C
    """)

    st.divider()

    # ========== UMIDADE ==========
    st.markdown("### 💧 Umidade Relativa")
    analisar_variavel_numerica(dt, 'humidity_%', 'Umidade Relativa', '%')

    st.info("""
    💡 **Interpretação:**
    - **< 40%**: Muito seco, aumenta evapotranspiração
    - **40-70%**: Faixa ideal para maioria das culturas
    - **> 90%**: Favorece doenças fúngicas
    """)

    st.divider()

    # ========== PRECIPITAÇÃO ==========
    st.markdown("### 🌧️ Precipitação (Chuva)")
    analisar_variavel_numerica(dt, 'rainfall_mm', 'Precipitação', 'mm')

    st.info("""
    💡 **Necessidade Hídrica Total (ciclo completo):**
    - **Milho**: 400-600 mm
    - **Arroz**: 1500-2000 mm (cultura inundada)
    - **Soja**: 450-800 mm
    - **Feijão**: 300-500 mm
    """)

# ============================================
#    TAB 3: MANEJO (irrigação, fertilização)
# ============================================

with tab3:
    st.subheader("💧 Análise de Práticas de Manejo")

    st.markdown("""
    As práticas de manejo são **decisões do agricultor** baseadas nas condições do solo e clima:
    """)

    st.divider()

    # ========== VOLUME DE IRRIGAÇÃO ==========
    st.markdown("### 💧 Volume de Irrigação")
    analisar_variavel_numerica(dt, 'volume_irrigacao_mm', 'Volume de Irrigação', 'mm')

    st.info("""
    💡 **Relação com Chuva:**
    - Irrigação **complementa** a precipitação natural
    - Em períodos secos, irrigação aumenta
    - Excesso pode causar lixiviação de nutrientes
    """)

    st.divider()

    # ========== FERTILIZAÇÃO N ==========
    st.markdown("### 🌿 Fertilização Nitrogenada")
    analisar_variavel_numerica(dt, 'N_fertilizacao_kg_ha', 'Fertilização N', 'kg/ha')

    st.divider()

    # ========== FERTILIZAÇÃO P ==========
    st.markdown("### 🌿 Fertilização Fosfatada")
    analisar_variavel_numerica(dt, 'P_fertilizacao_kg_ha', 'Fertilização P', 'kg/ha')

    st.divider()

    # ========== FERTILIZAÇÃO K ==========
    st.markdown("### 🌿 Fertilização Potássica")
    analisar_variavel_numerica(dt, 'K_fertilizacao_kg_ha', 'Fertilização K', 'kg/ha')

# ============================================
#    TAB 4: RENDIMENTO (variável target)
# ============================================

with tab4:
    st.subheader("🌾 Análise do Rendimento (Variável Target)")

    st.markdown("""
    O **rendimento** é a variável que queremos prever! 
    Ela representa a produtividade final da cultura em kg/hectare.
    """)

    st.divider()

    # ========== RENDIMENTO ==========
    st.markdown("### 📊 Rendimento Geral")
    analisar_variavel_numerica(dt, 'rendimento_kg_ha', 'Rendimento', 'kg/ha')

    st.info("""
    💡 **Benchmarks de Rendimento Brasileiro:**
    - **Milho**: Média nacional ~6.000 kg/ha, Alta produtividade 10.000+ kg/ha
    - **Soja**: Média nacional ~3.300 kg/ha, Alta produtividade 4.500+ kg/ha
    - **Arroz**: Média nacional ~6.000 kg/ha, Alta produtividade 9.000+ kg/ha
    - **Feijão**: Média nacional ~1.200 kg/ha, Alta produtividade 3.000+ kg/ha
    """)

    st.divider()

    # ========== RENDIMENTO POR CULTURA ==========
    st.markdown("### 🌾 Rendimento por Tipo de Cultura")

    # Boxplot comparativo
    fig = px.box(
        dt,
        x='crop_type',
        y='rendimento_kg_ha',
        title='Distribuição do Rendimento por Cultura',
        labels={'crop_type': 'Tipo de Cultura', 'rendimento_kg_ha': 'Rendimento (kg/ha)'},
        color='crop_type',
        color_discrete_sequence=px.colors.sequential.Greens
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tabela de estatísticas por cultura
    st.markdown("#### 📋 Estatísticas de Rendimento por Cultura")

    rendimento_por_cultura = dt.groupby('crop_type')['rendimento_kg_ha'].agg([
        ('Média', 'mean'),
        ('Mediana', 'median'),
        ('Desvio Padrão', 'std'),
        ('Mínimo', 'min'),
        ('Máximo', 'max')
    ]).round(2)

    st.dataframe(rendimento_por_cultura, use_container_width=True)



#==========================================================
#       🔗 FASE 5: ANÁLISE BIVARIADA
#==========================================================

st.header("🔗 Análise Bivariada")

st.markdown("""
Análise das **relações entre duas variáveis** para identificar:
- **Correlações**: Relações lineares entre variáveis
- **Padrões**: Como uma variável afeta outra
- **Dependências**: Influências e causas
- **Insights**: Descobertas para o modelo de ML
""")

st.divider()


# ============================================
#    FUNÇÃO AUXILIAR PARA SCATTER PLOTS
# ============================================

def plot_scatter_com_correlacao(df, var_x, var_y, titulo_x, titulo_y, unidade_x="", unidade_y=""):
    """Cria scatter plot com linha de tendência e correlação"""

    # Calcular correlação
    correlacao = df[[var_x, var_y]].corr().iloc[0, 1]

    # Criar scatter plot
    fig = px.scatter(
        df,
        x=var_x,
        y=var_y,
        title=f'{titulo_x} vs {titulo_y} (Correlação: {correlacao:.3f})',
        labels={
            var_x: f'{titulo_x} ({unidade_x})' if unidade_x else titulo_x,
            var_y: f'{titulo_y} ({unidade_y})' if unidade_y else titulo_y
        },
        trendline="ols",  # Linha de tendência
        color_discrete_sequence=['#2E7D32'],
        opacity=0.6
    )

    fig.update_layout(height=500)

    return fig, correlacao


# ============================================
#         ANÁLISE POR CATEGORIAS
# ============================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Matriz de Correlação",
    "🌾 Nutrientes vs Rendimento",
    "🌤️ Clima vs Rendimento",
    "💧 Manejo vs Rendimento"
])

# ============================================
#    TAB 1: MATRIZ DE CORRELAÇÃO COMPLETA
# ============================================

with tab1:
    st.subheader("📊 Matriz de Correlação Geral")

    st.markdown("""
    A matriz de correlação mostra a **força da relação linear** entre todas as variáveis:
    - **+1**: Correlação positiva perfeita (uma sobe, outra sobe)
    - **0**: Sem correlação linear
    - **-1**: Correlação negativa perfeita (uma sobe, outra desce)
    """)

    # Selecionar apenas variáveis numéricas
    colunas_numericas = dt.select_dtypes(include=[np.number]).columns

    # Calcular correlação
    matriz_corr = dt[colunas_numericas].corr()

    # Criar heatmap com Plotly
    fig = px.imshow(
        matriz_corr,
        text_auto='.2f',
        aspect="auto",
        title="Matriz de Correlação - Todas as Variáveis",
        color_continuous_scale='RdYlGn',
        color_continuous_midpoint=0
    )

    fig.update_layout(height=700)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Correlações mais fortes com rendimento
    st.markdown("### 🎯 Correlações mais Fortes com Rendimento")

    corr_rendimento = matriz_corr['rendimento_kg_ha'].sort_values(ascending=False)
    corr_rendimento = corr_rendimento.drop('rendimento_kg_ha')  # Remove autocorrelação

    # Criar DataFrame para exibição
    df_corr_rendimento = pd.DataFrame({
        'Variável': corr_rendimento.index,
        'Correlação': corr_rendimento.values,
        'Força': corr_rendimento.abs().values
    }).sort_values('Força', ascending=False)


    # Adicionar interpretação
    def interpretar_correlacao(valor):
        abs_valor = abs(valor)
        if abs_valor >= 0.7:
            return "🔴 Forte"
        elif abs_valor >= 0.4:
            return "🟡 Moderada"
        else:
            return "🟢 Fraca"


    df_corr_rendimento['Interpretação'] = df_corr_rendimento['Correlação'].apply(interpretar_correlacao)
    df_corr_rendimento = df_corr_rendimento[['Variável', 'Correlação', 'Interpretação']]
    df_corr_rendimento['Correlação'] = df_corr_rendimento['Correlação'].round(3)

    st.dataframe(df_corr_rendimento, use_container_width=True, hide_index=True)

    # Gráfico de barras das correlações
    fig = px.bar(
        df_corr_rendimento.head(10),
        x='Correlação',
        y='Variável',
        orientation='h',
        title='Top 10 Variáveis Correlacionadas com Rendimento',
        color='Correlação',
        color_continuous_scale='RdYlGn',
        color_continuous_midpoint=0
    )
    st.plotly_chart(fig, use_container_width=True)

    # Insights importantes
    st.info("""
    💡 **Como Interpretar:**
    - **Correlação Positiva**: Quando uma variável aumenta, a outra tende a aumentar
    - **Correlação Negativa**: Quando uma variável aumenta, a outra tende a diminuir
    - **Correlação Fraca (< 0.4)**: Pouca relação linear direta
    - **Correlação Forte (> 0.7)**: Forte relação linear (cuidado com multicolinearidade!)
    """)

# ============================================
#    TAB 2: NUTRIENTES VS RENDIMENTO
# ============================================

with tab2:
    st.subheader("🌱 Relação entre Nutrientes e Rendimento")

    st.markdown("""
    Análise de como os **níveis de NPK e pH** afetam o rendimento das culturas.
    """)

    st.divider()

    # ========== N vs RENDIMENTO ==========
    st.markdown("### 🔹 Nitrogênio (N) vs Rendimento")

    col1, col2 = st.columns([2, 1])

    with col1:
        fig, corr = plot_scatter_com_correlacao(
            dt, 'N', 'rendimento_kg_ha',
            'Nitrogênio', 'Rendimento',
            'kg/ha', 'kg/ha'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.metric("📊 Correlação", f"{corr:.3f}")

        if corr > 0.3:
            st.success("✅ Correlação Positiva: Mais N tende a aumentar o rendimento")
        elif corr < -0.3:
            st.warning("⚠️ Correlação Negativa: Mais N tende a reduzir o rendimento")
        else:
            st.info("ℹ️ Correlação Fraca: Relação linear pouco evidente")

    st.info("""
    💡 **Interpretação Agronômica:**
    - Nitrogênio é essencial para crescimento vegetativo
    - Correlação positiva esperada, mas pode saturar
    - Excesso pode causar acamamento e vulnerabilidade a pragas
    """)

    st.divider()

    # ========== P vs RENDIMENTO ==========
    st.markdown("### 🔹 Fósforo (P) vs Rendimento")

    col1, col2 = st.columns([2, 1])

    with col1:
        fig, corr = plot_scatter_com_correlacao(
            dt, 'P', 'rendimento_kg_ha',
            'Fósforo', 'Rendimento',
            'kg/ha', 'kg/ha'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.metric("📊 Correlação", f"{corr:.3f}")

        if corr > 0.3:
            st.success("✅ Correlação Positiva")
        elif corr < -0.3:
            st.warning("⚠️ Correlação Negativa")
        else:
            st.info("ℹ️ Correlação Fraca")

    st.info("""
    💡 **Interpretação Agronômica:**
    - Fósforo crucial para desenvolvimento radicular
    - Mais importante nas fases iniciais
    - Resposta pode ser não-linear (Lei dos Rendimentos Decrescentes)
    """)

    st.divider()

    # ========== K vs RENDIMENTO ==========
    st.markdown("### 🔹 Potássio (K) vs Rendimento")

    col1, col2 = st.columns([2, 1])

    with col1:
        fig, corr = plot_scatter_com_correlacao(
            dt, 'K', 'rendimento_kg_ha',
            'Potássio', 'Rendimento',
            'kg/ha', 'kg/ha'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.metric("📊 Correlação", f"{corr:.3f}")

        if corr > 0.3:
            st.success("✅ Correlação Positiva")
        elif corr < -0.3:
            st.warning("⚠️ Correlação Negativa")
        else:
            st.info("ℹ️ Correlação Fraca")

    st.info("""
    💡 **Interpretação Agronômica:**
    - Potássio importante para qualidade e resistência
    - Regula abertura estomática (eficiência hídrica)
    - Crítico em condições de estresse
    """)

    st.divider()

    # ========== pH vs RENDIMENTO ==========
    st.markdown("### 🔹 pH do Solo vs Rendimento")

    col1, col2 = st.columns([2, 1])

    with col1:
        fig, corr = plot_scatter_com_correlacao(
            dt, 'soil_pH', 'rendimento_kg_ha',
            'pH do Solo', 'Rendimento',
            '', 'kg/ha'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.metric("📊 Correlação", f"{corr:.3f}")

        # Análise específica para pH
        ph_ideal_min = 5.5
        ph_ideal_max = 7.0

        # Calcular rendimento médio por faixa de pH
        dt_ph_ideal = dt[(dt['soil_pH'] >= ph_ideal_min) & (dt['soil_pH'] <= ph_ideal_max)]
        dt_ph_fora = dt[(dt['soil_pH'] < ph_ideal_min) | (dt['soil_pH'] > ph_ideal_max)]

        if len(dt_ph_ideal) > 0 and len(dt_ph_fora) > 0:
            rend_ideal = dt_ph_ideal['rendimento_kg_ha'].mean()
            rend_fora = dt_ph_fora['rendimento_kg_ha'].mean()
            diferenca = ((rend_ideal - rend_fora) / rend_fora * 100)

            st.metric(
                "🎯 Ganho com pH Ideal",
                f"{diferenca:.1f}%",
                delta=f"{rend_ideal - rend_fora:.0f} kg/ha"
            )

    st.warning("""
    ⚠️ **Importante sobre pH:**
    - Relação pode ser **não-linear** (curva em sino)
    - pH ideal: 5.5-7.0 para maioria das culturas
    - Fora dessa faixa, nutrientes ficam indisponíveis
    - Correlação linear pode não capturar essa relação!
    """)

    st.divider()

    # ========== SCATTER MATRIX NPK ==========
    st.markdown("### 📊 Matriz de Dispersão NPK vs Rendimento")

    # Criar scatter matrix
    variaveis_npk = ['N', 'P', 'K', 'soil_pH', 'rendimento_kg_ha']

    fig = px.scatter_matrix(
        dt[variaveis_npk],
        dimensions=variaveis_npk,
        title="Matriz de Dispersão: Nutrientes e Rendimento",
        color_discrete_sequence=['#2E7D32'],
        opacity=0.5,
        height=800
    )

    fig.update_traces(diagonal_visible=False, showupperhalf=False)
    st.plotly_chart(fig, use_container_width=True)

# ============================================
#    TAB 3: CLIMA VS RENDIMENTO
# ============================================

with tab3:
    st.subheader("🌤️ Relação entre Clima e Rendimento")

    st.markdown("""
    Análise de como **temperatura, umidade e chuva** afetam o rendimento.
    """)

    st.divider()

    # ========== TEMPERATURA vs RENDIMENTO ==========
    st.markdown("### 🌡️ Temperatura vs Rendimento")

    col1, col2 = st.columns([2, 1])

    with col1:
        fig, corr = plot_scatter_com_correlacao(
            dt, 'temperature_C', 'rendimento_kg_ha',
            'Temperatura', 'Rendimento',
            '°C', 'kg/ha'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.metric("📊 Correlação", f"{corr:.3f}")

        if corr > 0.3:
            st.success("✅ Correlação Positiva")
        elif corr < -0.3:
            st.warning("⚠️ Correlação Negativa")
        else:
            st.info("ℹ️ Correlação Fraca")

    st.info("""
    💡 **Interpretação Agronômica:**
    - Cada cultura tem temperatura ótima
    - Temperaturas extremas (< 10°C ou > 40°C) prejudicam
    - Relação pode ser não-linear (pico no meio)
    """)

    st.divider()

    # ========== UMIDADE vs RENDIMENTO ==========
    st.markdown("### 💧 Umidade Relativa vs Rendimento")

    col1, col2 = st.columns([2, 1])

    with col1:
        fig, corr = plot_scatter_com_correlacao(
            dt, 'humidity_%', 'rendimento_kg_ha',
            'Umidade', 'Rendimento',
            '%', 'kg/ha'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.metric("📊 Correlação", f"{corr:.3f}")

        if corr > 0.3:
            st.success("✅ Correlação Positiva")
        elif corr < -0.3:
            st.warning("⚠️ Correlação Negativa")
        else:
            st.info("ℹ️ Correlação Fraca")

    st.info("""
    💡 **Interpretação Agronômica:**
    - Umidade ideal: 60-80%
    - Muito baixa: estresse hídrico
    - Muito alta (> 90%): favorece doenças fúngicas
    """)

    st.divider()

    # ========== CHUVA vs RENDIMENTO ==========
    st.markdown("### 🌧️ Precipitação vs Rendimento")

    col1, col2 = st.columns([2, 1])

    with col1:
        fig, corr = plot_scatter_com_correlacao(
            dt, 'rainfall_mm', 'rendimento_kg_ha',
            'Precipitação', 'Rendimento',
            'mm', 'kg/ha'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.metric("📊 Correlação", f"{corr:.3f}")

        if corr > 0.3:
            st.success("✅ Correlação Positiva")
        elif corr < -0.3:
            st.warning("⚠️ Correlação Negativa")
        else:
            st.info("ℹ️ Correlação Fraca")

    st.info("""
    💡 **Interpretação Agronômica:**
    - Água é limitante primário em agricultura
    - Déficit hídrico = principal causa de quebra de safra
    - Excesso também prejudica (encharcamento, lixiviação)
    """)

    st.divider()

    # ========== ÁGUA TOTAL (Chuva + Irrigação) vs RENDIMENTO ==========
    st.markdown("### 💦 Água Total (Chuva + Irrigação) vs Rendimento")

    # Criar nova variável
    dt_temp = dt.copy()
    dt_temp['agua_total_mm'] = dt_temp['rainfall_mm'] + dt_temp['volume_irrigacao_mm']

    col1, col2 = st.columns([2, 1])

    with col1:
        fig, corr = plot_scatter_com_correlacao(
            dt_temp, 'agua_total_mm', 'rendimento_kg_ha',
            'Água Total', 'Rendimento',
            'mm', 'kg/ha'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.metric("📊 Correlação", f"{corr:.3f}")

        if corr > 0.3:
            st.success("✅ Correlação Positiva")
        elif corr < -0.3:
            st.warning("⚠️ Correlação Negativa")
        else:
            st.info("ℹ️ Correlação Fraca")

    st.success("""
    ✅ **Insight Importante:**
    A correlação de **Água Total** (chuva + irrigação) tende a ser **mais forte** 
    que cada uma isoladamente, pois representa o disponível real para a planta!
    """)

# ============================================
#    TAB 4: MANEJO VS RENDIMENTO
# ============================================

with tab4:
    st.subheader("💧 Relação entre Manejo Agrícola e Rendimento")

    st.markdown("""
    Análise de como as **decisões de irrigação e fertilização** impactam o rendimento.
    """)

    st.divider()

    # ========== IRRIGAÇÃO vs RENDIMENTO ==========
    st.markdown("### 💧 Volume de Irrigação vs Rendimento")

    col1, col2 = st.columns([2, 1])

    with col1:
        fig, corr = plot_scatter_com_correlacao(
            dt, 'volume_irrigacao_mm', 'rendimento_kg_ha',
            'Volume de Irrigação', 'Rendimento',
            'mm', 'kg/ha'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.metric("📊 Correlação", f"{corr:.3f}")

        if corr > 0.3:
            st.success("✅ Correlação Positiva")
        elif corr < -0.3:
            st.warning("⚠️ Correlação Negativa")
        else:
            st.info("ℹ️ Correlação Fraca")

    st.info("""
    💡 **Interpretação:**
    - Irrigação compensa déficit hídrico
    - Mais efetiva em períodos secos
    - Correlação pode ser fraca se chuva já foi suficiente
    """)

    st.divider()

    # ========== FERTILIZAÇÃO N vs RENDIMENTO ==========
    st.markdown("### 🌿 Fertilização Nitrogenada vs Rendimento")

    col1, col2 = st.columns([2, 1])

    with col1:
        fig, corr = plot_scatter_com_correlacao(
            dt, 'N_fertilizacao_kg_ha', 'rendimento_kg_ha',
            'Fertilização N', 'Rendimento',
            'kg/ha', 'kg/ha'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.metric("📊 Correlação", f"{corr:.3f}")

        if corr > 0.3:
            st.success("✅ Correlação Positiva")
        elif corr < -0.3:
            st.warning("⚠️ Correlação Negativa")
        else:
            st.info("ℹ️ Correlação Fraca")

    st.divider()

    # ========== FERTILIZAÇÃO P vs RENDIMENTO ==========
    st.markdown("### 🌿 Fertilização Fosfatada vs Rendimento")

    col1, col2 = st.columns([2, 1])

    with col1:
        fig, corr = plot_scatter_com_correlacao(
            dt, 'P_fertilizacao_kg_ha', 'rendimento_kg_ha',
            'Fertilização P', 'Rendimento',
            'kg/ha', 'kg/ha'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.metric("📊 Correlação", f"{corr:.3f}")

        if corr > 0.3:
            st.success("✅ Correlação Positiva")
        elif corr < -0.3:
            st.warning("⚠️ Correlação Negativa")
        else:
            st.info("ℹ️ Correlação Fraca")

    st.divider()

    # ========== FERTILIZAÇÃO K vs RENDIMENTO ==========
    st.markdown("### 🌿 Fertilização Potássica vs Rendimento")

    col1, col2 = st.columns([2, 1])

    with col1:
        fig, corr = plot_scatter_com_correlacao(
            dt, 'K_fertilizacao_kg_ha', 'rendimento_kg_ha',
            'Fertilização K', 'Rendimento',
            'kg/ha', 'kg/ha'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.metric("📊 Correlação", f"{corr:.3f}")

        if corr > 0.3:
            st.success("✅ Correlação Positiva")
        elif corr < -0.3:
            st.warning("⚠️ Correlação Negativa")
        else:
            st.info("ℹ️ Correlação Fraca")

    st.divider()

    # ========== RELAÇÃO: Solo vs Fertilização ==========
    st.markdown("### 🔄 Solo vs Fertilização (Relação Inversa Esperada)")

    st.markdown("""
    Agricultores devem aplicar **mais fertilizante** quando o solo tem **menos nutriente**.
    Vamos verificar se isso acontece nos dados:
    """)

    col1, col2, col3 = st.columns(3)

    with col1:
        fig, corr = plot_scatter_com_correlacao(
            dt, 'N', 'N_fertilizacao_kg_ha',
            'N no Solo', 'N Fertilizado',
            'kg/ha', 'kg/ha'
        )
        st.plotly_chart(fig, use_container_width=True)

        if corr < -0.3:
            st.success("✅ Correlação Negativa: Prática correta!")
        else:
            st.warning("⚠️ Relação não é inversa como esperado")

    with col2:
        fig, corr = plot_scatter_com_correlacao(
            dt, 'P', 'P_fertilizacao_kg_ha',
            'P no Solo', 'P Fertilizado',
            'kg/ha', 'kg/ha'
        )
        st.plotly_chart(fig, use_container_width=True)

        if corr < -0.3:
            st.success("✅ Correlação Negativa: Prática correta!")
        else:
            st.warning("⚠️ Relação não é inversa como esperado")

    with col3:
        fig, corr = plot_scatter_com_correlacao(
            dt, 'K', 'K_fertilizacao_kg_ha',
            'K no Solo', 'K Fertilizado',
            'kg/ha', 'kg/ha'
        )
        st.plotly_chart(fig, use_container_width=True)

        if corr < -0.3:
            st.success("✅ Correlação Negativa: Prática correta!")
        else:
            st.warning("⚠️ Relação não é inversa como esperado")

st.divider()

# ============================================
#         CONCLUSÕES DA ANÁLISE BIVARIADA
# ============================================

st.divider()

st.header("📝 Principais Descobertas")

st.markdown("""
### 🎯 1. Variáveis Mais Correlacionadas com Rendimento

Após análise completa da matriz de correlação, identificamos as **5 variáveis** 
com maior correlação absoluta com o rendimento:

| Ranking | Variável | Correlação | Tipo |
|---------|----------|------------|------|
| 1º | Nitrogênio no Solo (N) | -0.100 | Fraca negativa |
| 2º | Precipitação (rainfall_mm) | -0.079 | Fraca negativa |
| 3º | Fósforo no Solo (P) | +0.078 | Fraca positiva |
| 4º | Fertilização N | -0.078 | Fraca negativa |
| 5º | Fertilização P | +0.071 | Fraca positiva |

""")

st.warning("""
⚠️ **Observação Importante:** 

Todas as correlações individuais são **fracas** (|r| < 0.15). Isso indica que o rendimento 
agrícola depende da **combinação de múltiplos fatores**, não de uma única variável isolada.
""")

st.divider()

st.markdown("""
### 🔍 2. Relações Não-Lineares Identificadas

A análise dos scatter plots revelou padrões importantes:

- **pH do Solo**: Relação em formato de "curva", com rendimentos maiores na faixa 5.5-7.0
- **Temperatura**: Pontos ótimos entre 20-30°C, com quedas nos extremos
- **Água Total**: Excesso ou escassez prejudicam o rendimento

Essas descobertas confirmam que **correlações lineares simples não capturam toda a complexidade** do problema.
""")

st.divider()

st.markdown("""
### 🔄 3. Interações Entre Variáveis

Identificamos interações importantes:

- **NPK Balanceado**: O efeito de N depende dos níveis de P e K
- **Clima + Manejo**: Irrigação compensa baixa precipitação
- **Solo + Fertilização**: Aplicação de fertilizante relacionada aos níveis do solo

Essas interações serão consideradas nos modelos de Machine Learning através de:
- Feature engineering (criação de variáveis derivadas)
- Regressão polinomial (termos de interação)
""")

st.divider()

st.markdown("""
### 🤖 4. Estratégia de Modelagem

Com base nas descobertas da análise bivariada, definimos a seguinte estratégia 
para os **3 modelos preditivos** do projeto:
""")

# Cards para os 3 modelos
col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    **💧 Modelo 1:**  
    **Volume de Irrigação**

    🎯 **Target**: volume_irrigacao_mm

    📊 **Features principais**:
    - Precipitação
    - Umidade
    - Temperatura
    - Tipo de cultura

    🔧 **Algoritmo**:
    - Regressão Linear Múltipla
    - Regressão Polinomial (grau 2)
    """)

with col2:
    st.success("""
    **🌿 Modelo 2:**  
    **Necessidade de Fertilização**

    🎯 **Target**: N_fertilizacao_kg_ha  
    (também P e K)

    📊 **Features principais**:
    - Nutrientes no solo (N, P, K)
    - pH do solo
    - Tipo de cultura
    - Rendimento esperado

    🔧 **Algoritmo**:
    - Regressão Linear Múltipla
    - Regressão Polinomial (grau 2)
    """)

with col3:
    st.warning("""
    **🌾 Modelo 3:**  
    **Estimativa de Rendimento**

    🎯 **Target**: rendimento_kg_ha

    📊 **Features principais**:
    - TODAS as 11 variáveis
    - Tipo de cultura
    - Interações NPK

    🔧 **Algoritmo**:
    - Regressão Linear Múltipla
    - Regressão Polinomial (grau 2)
    - Comparação de desempenho
    """)

st.divider()

st.markdown("""
### 📊 5. Métricas de Avaliação

Para avaliar o desempenho de cada modelo, utilizaremos:

- **MAE (Mean Absolute Error)**: Erro médio absoluto em unidades originais
- **MSE (Mean Squared Error)**: Erro quadrático médio (penaliza erros grandes)
- **RMSE (Root Mean Squared Error)**: Raiz do MSE (mesma unidade do target)
- **R² (Coeficiente de Determinação)**: Percentual da variação explicada (0 a 1)

🎯 **Meta de desempenho**: R² > 0.20 para todos os modelos
""")

st.divider()

st.success("""
✅ **Conclusão:**

A análise bivariada revelou que o rendimento agrícola é resultado de **relações complexas 
e multifatoriais**. Embora nenhuma variável isolada tenha correlação forte, a **combinação 
de múltiplas variáveis** através de modelos de regressão múltipla e polinomial permitirá:

1. Prever volume de irrigação necessário
2. Recomendar quantidades de fertilização NPK
3. Estimar rendimento esperado da cultura

Esses três modelos serão integrados em um **dashboard interativo** para auxiliar gestores 
agrícolas na **tomada de decisão baseada em dados**.
""")


#==========================================================
#       🎯 FASE 6: ANÁLISE MULTIVARIADA
#==========================================================

st.header("🎯 Análise Multivariada")

st.markdown("""
Enquanto a análise bivariada examinou **relações entre pares** de variáveis, 
a análise multivariada investiga como **múltiplas variáveis agem simultaneamente** 
e se há **interações** entre elas.

**Objetivo:** Descobrir padrões complexos que só aparecem quando consideramos 
3 ou mais variáveis juntas.
""")

st.divider()

# ============================================
#    TABS PARA ORGANIZAR AS ANÁLISES
# ============================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Scatter Matrix 3D",
    "🔄 Análise de Interações",
    "📉 PCA (Redução Dimensional)",
    "🎯 Heatmap de Correlações Agrupadas"
])

# ============================================
#    TAB 1: SCATTER MATRIX 3D (NPK)
# ============================================

with tab1:
    st.subheader("📊 Visualização 3D: Interações NPK")

    st.markdown("""
    Visualização tridimensional mostrando como **N, P e K interagem** 
    simultaneamente para determinar o rendimento.

    **Hipótese:** O rendimento depende do **balanço** entre os três nutrientes, 
    não de valores altos individuais.
    """)

    st.divider()

    # ========== VERIFICAR DADOS ==========
    st.markdown("#### 🔍 Verificação dos Dados")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total de Registros", len(dt))
    with col2:
        nulos_npk = dt[['N', 'P', 'K', 'rendimento_kg_ha']].isnull().sum().sum()
        st.metric("Valores Nulos (NPK+Rend)", nulos_npk)
    with col3:
        dt_clean = dt[['N', 'P', 'K', 'rendimento_kg_ha']].dropna()
        st.metric("Registros Válidos", len(dt_clean))

    st.divider()

    # ========== GRÁFICO 3D: N, P, K vs Rendimento ==========
    st.markdown("### 🎨 Gráfico 3D: N × P × K vs Rendimento")

    # Limpar dados (remover NaN)
    dt_clean = dt[['N', 'P', 'K', 'rendimento_kg_ha']].dropna()

    st.info(f"📊 Visualizando {len(dt_clean)} de {len(dt)} registros (após remover valores nulos)")

    if len(dt_clean) > 0:
        try:
            # Criar gráfico 3D
            fig = px.scatter_3d(
                dt_clean,
                x='N',
                y='P',
                z='K',
                color='rendimento_kg_ha',
                title='Interação Tridimensional NPK vs Rendimento',
                labels={
                    'N': 'Nitrogênio (kg/ha)',
                    'P': 'Fósforo (kg/ha)',
                    'K': 'Potássio (kg/ha)',
                    'rendimento_kg_ha': 'Rendimento'
                },
                color_continuous_scale='RdYlGn',
                height=700
            )

            # Configurações do layout
            fig.update_layout(
                scene=dict(
                    xaxis=dict(
                        title='Nitrogênio (kg/ha)',
                        backgroundcolor="rgb(230, 230, 230)",
                        gridcolor="white",
                        showbackground=True
                    ),
                    yaxis=dict(
                        title='Fósforo (kg/ha)',
                        backgroundcolor="rgb(230, 230, 230)",
                        gridcolor="white",
                        showbackground=True
                    ),
                    zaxis=dict(
                        title='Potássio (kg/ha)',
                        backgroundcolor="rgb(230, 230, 230)",
                        gridcolor="white",
                        showbackground=True
                    ),
                    camera=dict(
                        eye=dict(x=1.5, y=1.5, z=1.3)
                    )
                ),
                coloraxis_colorbar=dict(
                    title="Rendimento<br>(kg/ha)",
                    thickness=20,
                    len=0.7
                )
            )

            # Configuração dos pontos
            fig.update_traces(
                marker=dict(
                    size=4,
                    opacity=0.8,
                    line=dict(width=0)
                )
            )

            st.plotly_chart(fig, use_container_width=True)

            st.success("✅ Gráfico 3D renderizado com sucesso!")

            st.info("""
            💡 **Como interagir:**
            - **Clique e arraste**: Rotacionar o gráfico
            - **Scroll**: Zoom in/out
            - **Duplo clique**: Resetar visualização
            - **Hover**: Ver valores dos pontos

            **O que procurar:**
            - Pontos verdes (alto rendimento) aparecem quando N, P, K estão balanceados
            - Pontos vermelhos (baixo rendimento) indicam desbalanço nutricional
            """)

        except Exception as e:
            st.error(f"❌ Erro ao criar gráfico 3D: {str(e)}")

            # Mostrar detalhes do erro para debug
            st.code(f"""
            Tipo do erro: {type(e).__name__}
            Mensagem: {str(e)}

            Dados do subset:
            - Shape: {dt_clean.shape}
            - Colunas: {dt_clean.columns.tolist()}
            - Tipos: {dt_clean.dtypes.to_dict()}
            - Range N: {dt_clean['N'].min():.2f} a {dt_clean['N'].max():.2f}
            - Range P: {dt_clean['P'].min():.2f} a {dt_clean['P'].max():.2f}
            - Range K: {dt_clean['K'].min():.2f} a {dt_clean['K'].max():.2f}
            - Range Rend: {dt_clean['rendimento_kg_ha'].min():.2f} a {dt_clean['rendimento_kg_ha'].max():.2f}
            """)

            st.warning("🔄 Tentando visualização alternativa em 2D...")

            # Gráficos 2D alternativos
            col1, col2, col3 = st.columns(3)

            with col1:
                fig = px.scatter(
                    dt_clean,
                    x='N',
                    y='P',
                    color='rendimento_kg_ha',
                    title='N vs P',
                    color_continuous_scale='RdYlGn',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig = px.scatter(
                    dt_clean,
                    x='N',
                    y='K',
                    color='rendimento_kg_ha',
                    title='N vs K',
                    color_continuous_scale='RdYlGn',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

            with col3:
                fig = px.scatter(
                    dt_clean,
                    x='P',
                    y='K',
                    color='rendimento_kg_ha',
                    title='P vs K',
                    color_continuous_scale='RdYlGn',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("❌ Não há dados válidos para visualização! Todos os registros têm valores nulos.")

        # Diagnóstico
        st.warning("🔍 Diagnóstico:")
        st.write("Valores nulos por coluna:")
        st.write(dt[['N', 'P', 'K', 'rendimento_kg_ha']].isnull().sum())

    # ========== ANÁLISE DE BALANÇO NPK ==========
    st.markdown("### 🔍 Análise do Balanço NPK")

    if len(dt_clean) > 0:
        # Calcular razões NPK
        dt_temp = dt_clean.copy()
        dt_temp['razao_NP'] = dt_temp['N'] / (dt_temp['P'] + 0.1)
        dt_temp['razao_NK'] = dt_temp['N'] / (dt_temp['K'] + 0.1)
        dt_temp['razao_PK'] = dt_temp['P'] / (dt_temp['K'] + 0.1)

        # Classificar balanço
        dt_temp['balanco_NPK'] = 'Desbalanceado'

        condicao_balanceado = (
                (dt_temp['razao_NP'] > 0.7) & (dt_temp['razao_NP'] < 1.3) &
                (dt_temp['razao_NK'] > 0.7) & (dt_temp['razao_NK'] < 1.3) &
                (dt_temp['razao_PK'] > 0.7) & (dt_temp['razao_PK'] < 1.3)
        )

        dt_temp.loc[condicao_balanceado, 'balanco_NPK'] = 'Balanceado'

        # Comparar rendimentos
        col1, col2 = st.columns(2)

        with col1:
            rend_balanceado = dt_temp[dt_temp['balanco_NPK'] == 'Balanceado']['rendimento_kg_ha'].mean()
            rend_desbalanceado = dt_temp[dt_temp['balanco_NPK'] == 'Desbalanceado']['rendimento_kg_ha'].mean()

            st.metric(
                "🎯 Rendimento com NPK Balanceado",
                f"{rend_balanceado:.0f} kg/ha"
            )
            st.metric(
                "⚠️ Rendimento com NPK Desbalanceado",
                f"{rend_desbalanceado:.0f} kg/ha",
                delta=f"{rend_balanceado - rend_desbalanceado:.0f} kg/ha"
            )

        with col2:
            fig_bar = px.box(
                dt_temp,
                x='balanco_NPK',
                y='rendimento_kg_ha',
                color='balanco_NPK',
                title='Rendimento: Balanceado vs Desbalanceado',
                labels={'rendimento_kg_ha': 'Rendimento (kg/ha)', 'balanco_NPK': 'Balanço NPK'},
                color_discrete_map={'Balanceado': '#4CAF50', 'Desbalanceado': '#f44336'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        if rend_balanceado > rend_desbalanceado:
            diferenca_percentual = ((rend_balanceado - rend_desbalanceado) / rend_desbalanceado * 100)
            st.success(f"""
            ✅ **Comprovado!** Quando NPK estão balanceados, o rendimento é **{diferenca_percentual:.1f}% maior** 
            em média!
            """)

    st.divider()

    # ========== SCATTER MATRIX ==========
    st.markdown("### 📊 Matriz de Dispersão Completa: Nutrientes")

    variaveis_nutrientes = ['N', 'P', 'K', 'soil_pH', 'rendimento_kg_ha']
    dt_matrix = dt[variaveis_nutrientes].dropna()

    if len(dt_matrix) > 10:
        try:
            # Usar Seaborn para maior confiabilidade
            import matplotlib.pyplot as plt

            fig = sns.pairplot(
                dt_matrix,
                diag_kind='hist',
                plot_kws={'alpha': 0.5, 's': 20, 'color': '#2E7D32'},
                diag_kws={'color': '#2E7D32', 'bins': 20, 'alpha': 0.7}
            )

            fig.fig.suptitle('Matriz de Dispersão: Nutrientes vs Rendimento',
                             y=1.01, fontsize=14, fontweight='bold')

            st.pyplot(fig)

            st.success("✅ Matriz de dispersão renderizada!")

        except Exception as e:
            st.error(f"❌ Erro ao criar scatter matrix: {e}")
    else:
        st.warning("⚠️ Dados insuficientes para scatter matrix!")

    st.info("""
    💡 **Como interpretar:**
    - Diagonal: Histogramas mostrando distribuição de cada variável
    - Abaixo da diagonal: Scatter plots entre pares de variáveis
    - Procure por padrões lineares, clusters ou outliers
    """)

# ============================================
#    TAB 2: ANÁLISE DE INTERAÇÕES
# ============================================

with tab2:
    st.subheader("🔄 Análise de Efeitos de Interação")

    st.markdown("""
    **Pergunta:** O efeito de uma variável no rendimento **depende** do nível de outra variável?

    Exemplo: O efeito de Nitrogênio muda dependendo se o Fósforo está alto ou baixo?
    """)

    st.divider()

    # ========== INTERAÇÃO 1: N vs Rendimento (por níveis de P) ==========
    st.markdown("### 🔹 Interação: N vs Rendimento (estratificado por P)")

    # Criar grupos de P
    dt_temp = dt.copy()
    dt_temp['P_grupo'] = pd.cut(
        dt_temp['P'],
        bins=3,
        labels=['P Baixo\n(< 33%)', 'P Médio\n(33-66%)', 'P Alto\n(> 66%)']
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        # Scatter plot com grupos
        fig = px.scatter(
            dt_temp,
            x='N',
            y='rendimento_kg_ha',
            color='P_grupo',
            trendline='ols',
            title='Efeito de N depende do nível de P?',
            labels={
                'N': 'Nitrogênio (kg/ha)',
                'rendimento_kg_ha': 'Rendimento (kg/ha)',
                'P_grupo': 'Nível de Fósforo'
            },
            color_discrete_map={
                'P Baixo\n(< 33%)': '#f44336',
                'P Médio\n(33-66%)': '#ff9800',
                'P Alto\n(> 66%)': '#4caf50'
            },
            opacity=0.6,
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.info("""
        **💡 Interpretação:**

        Se as **linhas de tendência** 
        tiverem inclinações diferentes, 
        há **INTERAÇÃO**!

        Isso significa que o efeito 
        de N muda dependendo de P.

        **Exemplo:**
        - Com P baixo: mais N não ajuda
        - Com P alto: mais N aumenta rendimento

        Isso é a **Lei do Mínimo** 
        de Liebig em ação!
        """)

        # Calcular correlações por grupo
        st.markdown("**Correlações por grupo:**")
        for grupo in dt_temp['P_grupo'].unique():
            if pd.notna(grupo):
                subset = dt_temp[dt_temp['P_grupo'] == grupo]
                corr = subset[['N', 'rendimento_kg_ha']].corr().iloc[0, 1]
                st.metric(f"{grupo}", f"{corr:.3f}")

    st.divider()

    # ========== INTERAÇÃO 2: Temperatura vs Rendimento (por níveis de Umidade) ==========
    st.markdown("### 🔹 Interação: Temperatura vs Rendimento (estratificado por Umidade)")

    # Criar grupos de umidade
    dt_temp['Umidade_grupo'] = pd.cut(
        dt_temp['humidity_%'],
        bins=3,
        labels=['Seco\n(< 33%)', 'Moderado\n(33-66%)', 'Úmido\n(> 66%)']
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = px.scatter(
            dt_temp,
            x='temperature_C',
            y='rendimento_kg_ha',
            color='Umidade_grupo',
            trendline='ols',
            title='Efeito da Temperatura depende da Umidade?',
            labels={
                'temperature_C': 'Temperatura (°C)',
                'rendimento_kg_ha': 'Rendimento (kg/ha)',
                'Umidade_grupo': 'Nível de Umidade'
            },
            color_discrete_map={
                'Seco\n(< 33%)': '#ff5722',
                'Moderado\n(33-66%)': '#ffc107',
                'Úmido\n(> 66%)': '#2196f3'
            },
            opacity=0.6,
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.info("""
        **💡 Interpretação:**

        Temperatura e umidade 
        **interagem** para determinar 
        o estresse hídrico da planta.

        **Situações críticas:**
        - Quente + Seco = Alto estresse
        - Quente + Úmido = Pode ser OK
        - Frio + Úmido = Risco de doenças

        A combinação importa mais 
        que valores individuais!
        """)

        # Calcular correlações por grupo
        st.markdown("**Correlações por grupo:**")
        for grupo in dt_temp['Umidade_grupo'].unique():
            if pd.notna(grupo):
                subset = dt_temp[dt_temp['Umidade_grupo'] == grupo]
                corr = subset[['temperature_C', 'rendimento_kg_ha']].corr().iloc[0, 1]
                st.metric(f"{grupo}", f"{corr:.3f}")

    st.divider()

    # ========== INTERAÇÃO 3: Água Total vs Rendimento (por tipo de cultura) ==========
    st.markdown("### 🔹 Interação: Água Total vs Rendimento (por cultura)")

    # Criar variável água total
    dt_temp['agua_total'] = dt_temp['rainfall_mm'] + dt_temp['volume_irrigacao_mm']

    fig = px.scatter(
        dt_temp,
        x='agua_total',
        y='rendimento_kg_ha',
        color='crop_type',
        trendline='ols',
        title='Demanda Hídrica varia por Cultura',
        labels={
            'agua_total': 'Água Total (Chuva + Irrigação) em mm',
            'rendimento_kg_ha': 'Rendimento (kg/ha)',
            'crop_type': 'Tipo de Cultura'
        },
        color_discrete_sequence=px.colors.qualitative.Set2,
        opacity=0.6,
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    st.info("""
    💡 **Diferentes culturas, diferentes necessidades:**

    - **Arroz**: Alta demanda hídrica (1500-2000mm)
    - **Milho**: Demanda moderada (400-600mm)
    - **Soja**: Demanda moderada (450-800mm)

    Por isso a variável **crop_type** é essencial no modelo!
    """)

    # Tabela de correlações por cultura
    st.markdown("#### 📊 Correlação Água vs Rendimento por Cultura")

    corr_por_cultura = []
    for cultura in dt_temp['crop_type'].unique():
        subset = dt_temp[dt_temp['crop_type'] == cultura]
        corr = subset[['agua_total', 'rendimento_kg_ha']].corr().iloc[0, 1]
        n = len(subset)
        corr_por_cultura.append({
            'Cultura': cultura,
            'Correlação': corr,
            'Amostras': n
        })

    df_corr_cultura = pd.DataFrame(corr_por_cultura).sort_values('Correlação', ascending=False)
    st.dataframe(df_corr_cultura, use_container_width=True, hide_index=True)

# ============================================
#    TAB 3: PCA (ANÁLISE DE COMPONENTES)
# ============================================

with tab3:
    st.subheader("📉 PCA - Análise de Componentes Principais")

    st.markdown("""
    **O que é PCA?** Técnica que **agrupa variáveis correlacionadas** em 
    "componentes principais", reduzindo a dimensionalidade dos dados.

    **Por que usar?** 
    - Identificar variáveis redundantes
    - Visualizar dados complexos em 2D ou 3D
    - Simplificar o modelo de ML
    """)

    st.divider()

    # Selecionar variáveis numéricas
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler

    variaveis_pca = ['N', 'P', 'K', 'soil_pH', 'temperature_C',
                     'humidity_%', 'rainfall_mm', 'volume_irrigacao_mm']

    X = dt[variaveis_pca].values

    # Normalizar (ESSENCIAL para PCA!)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Aplicar PCA
    pca = PCA()
    X_pca = pca.fit_transform(X_scaled)

    # ========== SCREE PLOT (Variância Explicada) ==========
    st.markdown("### 📊 Scree Plot: Variância Explicada por Componente")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Criar DataFrame
        variancia_explicada = pd.DataFrame({
            'Componente': [f'PC{i + 1}' for i in range(len(pca.explained_variance_ratio_))],
            'Variância Explicada (%)': pca.explained_variance_ratio_ * 100,
            'Variância Acumulada (%)': np.cumsum(pca.explained_variance_ratio_) * 100
        })

        # Gráfico
        fig = px.line(
            variancia_explicada,
            x='Componente',
            y=['Variância Explicada (%)', 'Variância Acumulada (%)'],
            title='Variância Explicada por Componente',
            markers=True,
            height=400
        )

        fig.add_hline(y=80, line_dash="dash", line_color="green",
                      annotation_text="Meta: 80%", annotation_position="right")

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.metric(
            "Variância Explicada (PC1)",
            f"{pca.explained_variance_ratio_[0] * 100:.1f}%"
        )
        st.metric(
            "Variância Explicada (PC2)",
            f"{pca.explained_variance_ratio_[1] * 100:.1f}%"
        )
        st.metric(
            "Total (PC1 + PC2)",
            f"{sum(pca.explained_variance_ratio_[:2]) * 100:.1f}%"
        )

        # Quantos componentes para 80%?
        n_componentes_80 = np.argmax(np.cumsum(pca.explained_variance_ratio_) >= 0.80) + 1
        st.metric(
            "Componentes para 80%",
            f"{n_componentes_80} de {len(variaveis_pca)}"
        )

    st.divider()

    # ========== BIPLOT (PC1 vs PC2) ==========
    st.markdown("### 🎯 Biplot: Visualização em 2D")

    # Criar DataFrame com componentes principais
    dt_pca = pd.DataFrame({
        'PC1': X_pca[:, 0],
        'PC2': X_pca[:, 1],
        'rendimento': dt['rendimento_kg_ha'],
        'cultura': dt['crop_type']
    })

    # Scatter plot
    fig = px.scatter(
        dt_pca,
        x='PC1',
        y='PC2',
        color='rendimento',
        title=f'PCA: {pca.explained_variance_ratio_[0] * 100:.1f}% (PC1) + {pca.explained_variance_ratio_[1] * 100:.1f}% (PC2) = {sum(pca.explained_variance_ratio_[:2]) * 100:.1f}% da variância',
        color_continuous_scale='RdYlGn',
        opacity=0.7,
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ========== LOADINGS (Contribuição das Variáveis) ==========
    st.markdown("### 🔍 Loadings: Contribuição de Cada Variável")

    # Pegar os loadings (componentes principais)
    loadings = pca.components_.T * np.sqrt(pca.explained_variance_)

    # Criar DataFrame
    df_loadings = pd.DataFrame(
        loadings[:, :3],  # Primeiros 3 componentes
        columns=['PC1', 'PC2', 'PC3'],
        index=variaveis_pca
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        # Heatmap dos loadings
        fig = px.imshow(
            df_loadings.T,
            title='Contribuição das Variáveis nos Componentes Principais',
            labels=dict(x="Variável", y="Componente", color="Loading"),
            color_continuous_scale='RdBu',
            color_continuous_midpoint=0,
            aspect='auto',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Top 3 variáveis por componente:**")

        for i in range(3):
            st.markdown(f"**PC{i + 1}:**")
            top3 = df_loadings[f'PC{i + 1}'].abs().sort_values(ascending=False).head(3)
            for var, val in top3.items():
                st.write(f"- {var}: {val:.3f}")

    st.info("""
    💡 **Como interpretar loadings:**

    - **Valores altos** (próximos de ±1): variável contribui muito para o componente
    - **Valores baixos** (próximos de 0): variável contribui pouco
    - **Mesmo sinal**: variáveis se movem juntas
    - **Sinais opostos**: variáveis se movem em direções opostas

    Variáveis com loadings semelhantes são **redundantes** e podem ser agrupadas!
    """)

    st.divider()

    # ========== ANÁLISE POR CULTURA ==========
    st.markdown("### 🌾 PCA Colorido por Tipo de Cultura")

    fig = px.scatter(
        dt_pca,
        x='PC1',
        y='PC2',
        color='cultura',
        title='Culturas se Agrupam de Forma Diferente?',
        color_discrete_sequence=px.colors.qualitative.Set2,
        opacity=0.7,
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    st.info("""
    💡 Se culturas formarem **grupos separados** no PCA, significa que cada uma 
    tem um **padrão característico** de condições e manejo!
    """)

# ============================================
#    TAB 4: HEATMAP DE CORRELAÇÕES AGRUPADAS
# ============================================

with tab4:
    st.subheader("🎯 Heatmap de Correlações com Agrupamento Hierárquico")

    st.markdown("""
    **Objetivo:** Agrupar variáveis **similares** através de clustering hierárquico, 
    facilitando a identificação de variáveis redundantes.
    """)

    st.divider()

    # Calcular matriz de correlação
    colunas_numericas = dt.select_dtypes(include=[np.number]).columns
    matriz_corr = dt[colunas_numericas].corr()

    # Usar seaborn com clustering
    import matplotlib.pyplot as plt
    import seaborn as sns
    from scipy.cluster import hierarchy

    # Calcular dendrograma
    linkage = hierarchy.linkage(matriz_corr, method='average')

    # Ordenar matriz baseado no clustering
    dendro = hierarchy.dendrogram(linkage, no_plot=True)
    ordem = dendro['leaves']

    matriz_corr_ordenada = matriz_corr.iloc[ordem, ordem]

    # Criar figura
    fig, ax = plt.subplots(figsize=(12, 10))

    # Heatmap com clustering
    sns.heatmap(
        matriz_corr_ordenada,
        annot=True,
        fmt='.2f',
        cmap='RdYlGn',
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.8},
        ax=ax
    )

    ax.set_title('Matriz de Correlação com Agrupamento Hierárquico',
                 fontsize=16, fontweight='bold', pad=20)

    st.pyplot(fig)

    st.info("""
    💡 **Como interpretar:**

    - Variáveis **próximas** (agrupadas) têm comportamentos similares
    - **Blocos verdes/vermelhos**: grupos de variáveis fortemente correlacionadas
    - Essas variáveis são **candidatas a agrupamento** ou **remoção de redundância**

    **Para o modelo de ML:**
    - Se duas variáveis têm correlação > 0.9, considere usar apenas uma
    - Ou use PCA para combiná-las em um componente único
    """)

    st.divider()

    # ========== IDENTIFICAR GRUPOS ==========
    st.markdown("### 🔍 Identificação de Grupos de Variáveis")

    # Correlações muito altas (possível multicolinearidade)
    threshold = 0.8

    pares_alta_corr = []
    for i in range(len(matriz_corr.columns)):
        for j in range(i + 1, len(matriz_corr.columns)):
            if abs(matriz_corr.iloc[i, j]) >= threshold:
                pares_alta_corr.append({
                    'Variável 1': matriz_corr.columns[i],
                    'Variável 2': matriz_corr.columns[j],
                    'Correlação': matriz_corr.iloc[i, j]
                })

    if len(pares_alta_corr) > 0:
        df_alta_corr = pd.DataFrame(pares_alta_corr).sort_values('Correlação',
                                                                 key=abs,
                                                                 ascending=False)

        st.warning(f"""
        ⚠️ **{len(pares_alta_corr)} pares de variáveis** com correlação ≥ {threshold}:

        Isso indica **multicolinearidade** - as variáveis fornecem informação redundante!
        """)

        st.dataframe(df_alta_corr, use_container_width=True, hide_index=True)

        st.info("""
        💡 **Recomendações:**
        - **Opção 1**: Remover uma das variáveis de cada par
        - **Opção 2**: Usar PCA para combinar variáveis correlacionadas
        - **Opção 3**: Usar regularização (Ridge/Lasso) no modelo
        """)
    else:
        st.success(f"""
        ✅ Não há pares de variáveis com correlação ≥ {threshold}

        Isso é positivo - **baixo risco de multicolinearidade**!
        """)

    st.divider()

    # ========== RESUMO DOS GRUPOS ==========
    st.markdown("### 📊 Grupos Identificados por Clustering")

    # Cortar dendrograma em clusters
    from scipy.cluster.hierarchy import fcluster

    n_clusters = 3
    clusters = fcluster(linkage, n_clusters, criterion='maxclust')

    # Criar DataFrame
    df_clusters = pd.DataFrame({
        'Variável': matriz_corr.columns,
        'Grupo': clusters
    }).sort_values('Grupo')

    col1, col2 = st.columns([1, 2])

    with col1:
        st.dataframe(df_clusters, use_container_width=True, hide_index=True)

    with col2:
        st.markdown(f"""
        **{n_clusters} grupos identificados:**

        Variáveis no mesmo grupo têm comportamentos **similares** e podem:
        - Ser representadas por uma única variável
        - Ser combinadas via PCA
        - Ter coeficientes similares no modelo
        """)

        # Contar variáveis por grupo
        for i in range(1, n_clusters + 1):
            vars_grupo = df_clusters[df_clusters['Grupo'] == i]['Variável'].tolist()
            st.info(f"**Grupo {i}** ({len(vars_grupo)} variáveis): {', '.join(vars_grupo)}")

# ============================================
#         CONCLUSÕES DA ANÁLISE MULTIVARIADA
# ============================================

st.divider()
st.header("📝 Conclusões da Análise Multivariada")

st.markdown("""
### 🎯 Principais Descobertas:

**1. Interações Complexas Confirmadas:**
- O efeito de **N depende de P e K** (Lei do Mínimo de Liebig)
- **Temperatura + Umidade** interagem para determinar estresse hídrico
- Cada **cultura** responde diferentemente às mesmas condições

**2. Importância do Balanço NPK:**
- Rendimento é maior quando N, P, K estão **balanceados**
- Valores absolutos importam menos que as **proporções**
- Confirma necessidade de considerar os três simultaneamente

**3. Redução de Dimensionalidade (PCA):**
""")

# Calcular e mostrar estatísticas de PCA
n_comp_80 = np.argmax(np.cumsum(pca.explained_variance_ratio_) >= 0.80) + 1
n_comp_90 = np.argmax(np.cumsum(pca.explained_variance_ratio_) >= 0.90) + 1

st.info(f"""
- **{n_comp_80} componentes** explicam 80% da variância
- **{n_comp_90} componentes** explicam 90% da variância
- De {len(variaveis_pca)} variáveis originais, poderíamos usar {n_comp_80}-{n_comp_90} componentes
""")

st.markdown("""
**4. Multicolinearidade:**
""")

if len(pares_alta_corr) > 0:
    st.warning(f"""
    - Identificados **{len(pares_alta_corr)} pares** com correlação ≥ 0.8
    - Risco de instabilidade em modelos lineares
    - Recomenda-se regularização ou remoção de redundâncias
    """)
else:
    st.success("""
    - Não há multicolinearidade severa (correlações < 0.8)
    - Todas as variáveis podem ser mantidas no modelo
    """)

st.divider()

st.success("""
### ✅ Implicações para Machine Learning:

**Features a incluir:**
1. ✅ Todas as 11 variáveis numéricas originais
2. ✅ Variável categórica crop_type (one-hot encoding)
3. ✅ Features derivadas: água_total, balanço_NPK, razões NPK

**Modelos recomendados:**
1. ✅ **Regressão Linear Múltipla** (baseline)
2. ✅ **Regressão Polinomial grau 2** (capturar interações N×P, N×K, P×K)
3. ✅ Considerar **modelos por cultura** (diferentes padrões)

**Pré-processamento necessário:**
1. ✅ Normalização (StandardScaler) - essencial devido a escalas diferentes
2. ✅ One-hot encoding para crop_type
3. ✅ Criar termos de interação (polynomial features)

**Validação:**
- Usar **validação cruzada** para avaliar generalização
- Monitorar **multicolinearidade** através de VIF (Variance Inflation Factor)
- Comparar desempenho com e sem PCA

---
""")


#==========================================================
#       🚨 FASE 7: DETECÇÃO DE OUTLIERS
#==========================================================

st.header("🚨 Detecção de Outliers")

st.markdown("""
Outliers são valores extremos que podem afetar o modelo de regressão.
Vamos identificá-los usando **boxplots** e o método **IQR**.
""")

st.divider()

# ============================================
#    VISUALIZAÇÃO
# ============================================

st.subheader("📦 Visualização de Outliers")

# Variáveis principais para analisar
variaveis_analisar = ['N', 'P', 'K', 'soil_pH', 'temperature_C',
                      'humidity_%', 'rainfall_mm', 'rendimento_kg_ha']

# Criar boxplots
col1, col2, col3, col4 = st.columns(4)

colunas = [col1, col2, col3, col4]

for idx, var in enumerate(variaveis_analisar):
    with colunas[idx % 4]:
        fig = px.box(
            dt,
            y=var,
            title=var,
            color_discrete_sequence=['#2E7D32']
        )
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ============================================
#    RESUMO
# ============================================

st.subheader("📊 Resumo de Outliers")


# Contar outliers por variável
def contar_outliers(coluna):
    Q1 = dt[coluna].quantile(0.25)
    Q3 = dt[coluna].quantile(0.75)
    IQR = Q3 - Q1
    outliers = dt[(dt[coluna] < Q1 - 1.5 * IQR) | (dt[coluna] > Q3 + 1.5 * IQR)]
    return len(outliers)


# Criar tabela resumo
resumo = []
for var in variaveis_analisar:
    n_outliers = contar_outliers(var)
    percentual = (n_outliers / len(dt)) * 100
    resumo.append({
        'Variável': var,
        'Outliers': n_outliers,
        'Percentual': f'{percentual:.1f}%'
    })

df_resumo = pd.DataFrame(resumo)
st.dataframe(df_resumo, use_container_width=True, hide_index=True)

# Métricas
col1, col2 = st.columns(2)

with col1:
    total_outliers = df_resumo['Outliers'].sum()
    st.metric("🎯 Total de Outliers", f"{total_outliers:,}")

with col2:
    media_percentual = df_resumo['Outliers'].mean() / len(dt) * 100
    st.metric("📊 Média por Variável", f"{media_percentual:.1f}%")

st.divider()

# ============================================
#    DECISÃO
# ============================================

st.subheader("🎯 Decisão")

if media_percentual < 3:
    st.success("""
    ✅ **Decisão: MANTER todos os dados**

    - Poucos outliers detectados (< 3%)
    - Representam variabilidade natural da agricultura
    - Não vamos remover nenhum dado
    """)
else:
    st.warning(f"""
    ⚠️ **Decisão: MANTER com atenção**

    - {media_percentual:.1f}% de outliers em média
    - Vamos manter os dados (eventos agrícolas reais)
    - O modelo de regressão vai lidar com eles
    """)

st.info("""
💡 **Justificativa:**
Na agricultura, valores extremos são comuns (secas, geadas, etc.) e fazem parte da realidade.
Por isso, vamos mantê-los no modelo.
""")


#==========================================================
#    🧹 FASE 8: FEATURE ENGINEERING (Preparação para ML)
#==========================================================

# ==========================================================
#    🧹 FASE 8: FEATURE ENGINEERING (Preparação para ML)
# ==========================================================

st.header("🧹 Feature Engineering")

st.markdown("""
Preparação final dos dados para Machine Learning em **duas etapas**:
1. **Variáveis Derivadas Básicas** (combinações simples)
2. **Enriquecimento Avançado** (features específicas por modelo)
""")

st.divider()

# ============================================
#    8.1 VARIÁVEIS DERIVADAS BÁSICAS
# ============================================

st.subheader("➕ 8.1. Variáveis Derivadas Básicas")

# Criar cópia do dataset
dt_ml = dt.copy()

# Criar novas variáveis básicas
dt_ml['agua_total_mm'] = dt_ml['rainfall_mm'] + dt_ml['volume_irrigacao_mm']
dt_ml['NPK_total'] = dt_ml['N'] + dt_ml['P'] + dt_ml['K']
dt_ml['NPK_fertilizacao_total'] = (
        dt_ml['N_fertilizacao_kg_ha'] +
        dt_ml['P_fertilizacao_kg_ha'] +
        dt_ml['K_fertilizacao_kg_ha']
)

st.success("✅ 3 variáveis básicas criadas")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    **agua_total_mm**

    Chuva + Irrigação

    Água total disponível
    """)

with col2:
    st.info("""
    **NPK_total**

    N + P + K

    Nutrientes totais no solo
    """)

with col3:
    st.info("""
    **NPK_fertilizacao_total**

    Fertilizações N + P + K

    Fertilizante total aplicado
    """)

st.divider()

# ============================================
#    8.2 ENRIQUECIMENTO AVANÇADO
# ============================================

st.subheader("⭐ 8.2. Enriquecimento Avançado por Modelo")

st.markdown("""
Criação de **features específicas** para melhorar cada modelo preditivo.
Baseado em conhecimento agronômico e literatura científica.
""")

# Botão para executar enriquecimento
if st.button("🚀 Executar Enriquecimento Avançado", type="primary"):

    with st.spinner("Criando features avançadas..."):

        # FEATURES PARA IRRIGAÇÃO
        st.markdown("#### 💧 Features para Modelo de Irrigação")

        with st.expander("📖 Ver Lógica das Features"):
            st.markdown("""
            **1. Déficit Hídrico:** Diferença entre umidade ideal e real
            **2. Evapotranspiração:** Perda de água estimada pela temperatura
            **3. Demanda por Cultura:** Necessidade específica de cada cultura
            **4. Balanço Hídrico:** Entrada vs. Saída de água
            **5. Necessidade Teórica:** Quanto seria ideal irrigar
            """)

        # 1. Déficit hídrico
        dt_ml['deficit_hidrico_mm'] = np.maximum(0, 100 - dt_ml['humidity_%']) * 2

        # 2. Evapotranspiração estimada (Thornthwaite simplificado)
        dt_ml['evapotranspiracao_estimada'] = dt_ml['temperature_C'] * 0.6

        # 3. Demanda hídrica por cultura
        demanda_agua = {
            'Rice': 1500, 'Maize': 500, 'Wheat': 450,
            'Soybean': 600, 'Cotton': 700
        }
        dt_ml['demanda_agua_cultura'] = dt_ml['crop_type'].map(demanda_agua)

        # 4. Balanço hídrico
        dt_ml['balanco_hidrico'] = (
                dt_ml['rainfall_mm'] -
                dt_ml['evapotranspiracao_estimada'] +
                dt_ml['volume_irrigacao_mm']
        )

        # 5. Necessidade teórica de irrigação
        dt_ml['necessidade_irrigacao_teorica'] = np.maximum(
            0,
            dt_ml['evapotranspiracao_estimada'] - dt_ml['rainfall_mm']
        )

        # 6. Índice de aridez
        dt_ml['indice_aridez'] = dt_ml['rainfall_mm'] / (dt_ml['temperature_C'] + 10)

        # 7. Adequação da água disponível
        dt_ml['agua_adequacao'] = (
                dt_ml['agua_total_mm'] / dt_ml['demanda_agua_cultura']
        )

        st.success("✅ 7 features criadas para Irrigação")

        # FEATURES PARA FERTILIZAÇÃO
        st.markdown("#### 🌿 Features para Modelo de Fertilização")

        with st.expander("📖 Ver Lógica das Features"):
            st.markdown("""
            **1. Disponibilidade:** Nutrientes afetados pelo pH
            **2. Razões NPK:** Proporções entre nutrientes
            **3. Desvio do Ideal:** Distância da proporção ótima
            **4. Eficiência:** Quanto rendimento por unidade de nutriente
            """)

        # 1. Disponibilidade de nutrientes (afetada por pH)
        dt_ml['disponibilidade_nutrientes'] = np.where(
            (dt_ml['soil_pH'] >= 5.5) & (dt_ml['soil_pH'] <= 7.0),
            1.0, 0.6
        )

        dt_ml['N_disponivel'] = dt_ml['N'] * dt_ml['disponibilidade_nutrientes']
        dt_ml['P_disponivel'] = dt_ml['P'] * dt_ml['disponibilidade_nutrientes']
        dt_ml['K_disponivel'] = dt_ml['K'] * dt_ml['disponibilidade_nutrientes']

        # 2. Razões NPK
        dt_ml['razao_NP'] = dt_ml['N'] / (dt_ml['P'] + 0.1)
        dt_ml['razao_NK'] = dt_ml['N'] / (dt_ml['K'] + 0.1)
        dt_ml['razao_PK'] = dt_ml['P'] / (dt_ml['K'] + 0.1)

        # 3. Desvio do ideal (N:P:K = 4:2:1)
        dt_ml['desvio_NPK_ideal'] = np.abs(
            (dt_ml['N'] / 4) - (dt_ml['P'] / 2) - (dt_ml['K'] / 1)
        )

        # 4. Eficiência de uso de nutrientes
        dt_ml['eficiencia_N'] = dt_ml['rendimento_kg_ha'] / (
                dt_ml['N'] + dt_ml['N_fertilizacao_kg_ha'] + 1
        )
        dt_ml['eficiencia_P'] = dt_ml['rendimento_kg_ha'] / (
                dt_ml['P'] + dt_ml['P_fertilizacao_kg_ha'] + 1
        )
        dt_ml['eficiencia_K'] = dt_ml['rendimento_kg_ha'] / (
                dt_ml['K'] + dt_ml['K_fertilizacao_kg_ha'] + 1
        )

        st.success("✅ 13 features criadas para Fertilização")

        # FEATURES PARA RENDIMENTO
        st.markdown("#### 🌾 Features para Modelo de Rendimento")

        with st.expander("📖 Ver Lógica das Features"):
            st.markdown("""
            **1. Estresses:** Identificar condições limitantes
            **2. Condições Ideais:** Score de adequação climática
            **3. Interações:** NPK × Água e outras combinações
            **4. Potencial:** Rendimento máximo possível por cultura
            **5. Fatores Limitantes:** Identificar gargalo principal
            """)

        # 1. Estresses abióticos
        dt_ml['estresse_termico'] = np.where(
            (dt_ml['temperature_C'] > 35) | (dt_ml['temperature_C'] < 15),
            1, 0
        )

        dt_ml['estresse_hidrico'] = np.where(
            dt_ml['agua_total_mm'] < dt_ml['demanda_agua_cultura'] * 0.6,
            1, 0
        )

        dt_ml['estresse_total'] = dt_ml['estresse_termico'] + dt_ml['estresse_hidrico']

        # 2. Índice de condições ideais
        dt_ml['condicoes_ideais'] = (
                ((dt_ml['temperature_C'] >= 20) & (dt_ml['temperature_C'] <= 30)).astype(int) * 0.3 +
                ((dt_ml['humidity_%'] >= 60) & (dt_ml['humidity_%'] <= 80)).astype(int) * 0.3 +
                ((dt_ml['soil_pH'] >= 5.5) & (dt_ml['soil_pH'] <= 7.0)).astype(int) * 0.4
        )

        # 3. Interação NPK × Água
        dt_ml['NPK_agua_interacao'] = (
                dt_ml['NPK_total'] * dt_ml['agua_adequacao']
        )

        # 4. Rendimento potencial por cultura
        rend_potencial = {
            'Rice': 8000, 'Maize': 10000, 'Wheat': 6000,
            'Soybean': 4500, 'Cotton': 3500
        }
        dt_ml['rendimento_potencial'] = dt_ml['crop_type'].map(rend_potencial)
        dt_ml['taxa_realizacao'] = dt_ml['rendimento_kg_ha'] / dt_ml['rendimento_potencial']

        # 5. Adequação geral de insumos
        dt_ml['adequacao_insumos'] = (
                (dt_ml['NPK_total'] / 150) * 0.4 +
                dt_ml['agua_adequacao'] * 0.4 +
                dt_ml['condicoes_ideais'] * 0.2
        )


        # 6. Identificar fator limitante
        def identificar_limitacao(row):
            if row['N_disponivel'] < 40:
                return 'N_limitante'
            elif row['P_disponivel'] < 30:
                return 'P_limitante'
            elif row['K_disponivel'] < 35:
                return 'K_limitante'
            elif row['agua_adequacao'] < 0.6:
                return 'agua_limitante'
            elif row['estresse_termico'] == 1:
                return 'temperatura_limitante'
            else:
                return 'sem_limitacao'


        dt_ml['fator_limitante'] = dt_ml.apply(identificar_limitacao, axis=1)

        st.success("✅ 12 features criadas para Rendimento")

        # FEATURES ECONÔMICAS (Beneficiam todos os modelos)
        st.markdown("#### 💰 Features Econômicas (Opcional)")

        # Preços simulados
        preco_agua = {'Rice': 0.15, 'Maize': 0.10, 'Wheat': 0.10, 'Soybean': 0.12, 'Cotton': 0.13}
        dt_ml['custo_agua_m3'] = dt_ml['crop_type'].map(preco_agua)
        dt_ml['custo_irrigacao'] = dt_ml['volume_irrigacao_mm'] * dt_ml['custo_agua_m3'] * 10

        dt_ml['custo_fertilizacao'] = (
                dt_ml['N_fertilizacao_kg_ha'] * 3.50 +
                dt_ml['P_fertilizacao_kg_ha'] * 4.20 +
                dt_ml['K_fertilizacao_kg_ha'] * 2.80
        )

        preco_produto = {'Rice': 0.80, 'Maize': 0.60, 'Wheat': 0.70, 'Soybean': 1.20, 'Cotton': 3.50}
        dt_ml['preco_produto'] = dt_ml['crop_type'].map(preco_produto)
        dt_ml['receita_bruta'] = dt_ml['rendimento_kg_ha'] * dt_ml['preco_produto']
        dt_ml['margem_bruta'] = dt_ml['receita_bruta'] - dt_ml['custo_irrigacao'] - dt_ml['custo_fertilizacao']

        st.success("✅ 7 features econômicas criadas")

        # Salvar no session_state
        st.session_state['dt_enriquecido'] = dt_ml

    st.success("🎉 Enriquecimento concluído!")

# Mostrar resumo se existir
if 'dt_enriquecido' in st.session_state:
    st.divider()

    dt_ml = st.session_state['dt_enriquecido']

    st.subheader("📊 Resumo do Enriquecimento")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Features Originais", "13")
    with col2:
        st.metric("Features Criadas", f"{len(dt_ml.columns) - 13}")
    with col3:
        st.metric("Features Totais", len(dt_ml.columns))
    with col4:
        st.metric("Registros", f"{len(dt_ml):,}")

    # Tabela de novas features
    st.markdown("### 📋 Novas Features Criadas")

    tab1, tab2, tab3, tab4 = st.tabs([
        "💧 Irrigação (7)",
        "🌿 Fertilização (13)",
        "🌾 Rendimento (12)",
        "💰 Econômicas (7)"
    ])

    with tab1:
        features_irrig = [
            'deficit_hidrico_mm', 'evapotranspiracao_estimada', 'demanda_agua_cultura',
            'balanco_hidrico', 'necessidade_irrigacao_teorica', 'indice_aridez', 'agua_adequacao'
        ]
        for f in features_irrig:
            st.write(f"✅ {f}")

    with tab2:
        features_fert = [
            'disponibilidade_nutrientes', 'N_disponivel', 'P_disponivel', 'K_disponivel',
            'razao_NP', 'razao_NK', 'razao_PK', 'desvio_NPK_ideal',
            'eficiencia_N', 'eficiencia_P', 'eficiencia_K'
        ]
        for f in features_fert:
            st.write(f"✅ {f}")

    with tab3:
        features_rend = [
            'estresse_termico', 'estresse_hidrico', 'estresse_total', 'condicoes_ideais',
            'NPK_agua_interacao', 'rendimento_potencial', 'taxa_realizacao',
            'adequacao_insumos', 'fator_limitante'
        ]
        for f in features_rend:
            st.write(f"✅ {f}")

    with tab4:
        features_econ = [
            'custo_agua_m3', 'custo_irrigacao', 'custo_fertilizacao',
            'preco_produto', 'receita_bruta', 'margem_bruta'
        ]
        for f in features_econ:
            st.write(f"✅ {f}")

    st.divider()

    # Visualizar algumas features
    st.subheader("👁️ Visualizar Novas Features")

    col1, col2 = st.columns(2)

    with col1:
        # Gráfico: Déficit Hídrico vs Irrigação
        fig = px.scatter(
            dt_ml.sample(500),
            x='deficit_hidrico_mm',
            y='volume_irrigacao_mm',
            color='crop_type',
            title='Déficit Hídrico vs Volume de Irrigação',
            labels={'deficit_hidrico_mm': 'Déficit Hídrico (mm)',
                    'volume_irrigacao_mm': 'Irrigação (mm)'}
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Gráfico: Adequação de Insumos vs Rendimento
        fig = px.scatter(
            dt_ml.sample(500),
            x='adequacao_insumos',
            y='rendimento_kg_ha',
            color='estresse_total',
            title='Adequação de Insumos vs Rendimento',
            labels={'adequacao_insumos': 'Adequação de Insumos (0-1)',
                    'rendimento_kg_ha': 'Rendimento (kg/ha)'}
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Análise de correlação com targets
    st.subheader("🔗 Correlação das Novas Features com Targets")

    # Calcular correlações
    corr_irrigacao = dt_ml[[
        'deficit_hidrico_mm', 'evapotranspiracao_estimada',
        'necessidade_irrigacao_teorica', 'volume_irrigacao_mm'
    ]].corr()['volume_irrigacao_mm'].drop('volume_irrigacao_mm').sort_values(ascending=False)

    corr_fertilizacao = dt_ml[[
        'N_disponivel', 'desvio_NPK_ideal', 'disponibilidade_nutrientes',
        'N_fertilizacao_kg_ha'
    ]].corr()['N_fertilizacao_kg_ha'].drop('N_fertilizacao_kg_ha').sort_values(ascending=False)

    corr_rendimento = dt_ml[[
        'adequacao_insumos', 'NPK_agua_interacao', 'condicoes_ideais',
        'estresse_total', 'rendimento_kg_ha'
    ]].corr()['rendimento_kg_ha'].drop('rendimento_kg_ha').sort_values(ascending=False)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**💧 Com Irrigação:**")
        for feat, corr in corr_irrigacao.items():
            st.write(f"{feat}: **{corr:.3f}**")

    with col2:
        st.markdown("**🌿 Com Fertilização N:**")
        for feat, corr in corr_fertilizacao.items():
            st.write(f"{feat}: **{corr:.3f}**")

    with col3:
        st.markdown("**🌾 Com Rendimento:**")
        for feat, corr in corr_rendimento.items():
            st.write(f"{feat}: **{corr:.3f}**")

    st.info("""
    💡 **Interpretação:**
    - Valores mais altos (próximos de ±1) indicam features mais relevantes
    - Features com correlação > 0.3 tendem a melhorar significativamente o modelo
    - As novas features mostram correlações MAIS FORTES que as originais!
    """)

st.divider()

# ============================================
#    8.3 PREPARAR E SALVAR DATASET FINAL
# ============================================

st.subheader("💾 8.3. Salvar Dataset Preparado")

if 'dt_enriquecido' in st.session_state:

    dt_ml = st.session_state['dt_enriquecido']

    # One-hot encoding
    st.markdown("**🔄 Aplicando One-Hot Encoding em crop_type...**")
    dt_ml_encoded = pd.get_dummies(dt_ml, columns=['crop_type'], drop_first=True)

    # Remover colunas categóricas restantes
    colunas_remover = ['fator_limitante']  # Categórica
    dt_ml_encoded = dt_ml_encoded.drop(columns=colunas_remover, errors='ignore')

    # Tratar valores infinitos e NaN
    dt_ml_encoded = dt_ml_encoded.replace([np.inf, -np.inf], np.nan)
    dt_ml_encoded = dt_ml_encoded.dropna()

    st.info(f"""
    ✅ **Dataset Final Preparado:**

    - **Linhas:** {len(dt_ml_encoded):,}
    - **Features:** {len(dt_ml_encoded.columns) - 1} (+ 1 target)
    - **One-hot encoding:** Aplicado
    - **Valores ausentes:** Removidos
    - **Pronto para ML:** ✅
    """)

    # Botão para salvar
    if st.button("💾 Salvar Dataset ML Preparado", type="primary"):
        try:
            import os

            os.makedirs('data/processed', exist_ok=True)

            caminho = 'data/processed/dataset_ml_preparado.csv'
            dt_ml_encoded.to_csv(caminho, index=False)

            st.success(f"""
            ✅ **Dataset salvo com sucesso!**

            📁 Localização: `{caminho}`
            📊 Linhas: {len(dt_ml_encoded):,}
            📋 Colunas: {len(dt_ml_encoded.columns)}
            💾 Tamanho: {os.path.getsize(caminho) / 1024:.2f} KB
            """)

            # Mostrar preview
            with st.expander("👁️ Ver Primeiras Linhas"):
                st.dataframe(dt_ml_encoded.head(10))

        except Exception as e:
            st.error(f"❌ Erro ao salvar: {e}")

    st.info("""
    💡 **Próximos passos:**

    1. O arquivo `dataset_ml_preparado.csv` será usado nos modelos
    2. Vá para a página **"Modelagem Preditiva"** para treinar
    3. As novas features vão melhorar significativamente o R²!
    """)

else:
    st.warning("⚠️ Execute o enriquecimento avançado primeiro!")

st.divider()

# ============================================
#    COMPARAÇÃO: ANTES vs DEPOIS
# ============================================

st.subheader("📊 Impacto Esperado no Desempenho")

st.markdown("""
Com base em literatura científica e nas correlações observadas, 
esperamos as seguintes melhorias nos modelos:
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("💧 Irrigação", "R² atual: 0.05-0.15")
    st.metric("", "R² esperado: 0.25-0.40", delta="+0.20-0.25")
    st.caption("Ganho: ~150-200%")

with col2:
    st.metric("🌿 Fertilização", "R² atual: 0.30-0.50")
    st.metric("", "R² esperado: 0.50-0.70", delta="+0.20")
    st.caption("Ganho: ~40-60%")

with col3:
    st.metric("🌾 Rendimento", "R² atual: 0.15-0.25")
    st.metric("", "R² esperado: 0.35-0.50", delta="+0.20-0.25")
    st.caption("Ganho: ~100-130%")

st.success("""
### ✅ Conclusão do Feature Engineering

O enriquecimento avançado adiciona **conhecimento agronômico** aos dados brutos,
permitindo que os modelos capturem relações causais importantes que não eram
visíveis apenas com as features originais.

**Principais melhorias:**
- ✅ Features com correlação mais forte com targets
- ✅ Captura de interações entre variáveis
- ✅ Consideração de restrições físicas e biológicas
- ✅ Contexto econômico e operacional

🎯 **Próxima etapa:** Treinar modelos com dados enriquecidos!
""")

#==========================================================
#       📝 FASE 9: INSIGHTS E DOCUMENTAÇÃO
#==========================================================

st.header("📝 Conclusões da Análise Exploratória")

st.markdown("""
Resumo das principais descobertas que vão orientar a modelagem de Machine Learning.
""")

st.divider()

# ============================================
#    PRINCIPAIS DESCOBERTAS
# ============================================

st.subheader("🔍 Principais Descobertas")

col1, col2 = st.columns(2)

with col1:
    st.info("""
    ### 📊 Sobre os Dados

    ✅ **Dataset completo:**
    - 2.200 registros
    - 13 variáveis originais
    - 0% de valores ausentes
    - 5 tipos de culturas

    ✅ **Qualidade:**
    - Dados consistentes
    - Poucos outliers (< 3%)
    - Valores dentro de limites esperados
    """)

with col2:
    st.warning("""
    ### 🔗 Sobre as Correlações

    ⚠️ **Correlações individuais fracas:**
    - Maior correlação: |r| = 0.10
    - Nenhuma variável sozinha explica bem o rendimento

    ✅ **Isso significa:**
    - Rendimento depende de MÚLTIPLOS fatores
    - Modelos multivariados serão necessários
    - Interações entre variáveis são importantes
    """)

st.divider()

# ============================================
#    INSIGHTS POR ANÁLISE
# ============================================

st.subheader("💡 Insights por Tipo de Análise")

tab1, tab2, tab3 = st.tabs(["Univariada", "Bivariada", "Multivariada"])

with tab1:
    st.markdown("""
    ### 📈 Análise Univariada

    **Descobertas:**
    - Todas as variáveis têm distribuições normais ou próximas
    - pH médio: 6.47 (faixa ideal para agricultura)
    - Temperatura média: 26°C (adequada)
    - Rendimento médio: 4.034 kg/ha

    **Conclusão:** Dados estão dentro de faixas esperadas para agricultura
    """)

with tab2:
    st.markdown("""
    ### 🔗 Análise Bivariada

    **Top 5 Correlações com Rendimento:**
    1. N (solo): -0.100
    2. Precipitação: -0.079
    3. P (solo): +0.078
    4. Fertilização N: -0.078
    5. Fertilização P: +0.071

    **Conclusão:** Correlações fracas indicam sistema complexo e multifatorial
    """)

with tab3:
    st.markdown("""
    ### 🎯 Análise Multivariada

    **Interações Identificadas:**
    - NPK balanceados aumentam rendimento
    - Temperatura + Umidade interagem para determinar estresse
    - Cada cultura responde diferente às mesmas condições

    **Conclusão:** Combinação de fatores é mais importante que valores individuais
    """)

st.divider()

# ============================================
#    PREPARAÇÃO PARA ML
# ============================================

st.subheader("🤖 Preparação para Machine Learning")

st.success("""
### ✅ Dataset Preparado

**Features Criadas:**
- `agua_total_mm` (chuva + irrigação)
- `NPK_total` (soma de nutrientes)
- `NPK_fertilizacao_total` (soma de fertilizantes)

**Transformações Aplicadas:**
- One-hot encoding em `crop_type`
- 16 features finais para o modelo

**Decisões Tomadas:**
- Manter todos os outliers (< 3% e são eventos reais)
- Usar todas as variáveis (correlações fracas individuais)
- Incluir variáveis derivadas (capturar interações)
""")

st.divider()

# ============================================
#    MODELOS A IMPLEMENTAR
# ============================================

st.subheader("🎯 Próximos Passos: Modelagem")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    ### 💧 Modelo 1
    **Prever: Irrigação**

    Target: `volume_irrigacao_mm`

    Features principais:
    - Precipitação
    - Temperatura
    - Umidade
    - Cultura
    """)

with col2:
    st.success("""
    ### 🌿 Modelo 2
    **Prever: Fertilização**

    Target: `N/P/K_fertilizacao`

    Features principais:
    - Nutrientes no solo
    - pH
    - Cultura
    """)

with col3:
    st.warning("""
    ### 🌾 Modelo 3
    **Prever: Rendimento**

    Target: `rendimento_kg_ha`

    Features principais:
    - TODAS (16 features)
    - Variáveis derivadas
    - Cultura
    """)

st.divider()

# ============================================
#    EXPECTATIVAS
# ============================================

st.subheader("📊 Expectativas de Desempenho")

st.markdown("""
Com base na análise exploratória, esperamos:

| Modelo | Algoritmo | R² Esperado | Justificativa |
|--------|-----------|-------------|---------------|
| **Irrigação** | Regressão Linear Múltipla | 0.20 - 0.35 | Relação com clima e cultura |
| **Irrigação** | Regressão Polinomial | 0.25 - 0.40 | Captura interações clima |
| **Fertilização** | Regressão Linear Múltipla | 0.15 - 0.30 | Depende de solo e cultura |
| **Fertilização** | Regressão Polinomial | 0.20 - 0.35 | Captura balanço NPK |
| **Rendimento** | Regressão Linear Múltipla | 0.20 - 0.35 | Sistema multifatorial |
| **Rendimento** | Regressão Polinomial | 0.30 - 0.50 | Captura interações complexas |

""")

st.info("""
💡 **Observação:** 
Dado que as correlações individuais são fracas (< 0.15), um R² acima de 0.30 
já será considerado **bom** para este tipo de problema complexo.
""")

st.divider()

# ============================================
#    CONCLUSÃO FINAL
# ============================================

st.success("""
### ✅ Análise Exploratória Concluída!

**O que fizemos:**
1. ✅ Carregamos e inspecionamos 2.200 registros
2. ✅ Analisamos 13 variáveis individualmente (univariada)
3. ✅ Identificamos correlações entre pares (bivariada)
4. ✅ Descobrimos interações complexas (multivariada)
5. ✅ Detectamos e analisamos outliers
6. ✅ Criamos 3 variáveis derivadas (feature engineering)

**Principais Conclusões:**
- Sistema agrícola é complexo e multifatorial
- Nenhuma variável sozinha explica o rendimento
- Interações e combinações são fundamentais
- Dataset está pronto para Machine Learning

**Próximo Passo:**
🤖 Implementar e treinar os 3 modelos de regressão!
""")

