"""
FarmTech Solutions - Componentes Compartilhados
Funções reutilizáveis para header e sidebar em todas as páginas

Autores: Giovani Saavedra e Marcio Elifas
RM: RM566797 e RM567871
GRUPO 37
1TIAOS - FIAP

FIAP - Fase 4 - Novembro 2025

"""

import streamlit as st
from datetime import datetime

# ============================================
#         COMPONENTES VISUAIS
# ============================================

def render_header():
    """Renderização do header verde no topo do dashboard."""
    st.markdown("""
        <style>
        .header-container {
            background-color: #2E7D32;
            padding: 30px 50px;
            margin-bottom: 20px;
            margin-top: -50px;
            margin-left: -50px;
            margin-right: -50px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .header-title {
            color: white !important;
            font-size: 38px;
            font-weight: bold;
            margin: 0;
            padding: 0;
        }

        .header-subtitle {
            color: #C8E6C9;
            font-size: 18px;
            margin: 10px 0 0 0;
            padding: 0;
        }
        </style>

        <div class="header-container">
            <h1 class="header-title">🌾 FarmTech Solutions</h1>
            <p class="header-subtitle">Sistema de Previsão Agrícola com Machine Learning</p>
        </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Renderizar sidebar com informações do projeto (compartilhado entre todas as páginas)."""
    with st.sidebar:
        # Datasets disponíveis
        st.markdown("### 📁 Datasets Disponíveis")

        with st.expander("Ver detalhes"):
            st.info("""
            **Dataset 1:** dataset_final_farmtech.csv
            - 2.200 registros
            - 13 variáveis com dados de irrigação e fertilização
            """)

        st.divider()

        # Progresso CRISP-DM
        st.markdown("### 📄 Metodologia CRISP-DM")

        fases_crisp = {
            "1. Entendimento do Negócio": True,
            "2. Entendimento dos Dados": True,
            "3. Preparação dos Dados": True,
            "4. Modelagem": True,
            "5. Avaliação": True,
            "6. Implantação": True,
        }

        for fase, completo in fases_crisp.items():
            if completo:
                st.success(f"✅ {fase}")
            else:
                st.warning(f"⏳ {fase}")

        progresso = sum(fases_crisp.values()) / len(fases_crisp)
        st.progress(progresso)
        st.caption(f"Progresso geral: {progresso * 100:.0f}%")

        st.divider()

        # Informações do projeto
        st.markdown("### 👨‍💻 Informações")
        st.caption("**Fase:** 4 - Cap 1")
        st.caption("**Disciplina:** IA & ML")
        st.caption("**Instituição:** FIAP")
        st.caption(f"**Atualizado:** {datetime.now().strftime('%d/%m/%Y')}")