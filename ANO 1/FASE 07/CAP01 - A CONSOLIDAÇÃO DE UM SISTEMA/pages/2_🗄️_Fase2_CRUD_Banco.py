"""
FarmTech Solutions - Fase 2: CRUD do Banco de Dados
Interface Streamlit para operar o banco SQLite ``farmtech_iot.db``:
consulta de tabelas, cadastro de sensores e leituras, atualização
de status, exclusão controlada e visualização do modelo (MER/DER).

Atenção à concorrência: o simulador IoT pode estar gravando em
paralelo. Cada interação aqui abre uma conexão **curta** via
``FarmTechDatabase`` (que já usa ``sqlite3.connect(..., timeout=10)``)
e a fecha em ``finally``.

Autores: Giovani Saavedra e Marcio Elifas
RM: RM566797 e RM567871
GRUPO 37
1TIAOS - FIAP

FIAP - Fase 7 - 2026
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import date, timedelta
from pathlib import Path
from typing import Iterator

import pandas as pd
import streamlit as st

from database_manager import FarmTechDatabase
from utils import render_header, render_sidebar


# ==========================================================
#         CONFIGURAÇÃO DA PÁGINA
# ==========================================================

st.set_page_config(
    page_title="Fase 2 - CRUD Banco",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "farmtech_iot.db"
DOC_DER = BASE_DIR / "docs" / "der_fase2.md"


# ==========================================================
#         GERENCIADOR DE CONEXÃO CURTA
# ==========================================================

@contextmanager
def abrir_db() -> Iterator[FarmTechDatabase]:
    """Context manager que abre e fecha a conexão de forma segura.

    Usa o ``FarmTechDatabase`` (com ``timeout=10``) e garante o
    ``fechar_conexao`` mesmo em caso de exceção, evitando segurar
    o lock do SQLite enquanto o simulador IoT também está gravando.
    """
    db = FarmTechDatabase(str(DB_PATH))
    try:
        yield db
    finally:
        db.fechar_conexao()


# ==========================================================
#         SQL DE CRIAÇÃO (espelho do database_manager.py)
# ==========================================================

SQL_SCHEMA = """\
CREATE TABLE IF NOT EXISTS sensores (
    sensor_id         TEXT PRIMARY KEY,
    tipo_sensor       TEXT NOT NULL,
    localizacao       TEXT,
    farm_id           TEXT,
    latitude          REAL,
    longitude         REAL,
    data_instalacao   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status            TEXT      DEFAULT 'ativo',
    ultima_calibracao TIMESTAMP
);

CREATE TABLE IF NOT EXISTS leituras_sensores (
    leitura_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id            TEXT NOT NULL,
    timestamp            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    N                    REAL,
    P                    REAL,
    K                    REAL,
    soil_pH              REAL,
    soil_moisture        REAL,
    temperature_C        REAL,
    humidity_percent     REAL,
    rainfall_mm          REAL,
    sunlight_hours       REAL,
    irrigation_volume_mm REAL,
    qualidade_leitura    TEXT      DEFAULT 'normal',
    FOREIGN KEY (sensor_id) REFERENCES sensores (sensor_id)
);

CREATE TABLE IF NOT EXISTS culturas (
    cultura_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    farm_id                TEXT NOT NULL,
    crop_type              TEXT NOT NULL,
    area_hectares          REAL,
    data_plantio           DATE,
    data_colheita_prevista DATE,
    data_colheita_real     DATE,
    status_cultura         TEXT DEFAULT 'em_crescimento'
);

CREATE TABLE IF NOT EXISTS previsoes_ml (
    previsao_id               INTEGER PRIMARY KEY AUTOINCREMENT,
    cultura_id                INTEGER,
    timestamp                 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    input_N                   REAL,
    input_P                   REAL,
    input_K                   REAL,
    input_soil_pH             REAL,
    input_temperature         REAL,
    input_humidity            REAL,
    input_rainfall            REAL,
    previsao_irrigacao_mm     REAL,
    previsao_N_fertilizacao   REAL,
    previsao_P_fertilizacao   REAL,
    previsao_K_fertilizacao   REAL,
    previsao_rendimento_kg_ha REAL,
    modelo_usado              TEXT,
    confianca_previsao        REAL,
    FOREIGN KEY (cultura_id) REFERENCES culturas (cultura_id)
);

CREATE TABLE IF NOT EXISTS alertas (
    alerta_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id      TEXT,
    timestamp      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo_alerta    TEXT NOT NULL,
    severidade     TEXT      DEFAULT 'baixa',
    mensagem       TEXT,
    resolvido      INTEGER   DEFAULT 0,
    data_resolucao TIMESTAMP,
    FOREIGN KEY (sensor_id) REFERENCES sensores (sensor_id)
);
"""

MERMAID_DER = """\
erDiagram
    SENSORES ||--o{ LEITURAS_SENSORES : "gera"
    SENSORES ||--o{ ALERTAS           : "dispara"
    CULTURAS ||--o{ PREVISOES_ML      : "recebe"

    SENSORES {
        TEXT sensor_id PK
        TEXT tipo_sensor
        TEXT localizacao
        TEXT farm_id
        REAL latitude
        REAL longitude
        TEXT status
    }
    LEITURAS_SENSORES {
        INTEGER leitura_id PK
        TEXT sensor_id FK
        TIMESTAMP timestamp
        REAL N
        REAL P
        REAL K
        REAL soil_pH
        REAL soil_moisture
        REAL temperature_C
        REAL humidity_percent
        REAL rainfall_mm
    }
    CULTURAS {
        INTEGER cultura_id PK
        TEXT farm_id
        TEXT crop_type
        REAL area_hectares
        DATE data_plantio
    }
    PREVISOES_ML {
        INTEGER previsao_id PK
        INTEGER cultura_id FK
        REAL previsao_irrigacao_mm
        REAL previsao_rendimento_kg_ha
        TEXT modelo_usado
    }
    ALERTAS {
        INTEGER alerta_id PK
        TEXT sensor_id FK
        TIMESTAMP timestamp
        TEXT tipo_alerta
        TEXT severidade
        INTEGER resolvido
    }
"""


# ==========================================================
#         ABA 1 — CONSULTAR (READ)
# ==========================================================

def aba_consultar() -> None:
    """Listagem de tabelas com filtros específicos para leituras_sensores."""
    st.subheader("📖 Consultar dados (READ)")

    with abrir_db() as db:
        tabelas = db.listar_tabelas()

    if not tabelas:
        st.warning("Nenhuma tabela encontrada no banco.")
        return

    tabela = st.selectbox("Tabela", tabelas, index=tabelas.index("sensores") if "sensores" in tabelas else 0)

    with abrir_db() as db:
        total = db.contar_registros(tabela)

    st.caption(f"Total de registros em **{tabela}**: `{total}`")

    if tabela == "leituras_sensores":
        col1, col2, col3 = st.columns(3)
        with abrir_db() as db:
            sensores_df = db.listar_sensores()
        opcoes_sensor = ["(todos)"] + (
            sensores_df["sensor_id"].tolist() if not sensores_df.empty else []
        )
        with col1:
            filtro_sensor = st.selectbox("Sensor", opcoes_sensor)
        with col2:
            data_ini = st.date_input(
                "Data inicial",
                value=date.today() - timedelta(days=7),
            )
        with col3:
            data_fim = st.date_input("Data final", value=date.today())

        sensor_param = None if filtro_sensor == "(todos)" else filtro_sensor
        with abrir_db() as db:
            df = db.obter_leituras_filtradas(
                sensor_id=sensor_param,
                data_inicio=data_ini.isoformat() if data_ini else None,
                data_fim=data_fim.isoformat() if data_fim else None,
                limit=200,
            )
    else:
        with abrir_db() as db:
            df = db.obter_registros_tabela(tabela, limit=200)

    if df.empty:
        st.info("Nenhum registro encontrado com os filtros atuais.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"Exibindo {len(df)} de {total} registros (limite 200).")


# ==========================================================
#         ABA 2 — INSERIR (CREATE)
# ==========================================================

def _form_cadastrar_sensor() -> None:
    """Formulário para inserir um novo sensor no banco."""
    st.markdown("##### 🛰️ Cadastrar novo sensor")
    with st.form("form_novo_sensor"):
        col1, col2 = st.columns(2)
        with col1:
            sensor_id = st.text_input("ID do sensor", value="SENSOR_NEW_001")
            tipo = st.selectbox(
                "Tipo do sensor",
                ["NPK_pH_Temp", "Climático", "Umidade", "Multissensor"],
            )
            farm_id = st.text_input("ID da fazenda", value="FARM_001")
        with col2:
            localizacao = st.text_input("Localização", value="Área Central")
            latitude = st.number_input("Latitude", value=-30.0300, format="%.4f")
            longitude = st.number_input("Longitude", value=-51.2300, format="%.4f")

        if st.form_submit_button("➕ Cadastrar sensor", use_container_width=True):
            try:
                with abrir_db() as db:
                    ok = db.inserir_sensor(
                        sensor_id=sensor_id.strip(),
                        tipo_sensor=tipo,
                        localizacao=localizacao,
                        farm_id=farm_id,
                        latitude=latitude,
                        longitude=longitude,
                    )
                if ok:
                    st.success(f"✅ Sensor `{sensor_id}` cadastrado/atualizado.")
                    st.rerun()
                else:
                    st.error("Não foi possível cadastrar o sensor.")
            except Exception as exc:
                st.error(f"❌ Erro: {exc}")


def _form_inserir_leitura() -> None:
    """Formulário para inserir uma leitura manual em um sensor existente."""
    st.markdown("##### 📡 Inserir leitura manual")

    with abrir_db() as db:
        sensores_df = db.listar_sensores()

    if sensores_df.empty:
        st.warning("Cadastre um sensor antes de inserir leituras.")
        return

    with st.form("form_nova_leitura"):
        sensor_id = st.selectbox("Sensor", sensores_df["sensor_id"].tolist())

        col1, col2, col3 = st.columns(3)
        with col1:
            n_val = st.number_input("N (kg/ha)", value=45.0, step=1.0)
            p_val = st.number_input("P (kg/ha)", value=38.0, step=1.0)
            k_val = st.number_input("K (kg/ha)", value=42.0, step=1.0)
        with col2:
            ph_val = st.number_input("pH do solo", value=6.5, step=0.1, format="%.2f")
            umid_solo = st.number_input("Umidade do solo (%)", value=35.0, step=1.0)
            temp = st.number_input("Temperatura (°C)", value=25.0, step=0.5)
        with col3:
            umid_ar = st.number_input("Umidade do ar (%)", value=65.0, step=1.0)
            chuva = st.number_input("Chuva (mm)", value=2.0, step=0.5)
            sol = st.number_input("Horas de sol", value=8.0, step=0.5)
            irrig = st.number_input("Irrigação (mm)", value=0.0, step=0.5)

        if st.form_submit_button("➕ Inserir leitura", use_container_width=True):
            dados = {
                "N": n_val,
                "P": p_val,
                "K": k_val,
                "soil_pH": ph_val,
                "soil_moisture": umid_solo,
                "temperature_C": temp,
                "humidity_percent": umid_ar,
                "rainfall_mm": chuva,
                "sunlight_hours": sol,
                "irrigation_volume_mm": irrig,
            }
            try:
                with abrir_db() as db:
                    ok = db.inserir_leitura(sensor_id, dados)
                if ok:
                    st.success(f"✅ Leitura inserida para `{sensor_id}`.")
                    st.rerun()
                else:
                    st.error("Falha ao inserir leitura.")
            except Exception as exc:
                st.error(f"❌ Erro: {exc}")


def aba_inserir() -> None:
    """Aba com os dois formulários de cadastro."""
    st.subheader("➕ Inserir registros (CREATE)")
    col_a, col_b = st.columns(2)
    with col_a:
        _form_cadastrar_sensor()
    with col_b:
        _form_inserir_leitura()


# ==========================================================
#         ABA 3 — ATUALIZAR (UPDATE)
# ==========================================================

def aba_atualizar() -> None:
    """Permite alterar status do sensor e marcar alertas como resolvidos."""
    st.subheader("✏️ Atualizar registros (UPDATE)")

    col1, col2 = st.columns(2)

    # ---- UPDATE sensor.status ---------------------------
    with col1:
        st.markdown("##### 🛰️ Alterar status de sensor")
        with abrir_db() as db:
            sensores_df = db.listar_sensores()

        if sensores_df.empty:
            st.info("Sem sensores cadastrados.")
        else:
            sid = st.selectbox(
                "Sensor",
                sensores_df["sensor_id"].tolist(),
                key="upd_sensor_id",
            )
            status_atual = sensores_df.loc[
                sensores_df["sensor_id"] == sid, "status"
            ].iloc[0]
            st.caption(f"Status atual: `{status_atual}`")
            novo_status = st.selectbox(
                "Novo status",
                ["ativo", "inativo", "manutencao"],
                key="upd_novo_status",
            )
            if st.button("💾 Salvar novo status", use_container_width=True):
                try:
                    with abrir_db() as db:
                        ok = db.atualizar_status_sensor(sid, novo_status)
                    if ok:
                        st.success(f"Status de `{sid}` alterado para `{novo_status}`.")
                        st.rerun()
                    else:
                        st.error("Não foi possível atualizar.")
                except Exception as exc:
                    st.error(f"❌ Erro: {exc}")

    # ---- UPDATE alertas (resolver) ----------------------
    with col2:
        st.markdown("##### 🚨 Resolver alerta")
        with abrir_db() as db:
            alertas_df = db.obter_alertas_ativos()

        if alertas_df.empty:
            st.info("Nenhum alerta pendente.")
        else:
            opcoes = {
                int(row["alerta_id"]): (
                    f"#{int(row['alerta_id'])} • {row['tipo_alerta']} "
                    f"({row['severidade']}) — {row['mensagem']}"
                )
                for _, row in alertas_df.iterrows()
            }
            escolha = st.selectbox(
                "Alerta pendente",
                options=list(opcoes.keys()),
                format_func=lambda k: opcoes[k],
                key="upd_alerta_id",
            )
            if st.button("✅ Marcar como resolvido", use_container_width=True):
                try:
                    with abrir_db() as db:
                        ok = db.marcar_alerta_resolvido(escolha)
                    if ok:
                        st.success(f"Alerta #{escolha} resolvido.")
                        st.rerun()
                    else:
                        st.error("Não foi possível resolver o alerta.")
                except Exception as exc:
                    st.error(f"❌ Erro: {exc}")


# ==========================================================
#         ABA 4 — EXCLUIR (DELETE)
# ==========================================================

def aba_excluir() -> None:
    """Exclusões com confirmação obrigatória via checkbox."""
    st.subheader("🗑️ Excluir registros (DELETE)")

    col1, col2 = st.columns(2)

    # ---- DELETE leitura ---------------------------------
    with col1:
        st.markdown("##### 📡 Remover leitura")
        leitura_id = st.number_input(
            "ID da leitura",
            min_value=1,
            step=1,
            value=1,
            key="del_leitura_id",
        )
        confirma = st.checkbox(
            "Confirmo a exclusão desta leitura.",
            key="del_leitura_confirma",
        )
        if st.button(
            "🗑️ Excluir leitura",
            use_container_width=True,
            disabled=not confirma,
        ):
            try:
                with abrir_db() as db:
                    ok = db.deletar_leitura(int(leitura_id))
                if ok:
                    st.success(f"Leitura #{int(leitura_id)} removida.")
                    st.rerun()
                else:
                    st.warning("Leitura não encontrada.")
            except Exception as exc:
                st.error(f"❌ Erro: {exc}")

    # ---- DELETE sensor ----------------------------------
    with col2:
        st.markdown("##### 🛰️ Remover sensor")

        with abrir_db() as db:
            sensores_df = db.listar_sensores()

        if sensores_df.empty:
            st.info("Sem sensores cadastrados.")
            return

        sid = st.selectbox(
            "Sensor a remover",
            sensores_df["sensor_id"].tolist(),
            key="del_sensor_id",
        )
        with abrir_db() as db:
            n_leituras = db.contar_leituras_sensor(sid)

        if n_leituras > 0:
            st.warning(
                f"⚠️ Este sensor possui **{n_leituras}** leituras associadas. "
                "Marque o cascade abaixo para apagá-las junto."
            )
        cascade = st.checkbox(
            "Apagar leituras e alertas associados (cascade).",
            key="del_sensor_cascade",
            disabled=(n_leituras == 0),
        )
        confirma_s = st.checkbox(
            f"Confirmo a exclusão definitiva do sensor `{sid}`.",
            key="del_sensor_confirma",
        )
        if st.button(
            "🗑️ Excluir sensor",
            use_container_width=True,
            disabled=not confirma_s,
        ):
            try:
                with abrir_db() as db:
                    ok, n_assoc = db.deletar_sensor(sid, cascade=cascade)
                if ok:
                    msg = f"Sensor `{sid}` removido."
                    if cascade and n_assoc:
                        msg += f" ({n_assoc} leituras/alertas também apagados.)"
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(
                        f"Sensor possui {n_assoc} leituras associadas — "
                        "marque o cascade ou apague-as antes."
                    )
            except Exception as exc:
                st.error(f"❌ Erro: {exc}")


# ==========================================================
#         ABA 5 — MODELO DE DADOS (MER/DER)
# ==========================================================

def aba_modelo() -> None:
    """Mostra relacionamentos, DDL e diagrama Mermaid; persiste no docs/."""
    st.subheader("🗂️ Modelo de Dados (MER/DER)")

    st.markdown(
        """
        **Relacionamentos principais**

        - `sensores` **1 : N** `leituras_sensores` — *um sensor gera várias leituras*
        - `sensores` **1 : N** `alertas` — *um sensor pode disparar vários alertas*
        - `culturas` **1 : N** `previsoes_ml` — *cada cultura recebe várias previsões*
        """
    )

    with st.expander("📜 SQL de criação das tabelas", expanded=False):
        st.code(SQL_SCHEMA, language="sql")

    st.markdown("##### Diagrama (Mermaid `erDiagram`)")
    st.caption(
        "O bloco abaixo é renderizado automaticamente pelo GitHub. "
        "O mesmo conteúdo foi salvo em `docs/der_fase2.md`."
    )
    st.code(MERMAID_DER, language="mermaid")

    # Persiste novamente a versão atual (idempotente).
    try:
        DOC_DER.parent.mkdir(parents=True, exist_ok=True)
        if not DOC_DER.exists():
            DOC_DER.write_text(
                "# Diagrama ER — Fase 2\n\n```mermaid\n"
                + MERMAID_DER
                + "\n```\n",
                encoding="utf-8",
            )
        st.caption(f"📁 Documento: `{DOC_DER.relative_to(BASE_DIR)}`")
    except Exception as exc:  # pragma: no cover
        st.warning(f"Não foi possível gravar {DOC_DER}: {exc}")


# ==========================================================
#         PÁGINA PRINCIPAL
# ==========================================================

def main() -> None:
    """Ponto de entrada da página de CRUD da Fase 2."""
    render_header()
    render_sidebar()

    st.title("🗄️ Fase 2 — Banco de Dados (CRUD)")
    st.caption(
        "Operações CRUD sobre o banco SQLite `farmtech_iot.db`. "
        "Compatível com o simulador IoT rodando em paralelo."
    )

    abas = st.tabs(
        [
            "📖 Consultar (READ)",
            "➕ Inserir (CREATE)",
            "✏️ Atualizar (UPDATE)",
            "🗑️ Excluir (DELETE)",
            "🗂️ Modelo de Dados (MER/DER)",
        ]
    )
    with abas[0]:
        aba_consultar()
    with abas[1]:
        aba_inserir()
    with abas[2]:
        aba_atualizar()
    with abas[3]:
        aba_excluir()
    with abas[4]:
        aba_modelo()


if __name__ == "__main__":
    main()
