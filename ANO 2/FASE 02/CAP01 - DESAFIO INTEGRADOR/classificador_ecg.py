"""
CardioIA - Diagnostico Visual em Cardiologia com Rede Neural MLP (Ir Alem 2)
Disciplina: IA no Estetoscopio Digital - Fase 2
Aluno: Giovani Saavedra (RM566797) e Marcio Elifas (RM567871)
Framework: Keras (com backend PyTorch)
"""

import os
os.environ["KERAS_BACKEND"] = "torch"

import glob
import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import keras
from keras import layers, models

TAMANHO_IMAGEM = (64, 64)

def carregar_imagens_ecg():
    """
    Carrega imagens de ECG em escala de cinza, redimensiona para 64x64
    e achata em um vetor de 4096 atributos.
    Classe 0 = Normal
    Classe 1 = Anormal (Infarto, Batimentos Anormais, Historico IM)
    """
    diretorio_base = os.path.dirname(os.path.abspath(__file__))
    caminho_local = os.path.join(diretorio_base, "dados", "ecg_amostras")
    
    # Caminho do Google Drive da Fase 1 se disponivel
    caminho_drive = os.path.expanduser(
        "~/Library/CloudStorage/GoogleDrive-ggiovani.saavedra@gmail.com/Meu Drive/fiap/trabalhos/02 - ANO 02/Fase01 - Batimentos de Dados/03_dados_visuais_ecg/cardioia_ecg_para_drive"
    )

    candidatos = [
        caminho_drive,
        caminho_local,
        "dados/ecg_amostras",
        os.path.join(os.getcwd(), "dados", "ecg_amostras"),
        os.path.join(os.getcwd(), "ANO 2/FASE 02/CAP01 - DESAFIO INTEGRADOR/dados/ecg_amostras"),
    ]
    caminho_dados = next((c for c in candidatos if os.path.exists(c) and len(glob.glob(os.path.join(c, "*", "*.jpg"))) > 0), caminho_local)
    print(f"[*] Carregando base de ECG de: {caminho_dados}")

    X = []
    y = []

    pasta_normal = os.path.join(caminho_dados, "normal")
    pastas_anormais = [
        os.path.join(caminho_dados, "infarto_miocardio"),
        os.path.join(caminho_dados, "batimentos_anormais"),
        os.path.join(caminho_dados, "historico_im")
    ]

    # Carrega exames normais (classe 0)
    if os.path.exists(pasta_normal):
        arquivos_normais = sorted(glob.glob(os.path.join(pasta_normal, "*.jpg")))[:30]
        for arq in arquivos_normais:
            img = Image.open(arq).convert("L").resize(TAMANHO_IMAGEM)
            X.append(np.array(img, dtype=np.float32).flatten())
            y.append(0)

    # Carrega exames anormais (classe 1) balanceados
    for pasta in pastas_anormais:
        if os.path.exists(pasta):
            arquivos_anormais = sorted(glob.glob(os.path.join(pasta, "*.jpg")))[:10]
            for arq in arquivos_anormais:
                img = Image.open(arq).convert("L").resize(TAMANHO_IMAGEM)
                X.append(np.array(img, dtype=np.float32).flatten())
                y.append(1)

    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)

def construir_mlp_keras(dim_entrada=4096):
    """
    Constroi rede neural Multi-Layer Perceptron usando Keras Sequential.
    """
    modelo = models.Sequential([
        layers.Input(shape=(dim_entrada,)),
        layers.Dense(64, activation="relu", name="camada_densa_1"),
        layers.Dropout(0.3, name="dropout_1"),
        layers.Dense(32, activation="relu", name="camada_densa_2"),
        layers.Dense(1, activation="sigmoid", name="camada_saida")
    ])

    modelo.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.0005),
        loss="binary_crossentropy",
        metrics=["accuracy"]
    )
    return modelo

def main():
    print("=" * 65)
    print("TREINAMENTO DE REDE NEURAL MLP COM KERAS PARA ECG (IR ALEM 2)")
    print("=" * 65)

    X, y = carregar_imagens_ecg()
    if len(X) == 0:
        print("[!] Nenhuma imagem de ECG encontrada para treinamento.")
        return

    print(f"\n[+] Total de imagens carregadas: {len(X)}")
    print(f"[+] Dimensoes de cada vetor de entrada: {X.shape[1]} pixels (64x64)")
    print(f"[+] Distribuicao balanceada: {int(np.sum(y == 0))} Normais | {int(np.sum(y == 1))} Anormais")

    # Divisao treino e teste estratificada (75% treino, 25% teste)
    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    # Padronizacao com StandardScaler
    print("\n[*] Aplicando padronizacao estatistica (StandardScaler)...")
    scaler = StandardScaler()
    X_treino_esc = scaler.fit_transform(X_treino)
    X_teste_esc = scaler.transform(X_teste)

    # Construcao da MLP com Keras
    print("\n[*] Construindo Perceptron Multicamadas (Keras)...")
    modelo = construir_mlp_keras(dim_entrada=X.shape[1])
    modelo.summary()

    # Treinamento da rede
    print("\n[*] Iniciando treinamento da rede neural Keras (30 epocas)...")
    historico = modelo.fit(
        X_treino_esc,
        y_treino,
        epochs=30,
        batch_size=8,
        validation_split=0.2,
        verbose=1
    )

    # Avaliacao no conjunto de teste
    print("\n" + "=" * 65)
    print("AVALIACAO DO MODELO KERAS NO CONJUNTO DE TESTE INDEPENDENTE")
    print("=" * 65)

    probabilidades = modelo.predict(X_teste_esc, verbose=0)
    predicoes = (probabilidades >= 0.5).astype(int).flatten()
    y_teste_int = y_teste.astype(int)

    acc = accuracy_score(y_teste_int, predicoes)
    print(f"\nAcuracia no Teste: {acc * 100:.2f}%")

    print("\nRelatorio de Classificacao:")
    print(classification_report(y_teste_int, predicoes, target_names=["Normal", "Anormal"], zero_division=0))

    print("Matriz de Confusao:")
    print(confusion_matrix(y_teste_int, predicoes))

if __name__ == "__main__":
    main()
