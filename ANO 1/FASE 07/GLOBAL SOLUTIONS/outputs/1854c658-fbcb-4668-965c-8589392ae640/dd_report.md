## RELATÓRIO TÉCNICO DE DUE DILIGENCE (KYB/AML) - ANÁLISE GEOESPACIAL

**Empresa sob Análise:** Fabricante Industrial de Autopeças
**Endereço Declarado:** Av. Volkswagen, 100, São Bernardo do Campo, SP, Brasil
**Data da Análise:** 2026-05-05

---

### 📋 Resumo Executivo

A análise geoespacial automatizada do endereço declarado resultou em um score consolidado de **50/100**, com a decisão automatizada de **ATENÇÃO** e nível de risco **MÉDIO**. As evidências sugerem uma incompatibilidade entre a atividade declarada (fabricante industrial) e a classificação semântica predominante do local, que indica predominantemente área residencial. Portanto, recomenda-se diligência adicional para validação da infraestrutura operacional da empresa.

---

### 🔍 Análise das Evidências

A **análise espectral (Sentinel-2)**, utilizando o índice NDBI (Normalized Difference Built-up Index), aponta uma densidade de área construída de 45.1%, classificada como **ALTA**. Este indicador sugere a presença de edificações significativas, o que é parcialmente coerente com uma instalação industrial.

No entanto, a **classificação semântica de cena (CLIP)** apresenta uma forte predominância de **residencial (60% de confiança)**, seguida por áreas de estacionamento/armazenamento (14%) e apenas 10% de categoria industrial. Esta divergência é um ponto crítico, pois a declaração é de fabricação industrial. É importante considerar que o endereço geocodificado, "Volkswagen do Brasil, Parque Terra Nova I", pode se referir a uma área administrativa ou de serviços da Volkswagen, e não necessariamente às instalações fabris principais da empresa em análise.

A **detecção de objetos (YOLOv8 OBB)**, utilizando imagem aérea de alta resolução (Mapbox), identificou apenas 1 objeto de "piscina" e 1 objeto de "veículo grande". A ausência de detecção de equipamentos industriais pesados, empilhadeiras ou outras evidências típicas de uma fábrica nesta imagem de alta resolução é notável. A imagem de satélite Sentinel-2 não gerou detecções de objetos, o que é esperado devido à sua menor resolução para este tipo de análise específica.

A principal incoerência reside entre a alta densidade de área construída (NDBI) e a classificação semântica predominante como residencial. Enquanto o NDBI sugere edificações, a classificação semântica aponta para um uso não industrial.

---

### ⚠️ Red Flags Identificados

*   Predominância da classificação semântica como área residencial (60%), contrastando com a declaração de fabricante industrial.
*   Ausência de detecção de objetos típicos de atividade industrial em imagem aérea de alta resolução.

---

### ✅ Recomendação Final

Recomenda-se **aprovação com diligência adicional**. Dada a divergência significativa entre a natureza da atividade declarada e os sinais geoespaciais, é imperativo que sejam realizadas validações adicionais. Sugerimos os seguintes próximos passos:

1.  **Solicitação de documentação complementar:** Pedir plantas baixas, licenças de operação e fotos internas que comprovem a atividade fabril.
2.  **Inspeção presencial ou remota detalhada:** Caso possível, uma visita ao local ou uma videoconferência que permita visualizar as instalações de produção.
3.  **Validação por fontes de informação secundárias:** Buscar notícias, relatórios ou informações públicas que corroborem a operação industrial no endereço declarado.

---

### 📌 Limitações desta análise

Esta análise é automatizada e baseada em sinais geoespaciais e imagens de satélite disponíveis. Não substitui a diligência humana completa e a investigação de documentos e fontes de informação tradicionais. A precisão e a capacidade de detecção de objetos dependem intrinsecamente da qualidade e resolução das imagens de satélite e aéreas acessíveis.