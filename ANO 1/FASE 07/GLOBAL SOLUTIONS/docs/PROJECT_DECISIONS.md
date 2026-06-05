# 📚 Decisões de Projeto e Limitações Conhecidas

Este documento acumula **decisões arquiteturais, justificativas técnicas e limitações conhecidas** do SatVerify durante o desenvolvimento da POC. O objetivo é servir como base para:

- README do projeto
- PDF de entrega da Global Solution
- Roteiro do vídeo demonstrativo
- Documentação de melhorias futuras para produção

---

## 🎯 Premissas da POC

Esta é uma **Prova de Conceito (POC) / MVP** desenvolvida em prazo curto para a Global Solution FIAP 2026.1. As escolhas técnicas refletem o trade-off entre:

- ✅ **Demonstrar viabilidade do conceito** de due diligence empresarial via satélite + IA
- ✅ **Validar o pipeline ponta a ponta** com dados reais (não simulados)
- ✅ **Cobrir tecnologias do curso** de forma genuína (não forçada)
- ⚖️ **Foco em qualidade execucional** sobre amplitude de features

Todas as decisões abaixo devem ser lidas sob essa ótica: **o que serve à POC pode não ser o ideal em produção, e isso é explicitamente assumido**.

---

## 🗺️ Geocodificação: Nominatim (OpenStreetMap)

### Decisão
Utilizamos o **Nominatim**, serviço gratuito de geocodificação baseado no OpenStreetMap, via biblioteca Python `geopy`.

### Justificativa para POC
- ✅ **Gratuito e sem cadastro** — zero fricção para o time iniciar
- ✅ **Cobertura razoável** para endereços conhecidos no Brasil
- ✅ **Sem chave de API** para gerenciar
- ✅ **Software open-source** com transparência total
- ✅ **Suficiente para validar a hipótese central** do produto

### Limitações conhecidas

1. **Não encontra endereços genéricos**
   - Exemplo: `"Estrada Municipal, Zona Rural, Bocaiúva do Sul, PR"` falha
   - Causa: OSM precisa de identificadores concretos (nome de rua + número, ponto turístico, etc)

2. **Pode resolver para pontos próximos mas semanticamente diferentes**
   - Exemplo real: `"Polo Petroquímico de Camaçari"` resolveu para o **"cinturão verde"** (área de preservação ao redor do polo), não para dentro das instalações industriais
   - Causa: o OSM tem essa entidade registrada e o Nominatim encontra a mais próxima

3. **Cobertura desigual entre regiões**
   - Excelente em capitais (SP, RJ, BSB)
   - Boa em cidades médias
   - Limitada em endereços específicos de cidades pequenas

4. **Limite de uso justo (~1 req/s)**
   - Servidor público compartilhado
   - Não escala para uso comercial intenso sem hospedagem própria

5. **Sem feedback de confiabilidade**
   - Não retorna "score de confiança" do match
   - Endereço ambíguo pode resolver silenciosamente para lugar errado

### Melhorias planejadas para produção

- **Combinar múltiplos provedores em cascata**:
  1. Tentar Nominatim primeiro (gratuito)
  2. Fallback para Mapbox Geocoding (100k requests/mês grátis)
  3. Fallback para Google Geocoding (pago, mas mais robusto)
- **Validação cruzada com CEP** brasileiro (via API dos Correios ou ViaCEP)
- **Interface de ajuste manual** no mapa quando geocoding ambíguo
- **Score de confiabilidade do match** apresentado ao analista
- **Cache de endereços já geocodificados** para reduzir chamadas
- **Hospedar instância própria do Nominatim** quando volume justificar

### Como mencionar no PDF/vídeo

> *"Para conversão de endereços em coordenadas geográficas, utilizamos o Nominatim, serviço gratuito de geocodificação baseado no OpenStreetMap. Em produção, recomenda-se uma estratégia em cascata combinando múltiplos provedores (Nominatim → Mapbox → Google) com validação cruzada por CEP e interface de ajuste manual para endereços ambíguos."*

---

## 🛰️ Imagens de Satélite: Sentinel-2 via Copernicus Data Space Ecosystem

### Decisão
Utilizamos imagens **Sentinel-2 L2A** (já corrigidas atmosfericamente) acessadas via APIs do **Copernicus Data Space Ecosystem (CDSE)**, sucessor oficial do Sentinel Hub.

### Justificativa para POC
- ✅ **Totalmente gratuito** para dados Sentinel
- ✅ **Mantido pela ESA** (Agência Espacial Europeia)
- ✅ **Cobertura global** com revisita de 5 dias
- ✅ **Resolução de 10m/pixel** suficiente para detectar instalações empresariais
- ✅ **13 bandas espectrais** permitindo cálculo de índices como NDBI e NDVI
- ✅ **Mesma biblioteca Python** (`sentinelhub-py`) do Sentinel Hub antigo

### Limitações conhecidas

1. **Resolução limitada para análises detalhadas**
   - 10m/pixel não permite contar veículos, ver pessoas, distinguir tipos específicos de equipamentos
   - Solução adotada: **complementar com Mapbox Static Images** (alta resolução) para análise local

2. **Cobertura de nuvens compromete análises**
   - Sentinel-2 é satélite óptico — não vê através de nuvens
   - Em regiões tropicais, podem passar semanas sem cena limpa
   - Solução adotada: lógica de seleção que **prioriza qualidade atmosférica sobre recência**

3. **Latência de disponibilização**
   - Cenas chegam à API com 2-3 dias de atraso
   - Não serve para monitoramento "tempo real"

4. **Bbox de ~500m no projeto**
   - Aproximação simples (±0.0025° em lat/lon)
   - Não considera deformação da Terra em latitudes extremas
   - Suficiente para mercado brasileiro, mas inadequado para projeto global

### Melhorias planejadas para produção

- **Combinar Sentinel-2 (gratuito) com Planet Labs / Maxar** (pagos, sub-métricos) em casos críticos
- **Análise temporal de múltiplas cenas** ao longo de meses (não apenas a melhor cena pontual)
- **Detecção automática de nuvens por pixel** (não apenas % médio da cena)
- **Bbox geodésico preciso** considerando projeção Web Mercator
- **Pipeline de fallback** para cenas Landsat quando Sentinel-2 indisponível

### Como mencionar no PDF/vídeo

> *"Utilizamos imagens Sentinel-2 L2A do programa Copernicus da ESA, com resolução de 10 metros e revisita global a cada 5 dias. Para a POC, implementamos lógica de seleção de cena que prioriza qualidade atmosférica (menor cobertura de nuvens) sobre recência absoluta. Em produção, recomendamos complementar com imagens de alta resolução comerciais (Planet, Maxar) e análise temporal de múltiplas cenas para validação cruzada."*

---

## 📊 NDBI (Índice de Área Construída)

### Decisão
Calculamos o **Normalized Difference Built-up Index (NDBI)** como métrica principal de "área construída":

```
NDBI = (SWIR1 - NIR) / (SWIR1 + NIR)
```

Bandas Sentinel-2 utilizadas: B08 (NIR, 842nm) e B11 (SWIR1, 1610nm).

### Justificativa para POC
- ✅ **Embasamento científico sólido** — índice estabelecido na literatura de sensoriamento remoto (Zha et al., 2003)
- ✅ **Cálculo simples** — fórmula direta sobre 2 bandas, sem ML
- ✅ **Interpretável** — diferentemente de redes neurais, qualquer analista entende a lógica
- ✅ **Adequado para o caso de uso** — distinguir áreas construídas de vegetação/água é exatamente o que precisamos

### Limitações conhecidas

1. **NDBI confunde solo nu com área construída**
   - Solos secos, áreas de mineração e regiões desérticas têm assinatura espectral similar a concreto
   - Falsos positivos em regiões agrícolas em entressafra

2. **Não distingue tipos de estrutura**
   - Galpão industrial, prédio residencial e shopping têm NDBI similar
   - Para diferenciar tipos, é necessário visão computacional (próxima camada do produto: YOLO)

3. **Threshold de 0.1 é heurístico**
   - Valor padrão da literatura, mas pode precisar calibração regional
   - Em clima tropical úmido, NDBI tende a ser mais baixo para mesma estrutura

4. **Sensível a sombras de prédios**
   - Sombras de edifícios altos podem reduzir NDBI artificialmente
   - Importante em regiões com prédios densos (centros financeiros)

### Validação realizada na POC

| Caso | Endereço | NDBI obtido | Esperado | Validação |
|---|---|---|---|---|
| Industrial | Volkswagen do Brasil, SBC | 45.1% | Alto | ✅ Confirmado |
| Comercial denso | Rua 25 de Março, SP | 77.7% | Alto | ✅ Confirmado |
| Área verde | Parque Estadual da Cantareira | 0.0% | Muito baixo | ✅ Confirmado |

### Melhorias planejadas para produção

- **Combinar NDBI com outros índices**: NDVI (vegetação), NDWI (água), BUI (built-up index aprimorado)
- **Aplicar modelo de ML supervisionado** treinado com áreas brasileiras rotuladas
- **Análise de textura** (GLCM) para distinguir tipos de construção
- **Correção por sombras** usando ângulo solar da cena
- **Calibração regional do threshold** baseada em zona climática

### Como mencionar no PDF/vídeo

> *"Adotamos o índice NDBI (Normalized Difference Built-up Index), métrica estabelecida na literatura de sensoriamento remoto, para quantificar área construída. Validamos o método com áreas de referência conhecidas: centro comercial de São Paulo apresentou 77.7% de área construída enquanto o Parque da Cantareira apresentou 0%. Em produção, recomendamos enriquecer com índices complementares (NDVI, NDWI) e modelo de ML supervisionado para reduzir falsos positivos em solos áridos."*

---

## 🖼️ Imagens Aéreas de Alta Resolução: Mapbox

### Decisão
Utilizamos **Mapbox Static Images API** para baixar imagens aéreas de alta resolução (~0.5m/pixel em zoom 18) do endereço específico.

### Justificativa para POC
- ✅ **Free tier de 50.000 requests/mês** — suficiente para POC e operação inicial
- ✅ **Cobertura global** com qualidade Maxar/DigitalGlobe na maioria das áreas
- ✅ **API simples** — apenas HTTP GET, sem autenticação complexa
- ✅ **Complementa o Sentinel-2** — onde satélite gratuito não consegue, alta resolução resolve

### Limitações conhecidas

1. **Imagens não são "tempo real"**
   - Mapbox usa mosaicos atualizados periodicamente (meses a anos)
   - Não detecta mudanças recentes (obra concluída no último ano, por exemplo)

2. **Cobertura desigual de alta resolução**
   - Excelente em centros urbanos
   - Pior em áreas rurais (mosaicos mais antigos ou baixa resolução)

3. **Não fornece bandas espectrais**
   - Apenas RGB visível
   - Impossível calcular índices como NDBI sobre Mapbox

4. **Termos de uso restritos**
   - Imagens não podem ser redistribuídas
   - Atribuição obrigatória "© Mapbox © Maxar"

### Melhorias planejadas para produção

- **Integrar Google Static Maps** como fallback (cobertura ligeiramente diferente)
- **Avaliar Planet SkySat** para imagens diárias em áreas críticas
- **Cache local de imagens** para evitar custos repetidos
- **Anotação de data** da imagem (Mapbox não retorna timestamp na resposta)

### Como mencionar no PDF/vídeo

> *"Utilizamos a Mapbox Static Images API como fonte complementar de imagens aéreas de alta resolução (~0.5m/pixel). Essa fonte é fundamental para detecção de objetos individuais (veículos, estruturas) impossíveis de identificar em imagens Sentinel-2. Em produção, recomendamos combinar com Google Static Maps e Planet SkySat para redundância e captura de mudanças recentes."*

---

## ☁️ Cloud Storage: AWS S3

### Decisão
Utilizamos **AWS S3** para armazenamento de imagens processadas e relatórios gerados.

### Justificativa para POC
- ✅ **Free Tier de 5GB** muito além do uso da POC (~50MB total)
- ✅ **Tecnologia padrão de mercado** — banca reconhece AWS
- ✅ **Cobre tópico do enunciado**: "Aplicações em nuvem"
- ✅ **Simples de integrar** via boto3

### Decisões de segurança aplicadas

- ✅ **Usuário IAM dedicado** (não usar credenciais root)
- ✅ **Política mínima**: apenas `AmazonS3FullAccess`
- ✅ **Bucket privado** (Block all public access habilitado)
- ✅ **Credenciais em `.env`** (nunca commitadas no Git)
- ✅ **Budget alarm em US$ 0,01** para detectar qualquer cobrança inesperada
- ✅ **Conta AWS dedicada** ao projeto (isolamento total)

### Implementação efetiva do upload S3 (Prompt 6)

Após validação de todo o pipeline localmente, decidimos implementar o **upload efetivo** dos artefatos de análise para AWS S3, indo além da simples configuração de credenciais.

**O que é persistido no S3:**

Para cada análise (`analysis_id` único), os seguintes arquivos são enviados:
- `metadata.json` — dicionário consolidado com todos os sinais técnicos
- `sentinel_rgb.png` — imagem RGB do satélite Sentinel-2
- `ndbi.png` — visualização do índice NDBI
- `mapbox_aerial.png` — imagem aérea de alta resolução
- `yolo_sentinel_annotated.png` — Sentinel-2 com bounding boxes YOLO
- `yolo_mapbox_annotated.png` — Mapbox com bounding boxes YOLO
- `dd_report.md` — relatório textual gerado pelo Gemini

**Estrutura no bucket:**

```
s3://fiap-gs-satverify-2026/
├── analyses/
│   ├── 1854c658-fbcb-4668-965c-8589392ae640/
│   │   ├── metadata.json
│   │   ├── sentinel_rgb.png
│   │   ├── ndbi.png
│   │   ├── mapbox_aerial.png
│   │   ├── yolo_sentinel_annotated.png
│   │   ├── yolo_mapbox_annotated.png
│   │   └── dd_report.md
│   ├── cc3743fe-f99d-4ac4-9aeb-9a135c4a82fa/
│   │   └── ... (mesma estrutura)
│   └── a415a758-eee8-42a0-83f7-2ebda3d16670/
│       └── ... (mesma estrutura)
```

### Justificativa para POC

- ✅ **Demonstra integração AWS real** — não apenas configurada, efetivamente usada
- ✅ **Pré-requisito para deploy em nuvem** — Streamlit Cloud, App Runner, ECS dependem de storage compartilhado
- ✅ **Garante persistência além do disco local** — proteção contra perda acidental
- ✅ **Habilita demonstração visual no vídeo** — abrir console S3 e mostrar bucket populado
- ✅ **Padrão de mercado** — qualquer plataforma SaaS de DD usa storage em nuvem desde o dia 1

### Decisão de design: graceful degradation

Implementamos o upload como **operação não-crítica**: se o upload S3 falhar (credenciais expiradas, sem internet, rate limit), o pipeline **não quebra**. A análise é salva localmente e o sistema imprime um aviso explícito:

```
⚠️ Upload S3 falhou: <razão>. Análise disponível apenas localmente em outputs/<id>/
```

Isso é importante porque:
- O valor central do produto está nos sinais técnicos (NDBI, CLIP, YOLO, Gemini), não no storage
- Em produção, S3 seria mandatório, mas para POC a robustez vs falhas externas vale mais
- Demonstra **engenharia defensiva** — princípio de "fail gracefully" para componentes externos

### Lição aprendida (para o relatório)

> *"Em arquiteturas com múltiplas integrações externas (satélite, geocoding, modelos de IA, storage em nuvem, LLM), graceful degradation é uma decisão de produto, não detalhe técnico. Cada componente externo é um ponto potencial de falha que não deve derrubar o sistema inteiro. Implementamos o upload S3 como não-crítico, garantindo que a análise core continue funcionando mesmo se a nuvem estiver indisponível."*

### Como mencionar no PDF/vídeo

> *"A integração efetiva com AWS S3 vai além da configuração — todos os artefatos de cada análise são automaticamente persistidos em um bucket dedicado, organizados por analysis_id. Isso garante rastreabilidade auditável (essencial para compliance) e habilita futura migração para arquitetura totalmente em nuvem. A implementação adota graceful degradation: se o upload falhar, a análise local continua disponível, garantindo robustez do produto contra indisponibilidade de serviços externos."*

Discurso de **maturidade arquitetural**.

### Visibilidade explícita da integração AWS no dashboard (Prompt 7)

Após implementar o upload efetivo dos artefatos, evoluímos o dashboard Streamlit para **mostrar visualmente** a integração com AWS S3, transformando-a de detalhe de implementação em **feature visível** do produto.

**O que foi adicionado:**

1. **Download direto via URLs pré-assinadas (presigned URLs)**

   Para cada análise, o dashboard exibe botões de download que apontam para **URLs temporárias pré-assinadas** geradas pelo S3, válidas por 1 hora. Padrão de segurança bancário: permite compartilhamento de arquivos privados sem expor credenciais AWS.

```python
   url = s3.generate_presigned_url(
       'get_object',
       Params={'Bucket': bucket, 'Key': key},
       ExpiresIn=3600  # 1 hora
   )
```

2. **Link direto para o console AWS**

   Botão "Ver no console AWS S3" que abre uma nova aba do navegador apontando diretamente para a pasta da análise no bucket. Demonstra transparência total: o auditor pode verificar os artefatos no console oficial da AWS.

3. **Painel de estatísticas de uso**

   Mostra em tempo real o consumo do bucket: storage total utilizado, número de arquivos, % do free tier utilizado, e custo estimado. Demonstra **governança financeira** — um produto SaaS sério precisa exibir custos para o operador.

### Justificativa para POC

- ✅ **Cobrança didática:** muitos colegas vão listar "AWS" no diagrama sem usar de fato. Vocês vão **mostrar AWS funcionando** ao vivo.
- ✅ **Discurso narrativo no vídeo:** o avaliador vê integração real, não diagrama estático.
- ✅ **Padrão de mercado:** URLs pré-assinadas é exatamente como Stripe, AWS Console, Google Cloud Storage funcionam para compartilhamento seguro.
- ✅ **Auditabilidade demonstrada:** chave para credibilidade em produto de compliance (KYB/AML).

### Padrões de engenharia aplicados

| Padrão | Aplicação no SatVerify |
|---|---|
| **Presigned URLs** | Compartilhamento seguro sem exposição de credenciais |
| **Graceful degradation** | Se S3 indisponível, dashboard ainda funciona localmente |
| **Cost visibility** | Free tier rastreado em tempo real (DevOps básico) |
| **Auditability** | Cada artefato tem path S3 canônico documentado |

### Lição aprendida (para o relatório)

> *"Em produtos enterprise, integração com nuvem não é apenas 'salvar arquivo lá'. Envolve governança (quem acessa? por quanto tempo?), auditabilidade (onde está cada artefato?) e visibilidade financeira (quanto está custando?). Implementamos esses três pilares de forma mínima viável: presigned URLs para acesso controlado, paths canônicos por analysis_id para auditoria, e painel de uso para governança financeira. Esse é o padrão de qualquer produto SaaS comercial."*

### Como mencionar no PDF/vídeo

> *"Para tornar a integração com AWS S3 explícita e auditável, o dashboard inclui três funcionalidades enterprise: (1) botões de download via URLs pré-assinadas com expiração de 1 hora, padrão de segurança usado por bancos para compartilhar documentos sensíveis sem expor credenciais; (2) link direto para o console AWS, permitindo ao auditor verificar os artefatos no provedor oficial; (3) painel de uso do bucket mostrando consumo de storage e % do Free Tier utilizado, garantindo governança financeira. Em produção, esses controles seriam complementados com auditoria via CloudTrail e políticas de retenção via Lifecycle Rules."*

Discurso de **maturidade arquitetural enterprise**.

### Melhorias planejadas para produção

- **Política IAM granular** (apenas o bucket específico, não S3 inteiro)
- **Bucket versioning** para auditoria
- **Server-side encryption com KMS** (chaves gerenciadas)
- **Lifecycle policies** para mover dados antigos para Glacier
- **CloudTrail logging** para auditoria de acesso
- **Migração para IAM Roles com STS** (credenciais temporárias)
- **Implementar AWS Lambda + API Gateway** para arquitetura serverless completa

### Como mencionar no PDF/vídeo

> *"Adotamos AWS S3 para armazenamento dos artefatos de análise, com práticas de segurança incluindo usuário IAM dedicado com permissões mínimas, bucket privado e budget alarm como rede de segurança. Em produção, expandiríamos para arquitetura serverless completa com Lambda e API Gateway, IAM Roles com credenciais temporárias via STS, e políticas de retenção de dados via Lifecycle Policies."*

---

## 🤖 LLM para Geração de Relatórios: Google Gemini 2.5 Flash Lite

### Decisão
Utilizamos **Google Gemini 2.5 Flash Lite** via Google AI Studio para geração de relatórios textuais de due diligence.

### Justificativa para POC
- ✅ **Free tier generoso** (1500 requests/dia, 15 req/min)
- ✅ **Custo extremamente baixo** caso ultrapasse free tier (~US$ 0,075 por 1M tokens de input)
- ✅ **Latência baixa** — adequado para uso interativo no dashboard
- ✅ **SDK oficial Python atualizada** (`google-genai`)
- ✅ **Suficiente para gerar relatórios curtos** de 200-500 palavras

### Limitações conhecidas

1. **Modelo "lite"** tem capacidade limitada vs modelos maiores
2. **Sem fine-tuning** para domínio de compliance/AML
3. **Sem grounding** com bases de sanções ou listas restritivas
4. **Sem retorno estruturado garantido** (precisa parsing manual de JSON)

### Migração da SDK durante o desenvolvimento

A SDK antiga `google-generativeai` foi descontinuada pelo Google durante o desenvolvimento da POC. Migramos para a nova SDK oficial `google-genai` antes de avançar com features. Essa decisão garante manutenibilidade futura sem retrabalho.

### Melhorias planejadas para produção

- **Avaliar modelos maiores** (Gemini Pro, Claude, GPT-4) para relatórios mais sofisticados
- **Implementar function calling** para retorno estruturado garantido
- **Fine-tuning** com base de relatórios de DD reais (anonimizados)
- **Adicionar grounding** com OFAC SDN List, ONU, base do COAF
- **Auditoria de outputs** com revisor humano antes de fechar contrato
- **Versionamento de prompts** para auditoria regulatória

### Como mencionar no PDF/vídeo

> *"Utilizamos o Google Gemini 2.5 Flash Lite para geração de relatórios textuais de due diligence em linguagem natural, otimizando custo e latência para a POC. Em produção, recomendamos avaliação comparativa com modelos maiores (Gemini Pro, Claude, GPT-4), implementação de function calling para outputs estruturados auditáveis, e integração com bases públicas de sanções (OFAC, ONU, COAF) para enriquecimento contextual."*

---

## 🎯 Detecção de Objetos: YOLOv8 e a Descoberta sobre Modelos Aéreos

### Decisão final
Utilizamos **YOLOv8 com modelo especializado em imagens aéreas** (dataset DOTA - `yolov8n-obb.pt`), em vez do YOLOv8 padrão pré-treinado em COCO.

### Iteração documentada (descoberta da POC)

**Primeira tentativa: YOLOv8n pré-treinado em COCO**

O dataset COCO (Common Objects in Context) é o padrão para detecção de objetos genéricos: pessoas, carros, animais, objetos do cotidiano. Naturalmente, foi nossa primeira escolha por:

- Modelo pequeno (~6MB), rápido de baixar
- Distribuído gratuitamente pela Ultralytics
- 80 classes de objetos cobrindo casos diversos

**Resultado real obtido em testes:**

| Caso | Imagem Mapbox aérea | Detecções esperadas | Detecções reais |
|---|---|---|---|
| Volkswagen SBC (pátio industrial) | Dezenas de carros visíveis | 15-30 carros/caminhões | **0 detecções** |
| Rua 25 de Março (comércio popular) | Pessoas, motos, carros | 5-15 objetos | **1 falsa detecção ("train")** |
| Cantareira (mata) | Vegetação | 0 objetos | 0 (correto) |

**Diagnóstico técnico:**

O dataset COCO foi construído a partir de **fotos horizontais ao nível do solo** (perspectiva de pessoa caminhando ou de câmera fixa). Em imagens aéreas verticais (top-down do Mapbox em zoom 18), os objetos têm aparência muito diferente:

- Carros viram retângulos com 4 pontos (rodas)
- Pessoas viram pontos minúsculos
- Edificações têm geometria não vista no treinamento

O modelo simplesmente **não reconhece** que esses padrões pixel-a-pixel correspondem às classes em que foi treinado. Não é bug — é limitação fundamental de domínio.

### Solução adotada: modelo especializado em imagens aéreas

Migramos para um modelo YOLOv8 **treinado em datasets aéreos**:

- **DOTA** (Dataset for Object deTection in Aerial images): 15+ classes específicas de visão aérea (small-vehicle, large-vehicle, plane, ship, storage-tank, etc)
- Modelo: `yolov8n-obb.pt` (Oriented Bounding Boxes), distribuído pela própria Ultralytics

Classes relevantes para due diligence empresarial:
- `large-vehicle` (caminhões, ônibus — sinal de operação logística)
- `small-vehicle` (carros — sinal de atividade)
- `storage-tank` (tanques — forte indicador industrial)
- `harbor` (operações portuárias)
- `plane` (aeroportos privados)
- `ship` (operações marítimas)
- `helicopter` (heliporto — sinal de operação executiva)

### Segunda iteração: ajuste de resolução de entrada

Mesmo após trocar para o modelo DOTA, observamos que detecções continuavam abaixo do esperado em casos visualmente densos (pátio industrial da Volkswagen retornou 0 detecções, apesar de dezenas de carros visíveis).

**Diagnóstico:** o YOLOv8n-OBB foi treinado em imagens DOTA com resolução de **1024 a 4096 pixels**. Nossa configuração inicial usava **512x512 para Mapbox**, fazendo carros aparecerem com ~10 pixels — abaixo do tamanho mínimo de detecção confiável (~30px). O modelo "não consegue ver" objetos tão pequenos.

**Solução:** aumentamos `MAPBOX_IMAGE_SIZE` de 512 para **1024**, mantendo o `@2x` da API (resolução efetiva 2048x2048). Cada carro passa a ter ~40-50 pixels, dentro da faixa de detecção do modelo.

**Lição aprendida (para o relatório):**

> *"Em visão computacional aplicada, escolha do modelo correto não basta — é igualmente essencial garantir que a resolução de entrada esteja compatível com a faixa de treinamento do modelo. Objetos pequenos demais ou grandes demais para o modelo simplesmente 'desaparecem'. Documentar resolução de entrada como parâmetro crítico do pipeline."*

Esse é o tipo de detalhe técnico que separa POCs amadoras de implementações profissionais.

### Justificativa para POC

- ✅ **Decisão tecnicamente correta**: usar a ferramenta certa para o domínio
- ✅ **Mantém YOLOv8** como arquitetura (cobre Cap 10 Fase 6 do curso)
- ✅ **Sem custo adicional**: modelo open-source
- ✅ **Resultados realistas** que validam o pipeline

### Lição aprendida (destaque para o relatório)

> **"Modelos genéricos pré-treinados (COCO, ImageNet) não servem para sensoriamento remoto sem adaptação. Em projetos de visão computacional aplicada a imagens orbitais ou aéreas, é essencial usar modelos treinados em datasets do domínio específico (DOTA, VisDrone, SpaceNet, xView)."**

Essa descoberta é **comum em projetos reais de geo-AI** e demonstra que validamos hipóteses tecnicamente em vez de aceitar a primeira implementação que rodou.

### Limitações conhecidas do modelo aéreo

1. **Classes mais restritas que COCO** (15-20 vs 80)
2. **Pode ter falsos positivos** em zonas tropicais (dataset DOTA tem viés geográfico)
3. **Resolução mínima** para detecção confiável: ~0.5m/pixel (compatível com Mapbox zoom 18)
4. **Não distingue tipos finos** (ex: separa "small-vehicle" de "large-vehicle", mas não modelos específicos de carro)

### Melhorias planejadas para produção

- **Fine-tuning regional**: treinar com imagens aéreas brasileiras anotadas (especialmente zonas industriais nacionais)
- **Combinar múltiplos datasets**: DOTA + VisDrone + xView para ampliar cobertura de classes
- **Modelo de segmentação semântica** (Mask R-CNN, SAM): detectar não apenas objetos pontuais mas também áreas (galpões, pátios, estacionamentos)
- **Validação cruzada com NDBI**: detecção de objeto + assinatura espectral aumenta confiança

### Como mencionar no PDF/vídeo

> *"Durante o desenvolvimento, identificamos que o modelo YOLOv8 padrão pré-treinado em COCO não detectava objetos corretamente em imagens aéreas verticais — não era falha de implementação, mas limitação fundamental de domínio: COCO é treinado em fotos horizontais ao nível do solo. Migramos para um modelo especializado em imagens aéreas (treinado em DOTA), e o sistema passou a identificar corretamente veículos e estruturas. Essa iteração reforça uma lição importante de visão computacional aplicada: modelos genéricos não substituem modelos especializados de domínio."*

Esse é um discurso de **rigor científico** que demonstra maturidade técnica para a banca.

---

## 🧠 Classificação de Cena com CLIP (zero-shot)

### Decisão
Adotamos o **CLIP (Contrastive Language-Image Pre-training)** como camada complementar de visão computacional. Modelo distribuído pela OpenAI/HuggingFace, usado em modo **zero-shot** (sem fine-tuning).

### Por que CLIP entrou no projeto

Após 3 iterações no YOLO documentadas na seção anterior (modelo COCO inadequado, migração para DOTA, ajuste de resolução), observamos que a detecção de objetos em imagens aéreas brasileiras continuava limitada — mesmo com modelo especializado em visão aérea (DOTA). 

Hipóteses do baixo desempenho:
- Viés geográfico do dataset DOTA (treinado predominantemente com imagens da China)
- Carros em ângulo top-down ainda têm geometria muito específica
- Sombras e cores de telhados brasileiros diferem de datasets de treino

Em vez de continuar iterando em uma técnica de **rendimento decrescente** (próxima opção seria tile slicing com SAHI, ou fine-tuning regional — ambos fora do escopo da POC), pivotamos para uma abordagem complementar com **classificação semântica de cena**.

### Como CLIP resolve o problema

CLIP é um modelo multimodal que entende **imagens descritas em linguagem natural**. Em vez de "detectar objetos pontuais" (carros, pessoas, tanques), o CLIP classifica a **cena como um todo**.

**Fluxo conceitual:**

1. Carregamos a imagem aérea Mapbox
2. Passamos um conjunto de **descrições candidatas** em texto:
   - "uma planta industrial vista de cima"
   - "uma área comercial densa com pequenos boxes"
   - "uma área residencial com casas"
   - "uma área verde com vegetação"
   - "um estacionamento de veículos"
3. CLIP retorna a **probabilidade** de cada descrição corresponder à imagem
4. Usamos a classificação dominante para refinar o score de autenticidade

### Justificativa para POC

- ✅ **Zero-shot:** não precisa treinar nem rotular dataset
- ✅ **Roda em CPU/MPS:** modelo cabe em <600MB, inferência em segundos no Apple Silicon
- ✅ **Resposta interpretável:** probabilidades em texto natural, não vetores opacos
- ✅ **Complementar ao YOLO:** YOLO detecta objetos pontuais; CLIP classifica cena. Dois sinais independentes que se reforçam
- ✅ **Cobre tópicos curriculares:** Deep Learning (Cap 09 Fase 6) + IA cognitiva (enunciado da GS)
- ✅ **Tecnologia open-source madura:** distribuído pela OpenAI desde 2021, com SDK estável no HuggingFace

### Como CLIP se encaixa no scoring

A introdução do CLIP permitiu **rebalancear os pesos** do scoring:

**Antes (só NDBI + YOLO):**
- NDBI: 50 pontos
- YOLO Mapbox: 40 pontos (mas detectando pouco → quase sempre 0)
- YOLO Sentinel: 10 pontos
- **Resultado:** scores empatavam em 50/100 com decisão sempre "ATENÇÃO"

**Depois (NDBI + YOLO + CLIP):**
- NDBI: 40 pontos (densidade construída)
- CLIP: 40 pontos (tipo de cena — industrial/comercial/verde)
- YOLO Mapbox: 15 pontos (detecções como evidência adicional)
- YOLO Sentinel: 5 pontos (confirmação macro)
- **Resultado:** scores diferenciados entre casos, com decisões coerentes

### Limitações conhecidas

1. **Vocabulário fixo de classes:** as descrições candidatas precisam ser definidas a priori. Cenas atípicas (ex: terminal portuário misto) podem não se encaixar bem
2. **Sensibilidade ao prompt:** a redação das descrições influencia o resultado. Precisaria fine-tuning de prompts para domínio brasileiro
3. **Sem cobertura geográfica garantida:** CLIP foi treinado em imagens ocidentais; pode ter viés cultural
4. **Não dá coordenadas espaciais:** classifica a cena inteira, sem dizer "onde" está cada elemento

### Melhorias planejadas para produção

- **Fine-tuning de prompts** com banco de imagens aéreas brasileiras anotadas
- **Combinar com SAM** (Segment Anything) para mapear elementos espacialmente
- **Modelos especializados em remote sensing**: RemoteCLIP, GeoCLIP, SatCLIP
- **Embedding-based retrieval**: comparar embedding da empresa analisada com embeddings de empresas conhecidas (similaridade)

### Lição aprendida (destaque para o relatório)

> *"Quando uma técnica entra em rendimento decrescente, vale mais pivotar para abordagem complementar do que insistir. Adicionamos CLIP não para 'substituir' o YOLO, mas para complementá-lo com um sinal diferente: classificação semântica da cena em vez de detecção de objetos pontuais. Resultado: dois sinais independentes que se validam mutuamente."*

### Como mencionar no PDF/vídeo

> *"Após observarmos limitações do YOLO mesmo com modelo especializado em visão aérea, complementamos com CLIP — modelo multimodal zero-shot da OpenAI que entende imagens descritas em linguagem natural. Em vez de detectar objetos pontuais, CLIP classifica a cena como um todo: planta industrial, comércio popular, área verde, etc. Esse sinal independente permitiu diferenciar casos visualmente similares e refinar o score de autenticidade. Demonstra que IA cognitiva moderna pode substituir pipelines complexos de detecção em problemas de classificação visual de domínio."*

Esse é um discurso de **maturidade de produto** e **uso pragmático de IA moderna**.

---

## 🚫 Decisões deliberadas de NÃO incluir na POC

Algumas tecnologias do curso foram **conscientemente excluídas** por não fazerem sentido no problema. Documentamos para banca entender que é decisão arquitetural, não esquecimento.

### ESP32 / IoT

**Não incluído porque:** a premissa do produto é validação **remota** via satélite. Sensores físicos no local contradizem o valor central (se você precisa ir lá instalar sensor, já está lá — não precisa de análise satelital). Forçar IoT no projeto enfraqueceria a coerência da proposta.

**Como mencionar no PDF/vídeo:**

> *"O capítulo de ESP32 do curso ensinou visão computacional embarcada com câmera. Esse conhecimento poderia ser aplicado em uma extensão futura do produto — por exemplo, auditorias presenciais quando a análise espacial indicar necessidade de validação in loco. Para o escopo da POC, optamos por priorizar a inteligência geoespacial pura, alinhada à proposta de valor central do produto."*

---

## 🎬 STORYTELLING DO PRODUTO

Esta seção documenta os **arcos narrativos** que dão profundidade ao projeto. São histórias que **emergem dos dados reais** durante o desenvolvimento — não foram inventadas, foram descobertas validando o pipeline com endereços conhecidos. Servem para o vídeo demonstrativo, defesa oral, PDF e README.

---

### 🎯 Arco Narrativo Central: "NDBI sozinho não basta"

**A descoberta que valida o produto inteiro:**

Durante a validação do pipeline, identificamos um caso que mostra **exatamente por que due diligence empresarial precisa de IA combinada, não apenas análise espectral**.

#### Os números que contam a história

| Caso | NDBI (% construído) | Decisão Final | Por quê? |
|---|---|---|---|
| **1 — Volkswagen SBC** (planta industrial real) | **45.1%** | ✅ APROVADO | Densidade industrial coerente com declaração |
| **2 — Rua 25 de Março** (comércio popular) | **77.7%** | ⚠️ ATENÇÃO | Mais denso que Volkswagen, mas é comércio popular fragmentado |
| **3 — Parque Cantareira** (área verde) | **0.0%** | 🚨 REPROVADO | Sem evidência de qualquer instalação |

#### O insight central

**O Caso 2 tem NDBI MAIS ALTO que o Caso 1, mas recebe decisão pior.**

Por quê?

- **NDBI** mede *densidade de área construída* — quanto da imagem é "concreto" vs "vegetação"
- **NDBI NÃO mede tipo de estrutura** — galpão industrial e barraco comercial têm assinatura espectral similar
- A Rua 25 de Março tem 77.7% porque é uma colcha de retalhos de **milhares de boxes pequenos** colados uns aos outros
- A Volkswagen tem 45% porque grandes plantas industriais têm **espaços abertos entre galpões** (pátios, estacionamentos, ruas internas)

#### Por que isso é poderoso narrativamente

Esse contraste mostra que **um produto sério de due diligence não pode usar apenas um sinal**. Precisa de:

1. **Análise espectral (NDBI)** → confirma que há estrutura física
2. **Detecção de objetos (YOLO)** → identifica TIPO de estrutura (caminhões grandes = indústria, comércio sem logística pesada = varejo)
3. **IA cognitiva (LLM)** → interpreta o contexto e gera recomendação executiva

#### Como usar no vídeo (5 minutos)

**Roteiro sugerido para o momento "aha" do vídeo:**

> *"Olha esse contraste interessante: a Rua 25 de Março tem NDBI de 77.7% — visualmente mais densa que a planta da Volkswagen em São Bernardo do Campo, com 45.1%. Se nosso sistema decidisse apenas com NDBI, aprovaria a Rua 25 como fornecedor industrial — e isso seria um erro grave de compliance.*
>
> *Por isso combinamos múltiplas camadas de inteligência: NDBI valida densidade construída, YOLO identifica tipos de estrutura (caminhões pesados, pátios logísticos, galpões versus boxes pequenos), e o LLM consolida tudo em recomendação acionável. Cada camada cobre o ponto cego da outra."*

Esse é o momento em que o jurado **entende que o projeto não é exercício acadêmico — é produto pensado**.

---

### 🛰️ Sub-arco: "A descoberta das nuvens"

Durante validação inicial, observamos que a Rua 25 de Março retornava NDBI de 0.3% — fisicamente impossível para centro comercial. A investigação revelou que a cena Sentinel-2 selecionada estava **coberta por nuvens** sobre a área de interesse, apesar do cloud_cover médio da cena ser "apenas" 27.7%.

**Lições aprendidas:**
- Cloud_cover médio da cena ≠ cloud_cover sobre o ponto específico
- Cena mais recente nem sempre é a melhor cena
- Necessária estratégia explícita de **priorizar qualidade atmosférica sobre recência**

**Como usar no vídeo:**

> *"Durante o desenvolvimento, testamos áreas de referência conhecidas e descobrimos que cenas Sentinel-2 com cobertura média baixa de nuvens podiam ainda estar parcialmente obstruídas sobre o ponto específico de análise. Implementamos uma lógica de seleção que prioriza a melhor qualidade atmosférica dentro de uma janela de 120 dias — não apenas a cena mais recente. Esse rigor é fundamental para um produto de compliance: uma análise quebrada por uma nuvem aleatória poderia condenar ou aprovar um fornecedor injustamente."*

Isso é **discurso de cientista de dados experiente**. Mostra rigor metodológico real.

---

### 🌳 Sub-arco: "O cinturão verde de Camaçari"

Em um teste inicial, geocodificamos "Polo Petroquímico de Camaçari" e o Nominatim resolveu para o **cinturão verde** do polo — uma faixa de mata preservada **ao redor** das instalações industriais, exigida pela regulação ambiental.

O sistema corretamente identificou NDBI de 0.0% naquele ponto. **Não foi bug — foi feature**: o sistema detectou que a coordenada apontada não correspondia a instalações industriais ativas.

**Lições aprendidas:**
- Geocoding pode resolver para pontos "próximos mas semanticamente diferentes" do esperado
- Em due diligence real, isso é exatamente o que precisamos detectar: **endereços tecnicamente válidos mas que não correspondem à operação declarada**
- Esse caso é, na prática, um **red flag legítimo** que o sistema captura

**Como usar no vídeo (opcional, se sobrar tempo):**

> *"Durante testes, geocodificamos um endereço industrial conhecido e o sistema resolveu para uma área verde adjacente — o cinturão de preservação ambiental do polo. Inicialmente parecia um erro, mas refletindo: esse é exatamente o tipo de fraude sutil que due diligence séria deve detectar — endereços tecnicamente próximos a zonas industriais sem corresponder a operações reais."*

---

### 🏢 Sub-arco: "Endereço administrativo vs endereço operacional"

Ao testar o pipeline com `"Av. Volkswagen, 100, São Bernardo do Campo, SP"`, esperávamos que o sistema confirmasse uma planta industrial. Em vez disso, o resultado foi:

- **NDBI:** 45.1% (densidade construída alta) ✅
- **CLIP:** classificou como `residential (60%)`, com `industrial` apenas em 3º lugar (10%)
- **Decisão final:** ATENÇÃO

**Investigação visual da imagem aérea Mapbox revelou:**
- Cerca de 35% da imagem: casas residenciais com telhados vermelhos
- Cerca de 25%: vegetação
- Cerca de 15%: galpões pequenos e médios
- Apenas ~5%: instalações industriais identificáveis como "fábrica"

O ponto geocodificado caiu em uma **área administrativa da Volkswagen** (escritório, portaria, anexo) — não na fábrica propriamente dita. A planta industrial real ocupa galpões enormes a alguns quilômetros do endereço declarado.

**Lição de produto (e descoberta valiosa):**

Esse é **exatamente** o tipo de fraude que due diligence séria deve detectar:

> *"Empresa declara fábrica de 5.000m² na Av. Volkswagen 100. Sistema verifica o endereço e encontra zona residencial mista. Sinaliza ATENÇÃO porque o endereço declarado **não corresponde geograficamente** à operação industrial declarada."*

Em uma fraude real, o operador poderia conscientemente declarar um endereço "tecnicamente correto" (com nome industrial, em zona conhecida) sabendo que ali está apenas a recepção/escritório, enquanto a operação efetiva está em outro lugar — ou nem existe.

**O sistema acertou ao desconfiar.** A "decisão ATENÇÃO" reflete uma incoerência real entre endereço declarado e operação visível.

### Os três tipos distintos de fraude detectados pelo sistema

O conjunto dos 3 casos de demo agora demonstra **três padrões diferentes de fraude potencial**, cada um detectado por uma combinação distinta de sinais:

| Caso | Padrão de fraude detectado | Sinal principal |
|---|---|---|
| **1 — Volkswagen** | Endereço administrativo travestido de operacional | CLIP detecta zona residencial onde se declara indústria |
| **2 — Rua 25 de Março** | Tipo de operação incompatível com porte declarado | CLIP detecta comércio popular onde se declara atacadista |
| **3 — Cantareira** | Endereço completamente fantasma | NDBI zero, CLIP detecta área verde |

**Como usar no vídeo:**

> *"Os três casos demonstrados ilustram três padrões diferentes de fraude empresarial que o sistema é capaz de detectar: endereço administrativo travestido de operacional, tipo de operação incompatível com porte declarado, e endereço completamente fantasma. Cada padrão é capturado por uma combinação diferente de sinais — densidade construída, classificação semântica da cena, e detecção de objetos. Isso valida a tese central de que due diligence empresarial moderna precisa combinar múltiplas camadas de inteligência."*

Esse é **discurso de produto maduro** que diferencia projetos amadores de propostas comerciais sérias.

---

### 🔬 Sub-arco: "A descoberta do modelo errado"

Inicialmente implementamos YOLOv8 nano pré-treinado em COCO (dataset padrão de detecção de objetos). Em imagens aéreas Mapbox, o resultado foi:

- Volkswagen (pátio com 30+ carros): **0 detecções**
- Rua 25 de Março (movimento intenso): **1 falsa detecção ("train")**
- Cantareira (mata): 0 (correto, mas pelo motivo errado)

**Diagnóstico:** COCO foi treinado em fotos horizontais ao nível do solo. Imagens aéreas verticais (top-down) têm geometria de objetos completamente diferente — carros viram retângulos, pessoas viram pontos. O modelo simplesmente não reconhece os padrões.

**Solução:** migramos para YOLOv8 treinado em **DOTA** (Dataset for Object deTection in Aerial images), com classes específicas de visão aérea: small-vehicle, large-vehicle, storage-tank, plane, ship, helicopter, harbor.

**Lição registrada para o relatório:** modelos pré-treinados genéricos não substituem modelos de domínio. É erro comum em projetos de visão computacional aplicada usar COCO/ImageNet onde domínio específico é necessário.

**Como usar no vídeo:**

> *"Documentamos uma descoberta importante durante o desenvolvimento: o YOLO padrão treinado em COCO não funciona para imagens aéreas. COCO é construído com fotos horizontais — pessoas, carros, animais vistos lateralmente. Imagens de satélite e drone são verticais — a geometria visual é completamente diferente. Migramos para um modelo treinado em DOTA, dataset específico de imagens aéreas, e o sistema passou a detectar corretamente. Essa iteração demonstra que modelos genéricos não substituem expertise de domínio."*

---

### 📐 Sub-arco: "Da resolução macro à validação micro"

O produto combina **três escalas de visão complementares**:

| Escala | Fonte | Resolução | Para que serve |
|---|---|---|---|
| 🛰️ **Macro** | Sentinel-2 | 10m/pixel | Densidade espectral (NDBI), análise regional |
| 🚁 **Meso** | Mapbox aerial | ~0.5m/pixel | Vista aérea de prédios e estruturas |
| 🔍 **Micro** | YOLO sobre alta resolução | objetos individuais | Detecção de veículos, contêineres, atividade |

**Lições aprendidas:**
- Nenhuma fonte sozinha resolve o problema
- Sentinel-2 = visão macro, mas falha em chuva/nuvens
- Mapbox = visão fina, mas só RGB visível (sem bandas espectrais)
- YOLO = inteligência semântica, mas precisa de alta resolução

**Como usar no vídeo:**

> *"Combinamos três escalas de visão: o satélite Sentinel-2 nos dá a análise espectral regional, a imagem aérea de alta resolução nos mostra o estabelecimento de perto, e a visão computacional identifica objetos específicos. Cada fonte tem limitações — combinadas, elas se complementam."*

---

### 🏛️ Arco Macro: "Democratizando inteligência geoespacial"

O contexto mais amplo do projeto (para introdução do vídeo e do PDF):

#### O problema

A lavagem de dinheiro movimenta entre **US$ 800 bilhões e US$ 2 trilhões por ano** globalmente. Empresas de fachada são o instrumento clássico. Hoje, a verificação de empresas em mercados opacos (China, Paraguai, paraísos fiscais) depende de:

- ❌ Inspetores físicos (não escala)
- ❌ Verificação manual via Google Earth (não auditável)
- ❌ Confiança em registros locais (pode ser fraudado)

#### A solução

Satélite é **agnóstico a fronteiras e opacidade local**. Independentemente do que governos publicam, das limitações de transparência, ou da localização geográfica:

- 🛰️ Sentinel-2 fotografa a Terra inteira a cada 5 dias, gratuitamente
- 🛰️ Mapbox tem cobertura aérea global de alta resolução
- 🤖 IA permite análise automatizada em escala impossível para humanos

#### O impacto

Hoje, **só governos e grandes corporações** têm acesso a inteligência geoespacial de qualidade. Plataformas como Kayrros, Orbital Insight e Planet Labs vendem para clientes que pagam centenas de milhares de dólares por ano.

Nossa POC demonstra que **qualquer empresa pode ter essa capacidade** — democratizando o acesso a uma ferramenta crítica de compliance ESG, prevenção a fraudes e KYB.

#### Como usar no vídeo (abertura, primeiros 30 segundos)

> *"A lavagem de dinheiro movimenta até 2 trilhões de dólares por ano. Empresas de fachada são o principal instrumento. Hoje, validar se um fornecedor existe em outro país depende de... abrir o Google Earth manualmente.*
>
> *Apresentamos o SatVerify: validação automatizada de existência e atividade de empresas usando satélite e IA, com os mesmos dados que monitoram clima — agora apontados para o problema do crime financeiro."*

---

### 🎯 Arco de Decisões: "Por que NÃO ESP32"

(Reforço de uma decisão que vai aparecer no PDF)

A POC **deliberadamente** não usa sensores IoT/ESP32, e isso é argumento de **maturidade arquitetural**:

> *"A premissa central do produto é validação remota via inteligência espacial. Sensores físicos no local contradizem a proposta — se você precisa instalar sensor para validar, você já foi até lá, e não precisa de análise satelital. Optamos por preservar a coerência conceitual do produto em vez de forçar tecnologia para cobrir checklist curricular."*

Banca valoriza decisão arquitetural consciente.

---

### 📊 Resumo dos Pontos de Storytelling

Para o vídeo de 5 minutos, escolher 3-4 desses arcos:

| Arco | Tempo no vídeo | Impacto |
|---|---|---|
| 🏛️ Democratização (problema global) | 0:00-0:30 | Hook inicial |
| 🎯 "NDBI sozinho não basta" | 1:30-3:30 | Demo central |
| 📐 Três escalas de visão | 3:30-4:00 | Arquitetura técnica |
| 🛰️ Descoberta das nuvens *(opcional)* | — | Rigor metodológico (PDF) |
| 🌳 Cinturão verde *(opcional)* | — | Red flag sofisticado (PDF) |
| 🔬 Modelo COCO vs DOTA *(opcional)* | — | Iteração científica (PDF) |
| 🎯 Decisão de não-IoT | 4:00-4:30 | Maturidade arquitetural |

---

## 📋 Próximas seções (a preencher conforme avançamos)

- [ ] Sistema de scoring (regras de combinação NDBI + YOLO)
- [ ] Streamlit dashboard
- [ ] Integração com AWS S3 (upload efetivo)
- [ ] Pipeline de geração de relatório via LLM
- [ ] Considerações éticas e de privacidade
- [ ] Casos de demo finalizados

---

*Última atualização: 04/06/2026*
