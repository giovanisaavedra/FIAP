# 🌾 FarmTech Solutions - Sistema de Previsão Agrícola
## Modelos de Regressão para Irrigação, Fertilização e Rendimento

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.3+-orange)](https://scikit-learn.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red)](https://streamlit.io/)
[![CRISP-DM](https://img.shields.io/badge/methodology-CRISP--DM-purple)](https://www.datascience-pm.com/crisp-dm-2/)

---

## 👥 Equipe do Projeto

### 👨‍🎓 Integrantes

| Nome              | RM       |
|-------------------|----------|
| Giovani Saavedra  | RM566797 |
| Marcio Elifas     | RM567871 |

### 👩‍🏫 Orientação

**Tutor(a):** Sabrina Otoni   
**Coordenador(a):** André Godoi Chiovatto 

---

## 📋 Sumário

1. [Visão Geral — Fase 7](#-visão-geral--fase-7)
2. [Vídeo Demonstrativo](#-vídeo-demonstrativo)
3. [Arquitetura](#-arquitetura)
4. [Fases Integradas](#-fases-integradas)
5. [Funcionalidades do Sistema](#-funcionalidades-do-sistema)
6. [Serviço de Mensageria AWS (SNS)](#-serviço-de-mensageria-aws-sns)
7. [Como Executar](#-como-executar)
8. [Estrutura de Pastas](#-estrutura-de-pastas)
9. [Metodologia (resumo CRISP-DM da Fase 4)](#-metodologia--resumo-crisp-dm-da-fase-4)
10. [Histórico de Lançamentos](#-histórico-de-lançamentos)
11. [Licença](#-licença)

---

## 🌱 Visão Geral — Fase 7

A **Fase 7** consolida em um único repositório o trabalho realizado ao longo
das fases anteriores do projeto FarmTech Solutions e o expõe num **dashboard
Streamlit** que serve como **Central de Comando** da fazenda inteligente:

- **Fase 1** — cálculos agronômicos (área de plantio, insumos), consulta
  meteorológica via API Open-Meteo e análise estatística em **R**.
- **Fase 2** — banco de dados relacional (SQLite) com CRUD completo e
  diagrama Entidade-Relacionamento.
- **Fase 3** — simulador IoT (ESP32/Wokwi) gravando leituras em tempo real
  e lógica de **irrigação automatizada** (histerese de umidade, bloqueio por
  pH, recomendação de fertirrigação).
- **Fase 4** — modelos de **Machine Learning** (regressão para irrigação,
  fertilização e rendimento) com EDA, modelagem e previsões interativas.
- **Fase 5** — segurança em nuvem: alertas via **AWS SNS** disparados pelas
  regras de negócio sobre o banco.
- **Fase 6** — **Visão Computacional** com YOLOv8 para detecção de
  intrusos/pragas em imagens da lavoura.

> Cada serviço pode ser usado individualmente, mas o foco da Fase 7 é a
> **integração**: uma única origem de dados (`farmtech_iot.db`), um único
> ponto de entrada (`streamlit run app.py`) e regras de negócio compartilhadas
> entre ML, irrigação, visão e alertas em nuvem.

---

## 📹 Vídeo Demonstrativo

📹 **Vídeo demonstrativo:** https://youtu.be/n5SvTvx0XWU

> O roteiro completo (com timestamps) está em
> [`docs/roteiro_video.md`](docs/roteiro_video.md).

---

## 🏗️ Arquitetura

```mermaid
flowchart LR
    subgraph CAMPO["🌾 Campo / Aquisição"]
        ESP[ESP32 / Wokwi]
        SIM[iot_simulator.py]
        IMG[📷 Imagens da lavoura]
    end

    subgraph PERSIST["💾 Persistência"]
        DB[(farmtech_iot.db<br/>SQLite)]
    end

    subgraph SERV["⚙️ services/"]
        F1[fase1_calculos<br/>fase1_clima<br/>fase1_analise.R]
        F3[fase3_irrigacao]
        F6[fase6_vision<br/>YOLOv8]
        AS[alert_service]
    end

    subgraph UI["🖥️ Dashboard Streamlit"]
        HOME[app.py — Central]
        P1[Fase 1 — Cálculos/Clima]
        P2[Fase 2 — CRUD/DER]
        P3[Fase 3 — Monitoramento IoT]
        P4[Fase 4 — Previsões ML]
        P6[Fase 6 — YOLO]
        P5[Fase 5 — Alertas AWS]
    end

    subgraph CLOUD["☁️ AWS"]
        SNS[Tópico SNS<br/>farmtech-alertas]
        MAIL[📧 E-mail / SMS]
    end

    ESP -- WokwiSerial --> SIM
    SIM --> DB
    IMG --> F6
    F1 --> P1
    F3 --> P3
    F6 --> P6
    DB --> P1
    DB --> P2
    DB --> P3
    DB --> P4
    DB --> P6
    DB --> AS
    AS --> SNS
    SNS --> MAIL
    HOME --> P1 & P2 & P3 & P4 & P5 & P6
```

---

## 🔗 Fases Integradas

| Fase | O que foi integrado | Onde está no repositório | Como executar |
|------|---------------------|--------------------------|----------------|
| **Fase 1** — Cálculos agronômicos, clima e análise R | • Área (retângulo/triângulo/círculo) e insumos por cultura<br/>• Open-Meteo (clima atual + 7 dias)<br/>• Resumo estatístico em **R base** | `services/fase1_calculos.py`<br/>`services/fase1_clima.py`<br/>`services/fase1_analise.R`<br/>`pages/1_🚜_Fase1_Calculos_e_Clima.py` | Central → **Abrir Fase 1** (abas Área e Insumos / Clima / Análise R). O R é **opcional**: sem `Rscript`, a página faz fallback com `pandas.describe()`. |
| **Fase 2** — Banco relacional + CRUD + DER | • Tabelas SQLite + migrations idempotentes<br/>• CRUD completo (consulta, inserir, atualizar, excluir)<br/>• Diagrama ER em Mermaid | `database_manager.py`<br/>`pages/2_🗄️_Fase2_CRUD_Banco.py`<br/>`docs/der_fase2.md` | Central → **Abrir CRUD** (5 abas: READ / CREATE / UPDATE / DELETE / MER-DER). |
| **Fase 3** — IoT + irrigação automatizada | • Simulador de sensores gravando no SQLite<br/>• `ControladorIrrigacao` (histerese 30–60 %, bloqueio por pH, fertirrigação)<br/>• LCD 16×2 simulado, histórico e timeline Plotly | `iot_simulator.py`<br/>`services/fase3_irrigacao.py`<br/>`pages/3_📡_Fase3_Monitoramento_IoT.py` | Central → **▶ Iniciar Simulador IoT** (subprocess) → **Abrir Monitoramento IoT**. Standalone: `python iot_simulator.py`. |
| **Fase 4** — ML e previsões | • EDA, modelagem preditiva (regressão linear/múltipla), pipeline e previsões | `pages/4_📈_Fase4_Analise_Exploratoria.py`<br/>`pages/5_🤖_Fase4_Modelagem_Preditiva.py`<br/>`pages/6_🔮_Fase4_Previsoes_Manual_IoT.py`<br/>`pages/7_🎛️_Fase4_Previsoes_Interativas.py`<br/>`pages/8_💾_Fase4_Pipeline_ML.py` | Central → cards do Fase 4 (3 links). Detalhes da Fase 4 ficam no resumo CRISP-DM mais abaixo. |
| **Fase 5** — Alertas em nuvem (AWS SNS) | • `ServicoAlertas` com regras de severidade<br/>• Antideduplicação por cooldown<br/>• Modo simulado quando o `.env` não tem ARN | `services/alert_service.py`<br/>`pages/10_🔔_Fase5_Alertas_AWS.py`<br/>`.env.example` | Central → **Abrir Alertas AWS** → **✉️ Enviar alerta de teste** ou **🔍 Verificar sensores**. |
| **Fase 6** — Visão Computacional | • `AnalisadorVisual` com YOLOv8 (lazy-loading)<br/>• Diagnóstico agrícola sobre classes COCO<br/>• Persistência em `analises_visuais` | `services/fase6_vision.py`<br/>`pages/9_📷_Fase6_Visao_Computacional.py`<br/>`assets/images/` | Central → **Abrir Visão Computacional** → **🔍 Analisar imagens da pasta**. |

---

## 🖥️ Funcionalidades do Sistema

Um tour guiado pelas telas da Fase 7, na ordem em que aparecem no menu
lateral do Streamlit. Cada subseção começa com prosa explicando o que a
tela resolve, traz **uma tela-destaque** em destaque inline e, quando
faz sentido, esconde as demais imagens da mesma fase atrás de um bloco
recolhível **📸 Mais telas desta fase**.

### 🏠 Central de Comando

A **Central de Comando** é a porta de entrada do sistema e o que o
usuário vê assim que executa `streamlit run app.py`. No topo, um painel
de status indica se o simulador IoT está ativo (com o PID do processo),
quantas leituras já foram registradas no banco e os cinco alertas mais
recentes — em tempo real, lendo direto do SQLite. Abaixo, uma grade de
cartões com cores próprias para cada Fase reúne todos os atalhos do
projeto: **▶ Iniciar Simulador IoT** e **⏹ Parar Simulador** controlam
o subprocess do `iot_simulator.py` sem travar o dashboard, enquanto os
links **st.page_link** levam direto às páginas de cada Fase. A ideia é
que o operador comece e termine o dia nessa tela, usando-a como HUD da
fazenda inteligente.

![Central de Comando: inicia o simulador IoT e dá acesso a todas as fases, com painel de status (leituras registradas e alertas recentes).](docs/screenshots/00-01_central_comando.png)

<details>
<summary>📸 Mais telas desta fase (2 imagens)</summary>

![Central de Comando — tela 2](docs/screenshots/00-02_central_comando.png)
![Central de Comando — tela 3](docs/screenshots/00-03_central_comando.png)

</details>

### 🚜 Fase 1 — Cálculos, Clima e Análise R

A página da **Fase 1** consolida três utilidades agronômicas que antes
moravam em scripts soltos. A primeira aba calcula **área de plantio**
(retângulo, triângulo ou círculo/pivô central) e estima a quantidade do
insumo principal por cultura — milho, soja, café ou cana — registrando
o resultado num mini-CRUD em `data/fase1_calculos.csv`. A segunda aba
consulta a API pública **Open-Meteo** com latitude e longitude
informadas pelo usuário (default Porto Alegre), exibe métricas atuais e
um gráfico Plotly com a previsão de sete dias, gravando o retorno em
`data/clima_atual.csv`. A terceira aba executa o script
`services/fase1_analise.R` via `Rscript` sobre esse CSV e mostra o
relatório estatístico (média, desvio padrão, quartis); se o `R` não
estiver instalado, a página detecta a ausência com `shutil.which` e
oferece um fallback transparente com `pandas.describe()`, mantendo o
fluxo intacto para quem não tem o ambiente R configurado.

![Fase 1: cálculo de área de plantio e estimativa de insumos por cultura.](docs/screenshots/01-01_fase1_calculos.png)

<details>
<summary>📸 Mais telas desta fase (1 imagem)</summary>

![Fase 1 — tela 2](docs/screenshots/01-02_fase1_calculos.png)

</details>

### 🗄️ Fase 2 — Banco de Dados (CRUD)

A **Fase 2** expõe o banco SQLite (`farmtech_iot.db`) para operação
manual por meio de cinco abas: **READ** lista qualquer tabela com
contagem total e filtros específicos para `leituras_sensores` (sensor +
intervalo de datas); **CREATE** abre dois formulários (cadastrar sensor
e inserir leitura manual com valores realistas); **UPDATE** permite
mudar o status de um sensor entre `ativo/inativo/manutencao` e resolver
alertas pendentes com um clique; **DELETE** remove leituras e sensores
exigindo checkbox de confirmação, com cascade controlado quando o
sensor tem leituras associadas. A última aba, **MER/DER**, mostra o
diagrama Entidade-Relacionamento em Mermaid junto com o DDL completo
das sete tabelas — o mesmo diagrama fica versionado em
[`docs/der_fase2.md`](docs/der_fase2.md) e é renderizado pelo GitHub.
Todas as operações abrem conexão SQLite curta com `timeout=10`, então a
página convive bem com o simulador IoT gravando em paralelo.

![Fase 2: operações CRUD sobre o banco SQLite, compatível com o simulador IoT gravando em paralelo.](docs/screenshots/02_fase2_crud.png)

### 📡 Fase 3 — Monitoramento IoT e Irrigação

A página de **Monitoramento IoT** é onde a fazenda virtual ganha vida.
No topo, métricas agregadas mostram quantos sensores estão ativos, o
total de leituras e há quanto tempo chegou a mais recente. Logo abaixo,
a seção **💧 Irrigação Automatizada (Fase 3)** aplica o
`ControladorIrrigacao` à última leitura de cada sensor e desenha um
card por sensor com 🟢 LIGAR / 🔴 DESLIGAR / 🚫 BLOQUEADA, motivo da
decisão e recomendação. A regra usa histerese de 30 a 60 % para evitar
liga-desliga e bloqueia a bomba quando o pH cai fora de 5,5–7,5
(sugerindo calcário ou enxofre). Um botão registra todas as decisões em
`historico_irrigacao` e uma timeline Plotly mostra a evolução das ações
ao longo do tempo. O **display LCD 16×2** simulado fecha a seção
emulando o que sairia no firmware ESP32 da Fase 3. Logo abaixo, um
toggle conecta tudo à Fase 5: **🔔 Alertas AWS automáticos**, que chama
`ServicoAlertas.verificar_e_alertar()` a cada recarga.

![Fase 3: métricas em tempo real dos sensores e alertas ativos por severidade.](docs/screenshots/03_fase3_iot.png)

### 📈 Fase 4 — Análise Exploratória (EDA)

A página de **Análise Exploratória** dissecou os 2.200 registros do
dataset de treino antes que qualquer modelo fosse treinado. A interface
oferece dezenas de visualizações interativas — histogramas, boxplots,
matrizes de dispersão, mapas de correlação e gráficos por cultura — que
ajudam a entender a distribuição de cada feature e a identificar gaps
de qualidade. É a etapa "Data Understanding" do CRISP-DM materializada
na UI: o usuário troca a variável-alvo ou o filtro de cultura e os
gráficos se atualizam instantaneamente, viabilizando a inspeção
exaustiva que justificou as 36 features derivadas usadas na modelagem.

![Fase 4 (EDA): matriz de dispersão de nutrientes vs. rendimento, entre dezenas de visualizações exploratórias.](docs/screenshots/04-27_fase04-EDA.png)

<details>
<summary>📸 Mais telas desta fase (42 imagens)</summary>

![EDA — visualização 1](docs/screenshots/04-01_fase04-EDA.png)
![EDA — visualização 2](docs/screenshots/04-02_fase04-EDA.png)
![EDA — visualização 3](docs/screenshots/04-03_fase04-EDA.png)
![EDA — visualização 4](docs/screenshots/04-04_fase04-EDA.png)
![EDA — visualização 5](docs/screenshots/04-05_fase04-EDA.png)
![EDA — visualização 6](docs/screenshots/04-06_fase04-EDA.png)
![EDA — visualização 7](docs/screenshots/04-07_fase04-EDA.png)
![EDA — visualização 8](docs/screenshots/04-08_fase04-EDA.png)
![EDA — visualização 9](docs/screenshots/04-09_fase04-EDA.png)
![EDA — visualização 10](docs/screenshots/04-10_fase04-EDA.png)
![EDA — visualização 11](docs/screenshots/04-11_fase04-EDA.png)
![EDA — visualização 12](docs/screenshots/04-12_fase04-EDA.png)
![EDA — visualização 13](docs/screenshots/04-13_fase04-EDA.png)
![EDA — visualização 14](docs/screenshots/04-14_fase04-EDA.png)
![EDA — visualização 15](docs/screenshots/04-15_fase04-EDA.png)
![EDA — visualização 16](docs/screenshots/04-16_fase04-EDA.png)
![EDA — visualização 17](docs/screenshots/04-17_fase04-EDA.png)
![EDA — visualização 18](docs/screenshots/04-18_fase04-EDA.png)
![EDA — visualização 19](docs/screenshots/04-19_fase04-EDA.png)
![EDA — visualização 20](docs/screenshots/04-20_fase04-EDA.png)
![EDA — visualização 21](docs/screenshots/04-21_fase04-EDA.png)
![EDA — visualização 22](docs/screenshots/04-22_fase04-EDA.png)
![EDA — visualização 23](docs/screenshots/04-23_fase04-EDA.png)
![EDA — visualização 24](docs/screenshots/04-24_fase04-EDA.png)
![EDA — visualização 25](docs/screenshots/04-25_fase04-EDA.png)
![EDA — visualização 26](docs/screenshots/04-26_fase04-EDA.png)
![EDA — visualização 28](docs/screenshots/04-28_fase04-EDA.png)
![EDA — visualização 29](docs/screenshots/04-29_fase04-EDA.png)
![EDA — visualização 30](docs/screenshots/04-30_fase04-EDA.png)
![EDA — visualização 31](docs/screenshots/04-31_fase04-EDA.png)
![EDA — visualização 32](docs/screenshots/04-32_fase04-EDA.png)
![EDA — visualização 33](docs/screenshots/04-33_fase04-EDA.png)
![EDA — visualização 34](docs/screenshots/04-34_fase04-EDA.png)
![EDA — visualização 35](docs/screenshots/04-35_fase04-EDA.png)
![EDA — visualização 36](docs/screenshots/04-36_fase04-EDA.png)
![EDA — visualização 37](docs/screenshots/04-37_fase04-EDA.png)
![EDA — visualização 38](docs/screenshots/04-38_fase04-EDA.png)
![EDA — visualização 39](docs/screenshots/04-39_fase04-EDA.png)
![EDA — visualização 40](docs/screenshots/04-40_fase04-EDA.png)
![EDA — visualização 41](docs/screenshots/04-41_fase04-EDA.png)
![EDA — visualização 42](docs/screenshots/04-42_fase04-EDA.png)
![EDA — visualização 43](docs/screenshots/04-43_fase04-EDA.png)

</details>

### 🤖 Fase 4 — Modelagem Preditiva

A **Modelagem Preditiva** treina os três modelos centrais do projeto —
**irrigação, fertilização e rendimento** — sobre 2.200 registros e 51
features (13 originais + 36 derivadas via *feature engineering* +
dummies de cultura). O painel apresenta lado a lado as métricas MAE,
RMSE e R² de Regressão Linear Múltipla e Regressão Polinomial,
permitindo que o usuário escolha qual versão fica em sessão. Os modelos
treinados são salvos em `st.session_state` para uso imediato pelas
páginas de previsão, fechando o ciclo "Modeling → Evaluation →
Deployment" do CRISP-DM dentro de uma única página interativa.

![Fase 4: treinamento dos três modelos (irrigação, fertilização, rendimento) sobre 2.200 registros e 51 features.](docs/screenshots/05-01_fase04-ModPred.png)

<details>
<summary>📸 Mais telas desta fase (1 imagem)</summary>

![Modelagem Preditiva — tela 2](docs/screenshots/05-02_fase04-ModPred.png)

</details>

### 🔮 Fase 4 — Previsões (Manual/IoT)

A página de **Previsões (Manual/IoT)** oferece dois modos
complementares. No modo **Manual**, o usuário preenche um formulário
com parâmetros de solo (N, P, K, pH), clima (temperatura, umidade,
chuva) e cultura — ideal para simulações de cenário e planos de safra.
No modo **IoT**, a página lê automaticamente a leitura mais recente de
cada sensor cadastrado no banco SQLite, aplica os três modelos sobre
esses valores e devolve recomendações imediatas para cada talhão
monitorado, fechando o elo entre a infraestrutura IoT da Fase 3 e o
motor analítico da Fase 4.

![Fase 4: previsões em dois modos — entrada manual ou dados ao vivo dos sensores.](docs/screenshots/06-01_fase04-ManualIOT.png)

<details>
<summary>📸 Mais telas desta fase (1 imagem)</summary>

![Previsões Manual/IoT — tela 2](docs/screenshots/06-02_fase04-ManualIOT.png)

</details>

### 🎛️ Fase 4 — Previsões Interativas

A página de **Previsões Interativas** convida o usuário a explorar o
espaço de decisão arrastando sliders e observando o efeito imediato
sobre as três variáveis-alvo: volume de irrigação, fertilização N
(também P e K) e rendimento esperado. Cada predição vem acompanhada de
uma recomendação textual contextual — por exemplo, "aumentar a
irrigação para X L/m²/semana" ou "reduzir a dose de N para evitar
lixiviação" — facilitando a leitura por gestores que não dominam o
detalhe estatístico mas precisam tomar decisão rápida com base nos
modelos da Fase 4.

![Fase 4: resultados interativos de volume de irrigação, fertilização N e rendimento esperado, com recomendações.](docs/screenshots/07-03_fase04-PrevInterativas.png)

<details>
<summary>📸 Mais telas desta fase (4 imagens)</summary>

![Previsões Interativas — tela 1](docs/screenshots/07-01_fase04-PrevInterativas.png)
![Previsões Interativas — tela 2](docs/screenshots/07-02_fase04-PrevInterativas.png)
![Previsões Interativas — tela 4](docs/screenshots/07-04_fase04-PrevInterativas.png)
![Previsões Interativas — tela 5](docs/screenshots/07-05_fase04-PrevInterativas.png)

</details>

### 💾 Fase 4 — Pipeline de ML (CRISP-DM)

A página **Pipeline ML** funciona como documentação executiva do
processo de modelagem da Fase 4, organizada nos seis estágios do
**CRISP-DM**: *Business Understanding*, *Data Understanding*, *Data
Preparation*, *Modeling*, *Evaluation* e *Deployment*. Para cada
estágio, registramos as decisões tomadas, métricas relevantes, gráficos
de avaliação e amostras de dados — é a evidência metodológica que
torna o projeto auditável e reprodutível, e ponto de partida para
entender por que cada decisão de feature engineering foi tomada.

![Fase 4: documentação executiva do pipeline seguindo a metodologia CRISP-DM.](docs/screenshots/08-01_fase04-PipelineML.png)

<details>
<summary>📸 Mais telas desta fase (14 imagens)</summary>

![Pipeline ML — tela 2](docs/screenshots/08-02_fase04-PipelineML.png)
![Pipeline ML — tela 3](docs/screenshots/08-03_fase04-PipelineML.png)
![Pipeline ML — tela 4](docs/screenshots/08-04_fase04-PipelineML.png)
![Pipeline ML — tela 5](docs/screenshots/08-05_fase04-PipelineML.png)
![Pipeline ML — tela 6](docs/screenshots/08-06_fase04-PipelineML.png)
![Pipeline ML — tela 7](docs/screenshots/08-07_fase04-PipelineML.png)
![Pipeline ML — tela 8](docs/screenshots/08-08_fase04-PipelineML.png)
![Pipeline ML — tela 9](docs/screenshots/08-09_fase04-PipelineML.png)
![Pipeline ML — tela 10](docs/screenshots/08-10_fase04-PipelineML.png)
![Pipeline ML — tela 11](docs/screenshots/08-11_fase04-PipelineML.png)
![Pipeline ML — tela 12](docs/screenshots/08-12_fase04-PipelineML.png)
![Pipeline ML — tela 13](docs/screenshots/08-13_fase04-PipelineML.png)
![Pipeline ML — tela 14](docs/screenshots/08-14_fase04-PipelineML.png)
![Pipeline ML — tela 15](docs/screenshots/08-15_fase04-PipelineML.png)

</details>

### 📷 Fase 6 — Visão Computacional (YOLO)

A página de **Visão Computacional** aceita uploads múltiplos de imagens
da lavoura (`.jpg`, `.jpeg`, `.png`) que são gravadas em
`assets/images/`. Um clique em **🔍 Analisar imagens da pasta** roda o
`AnalisadorVisual` com lazy-loading do **YOLOv8n** — na primeira
execução um `st.spinner` informa que o peso (~6 MB) está sendo baixado.
Para cada imagem o sistema mostra, lado a lado, a foto original e a
versão anotada com as caixas das detecções; abaixo aparece uma tabela
com classe, confiança e bbox. A camada de **diagnóstico agrícola**
interpreta as classes do COCO em chave de campo: animais como vaca,
ovelha ou pássaro disparam alerta vermelho de "possível praga/animal na
lavoura"; nenhuma detecção devolve verde de "lavoura aparentemente
saudável". Tudo é persistido em `analises_visuais` e listado num
histórico no final da página, pronto para alimentar a Fase 5.

![Fase 6: detecção YOLOv8 em imagem de lavoura — bando de aves identificado como possível praga (original × anotada).](docs/screenshots/09-03_fase06-VisaoComp.png)

<details>
<summary>📸 Mais telas desta fase (8 imagens)</summary>

![Visão Computacional — tela 1](docs/screenshots/09-01_fase06-VisaoComp.png)
![Visão Computacional — tela 2](docs/screenshots/09-02_fase06-VisaoComp.png)
![Visão Computacional — tela 4](docs/screenshots/09-04_fase06-VisaoComp.png)
![Visão Computacional — tela 5](docs/screenshots/09-05_fase06-VisaoComp.png)
![Visão Computacional — tela 6](docs/screenshots/09-06_fase06-VisaoComp.png)
![Visão Computacional — tela 7](docs/screenshots/09-07_fase06-VisaoComp.png)
![Visão Computacional — tela 8](docs/screenshots/09-08_fase06-VisaoComp.png)
![Visão Computacional — tela 9](docs/screenshots/09-09_fase06-VisaoComp.png)

</details>

### 🔔 Fase 5 — Alertas em Nuvem (AWS SNS)

Os alertas em nuvem (Fase 5) têm seção dedicada logo abaixo, com os
prints reais do dashboard SNS, a tabela de regras e a prova de entrega
ponta a ponta — veja
[🔔 Serviço de Mensageria AWS (SNS)](#-serviço-de-mensageria-aws-sns).

---

## 🔔 Serviço de Mensageria AWS (SNS)

A Fase 5 (consolidada na Fase 7) implementa **notificações em nuvem**
disparadas pelas regras de negócio sobre o banco. O fluxo é:

> Sensor IoT → SQLite → `ServicoAlertas.verificar_e_alertar()` → AWS SNS
> → assinaturas confirmadas (e-mail/SMS).

### Passo a passo (do console AWS ao dashboard)

A trilha começa na infraestrutura provisionada na própria AWS e termina
na evidência humana — o e-mail chegando na caixa do destinatário.

0. **Console AWS SNS** — tópico `farmtech-alertas` provisionado, com
   ARN e proprietário visíveis, e assinatura de e-mail no estado
   *Confirmado*. É a fundação da Fase 5 sobre a qual o
   `ServicoAlertas` opera.
   ![Console AWS SNS: tópico farmtech-alertas criado (ARN e proprietário visíveis) e assinatura de e-mail com status Confirmado.](docs/screenshots/10-06_aws_console_topico.png)

1. **Painel de status** do dashboard — confirma que a página
   `🔔 Alertas AWS` está conectada ao tópico, mostra o ARN mascarado
   (apenas os 12 últimos caracteres) e o número de assinaturas
   confirmadas.
   ![Painel de status: dashboard conectado ao tópico SNS, com 1 assinatura confirmada e ARN mascarado.](docs/screenshots/10-01_fase05-AlertasAWS.png)

2. **Regras de alerta** com as condições, severidades e **ações
   corretivas** que o grupo definiu — espelha a tabela publicada
   logo abaixo.
   ![Regras de alerta implementadas com as ações corretivas definidas pelo grupo.](docs/screenshots/10-04_fase05-AlertasAWS.png)

3. **Histórico de envios** — cada publicação via `boto3` é registrada
   em `alertas` com `enviado_sns = 1` e fica auditável dentro do
   dashboard, com cabeçalho de severidade (`🔴 CRÍTICO` / `🟠 ALTO`),
   contexto e ação corretiva.
   ![Histórico de alertas publicados no SNS.](docs/screenshots/10-02_fase05-AlertasAWS.png)

4. **E-mails recebidos** na caixa do destinatário inscrito — **prova
   de entrega ponta a ponta**, do sensor IoT até a notificação humana.
   ![E-mails de alerta recebidos na caixa de entrada (prova de entrega ponta a ponta).](docs/screenshots/10-05_fase05-AlertasAWS.png)

5. **Diagrama do pipeline** com o fluxo completo: sensor → regra →
   SNS → e-mail/SMS, conforme implementado em
   `services/alert_service.py`.
   ![Diagrama do pipeline ponta a ponta (sensor → regra → SNS → e-mail).](docs/screenshots/10-03_fase05-AlertasAWS.png)


### Tabela de regras de alerta (definidas pelo grupo)

| Origem | Condição | Severidade | Ação Corretiva |
|--------|----------|-----------:|-----------------|
| `leituras_sensores` | `soil_moisture < ALERTA_UMIDADE_CRITICA` (default 20 %) | 🔴 **CRÍTICO** | "Acionar irrigação imediatamente no setor do sensor X" |
| `leituras_sensores` | `soil_pH < ALERTA_PH_MIN` ou `> ALERTA_PH_MAX` (5,0 / 8,0) | 🟠 **ALTO** | "Aplicar corretivo de solo: calcário (subir pH) ou enxofre (baixar pH)" |
| `leituras_sensores` | `temperature_C > ALERTA_TEMP_MAX` (40 °C) | 🟠 **ALTO** | "Risco de estresse térmico — antecipar irrigação" |
| `analises_visuais` | status contém "praga" (animais/pássaros detectados) | 🔴 **CRÍTICO** | "Inspecionar talhão e avaliar aplicação de defensivo / MIP" |

**Antideduplicação**: cada par `(sensor, tipo_alerta)` só é publicado
novamente após `ALERTA_COOLDOWN_MINUTOS` (default 30). O histórico fica em
`alertas.enviado_sns = 1`.

**Segurança**: credenciais AWS ficam **exclusivamente** em `.env`
(ignorado pelo Git). O ARN aparece mascarado na UI (apenas os 12 últimos
caracteres).

---

## ⚙️ Como Executar

### 1. Clonar e preparar o ambiente

```bash
git clone <repo-url> farmtech-fase07
cd farmtech-fase07

python -m venv venv
source venv/bin/activate          # macOS / Linux
# .\venv\Scripts\activate         # Windows PowerShell

pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configurar `.env`

```bash
cp .env.example .env
```

Edite `.env` com seus valores reais:

| Variável | Para que serve | Exemplo |
|----------|----------------|---------|
| `AWS_REGION` | Região do tópico SNS | `us-east-1` |
| `SNS_TOPIC_ARN` | ARN do tópico `farmtech-alertas`. Vazio = modo simulado. | `arn:aws:sns:us-east-1:000…:farmtech-alertas` |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | Credenciais IAM com permissão `sns:Publish` e `sns:GetTopicAttributes` | — |
| `ALERTA_UMIDADE_CRITICA` | Umidade do solo (%) que dispara alerta CRÍTICO | `20` |
| `ALERTA_PH_MIN` / `ALERTA_PH_MAX` | Faixa de pH aceitável | `5.0` / `8.0` |
| `ALERTA_TEMP_MAX` | Temperatura (°C) que dispara alerta ALTO | `40` |
| `ALERTA_COOLDOWN_MINUTOS` | Janela para não reenviar o mesmo alerta | `30` |
| `DB_PATH` | Caminho do SQLite | `farmtech_iot.db` |
| `CLIMA_LAT_DEFAULT` / `CLIMA_LON_DEFAULT` | Coordenadas default da página de clima | `-30.03` / `-51.23` |

> O banco SQLite é **criado automaticamente** na primeira execução — não
> é necessário rodar nenhum script de bootstrap.

### 3. Subir o dashboard

```bash
python -m streamlit run app.py
```

Abra `http://localhost:8501`. A Central de Comando lista todos os serviços.

### 4. Comandos por serviço

| Serviço | Como acionar |
|---------|--------------|
| **Simulador IoT (subprocess)** | Botão **▶ Iniciar Simulador IoT** na Central. |
| **Simulador IoT (standalone)** | `python iot_simulator.py` em outro terminal. |
| **Fase 1 — Análise R** *(opcional)* | Requer `Rscript` no PATH. Sem R, a página faz fallback em Python. |
| **Fase 6 — YOLO** | Primeiro clique em **🔍 Analisar imagens** baixa `yolov8n.pt` (~6 MB). |
| **Alertas AWS** | Botão **✉️ Enviar alerta de teste** na página *Alertas AWS*. |

---

## 📁 Estrutura de Pastas

```
fase07-cap01-sistema/
├── app.py                              # Central de Comando — Fase 7
├── utils.py                            # render_header / render_sidebar
├── iot_simulator.py                    # Simulador IoT (Fase 3)
├── database_manager.py                 # SQLite + CRUD + migrations
├── farmtech_iot.db                     # Banco local (ignorado pelo Git)
├── requirements.txt
├── .env                                # Credenciais (ignorado pelo Git)
├── .env.example                        # Template versionado
│
├── pages/                              # Páginas Streamlit (ordem do menu lateral)
│   ├── 1_🚜_Fase1_Calculos_e_Clima.py
│   ├── 2_🗄️_Fase2_CRUD_Banco.py
│   ├── 3_📡_Fase3_Monitoramento_IoT.py  # + Irrigação Fase 3 + toggle Alertas
│   ├── 4_📈_Fase4_Analise_Exploratoria.py
│   ├── 5_🤖_Fase4_Modelagem_Preditiva.py
│   ├── 6_🔮_Fase4_Previsoes_Manual_IoT.py
│   ├── 7_🎛️_Fase4_Previsoes_Interativas.py
│   ├── 8_💾_Fase4_Pipeline_ML.py
│   ├── 9_📷_Fase6_Visao_Computacional.py
│   ├── 10_🔔_Fase5_Alertas_AWS.py
│   └── 11_ℹ️_Sobre_o_Projeto.py
│
├── services/                           # Serviços integrados Fases 1, 3, 5, 6
│   ├── __init__.py
│   ├── fase1_calculos.py
│   ├── fase1_clima.py
│   ├── fase1_analise.R
│   ├── fase3_irrigacao.py
│   ├── fase6_vision.py
│   └── alert_service.py
│
├── assets/
│   └── images/                         # Imagens da lavoura (entrada do YOLO)
│
├── data/                               # CSV/insumos gerados pelo dashboard
│   ├── clima_atual.csv
│   ├── fase1_calculos.csv
│   ├── processed/
│   └── raw/
│
└── docs/
    ├── der_fase2.md                    # Diagrama ER (Mermaid)
    ├── roteiro_video.md                # Roteiro do vídeo (Fase 7)
    └── aws/                            # Prints do console AWS
        ├── 01_topico_criado.png
        ├── 02_assinatura_confirmada.png
        ├── 03_publicacao_boto3.png
        ├── 04_email_recebido.png
        └── 05_metricas_sns.png
```

---

## 📊 Metodologia — resumo CRISP-DM da Fase 4

A modelagem preditiva (regressão para irrigação / fertilização / rendimento)
seguiu integralmente o **CRISP-DM**, em 6 etapas:

1. **Business Understanding** — definição dos três alvos de regressão e
   métricas (MAE, RMSE, R²) com baselines competitivos da literatura.
2. **Data Understanding** — análise exploratória de 2.200+ registros
   (dataset `dataset_final_farmtech.csv`), validação de qualidade e
   identificação de gaps.
3. **Data Preparation** — feature engineering (45+ variáveis derivadas),
   geração sintética de NPK por cultura e *data augmentation*.
4. **Modeling** — Regressão Linear, Múltipla e pipelines Scikit-Learn.
5. **Evaluation** — comparação de métricas, validação cruzada e *holdout*.
6. **Deployment** — exportação dos modelos para uso nas páginas de
   previsões manual/interativa.

> Os detalhes técnicos completos da Fase 4 (notebooks, gráficos, tabelas
> de métricas) permanecem documentados nas próprias páginas do dashboard
> (**EDA**, **Modelagem Preditiva**, **Pipeline ML**, **Sobre o Projeto**)
> e foram **mantidos** intactos nesta Fase 7.

---

## 🗃 Histórico de Lançamentos

### 🚀 v3.0.0 — 07/06/2026 — Fase 7
- 🏠 Central de Comando (`app.py`) com cards, status do simulador
  (subprocess + PID em `st.session_state`) e contadores do banco.
- 🚜 Fase 1: cálculos agronômicos + Open-Meteo + análise R (fallback Python).
- 🗄️ Fase 2: CRUD completo, DER em Mermaid e migrations idempotentes
  (`enviado_sns`, `historico_irrigacao`, `analises_visuais`).
- 💧 Fase 3: `ControladorIrrigacao` com histerese, LCD 16×2 simulado e
  timeline Plotly.
- 📷 Fase 6: `AnalisadorVisual` (YOLOv8) + diagnóstico agrícola sobre COCO.
- 🔔 Fase 5: `ServicoAlertas` (AWS SNS) com cooldown e modo simulado.
- 🔒 Segurança: `.env` + `.env.example`, ARN mascarado, credenciais nunca
  logadas.

### 🚀 v0.6.0 — 22/11/2024
- 📄 Documentação final
- 🎥 Vídeo de apresentação

### 🚀 v0.5.0 — 21/11/2024
- 💾_PipelineML

### 🧠 v0.4.0 — 20/11/2024
- 🔮_Fazer Previsões

### 🤖 v0.3.0 — 19/11/2024
- 🔮 _Modelagem Preditiva

### 🎮 v0.2.0 — 18/11/2024
- Criação do dataset
- 📈_Análise Exploratória (EDA)

### 🗄️ v0.1.0 — 17/11/2024
- ✨ Estrutura inicial
- 📂 Organização de arquivos
- 🛠 Configuração do ambiente

---

## 📋 Licença

<div align="center">


🌾 FarmTech Solutions - Sistema de Previsão Agrícola foi desenvolvido por Giovani Agostini Saavedra e Márcio Elifas e está licenciado sob Attribution 4.0 International (CC BY 4.0).

Desenvolvido como projeto acadêmico para FIAP - Faculdade de Informática e Administração Paulista.

Turma: 1TIAOS
Disciplina: Fase 07 - Cap 1 - Sistema Integrado FarmTech Solutions
Ano: 2026.1

</div>

---

**Projeto desenvolvido para FIAP — Fase 7 (2026.1)**  
**Tema:** Sistema Integrado de Gestão Agrícola Inteligente  
**Equipe:** Giovani Saavedra (RM566797) e Marcio Elifas (RM567871).

---

<div align="center">

**Desenvolvido com 💚 para FIAP - Fase 7**

*Agricultura de Precisão com IA, IoT, Visão Computacional e AWS* 🌾

</div>

---

**Última atualização:** Junho 2026  
**Versão:** 3.0.0  
**Metodologia:** CRISP-DM  
**Curso:** FIAP - Inteligência Artificial
