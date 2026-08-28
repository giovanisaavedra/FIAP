# 📖 Dicionário de Dados — `heart_disease_cleveland.csv`

**Fonte:** Heart Disease (Cleveland) — UCI Machine Learning Repository (id=45)
**DOI:** 10.24432/C52P4X | **Licença:** CC BY 4.0
**Registros:** 303 pacientes | **Variáveis:** 14
**Valores ausentes:** representados como célula vazia (`ca`: 4 ausentes; `thal`: 2 ausentes)

| # | Variável | Tipo | Descrição | Domínio / Unidade |
|---|----------|------|-----------|-------------------|
| 1 | `age` | numérica | Idade do paciente | anos |
| 2 | `sex` | categórica | Sexo biológico | 1 = masculino; 0 = feminino |
| 3 | `cp` | categórica | Tipo de dor torácica | 1 = angina típica; 2 = angina atípica; 3 = dor não anginosa; 4 = assintomático |
| 4 | `trestbps` | numérica | Pressão arterial em repouso (na admissão) | mm Hg |
| 5 | `chol` | numérica | Colesterol sérico | mg/dl |
| 6 | `fbs` | categórica | Glicemia de jejum > 120 mg/dl | 1 = verdadeiro; 0 = falso |
| 7 | `restecg` | categórica | Resultado do ECG em repouso | 0 = normal; 1 = anormalidade de onda ST-T; 2 = hipertrofia ventricular esquerda provável/definitiva |
| 8 | `thalach` | numérica | Frequência cardíaca máxima atingida | bpm |
| 9 | `exang` | categórica | Angina induzida por exercício | 1 = sim; 0 = não |
| 10 | `oldpeak` | numérica | Depressão do segmento ST induzida por exercício em relação ao repouso | mm |
| 11 | `slope` | categórica | Inclinação do segmento ST no pico do exercício | 1 = ascendente; 2 = plana; 3 = descendente |
| 12 | `ca` | numérica | Número de vasos principais coloridos por fluoroscopia | 0 a 3 |
| 13 | `thal` | categórica | Cintilografia com tálio | 3 = normal; 6 = defeito fixo; 7 = defeito reversível |
| 14 | `num` | categórica (alvo) | Diagnóstico de doença cardíaca (estreitamento angiográfico) | 0 = ausência (< 50%); 1–4 = presença em graus crescentes (> 50%) |

## Notas de governança

- Os dados são **reais e anonimizados** (nomes e números de seguro social foram removidos pela fonte e substituídos por valores fictícios).
- A base de Cleveland é a única das quatro bases do repositório (Cleveland, Hungria, Suíça, Long Beach) amplamente utilizada por pesquisadores de ML, por sua qualidade e completude.
- **Viés conhecido:** predominância de pacientes do sexo masculino (~68%) e origem em um único centro (Cleveland Clinic Foundation, EUA, 1988) — considerar rebalanceamento e validação por subgrupo nas próximas fases.
- Para tarefas de classificação binária, é usual binarizar o alvo: `0` = sem doença; `1–4` = com doença.

## Referência

Janosi, A., Steinbrunn, W., Pfisterer, M., & Detrano, R. (1989). *Heart Disease* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C52P4X
