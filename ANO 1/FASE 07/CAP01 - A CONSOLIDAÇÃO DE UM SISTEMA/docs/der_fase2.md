# 🗄️ FarmTech Solutions — Fase 2: Modelo Entidade-Relacionamento

Diagrama do banco de dados SQLite utilizado pelo sistema (Fase 2)
e renderizado também na página `2_🗄️_Fase2_CRUD_Banco.py` do
dashboard. O GitHub renderiza blocos `mermaid` automaticamente.

## Relacionamentos

- `sensores` **1:N** `leituras_sensores` *(um sensor gera várias leituras)*
- `sensores` **1:N** `alertas` *(um sensor pode disparar vários alertas)*
- `culturas` **1:N** `previsoes_ml` *(cada cultura recebe várias previsões)*

## Diagrama (Mermaid)

```mermaid
erDiagram
    SENSORES ||--o{ LEITURAS_SENSORES : "gera"
    SENSORES ||--o{ ALERTAS           : "dispara"
    CULTURAS ||--o{ PREVISOES_ML      : "recebe"

    SENSORES {
        TEXT      sensor_id PK
        TEXT      tipo_sensor
        TEXT      localizacao
        TEXT      farm_id
        REAL      latitude
        REAL      longitude
        TIMESTAMP data_instalacao
        TEXT      status
        TIMESTAMP ultima_calibracao
    }

    LEITURAS_SENSORES {
        INTEGER   leitura_id PK
        TEXT      sensor_id FK
        TIMESTAMP timestamp
        REAL      N
        REAL      P
        REAL      K
        REAL      soil_pH
        REAL      soil_moisture
        REAL      temperature_C
        REAL      humidity_percent
        REAL      rainfall_mm
        REAL      sunlight_hours
        REAL      irrigation_volume_mm
        TEXT      qualidade_leitura
    }

    CULTURAS {
        INTEGER cultura_id PK
        TEXT    farm_id
        TEXT    crop_type
        REAL    area_hectares
        DATE    data_plantio
        DATE    data_colheita_prevista
        DATE    data_colheita_real
        TEXT    status_cultura
    }

    PREVISOES_ML {
        INTEGER   previsao_id PK
        INTEGER   cultura_id FK
        TIMESTAMP timestamp
        REAL      input_N
        REAL      input_P
        REAL      input_K
        REAL      input_soil_pH
        REAL      input_temperature
        REAL      input_humidity
        REAL      input_rainfall
        REAL      previsao_irrigacao_mm
        REAL      previsao_N_fertilizacao
        REAL      previsao_P_fertilizacao
        REAL      previsao_K_fertilizacao
        REAL      previsao_rendimento_kg_ha
        TEXT      modelo_usado
        REAL      confianca_previsao
    }

    ALERTAS {
        INTEGER   alerta_id PK
        TEXT      sensor_id FK
        TIMESTAMP timestamp
        TEXT      tipo_alerta
        TEXT      severidade
        TEXT      mensagem
        INTEGER   resolvido
        TIMESTAMP data_resolucao
    }
```
