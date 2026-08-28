# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
  <a href="https://www.fiap.com.br/">
    <img src="../../../assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width="40%">
  </a>
</p>

<br>

# 🫀 CardioIA — Fase 1: Batimentos de Dados
## A Busca de Dados — Coleta e Governança de Dados Cardiológicos

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![UCI Dataset](https://img.shields.io/badge/dataset-UCI%20Heart%20Disease-red)](https://archive.ics.uci.edu/dataset/45/heart+disease)
[![SciELO](https://img.shields.io/badge/textos-SciELO-orange)](https://www.scielo.br/)
[![Mendeley Data](https://img.shields.io/badge/imagens-Mendeley%20Data%20ECG-9cf)](https://data.mendeley.com/datasets/gwbz3fsgp8/2)

---

## 👥 Equipe do Projeto

### 👨‍🎓 Integrantes

| Nome              | RM       |
|-------------------|----------|
| Giovani Saavedra  | RM566797 |
| Marcio Elifas     | RM567871 |

### 👩‍🏫 Orientação

**Tutor(a):** Leonardo Ruiz Orabona / Sabrina Otoni   
**Coordenador(a):** André Godoi Chiovatto 

---

## 📋 Sumário

1. [Visão Geral — Fase 1](#-visão-geral--fase-1)
2. [Parte 1 — Dados Numéricos (IoT)](#-parte-1--dados-numéricos-iot)
3. [Parte 2 — Dados Textuais (NLP)](#-parte-2--dados-textuais-nlp)
4. [Parte 3 — Dados Visuais (Visão Computacional)](#%EF%B8%8F-parte-3--dados-visuais-visão-computacional)
5. [Governança de Dados e Viés](#%EF%B8%8F-governança-de-dados-e-viés)
6. [Links dos Dados (Google Drive)](#-links-dos-dados-google-drive)
7. [Como Executar](#%EF%B8%8F-como-executar)
8. [Estrutura de Pastas](#-estrutura-de-pastas)
9. [Histórico de Lançamentos](#-histórico-de-lançamentos)
10. [Licença](#-licença)
11. [Referências](#-referências)

---

## 🩺 Visão Geral — Fase 1

O **CardioIA** é um projeto acadêmico que simula o ecossistema de uma cardiologia moderna, integrando dados clínicos, Machine Learning, Visão Computacional, IoT e agentes inteligentes para triagem, diagnóstico, monitoramento e assistência remota.

Nesta **Fase 1 — Batimentos de Dados**, atuamos como cientistas de dados hospitalares para levantar, organizar e documentar os três tipos de dados que alimentarão os módulos inteligentes das próximas fases: **dados numéricos** (sinais vitais e atributos clínicos para modelos preditivos), **dados textuais** (artigos científicos para NLP) e **dados visuais** (imagens de ECG para Visão Computacional).

> Cada conjunto de dados foi selecionado por sua relevância clínica, procedência verificável e licença de uso aberto — princípios de governança que acompanham o projeto desde a origem dos dados.

---

## 📊 Parte 1 — Dados Numéricos (IoT)

**Origem:** dataset **Heart Disease (Cleveland) — UCI Machine Learning Repository**, dados **reais e anonimizados** de **303 pacientes** com **14 atributos clínicos**, licença CC BY 4.0.
Fonte: https://archive.ics.uci.edu/dataset/45/heart+disease

O arquivo versionado neste repositório é [`data/heart_disease_cleveland.csv`](data/heart_disease_cleveland.csv) (303 linhas + cabeçalho), e o dicionário de dados completo está em [`docs/dicionario_dados.md`](docs/dicionario_dados.md).

**Variáveis mais relevantes do ponto de vista clínico:**

| Variável | Descrição | Relevância clínica para IA |
|----------|-----------|----------------------------|
| `age` | Idade | O risco cardiovascular cresce com a idade; essencial para estratificação de risco. |
| `sex` | Sexo biológico | Prevalências e manifestações distintas entre sexos; exige atenção a viés. |
| `cp` | Tipo de dor torácica | Angina típica é forte preditor de doença coronariana; central na triagem. |
| `trestbps` | Pressão arterial em repouso | Hipertensão é fator de risco modificável para infarto e AVC. |
| `chol` | Colesterol sérico | Dislipidemia associada à aterosclerose; clássica em escores de risco. |
| `thalach` | Frequência cardíaca máxima | Baixa capacidade cronotrópica indica comprometimento; útil para IoT. |
| `exang` | Angina por exercício | Indicador funcional de isquemia; alto valor discriminativo. |
| `oldpeak` | Depressão do segmento ST | Alteração objetiva de ECG associada a isquemia. |
| `num` | Diagnóstico (alvo) | Variável-alvo para modelos supervisionados de classificação de risco. |

Essas variáveis combinam fatores demográficos, sintomas, exames laboratoriais e achados funcionais — o dado multimodal que um sistema de triagem inteligente precisa para estimar risco e apoiar decisões clínicas.

---

## 📄 Parte 2 — Dados Textuais (NLP)

**Textos selecionados (SciELO, em português)**, salvos em [`docs/textos/`](docs/textos/) com cabeçalho de metadados (título, autores, periódico, DOI, licença e data de acesso):

1. [`texto01_prevencao_dcv.txt`](docs/textos/texto01_prevencao_dcv.txt) — *Prevenção de doenças cardiovasculares e promoção da saúde* (Achutti, A. — Ciência & Saúde Coletiva, 2012 — CC BY-NC 4.0)
2. [`texto02_fatores_risco_dcv_idosos.txt`](docs/textos/texto02_fatores_risco_dcv_idosos.txt) — *Análise da prevalência de doenças cardiovasculares e fatores associados em idosos, 2000-2010* (Massa, K.H.C.; Duarte, Y.A.O.; Chiavegatto Filho, A.D.P. — Ciência & Saúde Coletiva, 2019 — CC BY)

**Exploração por NLP:**

- **Extração de entidades e sintomas (NER):** identificar doenças, sintomas e medicamentos, criando vocabulários clínicos para a triagem do CardioIA;
- **Classificação de tópicos:** organizar bases de conhecimento médico para agentes de assistência remota;
- **Análise de sentimentos:** avaliar percepção sobre tratamentos e políticas de saúde;
- **Sumarização automática:** condensar artigos científicos para pacientes e equipes clínicas.

**Relevância:** grande parte da informação médica está em texto não estruturado (prontuários, laudos, artigos); NLP transforma esse conhecimento em dados estruturados e acionáveis.

---

## 🖼️ Parte 3 — Dados Visuais (Visão Computacional)

**Origem:** **ECG Images Dataset of Cardiac Patients** (Ch. Pervaiz Elahi Institute of Cardiology, Multan), imagens **reais e anonimizadas** de ECGs de 12 derivações, categorizadas em quatro classes: **normal**, **infarto do miocárdio**, **batimentos anormais** e **histórico de IM**. Foi selecionada uma amostra **balanceada de ~120 imagens**, mantendo proporção entre classes, com proveniência documentada em `manifest.csv`.
Fonte: https://data.mendeley.com/datasets/gwbz3fsgp8/2 (Mendeley Data, V2 — DOI: 10.17632/gwbz3fsgp8.2, licença CC BY 4.0)

Uma amostra reduzida (2 imagens por classe) está versionada em [`assets/ecg_amostras/`](assets/ecg_amostras/); o conjunto completo de ~120 imagens está no Google Drive (link abaixo).

**Exploração por Visão Computacional:**

- **Classificação por CNNs:** distinguir ECGs normais de patológicos (infarto, arritmias);
- **Segmentação e detecção de bordas:** isolar o traçado do fundo quadriculado e medir intervalos (PR, QRS, QT) automaticamente;
- **Reconhecimento de anomalias:** sinalizar traçados atípicos para revisão prioritária — triagem automatizada.

**Relevância:** a análise automatizada de exames reduz tempo de laudo, amplia acesso ao diagnóstico onde faltam especialistas e padroniza a triagem.

---

## 🛡️ Governança de Dados e Viés

- **Privacidade:** dados públicos e anonimizados, alinhados aos princípios da LGPD;
- **Licenciamento:** fontes citadas com suas licenças (UCI — CC BY 4.0; SciELO — CC BY e CC BY-NC 4.0, registradas no cabeçalho de cada texto);
- **Viés amostral:** o dataset de Cleveland tem predominância masculina e origem geográfica única; a limitação está registrada para tratamento nas próximas fases (rebalanceamento, avaliação por subgrupo);
- **Proveniência:** origem, formato e transformações documentados desde a Fase 1 (dicionário de dados, cabeçalhos de metadados nos textos e `manifest.csv` das imagens).

---

## 🔗 Links dos Dados (Google Drive)

| Conjunto | Link |
|----------|------|
| 📊 Dataset numérico completo (CSV + dicionário de dados) | https://drive.google.com/drive/folders/18VHAzQ-RwwbE6o2IIM5L9ZDBybPm-YL3 |
| 📄 Corpus textual (2 artigos SciELO em .txt) | https://drive.google.com/drive/folders/1_zQnhz3SLcKLgKmDt1ZOimdvA_wUNfVo |
| 🖼️ Conjunto completo de imagens de ECG (~120, por classe) | https://drive.google.com/drive/folders/1T_0kY2fgTle-TfF1yDcuyDr055b9HexS |
| 📁 Pasta-raiz de todos os dados do projeto | https://drive.google.com/drive/folders/1Y2xisyVNfjm_z1qvOi_nCteqWEZe2i-P |

---

## ⚙️ Como Executar

Esta fase é de coleta e documentação de dados; não há aplicação executável. O dataset numérico pode ser reproduzido com o script versionado em [`src/coleta_dados_uci.py`](src/coleta_dados_uci.py):

```bash
pip install ucimlrepo pandas
python src/coleta_dados_uci.py
```

O script baixa o dataset Heart Disease (id=45) do UCI Machine Learning Repository, aplica os cabeçalhos das 14 variáveis e grava `data/heart_disease_cleveland.csv`.

---

## 📁 Estrutura de Pastas

```
CAP01 - A BUSCA DE DADOS/
├── README.md                            # Este arquivo
├── .gitignore
│
├── assets/                              # Imagens usadas no projeto
│   └── ecg_amostras/                    # Amostra de ECGs (2 por classe)
│       ├── normal/
│       ├── infarto_miocardio/
│       ├── batimentos_anormais/
│       └── historico_im/
│
├── data/                                # Dados coletados
│   └── heart_disease_cleveland.csv      # Dataset numérico UCI (303 linhas)
│
├── docs/                                # Documentação de apoio e corpus textual
│   ├── dicionario_dados.md              # Dicionário de dados do CSV
│   └── textos/                          # Corpus textual para NLP
│       ├── texto01_prevencao_dcv.txt
│       └── texto02_fatores_risco_dcv_idosos.txt
│
└── src/                                 # Scripts de coleta
    └── coleta_dados_uci.py              # Reprodução do download UCI
```

---

## 🗃 Histórico de Lançamentos

### 🚀 v1.0.0 — 27/08/2026 — Fase 1
- 📊 Dados numéricos: dataset Heart Disease (Cleveland/UCI) convertido para CSV com cabeçalhos (303 registros, 14 variáveis) e dicionário de dados.
- 📄 Dados textuais: 2 artigos da SciELO em `.txt` (UTF-8) com cabeçalho de metadados, fonte, DOI e licença.
- 🖼️ Dados visuais: amostra balanceada de ~120 imagens de ECG (4 classes) com `manifest.csv` de proveniência; 8 amostras versionadas no repositório.
- 🛡️ Governança: licenças verificadas, viés amostral documentado e links do Google Drive publicados.

---

## 📋 Licença

<div align="center">

🫀 CardioIA — Batimentos de Dados foi desenvolvido por Giovani Agostini Saavedra e Márcio Elifas e está licenciado sob Attribution 4.0 International (CC BY 4.0).

Desenvolvido como projeto acadêmico para FIAP - Faculdade de Informática e Administração Paulista.

Turma: 1TIAOS
Disciplina: Fase 1 - Cap 1 - CardioIA: A Busca de Dados
Ano: 2026.2

</div>

---

**Projeto desenvolvido para FIAP — Ano 2, Fase 1 (2026.2)**  
**Tema:** Coleta e Governança de Dados para IA em Cardiologia  
**Equipe:** Giovani Saavedra (RM566797) e Marcio Elifas (RM567871).

---

## 📚 Referências

- Janosi, A., Steinbrunn, W., Pfisterer, M., & Detrano, R. (1989). *Heart Disease* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C52P4X
- Achutti, A. (2012). Prevenção de doenças cardiovasculares e promoção da saúde. *Ciência & Saúde Coletiva*, 17(1), 18-20. https://doi.org/10.1590/S1413-81232012000100003
- Massa, K. H. C., Duarte, Y. A. O., & Chiavegatto Filho, A. D. P. (2019). Análise da prevalência de doenças cardiovasculares e fatores associados em idosos, 2000-2010. *Ciência & Saúde Coletiva*, 24(1), 105-114. https://doi.org/10.1590/1413-81232018241.02072017
- Khan, A. H., et al. *ECG Images dataset of Cardiac Patients*. Mendeley Data, V2. https://data.mendeley.com/datasets/gwbz3fsgp8/2

---

**Última atualização:** Agosto 2026  
**Versão:** 1.0.0  
**Curso:** FIAP - Inteligência Artificial
