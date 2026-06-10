"""
FarmTech Solutions - Fase 6: Visão Computacional (YOLO)
Página integrada da Fase 6: aceita uploads para ``assets/images/``,
analisa as imagens com YOLOv8 (``services.fase6_vision``),
exibe original × anotada lado a lado, tabela de detecções e
diagnóstico agrícola, persistindo cada análise em
``analises_visuais``.

Autores: Giovani Saavedra e Marcio Elifas
RM: RM566797 e RM567871
GRUPO 37
1TIAOS - FIAP

FIAP - Fase 7 - 2026
"""

from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import pandas as pd
import streamlit as st
from PIL import Image

from database_manager import FarmTechDatabase
from services.fase6_vision import (
    AnalisadorVisual,
    EXTENSOES_IMAGEM,
    serializar_deteccoes,
)
from utils import render_header, render_sidebar


# ==========================================================
#         CONFIGURAÇÃO DA PÁGINA
# ==========================================================

st.set_page_config(
    page_title="Fase 6 - Visão Computacional",
    page_icon="📷",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent.parent
PASTA_IMAGENS = BASE_DIR / "assets" / "images"
DB_PATH = BASE_DIR / "farmtech_iot.db"


# ==========================================================
#         CONEXÃO CURTA AO BANCO
# ==========================================================

@contextmanager
def abrir_db() -> Iterator[FarmTechDatabase]:
    """Context manager que abre e fecha a conexão SQLite com segurança."""
    db = FarmTechDatabase(str(DB_PATH))
    try:
        yield db
    finally:
        db.fechar_conexao()


# ==========================================================
#         HELPERS DE UI
# ==========================================================

def _cor_diagnostico(severidade: str):
    """Mapeia severidade -> função Streamlit (success/info/warning/error)."""
    return {
        "ok": st.success,
        "info": st.info,
        "media": st.warning,
        "alta": st.error,
    }.get(severidade, st.info)


def _salvar_uploads(arquivos) -> int:
    """Salva os arquivos do file_uploader em ``assets/images/``.

    Args:
        arquivos: lista de ``UploadedFile`` do Streamlit.

    Returns:
        Quantidade de arquivos efetivamente salvos.
    """
    PASTA_IMAGENS.mkdir(parents=True, exist_ok=True)
    salvos = 0
    for arq in arquivos or []:
        nome = Path(arq.name).name
        if Path(nome).suffix.lower() not in EXTENSOES_IMAGEM:
            st.warning(f"Ignorado: {nome} (formato não suportado).")
            continue
        destino = PASTA_IMAGENS / nome
        destino.write_bytes(arq.getbuffer())
        salvos += 1
    return salvos


# ==========================================================
#         SEÇÃO: UPLOAD
# ==========================================================

def secao_upload() -> None:
    """Multiupload + sumário de imagens disponíveis na pasta."""
    st.subheader("📤 Upload de imagens")
    st.caption(
        f"As imagens vão para `{PASTA_IMAGENS.relative_to(BASE_DIR)}` "
        "e ficam disponíveis para análise em lote."
    )

    arquivos = st.file_uploader(
        "Selecione uma ou mais imagens (jpg/jpeg/png)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
    )
    if st.button("💾 Salvar uploads", use_container_width=True, disabled=not arquivos):
        n = _salvar_uploads(arquivos)
        if n:
            st.success(f"✅ {n} imagem(ns) salva(s) em `{PASTA_IMAGENS.name}/`.")
            st.rerun()

    # Resumo da pasta
    if PASTA_IMAGENS.exists():
        existentes = sorted(
            p.name for p in PASTA_IMAGENS.iterdir()
            if p.suffix.lower() in EXTENSOES_IMAGEM
        )
    else:
        existentes = []

    if existentes:
        st.caption(f"📁 {len(existentes)} imagem(ns) na pasta:")
        st.code("\n".join(existentes), language="text")
    else:
        st.info("Pasta vazia — envie algumas imagens para começar.")


# ==========================================================
#         SEÇÃO: ANÁLISE
# ==========================================================

def secao_analise() -> None:
    """Roda o YOLO sobre a pasta e renderiza original × anotada."""
    st.subheader("🔍 Análise YOLO da pasta de imagens")

    if not PASTA_IMAGENS.exists() or not any(
        p.suffix.lower() in EXTENSOES_IMAGEM for p in PASTA_IMAGENS.iterdir()
    ):
        st.info("Sem imagens na pasta — faça upload na seção anterior.")
        return

    if st.button("🔍 Analisar imagens da pasta", use_container_width=True):
        # Spinner enfatiza o download do peso na primeira execução.
        with st.spinner("Baixando modelo YOLO (apenas na 1ª execução) e analisando..."):
            analisador = st.session_state.setdefault(
                "analisador_visual", AnalisadorVisual()
            )
            resultados = analisador.analisar_pasta(str(PASTA_IMAGENS))

        if not resultados:
            st.warning("Nenhuma imagem processada.")
            return

        # Persiste e renderiza por imagem
        with abrir_db() as db:
            for r in resultados:
                db.inserir_analise_visual(
                    imagem=Path(r["imagem"]).name,
                    deteccoes_json=serializar_deteccoes(r["deteccoes"]),
                    status=r["diagnostico"]["mensagem"],
                    num_deteccoes=len(r["deteccoes"]),
                    confianca_media=r["confianca_media"],
                )

        st.success(
            f"✅ {len(resultados)} imagem(ns) analisada(s) e registrada(s) "
            "em `analises_visuais`."
        )

        for r in resultados:
            nome = Path(r["imagem"]).name
            st.markdown(f"### 🖼️ {nome}")
            col1, col2 = st.columns(2)
            with col1:
                st.caption("Original")
                try:
                    st.image(Image.open(r["imagem"]), use_container_width=True)
                except Exception as exc:
                    st.error(f"Falha ao abrir imagem: {exc}")
            with col2:
                st.caption("Anotada (YOLO)")
                if r["imagem_anotada"] is not None:
                    st.image(r["imagem_anotada"], use_container_width=True)
                else:
                    st.warning("Sem imagem anotada disponível.")

            if r["deteccoes"]:
                df_det = pd.DataFrame(r["deteccoes"])
                st.dataframe(df_det, use_container_width=True, hide_index=True)
                if r["confianca_media"] is not None:
                    st.caption(f"Confiança média: {r['confianca_media']:.3f}")
            else:
                st.caption("Sem detecções nesta imagem.")

            diag = r["diagnostico"]
            _cor_diagnostico(diag["severidade"])(diag["mensagem"])

            st.divider()


# ==========================================================
#         SEÇÃO: HISTÓRICO
# ==========================================================

def secao_historico() -> None:
    """Mostra a tabela ``analises_visuais``."""
    st.subheader("📜 Histórico de Análises")
    with abrir_db() as db:
        df_hist = db.obter_analises_visuais(limit=100)

    if df_hist.empty:
        st.info("Nenhuma análise registrada ainda.")
        return

    # Mostra primeiro um resumo e depois o JSON completo num expander.
    colunas_resumo = ["id", "timestamp", "imagem", "num_deteccoes",
                      "confianca_media", "status"]
    st.dataframe(
        df_hist[colunas_resumo],
        use_container_width=True,
        hide_index=True,
    )
    with st.expander("Ver detecções (JSON bruto)"):
        for _, row in df_hist.iterrows():
            st.caption(
                f"#{int(row['id'])} · {row['imagem']} · {row['timestamp']}"
            )
            try:
                st.json(json.loads(row["deteccoes_json"]))
            except Exception:
                st.code(row["deteccoes_json"], language="text")


# ==========================================================
#         PÁGINA PRINCIPAL
# ==========================================================

def main() -> None:
    """Ponto de entrada da página Fase 6."""
    render_header()
    render_sidebar()

    st.title("📷 Fase 6 — Visão Computacional (YOLOv8)")
    st.caption(
        "Detecção de objetos com YOLOv8n + camada de diagnóstico "
        "agrícola sobre as classes COCO. O peso é carregado uma "
        "única vez por sessão (lazy-loading)."
    )

    secao_upload()
    st.divider()
    secao_analise()
    st.divider()
    secao_historico()


if __name__ == "__main__":
    main()
