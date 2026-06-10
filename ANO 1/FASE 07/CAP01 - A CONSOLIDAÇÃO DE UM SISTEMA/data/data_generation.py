import pandas as pd
import numpy as np

# =============================================================================
# PASSO 1: CARREGAR DATASET KAGGLE
# =============================================================================

df_kaggle = pd.read_csv('raw/Smart_Farming_Crop_Yield_2024.csv')
print(f"✅ Dataset Kaggle carregado: {df_kaggle.shape}")
print(f"Colunas: {df_kaggle.columns.tolist()}\n")

# =============================================================================
# PASSO 2: CARREGAR DATASET PRODUTOS_AGRICOLAS (PARA ESTATÍSTICAS NPK)
# =============================================================================

df_seu = pd.read_csv('raw/produtos_agricolas.csv')
print(f"✅ Dataset produtos_agricolas carregado: {df_seu.shape}")

# Calcular estatísticas de NPK por cultura
npk_stats = df_seu.groupby('label')[['N', 'P', 'K']].agg(['mean', 'std']).round(2)
print(f"✅ Estatísticas NPK calculadas para {len(npk_stats)} culturas\n")
print(npk_stats.head())
print()

# =============================================================================
# PASSO 3: CRIAR DICIONÁRIO DE MAPEAMENTO DE CULTURAS
# =============================================================================

# Mapeamento: Culturas do Kaggle → Culturas do seu dataset
cultura_map = {
    'Wheat': 'rice',
    'Rice': 'rice',
    'Maize': 'maize',
    'Cotton': 'cotton',
    'Soybean': 'kidneybeans'  # Aproximação
}

print(f"✅ Mapeamento de culturas criado:")
for k, v in cultura_map.items():
    print(f"   {k} → {v}")
print()


# =============================================================================
# PASSO 4: GERAR NPK SINTÉTICO NAS 500 LINHAS ORIGINAIS
# =============================================================================

def gerar_npk(row, npk_stats, cultura_map):
    """
    Gera valores sintéticos de N, P, K baseados em estatísticas reais

    Args:
        row: Linha do DataFrame
        npk_stats: Estatísticas de NPK por cultura
        cultura_map: Dicionário de mapeamento de culturas

    Returns:
        pd.Series com N, P, K
    """
    # Mapear cultura do Kaggle para cultura de referência
    cultura_kaggle = row['crop_type']
    cultura_ref = cultura_map.get(cultura_kaggle, 'rice')  # Default: rice

    # Buscar estatísticas da cultura
    if cultura_ref in npk_stats.index:
        n_mean = npk_stats.loc[cultura_ref, ('N', 'mean')]
        n_std = npk_stats.loc[cultura_ref, ('N', 'std')]

        p_mean = npk_stats.loc[cultura_ref, ('P', 'mean')]
        p_std = npk_stats.loc[cultura_ref, ('P', 'std')]

        k_mean = npk_stats.loc[cultura_ref, ('K', 'mean')]
        k_std = npk_stats.loc[cultura_ref, ('K', 'std')]
    else:
        # Valores padrão se não encontrar
        n_mean, n_std = 80, 15
        p_mean, p_std = 50, 10
        k_mean, k_std = 45, 10

    # Gerar valores com distribuição normal
    N = max(0, np.random.normal(n_mean, n_std))
    P = max(0, np.random.normal(p_mean, p_std))
    K = max(0, np.random.normal(k_mean, k_std))

    return pd.Series({
        'N': round(N, 2),
        'P': round(P, 2),
        'K': round(K, 2)
    })


# Aplicar função para gerar NPK
np.random.seed(42)  # Para reprodutibilidade
df_kaggle[['N', 'P', 'K']] = df_kaggle.apply(
    lambda row: gerar_npk(row, npk_stats, cultura_map),
    axis=1
)

print(f"✅ NPK sintético gerado!")
print(f"Amostra dos dados:")
print(df_kaggle[['crop_type', 'N', 'P', 'K']].head())
print()


# =============================================================================
# PASSO 5: CRIAR VARIÁVEIS TARGET
# =============================================================================

# TARGET 1: Volume de Irrigação
def calcular_volume_irrigacao(row):
    """
    Calcula volume de irrigação baseado no tipo e umidade do solo
    """
    umidade = row['soil_moisture_%']

    if row['irrigation_type'] == 'Drip':
        return round(umidade * 8, 2)
    elif row['irrigation_type'] == 'Sprinkler':
        return round(umidade * 12, 2)
    elif row['irrigation_type'] == 'Manual':
        return round(umidade * 10, 2)
    else:  # None
        return round(umidade * 5, 2)


df_kaggle['volume_irrigacao_mm'] = df_kaggle.apply(calcular_volume_irrigacao, axis=1)


# TARGET 2: Necessidade de Fertilização (NPK)
def calcular_fertilizacao(row):
    """
    Calcula necessidade de fertilização baseada no tipo de fertilizante
    """
    if row['fertilizer_type'] == 'Inorganic':
        fator = 0.30  # Precisa mais NPK
    elif row['fertilizer_type'] == 'Organic':
        fator = 0.15  # Precisa menos NPK
    else:  # Mixed
        fator = 0.20  # Intermediário

    return pd.Series({
        'N_fertilizacao_kg_ha': round(row['N'] * fator, 2),
        'P_fertilizacao_kg_ha': round(row['P'] * fator, 2),
        'K_fertilizacao_kg_ha': round(row['K'] * fator, 2)
    })


df_kaggle[['N_fertilizacao_kg_ha', 'P_fertilizacao_kg_ha', 'K_fertilizacao_kg_ha']] = \
    df_kaggle.apply(calcular_fertilizacao, axis=1)

# TARGET 3: Rendimento (já existe, apenas renomear)
df_kaggle['rendimento_kg_ha'] = df_kaggle['yield_kg_per_hectare']

print(f"✅ Variáveis target criadas!")
print(f"Targets disponíveis: volume_irrigacao_mm, N/P/K_fertilizacao_kg_ha, rendimento_kg_ha")
print()


# =============================================================================
# PASSO 6: GERAR 1700 REGISTROS SINTÉTICOS ADICIONAIS
# =============================================================================

def gerar_registros_sinteticos(df_original, n_novos=1700):
    """
    Gera registros sintéticos baseados nos dados originais
    Adiciona variação de ±15% nas variáveis numéricas
    Preserva variáveis categóricas

    Args:
        df_original: DataFrame com dados originais
        n_novos: Número de novos registros a gerar

    Returns:
        DataFrame com registros sintéticos
    """
    registros_sinteticos = []

    # Colunas numéricas e categóricas
    colunas_numericas = df_original.select_dtypes(include=[np.number]).columns
    colunas_categoricas = df_original.select_dtypes(exclude=[np.number]).columns

    for i in range(n_novos):
        # Escolher registro base aleatório
        idx_base = np.random.randint(0, len(df_original))
        base = df_original.iloc[idx_base]

        novo_registro = {}

        # Adicionar variação nas numéricas (±15%)
        for col in colunas_numericas:
            valor_base = base[col]
            variacao = np.random.uniform(-0.15, 0.15)
            novo_valor = valor_base * (1 + variacao)

            # Garantir valores não negativos para variáveis que não podem ser negativas
            if col in ['N', 'P', 'K', 'soil_moisture_%', 'temperature_C',
                       'rainfall_mm', 'humidity_%', 'yield_kg_per_hectare',
                       'volume_irrigacao_mm', 'N_fertilizacao_kg_ha',
                       'P_fertilizacao_kg_ha', 'K_fertilizacao_kg_ha',
                       'rendimento_kg_ha']:
                novo_valor = max(0, novo_valor)

            # Garantir pH entre 3.5 e 9.0
            if col == 'soil_pH':
                novo_valor = np.clip(novo_valor, 3.5, 9.0)

            novo_registro[col] = round(novo_valor, 2)

        # Manter variáveis categóricas iguais
        for col in colunas_categoricas:
            novo_registro[col] = base[col]

        registros_sinteticos.append(novo_registro)

    return pd.DataFrame(registros_sinteticos)


# Gerar registros sintéticos
print(f"🔄 Gerando {1700} registros sintéticos...")
df_sintetico = gerar_registros_sinteticos(df_kaggle, n_novos=1700)

# Combinar dados originais + sintéticos
df_completo = pd.concat([df_kaggle, df_sintetico], ignore_index=True)

print(f"✅ Registros sintéticos gerados!")
print(f"Total de registros: {len(df_completo)} (500 originais + 1700 sintéticos)")
print()

# =============================================================================
# SALVAR DATASET FINAL
# =============================================================================

# Selecionar apenas colunas relevantes
colunas_finais = [
    # Features (inputs)
    'N', 'P', 'K',
    'soil_pH',
    'temperature_C',
    'humidity_%',
    'rainfall_mm',
    'crop_type',

    # Targets (outputs)
    'volume_irrigacao_mm',
    'N_fertilizacao_kg_ha',
    'P_fertilizacao_kg_ha',
    'K_fertilizacao_kg_ha',
    'rendimento_kg_ha'
]

df_final = df_completo[colunas_finais].copy()

# Salvar
df_final.to_csv('dataset_final_farmtech.csv', index=False)

print(f"✅ Dataset final salvo: dataset_final_farmtech.csv")
print(f"\n📊 RESUMO FINAL:")
print(f"   - Total de registros: {len(df_final)}")
print(f"   - Total de colunas: {len(df_final.columns)}")
print(f"   - Features (X): {len(df_final.columns) - 5}")
print(f"   - Targets (y): 5")
print(f"\n📋 PRIMEIRAS LINHAS:")
print(df_final.head())
print(f"\n📈 ESTATÍSTICAS:")
print(df_final.describe())
print(f"\n✅ PRONTO PARA MODELAGEM!")