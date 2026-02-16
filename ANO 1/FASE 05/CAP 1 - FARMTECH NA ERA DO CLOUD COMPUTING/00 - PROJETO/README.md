# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
  <a href="https://www.fiap.com.br/">
    <img src="https://github.com/giovanisaavedra/FIAP/blob/main/assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Administração Paulista" border="0" width="40%">
  </a>
</p>

<br>

# Nome do projeto

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

📜 Descrição
Este projeto foi desenvolvido para a FarmTech Solutions, empresa que presta serviços de Inteligência Artificial para uma fazenda de médio porte (200 hectares) produtora de múltiplas culturas. O objetivo é aplicar técnicas de Machine Learning para prever o rendimento agrícola e estimar os custos de hospedagem do modelo em nuvem AWS.
O projeto está dividido em duas entregas:
Entrega 1 — Machine Learning: Análise exploratória de dados (EDA), clusterização não supervisionada (K-Means e DBSCAN) e treinamento de 5 modelos preditivos de regressão supervisionada para prever o rendimento das safras. O dataset crop_yield.csv contém 156 registros com dados de 4 culturas (Cocoa beans, Oil palm fruit, Rice paddy e Rubber natural), variáveis climáticas (precipitação, umidade, temperatura) e o rendimento em toneladas por hectare.
Entrega 2 — Computação em Nuvem: Estimativa de custos On-Demand na AWS, comparando as regiões de São Paulo (sa-east-1) e Virgínia do Norte (us-east-1) para hospedar uma API que receberá dados de sensores e executará o modelo de ML. A análise considera requisitos técnicos (latência), legais (LGPD) e financeiros.
Principais Achados

A EDA revelou que o rendimento é determinado quase exclusivamente pelo tipo de cultura, com baixa influência das variáveis climáticas
A clusterização confirmou esses padrões: o DBSCAN separou perfeitamente as 4 culturas e identificou 12 outliers correspondentes a 3 condições climáticas atípicas
O modelo de Linear Regression obteve o melhor desempenho (R² = 0,9951), superando modelos mais complexos como Random Forest e XGBoost — resultado coerente com a natureza linear da relação entre Crop e Yield
A cross-validation confirmou a robustez do modelo (R² médio = 0,9854, desvio padrão = 0,0047)


📁 Estrutura de pastas
📂 00 - PROJETO/
├── 📂 assets/
│   ├── crop_yield.csv              ← dataset utilizado
│   └── 📂 screenshots-aws/          ← prints da calculadora AWS
│       ├── sao-paulo-ec2.png
│       ├── virginia-ec2.png
│       └── comparativo-custos.png
├── 📂 src/
│   └── GiovaniSaavedra_rm566797_pbl_fase5.ipynb  ← notebook principal
├── .gitignore
├── requirements.txt
└── README.md                         ← este arquivo


🔧 Como executar o código
Pré-requisitos

Python 3.10+
Jupyter Notebook ou Google Colab
Bibliotecas listadas em requirements.txt

Instalação

Clone o repositório:

bashgit clone https://github.com/giovanisaavedra/projeto-farmtech.git
cd projeto-farmtech

Instale as dependências:

bashpip install -r requirements.txt

Abra o notebook:

bashjupyter notebook src/GiovaniSaavedra_rm566797_pbl_fase5.ipynb
Execução no Google Colab

Acesse o Google Colab
Faça upload do notebook (src/GiovaniSaavedra_rm566797_pbl_fase5.ipynb)
Faça upload do dataset (data/crop_yield.csv)
Execute todas as células em sequência

Bibliotecas utilizadas
BibliotecaVersãoUsopandas2.xManipulação de dadosnumpy1.xOperações numéricasmatplotlib3.xVisualizaçõesseaborn0.13+Visualizações estatísticasscikit-learn1.xModelos de ML, métricas, pré-processamentoxgboost2.xModelo XGBoost Regressor

📊 Entrega 1 — Machine Learning
O notebook está organizado em 3 tarefas sequenciais, onde cada etapa informa a seguinte:
Tarefa 1 — Análise Exploratória de Dados (EDA)

Estatísticas descritivas de todas as variáveis
Distribuição de cada variável (histogramas, boxplots)
Análise de correlação entre variáveis
Análise segmentada por tipo de cultura
Identificação e tratamento de valores ausentes e outliers

Tarefa 2 — Clusterização (Aprendizado Não Supervisionado)

Determinação do número ideal de clusters (método do cotovelo e silhouette score)
Aplicação do K-Means (K=4) e DBSCAN (eps=1.5, min_samples=5)
Redução de dimensionalidade com PCA para visualização
Interpretação dos clusters no contexto agrícola
Identificação de outliers multidimensionais

Tarefa 3 — Modelos Preditivos de Regressão Supervisionada
Cinco modelos treinados e avaliados:
ModeloMAERMSER²Linear Regression3.0904.3650,9951XGBoost3.7945.9270,9909Random Forest3.5556.8090,9880Decision Tree3.8587.7100,9847SVR38.95671.299-0,3105
Melhor modelo: Linear Regression (R² = 0,9951), validado com cross-validation 5-fold e análise de resíduos.

☁️ Entrega 2 — Estimativa de Custos em Nuvem AWS
Configuração da Máquina
RecursoEspecificaçãoSistema OperacionalLinuxCPUs2Memória1 GiBRedeAté 5 GigabitArmazenamento50 GB (HD)
Comparativo de Custos — On-Demand (100%)
ItemSão Paulo (sa-east-1)Virgínia do Norte (us-east-1)Instância EC2ver screenshotsver screenshotsArmazenamento EBS (50 GB)ver screenshotsver screenshotsCusto mensal totalver screenshotsver screenshots


Análise de Decisão
Qual é a solução mais barata?
A região da Virgínia do Norte (us-east-1) apresenta custo menor, por ser uma das regiões mais antigas e com maior escala de operação da AWS.
Considerando latência e LGPD, qual a melhor escolha?
Recomendação: São Paulo (sa-east-1), pelas seguintes razões:

Latência: A API receberá dados de sensores localizados no Brasil. Hospedar em São Paulo garante menor tempo de resposta (~20-40ms vs ~120-180ms para Virgínia), essencial para leitura em tempo real dos dados dos sensores.
LGPD (Lei Geral de Proteção de Dados): A Lei 13.709/2018 estabelece restrições para transferência internacional de dados pessoais. Embora dados de sensores agrícolas possam não ser dados pessoais, a base pode conter informações associadas a proprietários rurais ou funcionários. Hospedar em São Paulo elimina riscos de interpretação legal e garante conformidade total com a legislação brasileira.
Soberania de dados: Manter os dados em território nacional oferece maior controle e segurança jurídica para a FarmTech Solutions e seus clientes.

A diferença de custo entre as regiões é compensada pela segurança jurídica e pela melhor experiência do usuário proporcionada pela menor latência.

🎬 Vídeos de Demonstração

Entrega 1 — Machine Learning: Assistir no YouTube
Entrega 2 — Computação em Nuvem: Assistir no YouTube


🗃 Histórico de lançamentos

1.0.0 - 16/02/2026

Versão final com Entrega 1 (ML) e Entrega 2 (AWS)


-----    

## 📋 Licença

<img src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1" width="30"> <img src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1" width="30">

[MODELO GIT FIAP](https://github.com/agodoi/template) por [Fiap](https://fiap.com.br) está licenciado sobre [Attribution 4.0 International](http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1).
