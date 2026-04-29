# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
  <a href="https://www.fiap.com.br/">
    <img src="https://github.com/giovanisaavedra/FIAP/blob/main/assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Administração Paulista" border="0" width="40%">
  </a>
</p>

<br>

# Sistema de Visão Computacional para Classificação de Animais — FarmTech Solutions

---

## 👥 Equipe do Projeto

### 👨‍🎓 Integrantes

| Nome                                | RM       | 
|-------------------------------------|----------|
| Giovani Saavedra                    | RM566797 | 
| Marcio Elifas                       | RM567871 |
| Felipe Bernardo Papeleo de Oliveira | RM567782 |

### 👩‍🏫 Orientação

**Tutor(a):** Sabrina Otoni   
**Coordenador(a):** André Godoi Chiovatto 

---
## 📜 Descrição

Este projeto foi desenvolvido para a **FarmTech Solutions**, empresa que está expandindo seus serviços de Inteligência Artificial para a área de Visão Computacional. O objetivo é demonstrar ao cliente fictício o potencial e as limitações de diferentes abordagens de Deep Learning aplicadas a um mesmo problema: identificar dois objetos distintos — **gato** e **cachorro** — em imagens.

O projeto está dividido em duas entregas obrigatórias e uma demonstração extra:

- **Entrega 1 — YOLO Customizada:** Construção de um sistema de detecção de objetos usando o modelo YOLOv5, com transfer learning a partir do `yolov5s.pt`. Foram realizados dois experimentos com quantidades diferentes de épocas (30 e 60) para avaliar empiricamente o impacto desse parâmetro no desempenho do modelo. O dataset contém 80 imagens (40 gatos + 40 cachorros) extraídas do Oxford-IIIT Pet Dataset, divididas em 64 treino, 8 validação e 8 teste, todas rotuladas manualmente no Make Sense AI.

- **Entrega 2 — Comparação com Outras Abordagens:** Aplicação de duas abordagens "concorrentes" sobre a mesma base: YOLO padrão (`yolov5s.pt` pré-treinado no COCO, sem ajustes) e CNN treinada do zero em TensorFlow/Keras. As três abordagens (YOLO customizada, YOLO padrão e CNN do zero) são então comparadas criticamente nas dimensões exigidas pelo enunciado: facilidade de uso, precisão, tempo de treinamento e tempo de inferência.

- **Demonstração extra — Transfer Learning com MobileNetV2:** Implementação parcial da segunda opção do "Ir Além" (item 3.2 do enunciado), limitada à parte de Transfer Learning sem a etapa de segmentação. Inclui-se na análise comparativa final como quarta abordagem, totalizando quatro modelos avaliados.

### 🔍 Principais Achados

- **A YOLO customizada com 30 épocas superou a com 60 épocas** (mAP@0.5 = 0.901 vs 0.719), demonstrando empiricamente o conceito de overfitting: com poucos dados (64 imagens), mais épocas levam à memorização do treino e perda de generalização
- **A YOLO padrão (COCO) acertou 7/8 nas imagens de teste** sem nenhum treino adicional, superando a YOLO customizada (4/8) — exemplo de que customizar nem sempre é melhor quando o modelo pré-treinado já cobre as classes
- **A CNN treinada do zero atingiu apenas 50% de acurácia aparente**, mas a inspeção das predições revelou que classificou TODAS as imagens como "cachorro" — modelo completamente quebrado, "salvo" apenas pela sorte do dataset balanceado
- **O Transfer Learning com MobileNetV2 atingiu 87,5% de acurácia com apenas 2.562 parâmetros treináveis** (vs 4,8 milhões da CNN do zero), com confiança média de 96% nas predições corretas — demonstração clara do poder do conhecimento prévio
- **Todas as quatro abordagens erraram a classificação do gato Sphynx** (gato sem pelo), evidenciando o problema de "out-of-distribution" mesmo em modelos massivos
- **Bug pedagógico:** durante a Entrega 1, identificamos e corrigimos um problema crítico nos labels de validação que estavam invertidos — o que elevou o mAP@0.5 de 0.42 para 0.901 e gerou uma valiosa lição sobre a importância de auditar métricas anômalas antes de buscar soluções algorítmicas

### 📁 Estrutura de pastas

- 📂 **00 - PROJETO/**
  - 📓 `GiovaniSaavedra_rm566797_pbl_fase6.ipynb` — notebook principal
  - 📄 `README.md` — este arquivo

---
# 🔧 Como executar o código

## Execução no Google Colab (recomendado)

O notebook foi desenvolvido para rodar no Google Colab com aceleração GPU (Tesla T4). Para executá-lo:

1. Clique no botão **"Open In Colab"** no topo do notebook
2. No menu **Runtime → Change runtime type**, selecione **T4 GPU**
3. Tenha o dataset organizado no seu Google Drive na seguinte estrutura:

- 📂 **MyDrive/FIAP/fase06-cap01/dataset/**
  - 📂 **images/**
    - 📂 `train/` — 64 imagens (32 gatos + 32 cachorros)
    - 📂 `val/` — 8 imagens (4 gatos + 4 cachorros)
    - 📂 `test/` — 8 imagens (4 gatos + 4 cachorros)
  - 📂 **labels/**
    - 📂 `train/` — 64 arquivos `.txt` no formato YOLO
    - 📂 `val/` — 8 arquivos `.txt` no formato YOLO

4. Execute as células em sequência. A primeira célula montará o Google Drive e pedirá autorização

> 💡 **Importante:** as imagens da pasta `test/` não precisam de arquivos `.txt` correspondentes — o YOLO usa rótulos apenas no treino e validação. No teste é o modelo que "advinha" sozinho.

## Pré-requisitos

- Google Colab (gratuito)
- Conta Google com Drive
- Aceleração GPU ativada (Tesla T4 ou superior recomendado)

## Bibliotecas utilizadas

| Biblioteca | Versão | Uso |
|---|---|---|
| YOLOv5 | v7.0+ | Modelo de detecção de objetos (Entrega 1 e 2) |
| PyTorch | 2.x | Framework de Deep Learning utilizado pelo YOLOv5 |
| TensorFlow | 2.x | Framework para CNN do zero e Transfer Learning |
| Keras | 3.x | API de alto nível para construção de redes neurais |
| MobileNetV2 | — | Modelo pré-treinado na ImageNet (Transfer Learning) |
| NumPy | 1.x | Operações numéricas |
| Matplotlib | 3.x | Visualização dos gráficos de treino |

---

## 🎯 Entrega 1 — YOLO Customizada

### Pipeline executado

1. **Coleta e organização** de 80 imagens (40 gatos + 40 cachorros) do Oxford-IIIT Pet Dataset
2. **Rotulação manual** no Make Sense AI, gerando arquivos `.txt` no formato YOLO
3. **Configuração** do `petshop.yaml` para o YOLOv5 entender as classes e caminhos
4. **Experimento 1:** treinamento por 30 épocas com transfer learning a partir do `yolov5s.pt`
5. **Identificação e correção de bug** nos labels da pasta de validação (estavam com ordem invertida)
6. **Experimento 2:** treinamento por 60 épocas para comparar o impacto das épocas
7. **Teste** do melhor modelo nas 8 imagens não vistas

### Resultados dos experimentos

| Métrica (validação)  | 30 épocas (corrigido) | 60 épocas | Variação |
|---------------------|-----------------------|-----------|----------|
| Precision (all)     | 0.752                 | 0.858     | ↑ +14% |
| Recall (all)        | 0.741                 | 0.697     | ↓ -6% |
| **mAP@0.5 (all)**   | **0.901**             | 0.719     | ↓ -20% |
| **mAP@0.5:0.95 (all)** | **0.511**          | 0.424     | ↓ -17% |
| Tempo de treino     | ~1.4 min              | ~2.8 min  | ↑ +100% |

**Modelo escolhido:** 30 épocas (`exp_30epochs_corrigido`) — apresentou melhor mAP, melhor equilíbrio entre as classes e tempo de treino menor.

### Lição aprendida

> **Muitas épocas + Poucos dados = Overfitting**
>
> O modelo de 60 épocas memorizou melhor o treino, mas perdeu capacidade de generalizar para a validação. A `val/cls_loss` apresentou a curva clássica de overfitting (cai e depois sobe).

---

## 🤖 Entrega 2 — Comparação com Outras Abordagens

### Abordagens implementadas

#### YOLO Padrão (sem customização)
Uso direto do `yolov5s.pt` pré-treinado no dataset COCO (~330 mil imagens, 80 classes incluindo `cat` e `dog`), sem treino adicional.

#### CNN treinada do zero
Rede convolucional com 3 blocos Conv2D + MaxPooling, seguidos de Flatten + Dense + Dropout + Softmax. Treinada totalmente do zero em TensorFlow/Keras, com 4.828.610 parâmetros e 64 imagens.

### Resultados comparados nas imagens de teste

| Abordagem | Acurácia | Confiança média | Tempo treino | Tempo inferência |
|-----------|----------|-----------------|--------------|------------------|
| YOLO Customizada (30 épocas) | 4/8 (50%)  | ~39% | ~1.4 min | ~37 ms |
| **YOLO Padrão (COCO)** | **7/8 (87.5%)** | ~66% | 0 (já treinado) | ~25 ms |
| CNN do Zero | 4/8 (50%)¹ | ~57% (caótica) | ~9 s | ~178 ms |

> ¹ A CNN do zero classificou TODAS as 8 imagens como "cachorro" — os 4 acertos são apenas dos cachorros reais. O modelo não aprendeu a distinguir as classes, "salvo" pelo balanceamento do dataset.

### Lições aprendidas

> **Customizar nem sempre é melhor.** Quando o problema cai dentro do escopo de um modelo pré-treinado robusto, usá-lo direto pode ser superior a treinar uma versão própria com dados limitados.

> **Acurácia balanceada esconde modelos quebrados.** A CNN do zero teria reportado "87,5% de acurácia" se o teste fosse desbalanceado (7 cachorros + 1 gato). Por isso, métricas múltiplas (precision, recall, confiança) são essenciais.

---

## 🚀 Demonstração extra — Transfer Learning com MobileNetV2

Implementação parcial da segunda opção do "Ir Além" (item 3.2 do enunciado), limitada à parte de Transfer Learning sem a etapa de segmentação.

### Arquitetura
- **Backbone:** MobileNetV2 pré-treinada na ImageNet (~1,4 milhão de imagens), com pesos congelados
- **Cabeça customizada:** GlobalAveragePooling2D + Dropout(0.3) + Dense(2, softmax)
- **Parâmetros treináveis:** apenas 2.562 (vs 4.828.610 da CNN do zero)
- **Estratégia:** Feature Extraction (sem Fine Tuning, dispensável neste caso por já atingir 100% na validação)

### Resultados nas imagens de teste

| Métrica | Resultado |
|---|---|
| Acurácia | 7/8 (87.5%) |
| Confiança média (acertos) | **~96%** ⭐ |
| Único erro | Sphynx (caso out-of-distribution) |
| Tempo de treino | ~40 segundos |

### Lição aprendida

> **Transfer Learning é praticamente obrigatório com poucos dados.** A diferença entre 50% (CNN do zero) e 87,5% (Transfer Learning) usando a **mesma base de 64 imagens** comprova empiricamente que o conhecimento prévio é o fator mais determinante nesse regime.

---

## 📊 Análise Comparativa Final das 4 Abordagens

| Critério | YOLO Customizada | YOLO Padrão | CNN do Zero | Transfer Learning |
|----------|------------------|-------------|-------------|-------------------|
| **Tarefa** | Detecção | Detecção | Classificação | Classificação |
| **Pré-treino** | yolov5s.pt + 30 épocas | yolov5s.pt (COCO) | Nenhum | MobileNetV2 (ImageNet) |
| **Parâmetros treináveis** | ~7M | 0 | 4.828.610 | **2.562** |
| **Acurácia teste** | 4/8 (50%) | 7/8 (87,5%) | 4/8 (chutou) | **7/8 (87,5%)** |
| **Confiança média** | ~39% | ~66% | ~57% (caótica) | **~96%** ⭐ |
| **Tempo de treino** | ~1.4 min | 0 | ~9s | ~40s |
| **Facilidade de uso** | Média | **Alta** | Baixa | Média |

### Ranking prático para o cenário FarmTech

1. 🥇 **YOLO padrão** — máxima qualidade com zero esforço, pois COCO já cobre as classes
2. 🥈 **Transfer Learning (MobileNetV2)** — empata na precisão e oferece confiança superior
3. 🥉 **YOLO customizada** — ficou aquém das demais por causa do dataset pequeno
4. 🏳️ **CNN do zero** — não recomendada para este cenário (dados insuficientes)

---

## 🎬 Vídeo de Demonstração

- **Projeto Fase 6 — Visão Computacional:** [Assistir no YouTube](https://youtu.be/3qCpIr-ihRY)

## 🗃 Histórico de lançamentos

1.0.0 - 29/04/2026

Versão final com Entrega 1 (YOLO customizada), Entrega 2 (YOLO padrão + CNN do zero) e demonstração extra com Transfer Learning


-----    

## 📋 Licença

<img src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1" width="30"> <img src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1" width="30">

[MODELO GIT FIAP](https://github.com/agodoi/template) por [Fiap](https://fiap.com.br) está licenciado sobre [Attribution 4.0 International](http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1).