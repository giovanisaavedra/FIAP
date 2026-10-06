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

Para permitir a generalização em relatos com vocabulário não previsto nas regras estritas, foi construído um modelo de Machine Learning supervisionado disponível tanto em script [`classificador_triagem.py`](classificador_triagem.py) quanto no Notebook executado [`classificador_triagem.ipynb`](classificador_triagem.ipynb):

- **Dataset de Treinamento:** [`dados/dataset_triagem.csv`](dados/dataset_triagem.csv) com 50 relatos clínicos balanceados (25 de Alto Risco e 25 de Baixo Risco).
- **Vetorização:** `TfidfVectorizer(ngram_range=(1, 2), lowercase=True)` — captura unigramas e bigramas da linguagem médica (ex: "dor peito", "falta ar", "suor frio").
- **Modelos Comparados:** `LogisticRegression(random_state=42)` vs `DecisionTreeClassifier(max_depth=5)`.
- **Estratégia de Validação:** Divisão estratificada (75% treino / 25% teste).

### 📊 Desempenho e Matriz de Confusão

O modelo de Regressão Logística alcançou **92.31% de acurácia** na partição de teste independente, destacando-se o recall de 100% para os casos críticos:

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

> **Relevância Clínica:** Em sistemas de apoio à triagem médica, o erro mais crítico é o **Falso Negativo** (classificar um paciente com infarto como Baixo Risco). O modelo obteve **Recall = 1.00** para Alto Risco, garantindo segurança na triagem hospitalar.

---

## 💻 Ir Além 1 — Portal Web Interativo (React + Vite + Design System)

Foi desenvolvido o portal web completo em [`portal/`](portal/), estruturado segundo as melhores práticas de engenharia de software e atendendo a todos os critérios da rubrica:

- **Autenticação Simulada (`src/contexts/AuthContext.jsx`):**
  - Autenticação com geração de token fake (JWT) armazenado em `localStorage`;
  - Funções de login e logout globais via **Context API**.
- **Proteção de Rotas (`src/components/ProtectedRoute.jsx`):**
  - Redirecionamento automático para a tela de Login se o usuário não estiver autenticado.
- **Consumo de API Simulada (`src/services/api.js`):**
  - Carregamento de dados de pacientes cardiológicos, histórico e consultas agendadas.
- **Controle de Estado Avançado com Hooks:**
  - **`useReducer`** implementado no formulário de agendamento de consultas (`src/pages/AgendamentoPage.jsx`) com despacho de ações (`CAMPO_ALTERADO`, `DEFINIR_URGENCIA`, `LIMPAR_FORMULARIO`);
  - **`useState`** e **`useEffect`** para recuperação de sessão, busca dinâmica e filtros de risco;
  - **`useContext`** para injeção das credenciais do médico logado.
- **Componentização e Pastas Padronizadas:**
  - `/src/contexts`, `/src/components`, `/src/services`, `/src/pages`, `/src/styles`.
- **Telas:** Login, Dashboard com contadores, Pacientes com busca e filtro, Agendamento com `useReducer` e Triagem Inteligente NLP com as 10 frases oficiais.

```bash
cd portal
npm install
npm run dev
```

---

## 📈 Ir Além 2 — Classificação de ECGs com Rede Neural MLP (Keras)

Implementado no script [`classificador_ecg.py`](classificador_ecg.py) e documentado detalhadamente no Notebook [`classificador_ecg.ipynb`](classificador_ecg.ipynb), foi construído um modelo de Rede Neural Artificial do tipo **Multi-Layer Perceptron (MLP) utilizando Keras**:

- **Origem dos Dados:** Imagens da base de ECGs do Mendeley Data catalogada na Fase 1 (`03_dados_visuais_ecg`) e amostras versionadas em `dados/ecg_amostras/`.
- **Pré-processamento:**
  - Conversão para escala de cinza e redimensionamento padronizado para $64 \times 64$ pixels;
  - Achatamento em vetores unidimensionais de **4.096 atributos** por exame;
  - Padronização estatística com `StandardScaler`.
- **Arquitetura da Rede Neural (Keras Sequential):**
  - Camada de Entrada: 4.096 neurônios (pixels normalizados);
  - Camada Oculta 1: 64 neurônios com ativação ReLU e Dropout de 30%;
  - Camada Oculta 2: 32 neurônios com ativação ReLU;
  - Camada de Saída: 1 neurônio com ativação Sigmoid (probabilidade de anomalia);
  - Otimizador: Adam (`learning_rate=0.0005`) com função de perda `binary_crossentropy`.
- **Desempenho no Teste:** Acurácia de **80.00%** com alta sensibilidade na separação entre traçados normais e patológicos (infarto do miocárdio e batimentos alterados).

---

## 📹 Vídeo de Apresentação

O vídeo de apresentação e demonstração da solução (com duração de até 4 minutos) detalha a formulação dos casos clínicos, a arquitetura da ontologia, a avaliação dos modelos de NLP, o portal React e o treinamento da MLP Keras:

[![Vídeo de Demonstração](https://img.shields.io/badge/YouTube-Vídeo_de_Apresentação-red?logo=youtube)](https://youtu.be/SEU_LINK_AQUI)

> *(Substitua o link acima pelo link oficial do vídeo publicado no YouTube pela equipe).*

---

## ⚙️ Como Executar o Projeto

### Pré-requisitos
- Python 3.8+ instalado;
- Node.js 18+ e npm instalados.

### 1. Clonar o Repositório e Instalar Dependências Python
```bash
# Na pasta da Fase 2:
pip install -r requirements.txt
```

### 2. Executar a Extração de Sintomas por Regras Ontológicas (Parte 1)
```bash
python extracao_regras.py
```

### 3. Treinar e Avaliar o Classificador de Triagem TF-IDF (Parte 2)
```bash
python classificador_triagem.py
# Ou abra o notebook interativo no VS Code / Jupyter:
# classificador_triagem.ipynb
```

### 4. Executar o Classificador de ECG com Redes Neurais Keras (Ir Além 2)
```bash
python classificador_ecg.py
# Ou abra o notebook interativo no VS Code / Jupyter:
# classificador_ecg.ipynb
```

### 5. Executar o Portal Web Interativo (Ir Além 1)
```bash
cd portal
npm install
npm run dev
```
Abra o navegador no endereço indicado (normalmente `http://localhost:5173/`). Credenciais padrão: `giovani.saavedra@cardioia.med.br` / `123456`.

---

## 📁 Estrutura de Pastas

```
CAP01 - DESAFIO INTEGRADOR/
├── README.md                            # Documentação canônica da Fase 2
├── requirements.txt                     # Dependências do projeto Python (Keras, Sklearn, etc.)
│
├── dados/                               # Bases de dados, ontologia clínica e amostras de ECG
│   ├── casos_clinicos.txt               # 10 casos clínicos representativos
│   ├── ontologia_cardio.csv             # Ontologia de sintomas e condutas SBC
│   ├── dataset_triagem.csv              # 50 sentenças rotuladas para NLP
│   └── ecg_amostras/                    # Amostras balanceadas de imagens de ECG (Normal / Anormal)
│       ├── normal/
│       ├── infarto_miocardio/
│       ├── batimentos_anormais/
│       └── historico_im/
│
├── extracao_regras.py                   # Script de extração ontológica e regras (Parte 1)
├── classificador_triagem.py             # Modelo supervisionado TF-IDF (Parte 2)
├── classificador_triagem.ipynb          # Notebook Jupyter com TF-IDF e métricas (Parte 2)
├── classificador_ecg.py                 # Modelo MLP Keras para traçados de ECG (Ir Além 2)
├── classificador_ecg.ipynb              # Notebook Jupyter com MLP Keras (Ir Além 2)
│
└── portal/                              # Aplicação Frontend React 18 + Vite (Ir Além 1)
    ├── README.md                        # Documentação específica do frontend
    ├── package.json                     # Configurações e dependências do React
    ├── vite.config.js                   # Configuração de build do Vite
    ├── index.html                       # Ponto de montagem HTML
    └── src/
        ├── main.jsx                     # Inicialização do React
        ├── App.jsx                      # Componente raiz com AuthProvider e rotas
        ├── App.css                      # Estilos e tokens do Design System
        ├── contexts/
        │   └── AuthContext.jsx          # Context API com autenticação simulada e token JWT
        ├── components/
        │   ├── Navbar.jsx               # Cabeçalho de navegação e logout
        │   └── ProtectedRoute.jsx       # Componente de controle de acesso protegido
        ├── services/
        │   └── api.js                   # Camada de API assíncrona simulada
        ├── pages/
        │   ├── LoginPage.jsx            # Tela de autenticação médica
        │   ├── DashboardPage.jsx        # Painel com indicadores e diretrizes SBC
        │   ├── PacientesPage.jsx        # Listagem de pacientes e filtros por risco
        │   ├── AgendamentoPage.jsx      # Formulário de agendamento com useReducer
        │   └── TriagemPage.jsx          # Interface de triagem inteligente por texto
        └── styles/
            └── tokens.css               # Variáveis e tokens do Design System
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
