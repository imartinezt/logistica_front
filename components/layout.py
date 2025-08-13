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
    """CSS update"""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        /* Variables CSS */
        :root {
            --primary-blue: #2563eb;
            --secondary-blue: #1e40af;
            --success-green: #10b981;
            --warning-orange: #f59e0b;
            --error-red: #ef4444;
            --text-dark: #1f2937;
            --text-medium: #6b7280;
            --text-light: #9ca3af;
            --bg-light: #f9fafb;
            --bg-white: #ffffff;
            --border-light: #e5e7eb;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            --radius-sm: 6px;
            --radius-md: 8px;
            --radius-lg: 12px;
            --radius-xl: 16px;
        }

        /* Reset y base */
        * {
            box-sizing: border-box;
        }

        .main .block-container {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            max-width: 1200px;
            padding-top: 1rem;
            padding-bottom: 2rem;
        }

        /* Header principal */
        .main-header {
            text-align: center;
            margin-bottom: 3rem;
            padding: 2rem 0;
            background: linear-gradient(135deg, var(--primary-blue), var(--secondary-blue));
            color: white;
            border-radius: var(--radius-xl);
            box-shadow: var(--shadow-lg);
        }

        .main-header h1 {
            font-size: 3rem;
            font-weight: 700;
            margin: 0 0 0.5rem 0;
            letter-spacing: -0.025em;
        }

        .subtitle {
            font-size: 1.25rem;
            font-weight: 400;
            opacity: 0.9;
            margin: 0;
        }

        /* Contenedor del formulario */
        .form-container {
            background: var(--bg-white);
            padding: 2.5rem;
            border-radius: var(--radius-xl);
            box-shadow: var(--shadow-lg);
            border: 1px solid var(--border-light);
            margin: 2rem 0;
        }

        /* Tarjeta de fecha promesa de entrega */
        .delivery-promise-card {
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border: 2px solid var(--primary-blue);
            border-radius: var(--radius-xl);
            padding: 2.5rem;
            margin: 2rem 0;
            box-shadow: var(--shadow-lg);
        }

        .delivery-promise-card h2 {
            color: var(--primary-blue);
            font-size: 1.5rem;
            font-weight: 600;
            margin: 0 0 1rem 0;
            text-align: center;
        }

        .delivery-date {
            font-size: 2.5rem;
            font-weight: 800;
            text-align: center;
            color: var(--secondary-blue);
            margin: 1rem 0 2rem 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }

        .delivery-info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }

        .info-item {
            display: flex;
            flex-direction: column;
            background: var(--bg-white);
            padding: 1rem;
            border-radius: var(--radius-md);
            border: 1px solid var(--border-light);
        }

        .label {
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--text-medium);
            margin-bottom: 0.25rem;
        }

        .value {
            font-size: 1rem;
            font-weight: 600;
            color: var(--text-dark);
        }

        .value.highlight {
            color: var(--success-green);
            font-size: 1.125rem;
            font-weight: 700;
        }

        .delivery-details {
            background: var(--bg-white);
            border-radius: var(--radius-md);
            padding: 1.5rem;
            margin-top: 2rem;
            border: 1px solid var(--border-light);
        }

        .detail-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem 0;
            border-bottom: 1px solid var(--border-light);
        }

        .detail-row:last-child {
            border-bottom: none;
        }

        .detail-label {
            font-weight: 600;
            color: var(--text-dark);
            font-size: 0.875rem;
        }

        .detail-value {
            font-weight: 500;
            color: var(--text-medium);
            text-align: right;
        }

        /* Botones */
        .stButton > button {
            background: linear-gradient(135deg, var(--primary-blue), var(--secondary-blue));
            color: white;
            border: none;
            border-radius: var(--radius-lg);
            padding: 0.875rem 2rem;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.2s ease;
            box-shadow: var(--shadow-md);
            font-family: 'Inter', sans-serif;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
            background: linear-gradient(135deg, #1d4ed8, #1e40af);
        }

        /* Inputs del formulario */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stDateInput > div > div > input,
        .stTimeInput > div > div > input,
        .stSelectbox > div > div > select {
            border-radius: var(--radius-md);
            border: 2px solid var(--border-light);
            transition: border-color 0.2s ease;
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-white);
            color: var(--text-dark);
            font-size: 0.875rem;
            padding: 0.75rem;
        }

        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stDateInput > div > div > input:focus,
        .stTimeInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus {
            border-color: var(--primary-blue);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
            outline: none;
        }

        .stTextInput > label,
        .stNumberInput > label,
        .stDateInput > label,
        .stTimeInput > label,
        .stSelectbox > label {
            font-weight: 600;
            color: var(--text-dark);
            font-family: 'Inter', sans-serif;
            font-size: 0.875rem;
        }

        /* Métricas */
        .stMetric {
            background: var(--bg-white);
            padding: 1.5rem;
            border-radius: var(--radius-lg);
            border: 1px solid var(--border-light);
            box-shadow: var(--shadow-sm);
            transition: all 0.2s ease;
        }

        .stMetric:hover {
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            background: var(--bg-light);
            padding: 0.375rem;
            border-radius: var(--radius-lg);
            border: 1px solid var(--border-light);
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: var(--radius-md);
            padding: 0.75rem 1.5rem;
            font-weight: 500;
            transition: all 0.2s ease;
            font-family: 'Inter', sans-serif;
            color: var(--text-medium);
        }

        .stTabs [aria-selected="true"] {
            background: var(--primary-blue);
            color: white;
            box-shadow: var(--shadow-sm);
        }

        /* Alertas */
        .stSuccess {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid var(--success-green);
            border-radius: var(--radius-lg);
            color: var(--text-dark);
        }

        .stError {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid var(--error-red);
            border-radius: var(--radius-lg);
            color: var(--text-dark);
        }

        .stInfo {
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid var(--primary-blue);
            border-radius: var(--radius-lg);
            color: var(--text-dark);
        }

        .stWarning {
            background: rgba(245, 158, 11, 0.1);
            border: 1px solid var(--warning-orange);
            border-radius: var(--radius-lg);
            color: var(--text-dark);
        }

        /* DataFrames */
        .stDataFrame {
            border-radius: var(--radius-lg);
            overflow: hidden;
            box-shadow: var(--shadow-md);
            border: 1px solid var(--border-light);
        }

        /* Calendario */
        .fc {
            font-family: 'Inter', sans-serif;
            border-radius: var(--radius-lg);
            overflow: hidden;
            box-shadow: var(--shadow-md);
        }

        /* Scrollbar personalizada */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: var(--bg-light);
            border-radius: var(--radius-sm);
        }

        ::-webkit-scrollbar-thumb {
            background: var(--primary-blue);
            border-radius: var(--radius-sm);
        }

        ::-webkit-scrollbar-thumb:hover {
            background: var(--secondary-blue);
        }

        /* Responsive */
        @media (max-width: 768px) {
            .main-header h1 {
                font-size: 2rem;
            }

            .delivery-date {
                font-size: 2rem;
            }

            .form-container {
                padding: 1.5rem;
            }

            .delivery-promise-card {
                padding: 1.5rem;
            }

            .delivery-info-grid {
                grid-template-columns: 1fr;
            }

            .detail-row {
                flex-direction: column;
                align-items: flex-start;
                gap: 0.5rem;
            }

            .detail-value {
                text-align: left;
            }
        }
    </style>
    """, unsafe_allow_html=True)