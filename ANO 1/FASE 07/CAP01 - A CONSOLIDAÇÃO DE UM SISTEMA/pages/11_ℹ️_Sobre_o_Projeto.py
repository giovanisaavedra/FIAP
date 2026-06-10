"""
FarmTech Solutions - Sobre o Projeto (Fase 7)
Visão geral do sistema integrado de gestão agrícola — consolidação das
Fases 1 a 6 num único dashboard Streamlit com persistência SQLite,
serviços de ML, IoT, visão computacional e alertas em nuvem (AWS SNS).

Autores: Giovani Saavedra e Marcio Elifas
RM: RM566797 e RM567871
GRUPO 37
1TIAOS - FIAP

FIAP - Fase 7 - 2026
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================================
#         CONFIGURAÇÃO DA PÁGINA
# ==========================================================

st.set_page_config(
    page_title="Sobre - FarmTech",
    page_icon="ℹ️",
    layout="wide"
)

# CSS Customizado
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
    }
    .header-subtitle {
        color: #C8E6C9;
        font-size: 18px;
        margin: 10px 0 0 0;
    }
    .info-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2E7D32;
        margin: 15px 0;
    }
    .tech-badge {
        display: inline-block;
        background-color: #2E7D32;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        margin: 5px;
        font-size: 14px;
    }
    </style>

    <div class="header-container">
        <h1 class="header-title">🌾 FarmTech Solutions — Fase 7</h1>
        <p class="header-subtitle">Sistema Integrado de Gestão Agrícola Inteligente</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ℹ️ Navegação Rápida")
    st.markdown("""
    - [Visão Geral](#vis-o-geral)
    - [Arquitetura](#arquitetura-do-sistema)
    - [Funcionalidades](#funcionalidades)
    - [Tecnologias](#tecnologias)
    - [Equipe](#equipe-e-contexto)
    """)

    st.divider()

    st.markdown("### 📊 Status do Sistema")

    # Indicadores de fases integradas (Fase 7)
    fases = {
        "Fase 1 — Cálculos / Clima / R": True,
        "Fase 2 — Banco + CRUD + DER": True,
        "Fase 3 — IoT + Irrigação": True,
        "Fase 4 — ML / Previsões": True,
        "Fase 5 — AWS SNS": True,
        "Fase 6 — Visão YOLOv8": True,
    }
    for nome, ok in fases.items():
        st.caption(("✅ " if ok else "⏳ ") + nome)

    st.progress(sum(fases.values()) / len(fases))
    st.caption(f"{sum(fases.values())}/{len(fases)} fases integradas")

    st.divider()
    st.caption(f"Versão 3.0 (Fase 7) | {datetime.now().strftime('%Y')}")

# ==========================================================
#         VISÃO GERAL
# ==========================================================

st.title("ℹ️ Sobre o Projeto — Fase 7")
st.markdown("### Sistema Integrado de Gestão Agrícola (Fases 1 → 6 consolidadas)")

st.divider()

st.header("🎯 Visão Geral")

col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("""
    ### O Problema

    A agricultura moderna enfrenta desafios críticos de **eficiência e
    sustentabilidade**: uso excessivo de recursos hídricos, aplicação
    imprecisa de fertilizantes, falta de previsibilidade na produção e
    dificuldade de reagir rapidamente a anomalias (pragas, estresse
    térmico, pH desbalanceado).

    - **Desperdício de recursos**: água e fertilizantes aplicados sem precisão
    - **Custos elevados**: insumos representam 40-60% dos custos operacionais
    - **Impacto ambiental**: lixiviação de nutrientes, contaminação de aquíferos
    - **Falta de visibilidade**: decisões tomadas sem dados em tempo real

    ### A Solução — Fase 7

    A **Fase 7** consolida o trabalho das fases anteriores em um único
    sistema integrado. A partir de uma **Central de Comando Streamlit**
    o usuário aciona todos os serviços e acompanha o status operacional
    da fazenda inteligente:

    - 🚜 **Fase 1** — Cálculos agronômicos (área, insumos), consulta de
      clima na **API Open-Meteo** e análise estatística em **R**.
    - 🗄️ **Fase 2** — Banco relacional **SQLite** com CRUD completo e
      diagrama Entidade-Relacionamento.
    - 📡 **Fase 3** — Simulador IoT (ESP32/Wokwi) gravando leituras em
      tempo real e lógica de **irrigação automatizada** com histerese.
    - 🤖 **Fase 4** — Modelos de **Machine Learning** (regressão para
      irrigação, fertilização e rendimento) com EDA e pipeline.
    - 🔔 **Fase 5** — Alertas em nuvem via **AWS SNS** disparados pelas
      regras de negócio sobre o banco.
    - 📷 **Fase 6** — **Visão Computacional** com YOLOv8 para detecção
      de intrusos/pragas na lavoura.
    """)

with col2:
    st.markdown("""
    <div class="info-card">
        <h3>📊 Números do Projeto</h3>
        <p><strong>6</strong> fases integradas</p>
        <p><strong>11</strong> páginas Streamlit</p>
        <p><strong>5</strong> módulos em <code>services/</code></p>
        <p><strong>7</strong> tabelas SQLite (com migrations)</p>
        <p><strong>3</strong> modelos de ML (regressão)</p>
        <p><strong>1</strong> modelo YOLOv8 (visão)</p>
        <p><strong>1</strong> tópico AWS SNS</p>
        <hr>
        <h3>🎯 Entregáveis</h3>
        <p>✅ Central de Comando única</p>
        <p>✅ Pipeline IoT → DB → ML → SNS</p>
        <p>✅ Diagnóstico agrícola por visão</p>
        <p>✅ Alertas com ação corretiva</p>
        <p>✅ Documentação completa (README + roteiro)</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ==========================================================
#         ARQUITETURA
# ==========================================================

st.header("🗃️ Arquitetura do Sistema")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 📥 Camada de Aquisição

    **Entrada:**
    - Sensores IoT (ESP32 / Wokwi)
    - `iot_simulator.py` (subprocess)
    - Imagens em `assets/images/`
    - API Open-Meteo (clima)
    - Inputs do usuário

    **Persistência:**
    - SQLite (`farmtech_iot.db`)
    - 7 tabelas com migrations
    - `database_manager.py`
    """)

with col2:
    st.markdown("""
    ### ⚙️ Camada de Serviços

    **`services/` — Fases 1, 3, 5, 6:**
    - `fase1_calculos` / `fase1_clima`
    - `fase1_analise.R` (estatística)
    - `fase3_irrigacao` (`ControladorIrrigacao`)
    - `fase6_vision` (YOLOv8)
    - `alert_service` (AWS SNS)

    **Modelos ML (Fase 4):**
    - Regressão Linear Múltipla
    - Regressão Polinomial
    - Scikit-Learn pipeline
    """)

with col3:
    st.markdown("""
    ### 🖥️ Camada de Apresentação

    **Streamlit:**
    - `app.py` — Central de Comando
    - 11 páginas em `pages/`
    - Navegação por sidebar
    - `utils.py` (header/sidebar)

    **Saída para nuvem:**
    - `boto3` → AWS SNS
    - E-mail / SMS via assinaturas
    - ARN mascarado na UI
    - Antideduplicação por cooldown
    """)

st.divider()

# Fluxo do Sistema
st.markdown("### 🔄 Fluxo de Processamento")

st.code("""
┌──────────────────────┐    ┌──────────────────────┐
│  ESP32 / Wokwi       │    │  Imagens (.jpg/.png) │
│  iot_simulator.py    │    │  assets/images/      │
└──────────┬───────────┘    └──────────┬───────────┘
           │                            │
           ▼                            ▼
  ┌──────────────────────────────────────────────┐
  │   SQLite — farmtech_iot.db                   │
  │   sensores · leituras_sensores · culturas    │
  │   previsoes_ml · alertas · historico_irrig.  │
  │   analises_visuais                           │
  └──────────────────┬───────────────────────────┘
                     │
   ┌─────────────────┼─────────────────┐
   ▼                 ▼                 ▼
┌────────┐    ┌───────────────┐  ┌──────────────┐
│ ML     │    │ Irrigação     │  │ Visão YOLOv8 │
│ Fase 4 │    │ Fase 3        │  │ Fase 6       │
└───┬────┘    └───────┬───────┘  └──────┬───────┘
    │                 │                  │
    └──────────┬──────┴──────────────────┘
               ▼
   ┌──────────────────────────────────┐
   │  Dashboard Streamlit             │
   │  app.py (Central) + 11 páginas   │
   └──────────────┬───────────────────┘
                  │
                  ▼
   ┌──────────────────────────────────┐
   │  alert_service (regras + boto3)  │
   └──────────────┬───────────────────┘
                  │
                  ▼
   ┌──────────────────────────────────┐
   │  AWS SNS — farmtech-alertas      │
   │  → e-mail / SMS                  │
   └──────────────────────────────────┘
""", language="text")

st.divider()

# ==========================================================
#         FUNCIONALIDADES
# ==========================================================

st.header("⚙️ Funcionalidades")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🚜 Fase 1 — Cálculos, Clima e R

    **Cálculos agronômicos:**
    - Área de plantio (retângulo, triângulo, círculo/pivô)
    - Insumos por cultura (milho, soja, café, cana)

    **API meteorológica:**
    - Open-Meteo (sem chave) — clima atual + 7 dias
    - Fallback simulado em caso de falha de rede

    **Análise estatística em R:**
    - `services/fase1_analise.R` via `Rscript`
    - Média, desvio, quartis das colunas numéricas
    - Fallback `pandas.describe` se o R não estiver instalado
    """)

    st.markdown("""
    ### 📡 Fase 3 — IoT e Irrigação Automatizada

    **Simulador IoT:**
    - `iot_simulator.py` rodando em subprocess
    - Múltiplos sensores em paralelo com conexões próprias
    - Gravação contínua em `leituras_sensores`

    **`ControladorIrrigacao`:**
    - Histerese de umidade (30 % a 60 %)
    - Bloqueio quando pH fora de [5,5–7,5]
    - Recomendação de fertirrigação por NPK baixo
    - Display **LCD 16×2** simulado em `st.code`
    """)

    st.markdown("""
    ### 🔔 Fase 5 — Alertas AWS (SNS)

    **`ServicoAlertas`:**
    - `boto3` → tópico **SNS** `farmtech-alertas`
    - Regras: umidade crítica, pH fora, temperatura alta, praga (visão)
    - Severidade **🔴 CRÍTICO** / **🟠 ALTO** + ação corretiva
    - Antideduplicação via cooldown configurável

    **Segurança:**
    - Credenciais somente em `.env` (ignorado pelo Git)
    - ARN mascarado na UI
    - Modo simulado (log local) sem ARN configurado
    """)

with col2:
    st.markdown("""
    ### 🗄️ Fase 2 — Banco de Dados e CRUD

    **`database_manager.py`:**
    - SQLite com `timeout=10` (convive com o simulador)
    - 7 tabelas + migrations idempotentes

    **Página CRUD (5 abas):**
    - READ (filtros por sensor / período)
    - CREATE (sensor + leitura manual)
    - UPDATE (status / resolver alertas)
    - DELETE (cascade controlado)
    - MER/DER (Mermaid + DDL — `docs/der_fase2.md`)
    """)

    st.markdown("""
    ### 🤖 Fase 4 — ML e Previsões

    **Modelos de regressão (herança Fase 4):**
    - 💧 **Irrigação** — volume semanal (L/m²)
    - 🌿 **Fertilização** — dosagem NPK (kg/ha)
    - 🌾 **Rendimento** — produtividade (kg/ha)

    **Algoritmos & métricas:**
    - Regressão Linear Múltipla
    - Regressão Polinomial (grau 2)
    - MAE, RMSE, R² · train/test 80/20

    **Páginas dedicadas:**
    - EDA, Modelagem, Previsões Manual/IoT,
      Previsões Interativas, Pipeline ML
    """)

    st.markdown("""
    ### 📷 Fase 6 — Visão Computacional (YOLOv8)

    **`AnalisadorVisual`:**
    - `ultralytics.YOLO("yolov8n.pt")` em lazy-loading
    - `OpenCV` para conversão BGR → RGB
    - Persiste em `analises_visuais` (deteccoes_json)

    **Diagnóstico agrícola sobre COCO:**
    - Animais (bird, cow, horse, sheep…) → ⚠️ "Possível praga"
    - Pessoa → 👤 informativo
    - Sem detecção → 🌱 "Lavoura saudável"
    """)

st.divider()

# ==========================================================
#         TECNOLOGIAS
# ==========================================================

st.header("💻 Tecnologias")

st.markdown("""
Todas as bibliotecas foram cuidadosamente selecionadas para criar um sistema robusto, 
escalável e de fácil manutenção.
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🐍 Python & Core

    <span class="tech-badge">Python 3.11</span>
    <span class="tech-badge">Pandas</span>
    <span class="tech-badge">NumPy</span>
    <span class="tech-badge">Requests</span>
    <span class="tech-badge">python-dotenv</span>

    **Pandas / NumPy**: manipulação de dados e álgebra linear.
    **Requests**: consumo da API Open-Meteo (Fase 1).
    **python-dotenv**: carrega `.env` com credenciais (Fase 5/7).

    ### 🤖 Machine Learning (Fase 4)

    <span class="tech-badge">Scikit-Learn</span>
    <span class="tech-badge">StandardScaler</span>
    <span class="tech-badge">LinearRegression</span>

    **Scikit-Learn**: pipeline de regressão (linear, polinomial).
    **Métricas**: MAE, RMSE, R².

    ### 📷 Visão Computacional (Fase 6)

    <span class="tech-badge">Ultralytics</span>
    <span class="tech-badge">YOLOv8n</span>
    <span class="tech-badge">OpenCV</span>
    <span class="tech-badge">Pillow</span>

    **Ultralytics YOLOv8**: detecção de objetos sobre classes COCO.
    **OpenCV (headless)**: conversão BGR ⇄ RGB e processamento de
    imagem sem dependência de GUI nativa.

    ### 📊 Visualização & UI

    <span class="tech-badge">Streamlit</span>
    <span class="tech-badge">Plotly</span>

    **Streamlit**: 11 páginas + Central de Comando.
    **Plotly**: timelines, scatter, séries temporais interativas.
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    ### 📡 IoT & Persistência

    <span class="tech-badge">SQLite</span>
    <span class="tech-badge">ESP32</span>
    <span class="tech-badge">Wokwi</span>

    **SQLite**: banco local (`farmtech_iot.db`) com `timeout=10` e
    migrations idempotentes (`CREATE TABLE IF NOT EXISTS`).
    **ESP32 / Wokwi**: hardware/simulador da Fase 3, espelhado pelo
    `iot_simulator.py` no dashboard.

    ### ☁️ AWS & Mensageria (Fase 5/7)

    <span class="tech-badge">boto3</span>
    <span class="tech-badge">AWS SNS</span>
    <span class="tech-badge">IAM</span>

    **boto3**: cliente Python da AWS — `sns.publish` e
    `sns.get_topic_attributes`.
    **SNS — `farmtech-alertas`**: tópico com assinatura de e-mail
    confirmada; antideduplicação no banco via `alertas.enviado_sns`.

    ### 🌦️ APIs Externas

    <span class="tech-badge">Open-Meteo</span>

    **Open-Meteo**: API pública (sem chave) para clima atual + previsão
    de 7 dias, consumida em `services/fase1_clima.py`.

    ### 📊 Análise Estatística (Fase 1)

    <span class="tech-badge">R base</span>
    <span class="tech-badge">Rscript</span>

    **R**: `services/fase1_analise.R` lê o CSV de clima e devolve
    média, desvio padrão, mín, máx e quartis usando apenas R base
    (sem pacotes externos). Fallback `pandas.describe` quando o
    `Rscript` não estiver disponível.

    ### 📦 Gerenciamento

    <span class="tech-badge">Git</span>
    <span class="tech-badge">pip</span>
    <span class="tech-badge">venv</span>
    <span class="tech-badge">.env</span>

    **Git**: controle de versão (`.env` ignorado, `.env.example` versionado).
    **venv + pip**: ambiente isolado com versões pinadas em
    `requirements.txt`.
    """, unsafe_allow_html=True)

st.divider()

# ==========================================================
#         ESTRUTURA DO PROJETO
# ==========================================================

st.header("📂 Estrutura do Projeto")

col1, col2 = st.columns([1, 1])

with col2:
    st.code("""
wokwi_farmatech_fase04_cap01/
│
├── README.md                           
├── requirements.txt                    
├── .gitignore                          
│
├── .venv/                              
│
├── data/
│   ├── raw/
│   │   ├── produtos_agricolas.csv
│   │   └── Smart_Farming_Crop_Yield_2024.csv
│   ├── processed/
│   │   ├── dataset_ml_preparado.csv
│   │   └── dataset_final_farmtech.csv
│   └── data_generation.py              
│
├── docs/
│
├── pages/
│   ├── 1_🚜_Fase1_Calculos_e_Clima.py
│   ├── 2_🗄️_Fase2_CRUD_Banco.py
│   ├── 3_📡_Fase3_Monitoramento_IoT.py
│   ├── 4_📈_Fase4_Analise_Exploratoria.py
│   ├── 5_🤖_Fase4_Modelagem_Preditiva.py
│   ├── 6_🔮_Fase4_Previsoes_Manual_IoT.py
│   ├── 7_🎛️_Fase4_Previsoes_Interativas.py
│   ├── 8_💾_Fase4_Pipeline_ML.py
│   ├── 9_📷_Fase6_Visao_Computacional.py
│   ├── 10_🔔_Fase5_Alertas_AWS.py
│   └── 11_ℹ️_Sobre_o_Projeto.py
│
│
├── database_manager.py                 
├── farmtech_iot.db                     
├── iot_simulator.py                    
├── utils.py                           
└── app.py                              
    """)

with col1:
    st.markdown("""
    ### Descrição dos Arquivos

    **Principais (ordem do menu lateral):**
    - `app.py`: Central de Comando (Fase 7)
    - `pages/1_*.py`: Fase 1 — Cálculos agronômicos + Clima + R
    - `pages/2_*.py`: Fase 2 — CRUD do banco + DER
    - `pages/3_*.py`: Fase 3 — Monitoramento IoT + irrigação automatizada
    - `pages/4_*.py`: Fase 4 — Análise exploratória (EDA)
    - `pages/5_*.py`: Fase 4 — Modelagem preditiva
    - `pages/6_*.py`: Fase 4 — Previsões (manual / IoT)
    - `pages/7_*.py`: Fase 4 — Previsões interativas
    - `pages/8_*.py`: Fase 4 — Pipeline ML
    - `pages/9_*.py`: Fase 6 — Visão Computacional (YOLO)
    - `pages/10_*.py`: Fase 5 — Alertas AWS (SNS)
    - `pages/11_*.py`: Sobre o projeto (esta página)

    **Dados:**
    - `dataset_final_farmtech.csv`: Dataset original (2.200 registros)
    - `dataset_ml_preparado.csv`: Dataset processado (36 features derivadas, 51 totais)
    - `farmtech_iot.db`: Banco SQLite com dados dos sensores IoT

    **Módulos IoT:**
    - `database_manager.py`: Classe para gerenciar banco SQLite
    - `iot_simulator.py`: Simulador de dados de sensores

    **Configuração:**
    - `requirements.txt`: Lista de dependências
    - `.gitignore`: Controle de versionamento
    """)

st.divider()

# ==========================================================
#         EQUIPE E CONTEXTO
# ==========================================================

st.header("👥 Equipe e Contexto")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### 🎓 Contexto Acadêmico

    **Instituição:** FIAP - Faculdade de Informática e Administração Paulista
    **Curso:** Inteligência Artificial
    **Turma:** 1TIAOS
    **Disciplina:** Fase 7 - Cap 1 — Sistema Integrado FarmTech Solutions
    **Período:** Junho 2026

    **Orientação:**
    - 👩‍🏫 **Tutora:** Sabrina Otoni
    - 🧭 **Coordenador:** André Godoi Chiovatto

    ### 📋 Objetivo da Atividade

    Consolidar em **um único repositório integrado** o trabalho das
    Fases 1 a 6 do projeto FarmTech Solutions e expô-lo num
    **dashboard Streamlit** que serve como Central de Comando da
    fazenda inteligente — combinando IoT, banco de dados, ML, visão
    computacional e alertas em nuvem.

    ### 🎯 Entregas da Fase 7

    **Integração:**
    - ✅ Central de Comando (`app.py`) com cards para todos os serviços
    - ✅ Banco SQLite único com migrations idempotentes
    - ✅ 5 módulos em `services/` reaproveitando o código das fases

    **Operação:**
    - ✅ Simulador IoT em subprocess controlado pela UI
    - ✅ Regras de irrigação (histerese + pH + NPK)
    - ✅ Visão YOLOv8 com diagnóstico agrícola
    - ✅ Alertas SNS reais (tópico `farmtech-alertas`)

    **Engenharia & documentação:**
    - ✅ `.env` + `.env.example` (credenciais fora do Git)
    - ✅ README com diagrama Mermaid + prints AWS
    - ✅ Roteiro de vídeo com timestamps em `docs/roteiro_video.md`
    - ✅ Histórico CRISP-DM da Fase 4 preservado
    """)

with col2:
    st.markdown("""
    <div class="info-card">
        <h3>👨‍💻 Equipe</h3>
        <p><strong>GRUPO 37 — 1TIAOS — FIAP</strong></p>
        <p>Giovani Saavedra — RM566797</p>
        <p>Marcio Elifas — RM567871</p>
        <hr>
        <h3>👩‍🏫 Orientação</h3>
        <p><strong>Tutora:</strong> Sabrina Otoni</p>
        <p><strong>Coordenador:</strong> André Godoi Chiovatto</p>
        <hr>
        <h3>📅 Histórico do Projeto</h3>
        <p><strong>Fases 1–6:</strong> 2024 → 2025</p>
        <p><strong>Fase 7 (integração):</strong> Junho 2026</p>
        <p><strong>Status:</strong> ✅ Concluído</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ==========================================================
#         RESULTADOS E IMPACTO
# ==========================================================

st.header("📊 Resultados e Impacto")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 🎯 Técnicos

    **Integração (Fase 7):**
    - Central de Comando unificada
    - Pipeline IoT → DB → ML → SNS
    - Migrations idempotentes no SQLite
    - Conexões curtas + cooldown

    **Performance ML (Fase 4):**
    - Modelos de regressão validados
    - Métricas MAE, RMSE, R²
    - Pipeline Scikit-Learn reproduzível
    """)

with col2:
    st.markdown("""
    ### 💼 Negócio

    **Valor Gerado:**
    - Sistema demonstrável ponta a ponta
    - Alertas com **ação corretiva** explícita
    - Diagnóstico visual de pragas (YOLO)
    - Recomendação de irrigação automática

    **Benefícios Esperados:**
    - ↓ 15 % uso de água
    - ↓ 10 % uso de fertilizantes
    - ↑ 10 % produtividade
    - ⏱️ Reação mais rápida a anomalias
    """)

with col3:
    st.markdown("""
    ### 🌱 Sustentabilidade

    **Impacto Ambiental:**
    - Uso consciente de recursos hídricos
    - Bloqueio de irrigação em solo desbalanceado
    - Detecção de pragas antes da aplicação massiva

    **Escalabilidade:**
    - Arquitetura em camadas (`services/`)
    - Banco único e migrations seguras
    - Pronto para múltiplos sensores e fazendas
    - Base sólida para próximas iterações
    """)

st.divider()

# ==========================================================
#         RECURSOS E REFERÊNCIAS
# ==========================================================

st.header("📚 Recursos e Referências")

tab1, tab2, tab3 = st.tabs(["Documentação", "Referências", "Contato"])

with tab1:
    st.markdown("""
    ### 📖 Documentação Técnica

    **Metodologia (herança Fase 4):**
    - [CRISP-DM 1.0](https://www.datascience-pm.com/crisp-dm-2/) — Cross-Industry Standard Process

    **Frameworks e bibliotecas usados na Fase 7:**
    - [Streamlit](https://docs.streamlit.io/) — dashboard e Central de Comando
    - [Scikit-Learn](https://scikit-learn.org/stable/) — modelos de regressão (Fase 4)
    - [Ultralytics YOLOv8](https://docs.ultralytics.com/) — visão computacional (Fase 6)
    - [OpenCV](https://docs.opencv.org/) — processamento de imagens
    - [Plotly](https://plotly.com/python/) — visualizações interativas
    - [Pandas](https://pandas.pydata.org/docs/) — manipulação de dados
    - [SQLite](https://www.sqlite.org/docs.html) — persistência local
    - [boto3 / AWS SNS](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html) — mensageria em nuvem (Fase 5/7)
    - [python-dotenv](https://github.com/theskumar/python-dotenv) — variáveis de ambiente
    - [Open-Meteo API](https://open-meteo.com/en/docs) — clima (Fase 1)
    - [R base](https://stat.ethz.ch/R-manual/R-devel/library/base/html/00Index.html) — análise estatística (Fase 1)
    - [ESP32](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/) + [Wokwi](https://docs.wokwi.com/) — hardware/simulador IoT
    """)

with tab2:
    st.markdown("""
    ### 📚 Referências Bibliográficas

    **Machine Learning & Ciência de Dados:**
    - Géron, A. (2019). *Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow*
    - McKinney, W. (2017). *Python for Data Analysis*
    - VanderPlas, J. (2016). *Python Data Science Handbook*

    **Visão computacional:**
    - Redmon, J. et al. *YOLO: Unified, Real-Time Object Detection* (CVPR 2016)
    - Ultralytics (2023). *YOLOv8 Documentation & Tutorials*

    **Agricultura de precisão (CRISP-DM/Fase 4):**
    - Khaki & Wang (2019). *Crop Yield Prediction Using Deep Neural Networks*
    - Jeong et al. (2016). *Random Forests for Global and Regional Crop Yield Predictions*
    - Patil et al. (2023). *Crop Selection and Yield Prediction using Machine Learning*
    """)

with tab3:
    st.markdown("""
    ### 📧 Informações de Contato

    **Equipe — GRUPO 37 — 1TIAOS — FIAP:**
    - Giovani Saavedra — RM566797
    - Marcio Elifas — RM567871

    **Orientação:**
    - 👩‍🏫 Tutora: Sabrina Otoni
    - 🧭 Coordenador: André Godoi Chiovatto

    **Instituição:**
    - FIAP — Faculdade de Informática e Administração Paulista
    - Site: https://www.fiap.com.br
    - Endereço: Av. Lins de Vasconcelos, 1264 — São Paulo/SP
    """)

st.divider()

# ==========================================================
#         CONCLUSÃO
# ==========================================================

st.header("✅ Conclusão")

st.markdown("""
A **Fase 7** demonstra com sucesso a **consolidação** das Fases 1 a 6 do
projeto FarmTech Solutions num **sistema único, demonstrável e seguro**.
A partir de uma Central de Comando Streamlit, sensores simulados,
modelos de Machine Learning, visão computacional e alertas em nuvem
operam sobre uma mesma origem de dados, com regras de negócio
compartilhadas e ação corretiva explícita.

### 🎯 Principais Conquistas

✅ **Integração** — 6 fases num único repositório com um único ponto de entrada (`streamlit run app.py`)
✅ **IoT real** — simulador em subprocess gravando ao vivo no SQLite
✅ **ML preservado** — modelos da Fase 4 mantidos e acessíveis via dashboard
✅ **Visão YOLO** — detecção de animais → diagnóstico de praga
✅ **Mensageria** — AWS SNS publicando alertas com severidade e ação corretiva
✅ **Segurança** — credenciais em `.env` (fora do Git), ARN mascarado, antideduplicação
✅ **Documentação** — README com diagrama Mermaid, prints AWS e roteiro de vídeo

O sistema serve como **base sólida** para futuras evoluções (multi-fazenda,
modelos específicos de domínio agrícola, integração com APIs comerciais).
""")

st.divider()

# Footer
st.markdown("""
---
<div style='text-align: center; padding: 20px; color: #666;'>
    <p><strong>🌾 FarmTech Solutions — Fase 7</strong></p>
    <p>Sistema Integrado de Gestão Agrícola Inteligente</p>
    <p>FIAP — Fase 7 — 2026.1 — Turma 1TIAOS</p>
    <p>Desenvolvido por Giovani Saavedra (RM566797) e Marcio Elifas (RM567871)</p>
    <p>Tutora: Sabrina Otoni · Coordenador: André Godoi Chiovatto</p>
    <hr style='width: 50%; margin: 20px auto;'>
    <p style='font-size: 12px;'>
        Tecnologias: Python · Streamlit · Scikit-Learn · Plotly · Pandas ·
        Ultralytics YOLOv8 · OpenCV · boto3 (AWS SNS) · SQLite · R · Open-Meteo<br>
        Metodologia: CRISP-DM (herança Fase 4) · Versão 3.0 · Junho 2026
    </p>
</div>
""", unsafe_allow_html=True)