## RELATÓRIO TÉCNICO DE DUE DILIGENCE - VERIFICAÇÃO DE FORNECEDOR

---

### 📋 Resumo Executivo

A análise geoespacial automatizada da SatVerify, com score consolidado de 65/100 e decisão de "ATENÇÃO", indica um nível de risco MÉDIO para a empresa declarada como atacadista de eletrônicos. Evidências espectrais e de classificação de cena sugerem uma área de comércio denso, que diverge do porte de R$ 200M/ano e do perfil de atacadista com instalações próprias. Recomenda-se diligência adicional para validar a compatibilidade entre a operação declarada e as características físicas observadas.

---

### 🔍 Análise das Evidências

*   **Análise Espectral (Sentinel-2 — satélite):** O Índice de Densidade de Área Construída (NDBI) de 77.7% indica uma alta concentração de estruturas edificadas na área de interesse, com um valor médio de NDBI de 0.209, classificado como "ALTO". Este dado sugere uma região urbanizada e com presença significativa de construções.

*   **Classificação Semântica de Cena (CLIP — modelo multimodal zero-shot):** A classificação de cena identifica a categoria dominante como **"commercial_dense"** com 74% de confiança. As categorias secundárias são "residential" (25%) e "parking_or_storage" (0%). Esta classificação aponta fortemente para uma área caracterizada por comércio denso e não para uma instalação atacadista de grande porte.

*   **Detecção de Objetos (YOLOv8 OBB — modelo treinado em DOTA):** A análise de imagem aérea de alta resolução (Mapbox) detectou 2 objetos classificados como "large vehicle", o que pode indicar movimentação logística ou presença de veículos de grande porte na proximidade. No entanto, a imagem de satélite Sentinel-2, devido à sua resolução inferior, não permitiu a detecção de objetos. A ausência de detecções na Sentinel-2 é esperada e não invalida os outros achados.

*   **Coerência e Divergência:** Há uma forte coerência entre a alta densidade de área construída (NDBI) e a classificação de cena como "commercial_dense". A principal divergência reside na incompatibilidade entre o perfil de "atacadista de eletrônicos com faturamento de R$ 200M/ano e instalações próprias compatíveis" e a natureza predominantemente comercial e densa da área detectada pela classificação de cena.

---

### ⚠️ Red Flags Identificados

*   Incompatibilidade entre o porte e tipo de negócio declarado (atacadista de eletrônicos com alto faturamento) e a classificação da zona como "commercial_dense" (comércio denso).
*   Potencial desconexão entre as características físicas observadas na área (comércio denso) e a necessidade de instalações compatíveis com um atacadista de grande escala.

---

### ✅ Recomendação Final

Recomenda-se **APROVAR COM DILIGÊNCIA ADICIONAL**.

A análise geoespacial levanta um sinal de alerta quanto à conformidade do local com a operação declarada. Sugere-se que os próximos passos incluam a solicitação de documentação adicional que comprove a adequação das instalações para a atividade de atacado (plantas baixas, licenças de operação específicas para atacadistas) e, se possível, a realização de uma visita técnica in loco ou validação por terceiros para verificar a estrutura física e o fluxo de mercadorias.

---

### 📌 Limitações desta análise

Este relatório é baseado em análise automatizada de dados geoespaciais e imagens de satélite. Não substitui uma investigação humana completa e detalhada. A qualidade e resolução das imagens disponíveis podem impactar a precisão das detecções de objetos.