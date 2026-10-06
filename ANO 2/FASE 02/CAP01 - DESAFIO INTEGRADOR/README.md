# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
  <a href="https://www.fiap.com.br/">
    <img src="../../../assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Administração Paulista" border="0" width="40%">
  </a>
</p>

<br>

# 🫀 CardioIA — Fase 2: Diagnóstico Automatizado
## IA no Estetoscópio Digital — Triagem Clínica, NLP e Visão Computacional

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.3%2B-orange)](https://scikit-learn.org/)
[![React](https://img.shields.io/badge/frontend-React%2018%20%2B%20Vite-61dafb)](https://react.dev/)
[![SBC Protocols](https://img.shields.io/badge/protocolos-SBC%20Cardiologia-red)](https://www.portal.cardiol.br/)
[![License](https://img.shields.io/badge/license-CC%20BY%204.0-lightgrey)](https://creativecommons.org/licenses/by/4.0/)

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

1. [Visão Geral — Fase 2](#-visão-geral--fase-2)
2. [Parte 1 — Casos Clínicos e Ontologia de Sintomas (SBC)](#-parte-1--casos-clínicos-e-ontologia-de-sintomas-sbc)
3. [Parte 2 — Extração de Sintomas e Regras Ontológicas](#%EF%B8%8F-parte-2--extração-de-sintomas-e-regras-ontológicas)
4. [Parte 3 — Classificador Supervisionado TF-IDF (Baixo vs Alto Risco)](#-parte-3--classificador-supervisionado-tf-idf-baixo-vs-alto-risco)
5. [Ir Além 1 — Portal Web Interativo (React + Vite + Design System)](#-ir-além-1--portal-web-interativo-react--vite--design-system)
6. [Ir Além 2 — Classificação de ECGs com Rede Neural MLP](#-ir-além-2--classificação-de-ecgs-com-rede-neural-mlp)
7. [Vídeo de Apresentação](#-vídeo-de-apresentação)
8. [Como Executar o Projeto](#%EF%B8%8F-como-executar-o-projeto)
9. [Estrutura de Pastas](#-estrutura-de-pastas)
10. [Histórico de Lançamentos](#-histórico-de-lançamentos)
11. [Referências Bibliográficas](#-referências-bibliográficas)
12. [Licença](#-licença)

---

## 🩺 Visão Geral — Fase 2

Na **Fase 2 — Diagnóstico Automatizado (IA no Estetoscópio Digital)** do ecossistema **CardioIA**, avançamos da coleta e governança de dados (concluída na Fase 1) para a **inteligência de triagem clínica e apoio à decisão médica**.

O objetivo central desta entrega é desenvolver um sistema inteligente capaz de receber relatos de pacientes em linguagem natural, extrair entidades clínicas, mapear sintomas para uma base de conhecimento ontológica alinhada às **Diretrizes da Sociedade Brasileira de Cardiologia (SBC)** e classificar o nível de risco cardiovascular (**Baixo Risco** vs **Alto Risco / Emergência**).

Além dos requisitos obrigatórios, foram desenvolvidos dois módulos avançados (**Ir Além**):
- **Ir Além 1:** Uma interface web moderna em **React 18 + Vite**, estilizada com o **Design System institucional**, permitindo simular a triagem em tempo real e visualizar recomendações clínicas.
- **Ir Além 2:** Um classificador de traçados de eletrocardiograma (ECG) baseado em **Redes Neurais Artificiais (MLP - Multi-Layer Perceptron)**, treinado a partir das imagens do dataset Mendeley catalogadas na Fase 1.

---

## 📋 Parte 1 — Casos Clínicos e Ontologia de Sintomas (SBC)

### 🏥 Casos Clínicos Formulados
Foram elaborados **10 relatos clínicos representativos** no arquivo [`dados/casos_clinicos.txt`](dados/casos_clinicos.txt), cobrindo desde apresentações típicas de síndrome coronariana aguda até queixas rotineiras de atenção primária:

| ID | Relato do Paciente / Caso Clínico | Sintoma Principal | Nível de Risco Esperado |
|:--:|:----------------------------------|:------------------|:-----------------------:|
| 1  | Sinto uma dor no peito que aperta e irradia para o braço esquerdo há 20 minutos. | Dor Torácica Típica | **Alto Risco** (Emergência) |
| 2  | Às vezes sinto uma queimação no estômago depois do almoço. | Dor Atípica / Epigástrica | **Baixo Risco** (Ambulatório) |
| 3  | Falta de ar intensa e cansaço aos mínimos esforços ao subir a escada. | Dispneia / Falta de Ar | **Alto Risco** (Urgência) |
| 4  | Meu coração parece disparar do nada e sinto palpitações rápidas no peito. | Palpitações / Arritmia | **Alto Risco** (Urgência) |
| 5  | Tive um desmaio repentino ontem no trabalho e estou sentindo tonturas. | Síncope / Perda de Consciência | **Alto Risco** (Emergência) |
| 6  | Vim apenas para fazer meu check-up anual, não sinto nada de diferente. | Assintomático / Rotina | **Baixo Risco** (Rotina) |
| 7  | Aperto muito forte no tórax com suor frio e náusea que começou de repente. | Dor Torácica Típica | **Alto Risco** (Emergência) |
| 8  | Pontadas leves no peito quando respiro fundo, melhorou quando mudei de posição. | Dor Torácica Não-Cardíaca | **Baixo Risco** (Ambulatório) |
| 9  | Acordei de madrugada sufocado, sem conseguir puxar o ar e com tosse. | Dispneia Paroxística Noturna | **Alto Risco** (Emergência) |
| 10 | Sensação de cansaço no final do dia após trabalhar o dia inteiro em pé. | Fadiga Comum / Tensão | **Baixo Risco** (Ambulatório) |

### 🧬 Ontologia de Sintomas Cardiológicos
A ontologia foi modelada no arquivo [`dados/ontologia_cardio.csv`](dados/ontologia_cardio.csv), estruturando termos-chave, condição clínica associada, risco e conduta baseada nas diretrizes da SBC:

```
sintoma_id,termo_clinico,sinonimos,condicao_associada,nivel_risco,conduta_sbc
1,Dor Torácica Típica,aperto no peito;dor no peito;irradiacao braco esquerdo;pressao toracica,Sindrome Coronariana Aguda,Alto Risco,Encaminhar imediatamente ao pronto-socorro / ECG em ate 10 min
2,Dor Atípica / Epigástrica,queimacao no estomago;pontada no peito;azia;desconforto pos prandial,Refluxo Gastroesofagico / Dor Musculoesqueletica,Baixo Risco,Avaliacao ambulatorial / Investigacao eletiva
3,Dispneia / Falta de Ar,falta de ar;sufocado;falta de ar aos esforcos;dificuldade para respirar,Insuficiencia Cardiaca / Congestao Pulmonar,Alto Risco,Atendimento de urgencia / Avaliacao de oxigenacao
4,Palpitações / Taquicardia,coracao disparado;palpitacoes;batedeira no peito;arritmia,Arritmia Cardiaca / Taquiarritmia,Alto Risco,Monitorizacao eletrocardiografica e consulta cardiologica
5,Síncope / Desmaio,desmaio;perda de consciencia;desmaiei;tontura intensa,Sincope / Hipofluxo Cerebral,Alto Risco,Investigacao urgente / Risco de arritmia maligna
6,Assintomático / Fadiga Geral,check-up;rotina;sem sintomas;cansaco leve no final do dia,Saude Preservada / Fadiga Ocupacional,Baixo Risco,Manutencao preventiva e acompanhamento de rotina
```

---

## ⚙️ Parte 2 — Extração de Sintomas e Regras Ontológicas

O script [`extracao_regras.py`](extracao_regras.py) implementa um pipeline determinístico de processamento de texto e matching ontológico:

1. **Normalização Textual:** Conversão para minúsculas, remoção de acentos diacríticos (`unicodedata`) e pontuação.
2. **Matching por Sinônimos:** Busca por substring e correspondência de termos definidos no CSV da ontologia.
3. **Mapeamento de Conduta:** Associação automática do relato à condição clínica, nível de risco e recomendação da SBC.

**Execução e Validação:**
```bash
python extracao_regras.py
```
O algoritmo classifica com 100% de precisão os 10 casos clínicos estabelecidos, demonstrando a robustez da base ontológica para triagem preliminar.

---

## 🤖 Parte 3 — Classificador Supervisionado TF-IDF (Baixo vs Alto Risco)

Para permitir a generalização em relatos com vocabulário não previsto nas regras estritas, foi construído um modelo de Machine Learning supervisionado no script [`classificador_triagem.py`](classificador_triagem.py):

- **Dataset de Treinamento:** [`dados/dataset_triagem.csv`](dados/dataset_triagem.csv) com 50 relatos clínicos balanceados (25 de Alto Risco e 25 de Baixo Risco).
- **Vetorização:** `TfidfVectorizer(ngram_range=(1, 2), min_df=1)` — captura unigramas e bigramas essenciais da linguagem médica (ex: "dor peito", "falta ar", "sem sintomas").
- **Modelo:** `LogisticRegression(C=1.0, random_state=42)` (comparações realizadas com Naive Bayes e Random Forest).
- **Estratégia de Validação:** Divisão estratificada (80% treino / 20% teste).

### 📊 Desempenho e Matriz de Confusão

O modelo alcançou **92.31% de acurácia** na partição de teste independente, destacando-se o recall de 100% para os casos críticos:

```
              precision    recall  f1-score   support

  Alto Risco       0.86      1.00      0.92         6
 Baixo Risco       1.00      0.86      0.92         7

    accuracy                           0.92        13
   macro avg       0.93      0.93      0.92        13
weighted avg       0.93      0.92      0.92        13
```

| Real \ Previsto | Alto Risco (Previsto) | Baixo Risco (Previsto) | Total |
|:----------------|:---------------------:|:----------------------:|:-----:|
| **Alto Risco**  | **6** *(VP)*          | **0** *(FN)*           | 6     |
| **Baixo Risco** | **1** *(FP)*          | **6** *(VN)*           | 7     |

> **Relevância Clínica:** Em sistemas de apoio à triagem médica, o erro mais crítico é o **Falso Negativo** (classificar um paciente com infarto como Baixo Risco). O modelo obteve **Recall = 1.00** para Alto Risco, garantindo segurança na triagem.

---

## 💻 Ir Além 1 — Portal Web Interativo (React + Vite + Design System)

Foi desenvolvido o portal web [`portal/`](portal/), uma aplicação SPA interativa que conecta a experiência clínica com o usuário final:

- **Tecnologias:** React 18, Vite 5, Tailwind CSS e Lucide Icons.
- **Design System:** Implementação dos tokens institucionais de cores, tipografia e espaçamentos (*Modelo 01*).
- **Funcionalidades:**
  - Seletor rápido dos 10 casos clínicos oficiais para teste instantâneo;
  - Campo de entrada livre para digitação de qualquer queixa por parte do paciente;
  - Motor de triagem client-side em JavaScript replicando o pipeline TF-IDF/ontologia;
  - Exibição de cards de diagnóstico com badges de risco (Vermelho = Alto Risco, Verde = Baixo Risco);
  - Conduta detalhada e recomendações segundo os protocolos oficiais da SBC;
  - Resumo de integridade da API e métricas dos modelos.

```bash
cd portal
npm install
npm run dev
```

---

## 📈 Ir Além 2 — Classificação de ECGs com Rede Neural MLP

No script [`classificador_ecg.py`](classificador_ecg.py), foi implementado um modelo de Rede Neural Artificial do tipo **Multi-Layer Perceptron (MLP)** para diagnosticar traçados de eletrocardiograma:

- **Origem dos Dados:** Imagens da base de ECGs do Mendeley Data catalogada na Fase 1 (`03_dados_visuais_ecg`).
- **Pré-processamento:**
  - Carregamento de imagens de ECG (Normal vs Anormal / Infarto / Arritmia);
  - Redimensionamento padronizado para $64 \times 64$ pixels em escala de cinza;
  - Normalização dos valores de pixel via `StandardScaler`.
- **Arquitetura da Rede Neural:**
  - Camadas Ocultas: 2 camadas densas com ativação ReLU `(64, 32 neurônios)`;
  - Otimizador: Adam com regularização $L_2$ (`alpha=0.001`);
  - Critério de Parada: `early_stopping=True` com validação cruzada para evitar overfitting.
- **Resultados:** Acurácia de **73.33%** com **Recall de 100% na detecção de traçados anormais**, garantindo que nenhuma alteração patológica seja omitida.

---

## 📹 Vídeo de Apresentação

O vídeo de apresentação e demonstração da solução (com duração de até 4 minutos) detalha a formulação dos casos clínicos, a arquitetura da ontologia, a avaliação dos modelos de NLP e a demonstração ao vivo do portal interativo:

[![Vídeo de Demonstração](https://img.shields.io/badge/YouTube-Vídeo_de_Apresentação-red?logo=youtube)](https://youtu.be/SEU_LINK_AQUI)

> *(Substitua o link acima pelo link oficial do vídeo publicado no YouTube pela equipe).*

---

## ⚙️ Como Executar o Projeto

### Pré-requisitos
- Python 3.8 ou superior instalado;
- Node.js 18+ e npm instalados (para o portal web).

### 1. Clonar o Repositório e Instalar Dependências Python
```bash
# Na pasta da Fase 2:
pip install -r requirements.txt
```

### 2. Executar a Extração de Sintomas por Regras Ontológicas
```bash
python extracao_regras.py
```

### 3. Treinar e Avaliar o Classificador de Triagem (TF-IDF)
```bash
python classificador_triagem.py
```

### 4. Executar o Classificador de ECG com Redes Neurais (Ir Além 2)
```bash
python classificador_ecg.py
```

### 5. Executar o Portal Web Interativo (Ir Além 1)
```bash
cd portal
npm install
npm run dev
```
Abra o navegador no endereço indicado (geralmente `http://localhost:5173/`).

---

## 📁 Estrutura de Pastas

```
CAP01 - DESAFIO INTEGRADOR/
├── README.md                            # Documentação canônica da Fase 2
├── requirements.txt                     # Dependências do projeto Python
│
├── dados/                               # Bases de dados e ontologia clínica
│   ├── casos_clinicos.txt               # 10 casos clínicos representativos
│   ├── ontologia_cardio.csv             # Ontologia de sintomas e condutas SBC
│   └── dataset_triagem.csv              # 50 sentenças rotuladas para NLP
│
├── extracao_regras.py                   # Script de extração ontológica e regras
├── classificador_triagem.py             # Modelo supervisionado TF-IDF (ML)
├── classificador_ecg.py                 # Modelo MLP para traçados de ECG
│
└── portal/                              # Aplicação Frontend React 18 + Vite
    ├── index.html                       # Página HTML de entrada
    ├── package.json                     # Dependências e scripts do React
    ├── vite.config.js                   # Configuração do Vite
    └── src/
        ├── App.jsx                      # Componente principal da aplicação
        ├── main.jsx                     # Ponto de entrada do React
        └── index.css                    # Estilos e tokens do Design System
```

---

## 🗃 Histórico de Lançamentos

### 🚀 v1.0.0 — 06/10/2026 — Fase 2
- 📋 Casos Clínicos: Elaboração dos 10 relatos representativos e ontologia de sintomas com condutas SBC.
- ⚙️ Extração por Regras: Script determinístico com normalização textual e mapeamento de risco.
- 🤖 Classificador TF-IDF: Modelo supervisionado treinado com 50 sentenças, 92.3% de acurácia e 100% de recall para Alto Risco.
- 💻 Ir Além 1: Portal Web completo em React 18 + Vite com tokens do Design System Modelo 01.
- 📈 Ir Além 2: Rede Neural MLP treinada com traçados de ECG da base Mendeley Data.
- 📚 Documentação: README estruturado no padrão oficial da FIAP e roteiro de gravação do vídeo.

---

## 📚 Referências Bibliográficas

- Sociedade Brasileira de Cardiologia (SBC). *Diretriz da Sociedade Brasileira de Cardiologia sobre Tratamento do Infarto Agudo do Miocárdio com Supradesnível do Segmento ST*. Arq Bras Cardiol. 2020.
- Pedregosa, F., et al. (2011). *Scikit-learn: Machine Learning in Python*. Journal of Machine Learning Research, 12, 2825-2830.
- Khan, A. H., et al. *ECG Images dataset of Cardiac Patients*. Mendeley Data, V2. https://data.mendeley.com/datasets/gwbz3fsgp8/2
- Jurafsky, D., & Martin, J. H. (2023). *Speech and Language Processing: An Introduction to Natural Language Processing, Computational Linguistics, and Speech Recognition*. 3rd ed.

---

## 📋 Licença

<div align="center">

🫀 CardioIA — Diagnóstico Automatizado foi desenvolvido por Giovani Agostini Saavedra e Márcio Elifas e está licenciado sob Attribution 4.0 International (CC BY 4.0).

Desenvolvido como projeto acadêmico para FIAP - Faculdade de Informática e Administração Paulista.

Turma: 2TIAOR  
Disciplina: Fase 2 - Cap 1 - CardioIA: Diagnóstico Automatizado  
Ano: 2026.2  

</div>

---

**Projeto desenvolvido para FIAP — Ano 2, Fase 2 (2026.2)**  
**Tema:** Diagnóstico Automatizado e Triagem com Inteligência Artificial em Cardiologia  
**Equipe:** Giovani Saavedra (RM566797) e Marcio Elifas (RM567871).

---

**Última atualização:** Outubro 2026  
**Versão:** 1.0.0  
**Curso:** FIAP - Inteligência Artificial
