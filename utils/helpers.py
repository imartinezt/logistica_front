from datetime import datetime
import streamlit as st


def init_session_state():
    """Inicializar el estado de la sesión"""
    if 'prediction_data' not in st.session_state:
        st.session_state.prediction_data = None
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False
    if 'original_request' not in st.session_state:
        st.session_state.original_request = {}


def format_currency(amount: float) -> str:
    return f"${amount:,.2f}"


def format_percentage(value: float) -> str:
    return f"{value * 100:.1f}%"


def format_datetime(datetime_str: str) -> str:
    try:
        if not datetime_str:
            return "N/A"
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        return dt.strftime('%d/%m/%Y %H:%M')
    except:
        return str(datetime_str) if datetime_str else "N/A"


def get_delivery_status_badge(delivery_type: str) -> str:
    delivery_type_upper = delivery_type.upper()
    badge_config = {
        "FLOTA LIVERPOOL": {"color": "#e3f2fd", "icon": "🏠", "text_color": "#1565c0"},
        "MENSAJERIA EXTERNA": {"color": "#f3e5f5", "icon": "🚚", "text_color": "#7b1fa2"},
        "EDT FLASH": {"color": "#fff3e0", "icon": "⚡", "text_color": "#ef6c00"},
        "EDT DIRECTA": {"color": "#e8f5e8", "icon": "🎯", "text_color": "#2e7d32"},
        "EDT EXTENDIDO": {"color": "#fce4ec", "icon": "📦", "text_color": "#c2185b"},
    }
    config = None
    for key, value in badge_config.items():
        if key in delivery_type_upper:
            config = value
            break

    if not config:
        config = {"color": "#f5f5f5", "icon": "📋", "text_color": "#424242"}

    return f'''
    <span style="
        background: {config["color"]};
        color: {config["text_color"]};
        padding: 0.375rem 0.875rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid {config["text_color"]}33;
    ">
        {config["icon"]} {delivery_type}
    </span>
    '''