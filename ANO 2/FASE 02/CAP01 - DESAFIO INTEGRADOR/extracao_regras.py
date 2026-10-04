"""
CardioIA - Extracao de Informacoes e Diagnostico Baseado em Regras (Parte 1)
Disciplina: IA no Estetoscopio Digital - Fase 2
Aluno: Giovani Saavedra (RM566797) e Marcio Elifas (RM567871)
"""

import csv
import os

# Carrega o mapa de conhecimento / ontologia
def carregar_ontologia(caminho_csv):
    regras = []
    with open(caminho_csv, mode="r", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            termos = [linha["sintoma"].strip().lower()]
            # Adiciona os sinonimos da coluna variacoes
            for var in linha["variacoes"].split(";"):
                if var.strip():
                    termos.append(var.strip().lower())
            
            regras.append({
                "sintoma_principal": linha["sintoma"],
                "termos": termos,
                "diagnostico": linha["diagnostico"],
                "protocolo": linha["protocolo"],
                "risco": linha["risco"]
            })
    return regras

# Processa cada frase de caso clinico
def analisar_casos(caminho_casos, regras):
    with open(caminho_casos, mode="r", encoding="utf-8") as f:
        linhas = f.readlines()

    print("=" * 70)
    print("RELATORIO DE TRIAGEM BASEADA EM REGRAS E ONTOLOGIA (PARTE 1)")
    print("=" * 70)

    for i, linha in enumerate(linhas, 1):
        texto = linha.strip()
        if not texto:
            continue
        
        texto_lower = texto.lower()
        sintomas_encontrados = []
        diagnostico_sugerido = "Acompanhamento preventivo"
        protocolo_sugerido = "Orientacao geral ambulatorial"
        risco_sugerido = "baixo risco"

        # Verifica regras ontologicas
        for regra in regras:
            for termo in regra["termos"]:
                if termo in texto_lower:
                    if termo not in sintomas_encontrados:
                        sintomas_encontrados.append(termo)
                    diagnostico_sugerido = regra["diagnostico"]
                    protocolo_sugerido = regra["protocolo"]
                    risco_sugerido = regra["risco"]

        print(f"\n[Caso {i}]")
        print(f"Relato: {texto}")
        print(f"Sintomas Detectados: {', '.join(sintomas_encontrados) if sintomas_encontrados else 'Nenhum identificado'}")
        print(f"Diagnostico Assistido: {diagnostico_sugerido}")
        print(f"Classificacao de Risco: {risco_sugerido.upper()}")
        print(f"Protocolo SBC Recomendado: {protocolo_sugerido}")
        print("-" * 70)

if __name__ == "__main__":
    diretorio_base = os.path.dirname(os.path.abspath(__file__))
    caminho_ontologia = os.path.join(diretorio_base, "dados", "ontologia_cardio.csv")
    caminho_casos = os.path.join(diretorio_base, "dados", "casos_clinicos.txt")

    regras = carregar_ontologia(caminho_ontologia)
    analisar_casos(caminho_casos, regras)
