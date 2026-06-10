# 🎥 Roteiro de Vídeo — FarmTech Solutions Fase 7

📹 **Vídeo publicado:** https://youtu.be/n5SvTvx0XWU

Duração-alvo: **até 10 minutos**. Cada bloco lista **o que mostrar** na tela
e a **frase-chave** a dizer. Ajuste o tom conforme o seu estilo, mas mantenha
o ritmo dos timestamps para caber na duração.

---

## 0:00 — 1:00 · Abertura e Arquitetura

**Tela:**
- Slide/print do diagrama Mermaid que está no README (seção "🏗️ Arquitetura").
- Sobre o slide, deixar visível: nome do grupo, RMs, turma 1TIAOS - FIAP.

**Falar:**
> "Olá! Somos o Grupo 37 — Giovani Saavedra e Marcio Elifas,
> da 1TIAOS da FIAP. Neste vídeo apresentamos a **Fase 7** da FarmTech
> Solutions, que **integra em um único sistema** as Fases 1 a 6 do projeto:
> cálculos agronômicos, banco relacional, IoT e irrigação automatizada, ML,
> visão computacional e alertas em nuvem. A arquitetura é essa: sensores
> alimentam o SQLite, os serviços consomem o banco, o dashboard Streamlit
> coordena tudo e o `alert_service` publica eventos críticos no AWS SNS."

---

## 1:00 — 1:45 · Central de Comando + simulador IoT

**Tela:**
- `streamlit run app.py` no terminal e, em seguida, a Central no navegador.
- Mostrar o painel de **Status do Sistema** (simulador parado, contagem de
  leituras, alertas) e os 6 cards de serviços.
- Clicar em **▶ Iniciar Simulador IoT** → status muda para 🟢 + PID.

**Falar:**
> "A Central de Comando é a porta de entrada. Daqui inicio o simulador IoT
> com um clique — repare que ele roda em **subprocess** sem travar o
> Streamlit. Os cards levam para cada Fase integrada."

---

## 1:45 — 3:15 · Fase 1: Área e insumos, Clima (API), Análise em R

**Tela:**
- Abrir **🚜 Fase 1**, aba **Área e Insumos**: cultura *milho*, retângulo
  100 × 250 m → mostrar as métricas (25 000 m², 2,5 ha, 875 kg de NPK).
- Aba **Clima (API)**: lat/lon default (Porto Alegre), **🔄 Buscar clima** →
  exibir métricas atuais e o gráfico Plotly da previsão 7 dias.
- Aba **Análise Estatística (R)**: **▶ Executar análise em R** → mostrar o
  `st.code` com média/desvio/quartis. Comentar o fallback Python.

**Falar:**
> "Na Fase 1 calculo área e insumos para uma cultura, consulto o clima na
> **Open-Meteo** em tempo real e, no final, rodo uma análise estatística em
> **R base** sobre o CSV de clima que acabei de salvar. Se o R não estiver
> instalado, a página faz fallback para `pandas.describe` — então funciona
> em qualquer máquina."

---

## 3:15 — 4:15 · Fase 2: CRUD + DER

**Tela:**
- Abrir **🗄️ CRUD**, aba **Consultar (READ)**: trocar entre tabelas, filtrar
  `leituras_sensores` por data.
- Aba **Inserir (CREATE)**: cadastrar um sensor de teste.
- Aba **Atualizar (UPDATE)**: alterar status do sensor para *manutenção*.
- Aba **Excluir (DELETE)**: demonstrar checkbox de confirmação obrigatório.
- Aba **MER/DER**: mostrar o diagrama Mermaid e o DDL.

**Falar:**
> "A Fase 2 expõe um **CRUD completo** sobre o banco SQLite, com
> antideduplicação, cascade controlado na exclusão e o **diagrama
> Entidade-Relacionamento** versionado em `docs/der_fase2.md`."

---

## 4:15 — 5:30 · Fase 3: Irrigação automatizada + LCD

**Tela:**
- Abrir **3 – 📡 Fase3 Monitoramento IoT** → rolar até a seção
  **💧 Irrigação Automatizada (Fase 3)**.
- Mostrar os cards por sensor (🟢/🔴/🚫), o **display LCD 16×2** simulado e a
  timeline Plotly das decisões.
- Clicar em **⚙️ Avaliar e registrar agora** e mostrar a tabela
  `historico_irrigacao` ganhando uma linha nova.

**Falar:**
> "A Fase 3 traz a lógica de **irrigação inteligente**: histerese de
> umidade (30–60 %), bloqueio quando o pH está fora da faixa ideal, e
> recomendação de fertirrigação se o NPK estiver baixo. Cada decisão é
> persistida e visualizada na timeline — é a réplica em software do firmware
> ESP32 da Fase 3."

---

## 5:30 — 6:45 · Fase 4: Previsões ML

**Tela:**
- Abrir uma das páginas de Fase 4 (sugiro
  **🔮 Previsões interativas**): inserir parâmetros, gerar previsão de
  irrigação/fertilização/rendimento e mostrar os resultados.
- Comentar rapidamente a metodologia CRISP-DM (link para a seção do README).

**Falar:**
> "A Fase 4 contém os modelos de regressão treinados sob a metodologia
> **CRISP-DM**. Aqui faço uma previsão interativa: ajusto N, P, K, pH e
> clima e o modelo devolve as três variáveis-alvo — irrigação, fertilização
> e rendimento esperado."

---

## 6:45 — 8:00 · Fase 6: Visão computacional (YOLO)

**Tela:**
- Abrir **📷 Visão Computacional** → confirmar as imagens em `assets/images/`.
- Clicar em **🔍 Analisar imagens da pasta** → mostrar `st.spinner`
  ("Baixando modelo YOLO...") na primeira execução.
- Destacar dois resultados:
  - `corn_field_liechtenstein.jpg` → 🌱 "Lavoura saudável" (verde).
  - `geese_in_crops.jpg` → 21 pássaros detectados → ⚠️ **ALTA** "Possível
    praga/animal na lavoura" (vermelho).
- Rolar até **📜 Histórico de Análises** para mostrar a tabela populada.

**Falar:**
> "A Fase 6 roda **YOLOv8** sobre as fotos da lavoura. Numa imagem de
> milharal limpo, ele acerta dizendo 'lavoura saudável'. Numa imagem com
> gansos invadindo o campo, dispara o alerta de **praga** com severidade
> alta — esse mesmo alerta vai virar e-mail na próxima seção."

---

## 8:00 — 9:15 · Alertas AWS: teste, e-mail e console SNS

**Tela:**
- Abrir **🔔 Alertas AWS**: mostrar o painel de status (✅ "Conectado ao
  tópico SNS", ARN **mascarado**, "assinaturas confirmadas: 1").
- Clicar em **✉️ Enviar alerta de teste** → mostrar o `MessageId`.
- Alternar para a caixa de e-mail e mostrar o e-mail chegando com cabeçalho
  `[FarmTech] 🟠 ALTO — …`.
- Mostrar rapidamente o **console AWS SNS** (aba *Monitoring* / métricas).
- Voltar à página, clicar em **🔍 Verificar sensores e enviar alertas** e
  mostrar o resumo (enviados / cooldown).

**Falar:**
> "A Fase 5 fecha o ciclo: o `ServicoAlertas` lê o banco, aplica as regras
> que combinamos com o agrônomo — umidade crítica, pH fora da faixa,
> temperatura alta, praga detectada pela visão — e publica no tópico
> **AWS SNS** `farmtech-alertas`. O e-mail chega na caixa do produtor com
> a **ação corretiva** já recomendada. A antideduplicação garante que o
> mesmo alerta não vire spam — por isso o segundo clique cai em *cooldown*."

---

## 9:15 — 10:00 · README, GitHub e encerramento

**Tela:**
- Abrir o repositório no GitHub: mostrar `README.md` renderizando o
  diagrama Mermaid e os prints da AWS em `docs/aws/`.
- Mostrar a estrutura de pastas (`services/`, `pages/`, `docs/`).
- Mostrar o arquivo `.env.example` e comentar que o `.env` real **não** vai
  para o Git.

**Falar:**
> "Todo o código está no GitHub, com README que documenta cada Fase, os
> prints da configuração AWS, o diagrama ER do banco e este próprio
> roteiro. As credenciais ficam no `.env` que **não** é versionado — apenas
> um `.env.example` com placeholders sobe pro repositório.
>
> Esse é o nosso entregável da Fase 7: um sistema **integrado, seguro e
> demonstrável** de gestão agrícola inteligente. Obrigado!"

---

## ✅ Checklist pré-gravação

- [ ] Banco com algumas leituras (deixar o simulador 30–60 s ligado).
- [ ] `farmtech_iot.db` populado e `assets/images/` com as 6 imagens.
- [ ] `yolov8n.pt` já baixado (rodar uma análise antes da gravação).
- [ ] Caixa de e-mail aberta para mostrar o alerta chegando.
- [ ] Console AWS SNS aberto em outra aba.
- [ ] `.env` configurado com credenciais válidas.
- [ ] Resolução do navegador em 1080p e fonte aumentada se necessário.
