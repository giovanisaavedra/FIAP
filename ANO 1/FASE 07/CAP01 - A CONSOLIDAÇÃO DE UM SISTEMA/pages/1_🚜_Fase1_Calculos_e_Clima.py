"""
FarmTech Solutions - Fase 1: Cálculos Agrícolas, Clima e Análise em R
Página integrada da Fase 1: combina o motor de cálculos (área e
insumos), a consulta meteorológica via Open-Meteo e a análise
estatística em R sobre o CSV de clima.

Autores: Giovani Saavedra e Marcio Elifas
RM: RM566797 e RM567871
GRUPO 37
1TIAOS - FIAP

FIAP - Fase 7 - 2026
"""

from __future__ import annotations

import shutil
import subprocess
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from services.fase1_calculos import (
    CATALOGO_INSUMOS,
    calcular_area_plantio,
    calcular_insumos,
)
from services.fase1_clima import obter_clima
from utils import render_header, render_sidebar


# ==========================================================
#         CONFIGURAÇÃO DA PÁGINA
# ==========================================================

st.set_page_config(
    page_title="Fase 1 - Cálculos e Clima",
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CSV_CALCULOS = DATA_DIR / "fase1_calculos.csv"
CSV_CLIMA = DATA_DIR / "clima_atual.csv"
R_SCRIPT = BASE_DIR / "services" / "fase1_analise.R"


# ==========================================================
#         HELPERS DE PERSISTÊNCIA (mini-CRUD)
# ==========================================================

def _carregar_csv(caminho: Path) -> pd.DataFrame:
    """Lê um CSV se existir; caso contrário devolve DataFrame vazio."""
    if caminho.exists():
        try:
            return pd.read_csv(caminho)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()


def _salvar_csv(df: pd.DataFrame, caminho: Path) -> None:
    """Persiste o DataFrame no caminho, criando a pasta `data/` se preciso."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(caminho, index=False)


def _registrar_calculo(linha: dict) -> None:
    """Adiciona uma linha ao histórico de cálculos da Fase 1."""
    df = _carregar_csv(CSV_CALCULOS)
    df = pd.concat([df, pd.DataFrame([linha])], ignore_index=True)
    _salvar_csv(df, CSV_CALCULOS)


# ==========================================================
#         ABA 1 — ÁREA E INSUMOS
# ==========================================================

def aba_area_insumos() -> None:
    """Formulário de área + insumos, com mini-CRUD do histórico."""
    st.subheader("📐 Cálculo de Área de Plantio e Insumos")
    st.caption("Defina a geometria, a cultura e veja a estimativa de insumos.")

    culturas_disp = sorted(CATALOGO_INSUMOS.keys())

    with st.form("form_fase1_area"):
        col1, col2 = st.columns(2)

        with col1:
            cultura = st.selectbox(
                "Cultura",
                options=culturas_disp,
                format_func=str.capitalize,
                help="Cultura plantada — usada para estimar o insumo principal.",
            )
            geometria = st.selectbox(
                "Geometria do talhão",
                options=["retangulo", "triangulo", "circulo"],
                format_func=lambda v: {
                    "retangulo": "Retângulo",
                    "triangulo": "Triângulo",
                    "circulo": "Círculo (pivô central)",
                }[v],
            )

        with col2:
            dim1 = st.number_input(
                "Medida 1 (m)",
                min_value=0.0,
                value=100.0,
                step=1.0,
                help=(
                    "Retângulo: largura • Triângulo: base • "
                    "Círculo: raio (centro até a borda)."
                ),
            )
            dim2 = st.number_input(
                "Medida 2 (m)",
                min_value=0.0,
                value=250.0,
                step=1.0,
                help=(
                    "Retângulo: comprimento • Triângulo: altura • "
                    "Círculo: não utilizado (deixe qualquer valor)."
                ),
                disabled=(geometria == "circulo"),
            )

        submitted = st.form_submit_button("Calcular", use_container_width=True)

    if not submitted:
        st.info("Preencha o formulário acima e clique em **Calcular**.")
    else:
        try:
            if geometria == "retangulo":
                dimensoes = {"largura": dim1, "comprimento": dim2}
            elif geometria == "triangulo":
                dimensoes = {"base": dim1, "altura": dim2}
            else:
                dimensoes = {"raio": dim1}

            area = calcular_area_plantio(geometria, dimensoes)
            insumos = calcular_insumos(cultura, area["area_ha"])

            st.success("Cálculo concluído com sucesso!")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Área (m²)", f"{area['area_m2']:.2f}")
            c2.metric("Área (ha)", f"{area['area_ha']:.4f}")
            c3.metric("Perímetro (m)", f"{area['perimetro_m']:.2f}")
            c4.metric(
                f"{insumos['insumo_principal']} ({insumos['unidade']})",
                f"{insumos['quantidade_total']:.2f}",
                help=insumos["observacao"],
            )

            _registrar_calculo(
                {
                    "timestamp": datetime.now().isoformat(timespec="seconds"),
                    "cultura": insumos["cultura"],
                    "geometria": area["geometria"],
                    "medida_1_m": dim1,
                    "medida_2_m": dim2 if geometria != "circulo" else None,
                    "area_m2": area["area_m2"],
                    "area_ha": area["area_ha"],
                    "perimetro_m": area["perimetro_m"],
                    "insumo": insumos["insumo_principal"],
                    "dosagem_por_ha": insumos["dosagem_por_ha"],
                    "unidade": insumos["unidade"],
                    "quantidade_total": insumos["quantidade_total"],
                }
            )
            st.toast("Cálculo salvo em data/fase1_calculos.csv", icon="💾")
        except ValueError as exc:
            st.error(f"❌ {exc}")

    st.divider()

    # --- Mini-CRUD do histórico --------------------------------
    st.markdown("#### 🗂️ Histórico de Cálculos")
    df_hist = _carregar_csv(CSV_CALCULOS)

    if df_hist.empty:
        st.info("Nenhum cálculo registrado ainda.")
        return

    st.dataframe(df_hist, use_container_width=True, hide_index=False)

    col_del1, col_del2 = st.columns([2, 1])
    with col_del1:
        idx = st.number_input(
            "Índice para deletar",
            min_value=0,
            max_value=int(max(df_hist.index)),
            step=1,
            value=0,
        )
    with col_del2:
        st.write("")
        st.write("")
        if st.button("🗑️ Deletar registro", use_container_width=True):
            df_hist = df_hist.drop(index=idx).reset_index(drop=True)
            _salvar_csv(df_hist, CSV_CALCULOS)
            st.success(f"Registro {idx} removido.")
            st.rerun()


# ==========================================================
#         ABA 2 — CLIMA (API)
# ==========================================================

def _grafico_previsao(previsao_df: pd.DataFrame) -> go.Figure:
    """Monta o gráfico Plotly da previsão de 7 dias."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=previsao_df["data"],
            y=previsao_df["temp_max_C"],
            mode="lines+markers",
            name="Temp. máx (°C)",
            line=dict(color="#E53935"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=previsao_df["data"],
            y=previsao_df["temp_min_C"],
            mode="lines+markers",
            name="Temp. mín (°C)",
            line=dict(color="#1E88E5"),
        )
    )
    fig.add_trace(
        go.Bar(
            x=previsao_df["data"],
            y=previsao_df["chuva_mm"],
            name="Chuva (mm)",
            marker_color="#43A047",
            opacity=0.55,
            yaxis="y2",
        )
    )
    fig.update_layout(
        title="Previsão para os próximos 7 dias",
        xaxis_title="Data",
        yaxis=dict(title="Temperatura (°C)"),
        yaxis2=dict(title="Chuva (mm)", overlaying="y", side="right"),
        legend=dict(orientation="h", y=-0.2),
        height=420,
        margin=dict(t=60, b=40, l=40, r=40),
    )
    return fig


def aba_clima() -> None:
    """Consulta Open-Meteo e exibe métricas + gráfico de previsão."""
    st.subheader("🌦️ Clima Atual e Previsão (API Open-Meteo)")
    st.caption(
        "Coordenadas padrão: Porto Alegre/RS (-30.03, -51.23). "
        "Em caso de falha de rede, são exibidos dados simulados."
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        latitude = st.number_input("Latitude", value=-30.03, format="%.4f")
    with col2:
        longitude = st.number_input("Longitude", value=-51.23, format="%.4f")
    with col3:
        st.write("")
        st.write("")
        buscar = st.button("🔄 Buscar clima", use_container_width=True)

    if buscar:
        with st.spinner("Consultando Open-Meteo..."):
            dados = obter_clima(latitude, longitude)
        st.session_state["fase1_clima"] = dados

    dados = st.session_state.get("fase1_clima")
    if not dados:
        st.info("Clique em **Buscar clima** para consultar a API.")
        return

    if dados.get("simulado"):
        st.warning(
            f"⚠️ Dados **simulados** (fallback) — motivo: {dados.get('motivo', 'desconhecido')}."
        )
    else:
        st.success(f"✅ Dados reais de {dados.get('fonte')}.")

    atual = dados.get("atual", {})
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🌡️ Temperatura (°C)", f"{atual.get('temperatura_C', 0):.1f}")
    c2.metric("💧 Umidade (%)", f"{atual.get('umidade_percent', 0):.0f}")
    c3.metric("🌧️ Precipitação (mm)", f"{atual.get('precipitacao_mm', 0):.1f}")
    c4.metric("💨 Vento (km/h)", f"{atual.get('vento_kmh', 0):.1f}")
    st.caption(f"Última leitura: {atual.get('timestamp', '—')}")

    previsao_df = pd.DataFrame(dados.get("previsao_7d", []))
    if not previsao_df.empty:
        st.plotly_chart(_grafico_previsao(previsao_df), use_container_width=True)
        _salvar_csv(previsao_df, CSV_CLIMA)
        st.caption(f"📁 Previsão salva em `{CSV_CLIMA.relative_to(BASE_DIR)}`.")
    else:
        st.info("Sem dados de previsão para exibir.")


# ==========================================================
#         ABA 3 — ANÁLISE ESTATÍSTICA (R)
# ==========================================================

def _fallback_analise_pandas(df: pd.DataFrame) -> str:
    """Replica o resumo do script R com pandas.describe quando R não existe."""
    numericas = df.select_dtypes(include="number")
    if numericas.empty:
        return "Nenhuma coluna numérica encontrada no CSV."

    descricao = numericas.describe(percentiles=[0.25, 0.5, 0.75]).round(4)
    linhas = [
        "============================================================",
        "  FarmTech Solutions - Análise Estatística (Python fallback)",
        "============================================================",
        f"Arquivo:        {CSV_CLIMA}",
        f"Linhas:         {len(df)}",
        f"Colunas totais: {len(df.columns)}",
        f"Colunas numéricas analisadas: {len(numericas.columns)}",
        "------------------------------------------------------------",
        descricao.to_string(),
        "",
        "============================================================",
        "  Análise concluída com sucesso (Python fallback).",
        "============================================================",
    ]
    return "\n".join(linhas)


def aba_analise_r() -> None:
    """Executa o script R sobre o CSV de clima, ou faz fallback em Python."""
    st.subheader("📊 Análise Estatística (R)")
    st.caption(
        "Roda `Rscript services/fase1_analise.R` sobre `data/clima_atual.csv`. "
        "Se o R não estiver instalado, calcula as mesmas estatísticas em Python."
    )

    if not CSV_CLIMA.exists():
        st.warning(
            "🌧️ Nenhum dado de clima salvo ainda. Vá até a aba **Clima (API)** "
            "e clique em **Buscar clima** primeiro."
        )
        return

    rscript_path = shutil.which("Rscript")

    col1, col2 = st.columns([1, 3])
    with col1:
        executar = st.button("▶ Executar análise em R", use_container_width=True)
    with col2:
        if rscript_path:
            st.success(f"R detectado em `{rscript_path}`.")
        else:
            st.warning("R não detectado — será usado o fallback em Python.")

    if not executar:
        st.info("Clique em **Executar análise em R** para gerar o resumo estatístico.")
        return

    if rscript_path is None:
        df = _carregar_csv(CSV_CLIMA)
        saida = _fallback_analise_pandas(df)
        st.warning("R não encontrado — análise feita em Python.")
        st.code(saida, language="text")
        with st.expander("📜 Ver código R que seria executado (services/fase1_analise.R)"):
            try:
                st.code(R_SCRIPT.read_text(encoding="utf-8"), language="r")
            except Exception as exc:
                st.error(f"Não foi possível ler o script R: {exc}")
        return

    try:
        resultado = subprocess.run(
            [rscript_path, str(R_SCRIPT), str(CSV_CLIMA)],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except Exception as exc:
        st.error(f"❌ Falha ao executar o R: {exc}")
        return

    if resultado.returncode != 0:
        st.error(f"O script R terminou com código {resultado.returncode}.")
        if resultado.stderr:
            st.code(resultado.stderr, language="text")
        return

    st.success("Análise R executada com sucesso!")
    st.code(resultado.stdout, language="text")
    if resultado.stderr:
        with st.expander("⚠️ stderr do R"):
            st.code(resultado.stderr, language="text")


# ==========================================================
#         PÁGINA PRINCIPAL
# ==========================================================

def main() -> None:
    """Ponto de entrada da página Fase 1."""
    render_header()
    render_sidebar()

    st.title("🚜 Fase 1 — Cálculos Agrícolas, Clima e Análise em R")
    st.caption(
        "Integração dos serviços da Fase 1 (Python + API Meteorológica + Rscript)."
    )

    abas = st.tabs(
        [
            "📐 Área e Insumos",
            "🌦️ Clima (API)",
            "📊 Análise Estatística (R)",
        ]
    )

    with abas[0]:
        aba_area_insumos()
    with abas[1]:
        aba_clima()
    with abas[2]:
        aba_analise_r()


if __name__ == "__main__":
    main()
