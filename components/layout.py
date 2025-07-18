import streamlit as st
from config.settings import Config


def setup_page_config():
    """Configurar la página de Streamlit"""
    st.set_page_config(
        page_title=Config.APP_TITLE,
        page_icon=Config.APP_ICON,
        layout=Config.LAYOUT,
        initial_sidebar_state="collapsed",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': f"# {Config.APP_TITLE}\nSistema de predicción de entregas"
        }
    )


def load_custom_css():
    """Cargar estilos CSS simplificados"""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        .main .block-container {
            font-family: 'Inter', sans-serif;
            max-width: 1200px;
            padding-top: 2rem;
        }

        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1e293b;
            text-align: center;
            margin-bottom: 2rem;
        }

        .stButton > button {
            background: linear-gradient(135deg, #1e40af, #3b82f6);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            transition: all 0.2s;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }

        .stMetric {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        .stDataFrame {
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .stInfo {
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
        }

        .stSuccess {
            border-radius: 8px;
            border-left: 4px solid #10b981;
        }

        .stError {
            border-radius: 8px;
            border-left: 4px solid #ef4444;
        }
    </style>
    """, unsafe_allow_html=True)


def render_header(title: str, subtitle: str = None):
    """Renderizar header de página"""
    st.markdown(f"<h1 class='main-header'>{title}</h1>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(
            f"<p style='text-align: center; color: #64748b; font-size: 1.1rem; margin-bottom: 2rem;'>{subtitle}</p>",
            unsafe_allow_html=True
        )


def render_back_button():
    """Renderizar botón de regreso"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← Volver al Formulario", key="back_button"):
            st.session_state.show_results = False
            st.rerun()