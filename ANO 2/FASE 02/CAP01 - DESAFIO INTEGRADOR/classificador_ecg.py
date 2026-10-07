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
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import keras
from keras import layers, models

TAMANHO_IMAGEM = (64, 64)

def carregar_dados_ecg():
    """
    Carrega imagens de ECG em escala de cinza, redimensiona para 64x64,
    normaliza a intensidade dos pixels (escala 0 a 1) e achata em um vetor de 4096 atributos.
    Classe 0 = Normal
    Classe 1 = Anormal (Infarto, Batimentos Anormais, Historico IM)
    """
    candidatos = [
        "dados/ecg_amostras",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados", "ecg_amostras"),
        os.path.join(os.getcwd(), "dados", "ecg_amostras")
    ]
    caminho = next((c for c in candidatos if os.path.exists(c) and len(glob.glob(os.path.join(c, "*", "*.jpg"))) > 0), "dados/ecg_amostras")
    print(f"[*] Carregando base de ECG de: {caminho}")

    X = []
    y = []

    pasta_normal = os.path.join(caminho, "normal")
    pastas_anormais = [
        os.path.join(caminho, "infarto_miocardio"),
        os.path.join(caminho, "batimentos_anormais"),
        os.path.join(caminho, "historico_im")
    ]

    # Carrega exames normais (classe 0)
    for arq in sorted(glob.glob(os.path.join(pasta_normal, "*.jpg"))):
        img = Image.open(arq).convert("L").resize(TAMANHO_IMAGEM)
        X.append(np.array(img, dtype=np.float32).flatten() / 255.0)
        y.append(0)

    # Carrega exames anormais (classe 1)
    for p in pastas_anormais:
        for arq in sorted(glob.glob(os.path.join(p, "*.jpg"))):
            img = Image.open(arq).convert("L").resize(TAMANHO_IMAGEM)
            X.append(np.array(img, dtype=np.float32).flatten() / 255.0)
            y.append(1)

    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)

def construir_mlp_keras(dim_entrada=4096):
    """
    Constroi rede neural Multi-Layer Perceptron usando Keras Sequential.
    """
    modelo = models.Sequential([
        layers.Input(shape=(dim_entrada,)),
        layers.Dense(128, activation="relu", name="camada_densa_1"),
        layers.Dropout(0.2, name="dropout_1"),
        layers.Dense(64, activation="relu", name="camada_densa_2"),
        layers.Dropout(0.2, name="dropout_2"),
        layers.Dense(1, activation="sigmoid", name="camada_saida")
    ], name="sequential_ecg_mlp")

    modelo.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy"]
    )
    return modelo

def main():
    print("=" * 65)
    print("TREINAMENTO DE REDE NEURAL MLP COM KERAS PARA ECG (IR ALEM 2)")
    print("=" * 65)

    X, y = carregar_dados_ecg()
    if len(X) == 0:
        print("[!] Nenhuma imagem de ECG encontrada para treinamento.")
        return

    print(f"\n[+] Total de imagens processadas: {len(X)}")
    print(f"[+] Dimensoes do vetor de entrada: {X.shape[1]} atributos por exame (64x64)")
    print(f"[+] Distribuicao: {int(np.sum(y == 0))} Normais | {int(np.sum(y == 1))} Anormais")

    # Divisao treino e teste estratificada (75% treino, 25% teste)
    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    print(f"\n[+] Exames para Treinamento: {len(X_treino)}")
    print(f"[+] Exames para Teste:       {len(X_teste)}")

    # Construcao da MLP com Keras
    print("\n[*] Construindo Perceptron Multicamadas (Keras)...")
    modelo = construir_mlp_keras(dim_entrada=X.shape[1])
    modelo.summary()

    # Treinamento da rede
    print("\n[*] Iniciando treinamento da rede neural Keras (30 epocas)...")
    historico = modelo.fit(
        X_treino,
        y_treino,
        epochs=30,
        batch_size=16,
        validation_split=0.2,
        verbose=1
    )

    # Avaliacao no conjunto de teste
    print("\n" + "=" * 65)
    print("AVALIACAO DO MODELO KERAS NO CONJUNTO DE TESTE INDEPENDENTE")
    print("=" * 65)

    perda, acuracia = modelo.evaluate(X_teste, y_teste, verbose=0)
    print(f"\nAcuracia Global no Teste: {acuracia * 100:.2f}%")
    print(f"Loss no Teste:            {perda:.4f}\n")

    probabilidades = modelo.predict(X_teste, verbose=0)
    predicoes = (probabilidades >= 0.5).astype(int).flatten()
    y_teste_int = y_teste.astype(int)

    print("Relatorio de Classificacao Detalhado:")
    print(classification_report(y_teste_int, predicoes, target_names=["Normal", "Anormal"], zero_division=0))

    print("Matriz de Confusao:")
    print(confusion_matrix(y_teste_int, predicoes))

if __name__ == "__main__":
    main()
