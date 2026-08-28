"""
CardioIA — Fase 1: Batimentos de Dados
Script de coleta do dataset numérico (Parte 1).

Baixa o dataset Heart Disease (Cleveland) do UCI Machine Learning Repository
(id=45), aplica os cabeçalhos das 14 variáveis e grava o CSV em
data/heart_disease_cleveland.csv.

Uso:
    pip install ucimlrepo pandas
    python src/coleta_dados_uci.py
"""

from pathlib import Path

import pandas as pd
from ucimlrepo import fetch_ucirepo

COLUNAS = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal", "num",
]

SAIDA = Path(__file__).resolve().parent.parent / "data" / "heart_disease_cleveland.csv"


def main() -> None:
    print("Baixando Heart Disease (Cleveland) — UCI id=45...")
    heart = fetch_ucirepo(id=45)

    df = pd.concat([heart.data.features, heart.data.targets], axis=1)
    df.columns = COLUNAS

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SAIDA, index=False)

    print(f"OK: {len(df)} linhas x {len(df.columns)} colunas gravadas em {SAIDA}")
    print(df.head().to_string())
    print(df.describe().round(2).to_string())


if __name__ == "__main__":
    main()
