"""
CardioIA - Classificador Basico de Texto para Triagem Clinica (Parte 2)
Disciplina: IA no Estetoscopio Digital - Fase 2
Aluno: Giovani Saavedra (RM566797) e Marcio Elifas (RM567871)
"""

import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

def main():
    diretorio_base = os.path.dirname(os.path.abspath(__file__))
    caminho_dados = os.path.join(diretorio_base, "dados", "dataset_triagem.csv")

    print("=" * 60)
    print("TREINAMENTO E COMPARACAO DE MODELOS DE TRIAGEM (TF-IDF)")
    print("=" * 60)

    # 1. Carregamento dos dados
    print("\n[Passo 1] Carregando dataset rotulado...")
    df = pd.read_csv(caminho_dados)
    print(f"Total de relatos: {len(df)}")
    print(df["risco"].value_counts())

    X = df["relato"]
    y = df["risco"]

    # 2. Divisao entre treino e teste (75% treino, 25% teste)
    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    # 3. Vetorizacao com TF-IDF
    print("\n[Passo 2] Extraindo caracteristicas com TF-IDF...")
    vetorizador = TfidfVectorizer(ngram_range=(1, 2), lowercase=True)
    X_treino_vec = vetorizador.fit_transform(X_treino)
    X_teste_vec = vetorizador.transform(X_teste)
    print(f"Total de termos no vocabulario: {len(vetorizador.get_feature_names_out())}")

    # 4. Treinamento e comparacao dos modelos
    # Modelo A: Regressao Logistica
    print("\n" + "-" * 50)
    print("Treinando Modelo 1: Regressao Logistica")
    modelo_lr = LogisticRegression(random_state=42)
    modelo_lr.fit(X_treino_vec, y_treino)
    pred_lr = modelo_lr.predict(X_teste_vec)

    acc_lr = accuracy_score(y_teste, pred_lr)
    print(f"Acuracia no Teste: {acc_lr * 100:.2f}%")
    print(classification_report(y_teste, pred_lr))
    print("Matriz de Confusao:")
    print(confusion_matrix(y_teste, pred_lr))

    # Modelo B: Arvore de Decisao
    print("\n" + "-" * 50)
    print("Treinando Modelo 2: Arvore de Decisao")
    modelo_dt = DecisionTreeClassifier(random_state=42, max_depth=5)
    modelo_dt.fit(X_treino_vec, y_treino)
    pred_dt = modelo_dt.predict(X_teste_vec)

    acc_dt = accuracy_score(y_teste, pred_dt)
    print(f"Acuracia no Teste: {acc_dt * 100:.2f}%")
    print(classification_report(y_teste, pred_dt))
    print("Matriz de Confusao:")
    print(confusion_matrix(y_teste, pred_dt))

    # 5. Teste pratico em frases com diferentes niveis de gravidade
    print("\n" + "=" * 60)
    print("TESTE PRATICO EM FRASES NOVAS (PREDICAO EM TEMPO REAL)")
    print("=" * 60)
    
    frases_teste = [
        "Estou sentindo uma dor muito forte no meio do peito e falta de ar",
        "Tive apenas uma leve pontada muscular nas costas apos a academia",
        "Aperto insuportavel no torax com suor frio e sensacao de desmaio",
        "Desconforto nos ombros por ficar muito tempo sentado trabalhando"
    ]

    frases_vec = vetorizador.transform(frases_teste)
    predicoes = modelo_lr.predict(frases_vec)
    probabilidades = modelo_lr.predict_proba(frases_vec)

    for frase, pred, prob in zip(frases_teste, predicoes, probabilidades):
        conf = prob.max() * 100
        print(f"\nFrase: \"{frase}\"")
        print(f"--> Classificacao: {pred.upper()} (Confianca: {conf:.1f}%)")

if __name__ == "__main__":
    main()
