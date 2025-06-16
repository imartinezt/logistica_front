import streamlit as st
from pathlib import Path
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
            'About': f"# {Config.APP_TITLE}\nSistema inteligente de predicción de entregas"
        }
    )


def load_custom_css():
    """Cargar estilos CSS personalizados"""
    try:
        css_file = Path(__file__).parent.parent / "styles" / "custom.css"
        if css_file.exists():
            with open(css_file) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
                @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

                .main .block-container {
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                    max-width: 1400px;
                    padding-top: 2rem;
                }

                .main-header {
                    font-family: 'Poppins', sans-serif;
                    font-size: 3rem;
                    font-weight: 800;
                    color: #2D5016;
                    text-align: center;
                    margin-bottom: 3rem;
                    background: linear-gradient(135deg, #2D5016, #8B4513);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                }

                .form-container {
                    background: white;
                    padding: 2.5rem;
                    border-radius: 20px;
                    box-shadow: 0 20px 35px -5px rgba(45, 80, 22, 0.2);
                    border: 1px solid #8B7355;
                    margin: 2rem 0;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .metric-card {
                    background: white;
                    padding: 2rem;
                    border-radius: 12px;
                    box-shadow: 0 10px 25px -5px rgba(45, 80, 22, 0.15);
                    border: 1px solid #8B7355;
                    margin: 1rem 0;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    position: relative;
                    overflow: hidden;
                }

                .metric-card::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 4px;
                    background: linear-gradient(90deg, #2D5016, #8B4513);
                }

                .insight-card {
                    background: linear-gradient(135deg, #2D5016 0%, #1B4332 100%);
                    color: white;
                    padding: 2.5rem;
                    border-radius: 20px;
                    margin: 2rem 0;
                    box-shadow: 0 20px 35px -5px rgba(45, 80, 22, 0.2);
                }

                .badge {
                    padding: 0.4rem 1rem;
                    border-radius: 50px;
                    font-size: 0.875rem;
                    font-weight: 600;
                    text-align: center;
                    display: inline-block;
                }

                .badge-success {
                    background: linear-gradient(135deg, #1B4332, #0F2419);
                    color: white;
                }

                .badge-warning {
                    background: linear-gradient(135deg, #6D4C41, #5D4037);
                    color: white;
                }

                .badge-info {
                    background: linear-gradient(135deg, #2D5016, #1A3A0E);
                    color: white;
                }

                .stButton > button {
                    background: linear-gradient(135deg, #2D5016, #8B4513);
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 0.875rem 2.5rem;
                    font-weight: 600;
                    font-size: 1rem;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    box-shadow: 0 4px 15px rgba(45, 80, 22, 0.3);
                    font-family: 'Poppins', sans-serif;
                }

                .stButton > button:hover {
                    transform: translateY(-3px);
                    box-shadow: 0 15px 35px rgba(45, 80, 22, 0.4);
                }
            </style>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error cargando estilos: {e}")


def render_header(title: str, subtitle: str = None):
    """Renderizar header de página"""
    st.markdown(f"<h1 class='main-header'>{title}</h1>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(
            f"<p style='text-align: center; color: #64748b; font-size: 1.2rem; margin-bottom: 2rem;'>{subtitle}</p>",
            unsafe_allow_html=True)


def render_back_button():
    """Renderizar botón de regreso"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← Volver al Formulario", key="back_button"):
            st.session_state.show_results = False
            st.rerun()