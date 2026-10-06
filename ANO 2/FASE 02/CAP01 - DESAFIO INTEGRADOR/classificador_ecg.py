"""
CardioIA - Diagnostico Visual em Cardiologia com Rede Neural MLP (Ir Alem 2)
Disciplina: IA no Estetoscopio Digital - Fase 2
Aluno: Giovani Saavedra (RM566797) e Marcio Elifas (RM567871)
"""

import os
import glob
import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, classification_report

TAMANHO_IMAGEM = (64, 64)

def carregar_imagens_ecg(diretorio_raiz):
    """
    Carrega imagens de ECG em escala de cinza, redimensiona para 64x64
    e achata em um vetor de 4096 posicoes (64x64).
    Classe 0 = Normal
    Classe 1 = Anormal (Infarto, Batimentos Anormais, Historico IM)
    """
    X = []
    y = []

    pasta_normal = os.path.join(diretorio_raiz, "normal")
    pastas_anormais = [
        os.path.join(diretorio_raiz, "infarto_miocardio"),
        os.path.join(diretorio_raiz, "batimentos_anormais"),
        os.path.join(diretorio_raiz, "historico_im")
    ]

    print(f"[*] Carregando imagens normais de: {pasta_normal}")
    if os.path.exists(pasta_normal):
        for arquivo in glob.glob(os.path.join(pasta_normal, "*.jpg")):
            img = Image.open(arquivo).convert("L").resize(TAMANHO_IMAGEM)
            vetor = np.array(img, dtype=np.float32).flatten() / 255.0
            X.append(vetor)
            y.append(0) # Normal

    print(f"[*] Carregando imagens anormais de {len(pastas_anormais)} categorias...")
    for pasta in pastas_anormais:
        if os.path.exists(pasta):
            for arquivo in glob.glob(os.path.join(pasta, "*.jpg")):
                img = Image.open(arquivo).convert("L").resize(TAMANHO_IMAGEM)
                vetor = np.array(img, dtype=np.float32).flatten() / 255.0
                X.append(vetor)
                y.append(1) # Anormal

    return np.array(X), np.array(y)

def main():
    print("=" * 60)
    print("TREINAMENTO DA REDE NEURAL MLP PARA ELETROCARDIOGRAMAS (ECG)")
    print("=" * 60)

    # Caminho do dataset curado na Fase 1
    caminho_padrao = os.path.expanduser(
        "~/Library/CloudStorage/GoogleDrive-ggiovani.saavedra@gmail.com/Meu Drive/fiap/trabalhos/02 - ANO 02/Fase01 - Batimentos de Dados/03_dados_visuais_ecg/cardioia_ecg_para_drive"
    )

    if not os.path.exists(caminho_padrao):
        # Fallback para pasta local se executado em outro diretorio
        caminho_padrao = os.path.join(os.path.dirname(__file__), "dados", "ecg")

    if not os.path.exists(caminho_padrao):
        print(f"[!] Diretorio de ECG nao encontrado em: {caminho_padrao}")
        return

    X, y = carregar_imagens_ecg(caminho_padrao)
    print(f"\n[+] Total de exames carregados: {len(X)}")
    print(f"[+] Dimensoes do vetor de entrada: {X.shape[1]} pixels (64x64)")
    print(f"[+] Classes: {np.sum(y == 0)} Normais | {np.sum(y == 1)} Anormais")

    # Divisao treino e teste estratificada
    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    # Arquitetura MLP: Camadas Ocultas (128, 64) com ativacao ReLU e otimizador Adam
    print("\n[*] Treinando Perceptron Multicamadas (MLP: 4096 -> 128 -> 64 -> 1)...")
    mlp = MLPClassifier(
        hidden_layer_sizes=(128, 64),
        activation="relu",
        solver="adam",
        max_iter=200,
        random_state=42
    )
    mlp.fit(X_treino, y_treino)

    # Avaliacao de metricas
    predicoes = mlp.predict(X_teste)
    acc = accuracy_score(y_teste, predicoes)
    prec = precision_score(y_teste, predicoes)
    rec = recall_score(y_teste, predicoes)

    print("\n" + "=" * 60)
    print("METRICAS DE AVALIACAO NO CONJUNTO DE TESTE (IR ALEM 2)")
    print("=" * 60)
    print(f"Acuracia Global:  {acc * 100:.2f}%")
    print(f"Precisao (Recall): {prec * 100:.2f}%")
    print(f"Sensibilidade:    {rec * 100:.2f}%")
    print("\nRelatorio Completo:")
    print(classification_report(y_teste, predicoes, target_names=["Normal", "Anormal"]))

if __name__ == "__main__":
    main()
