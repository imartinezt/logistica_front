from datetime import datetime

import streamlit as st


def init_session_state():
    """Inicializar variables de estado de sesión"""
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False
    if 'prediction_data' not in st.session_state:
        st.session_state.prediction_data = None
    if 'original_request' not in st.session_state:
        st.session_state.original_request = {}


def format_currency(amount: float) -> str:
    """Formatear cantidad como moneda mexicana"""
    if amount is None or amount == 'N/A':
        return 'N/A'
    try:
        return f"${amount:,.2f} MXN"
    except (ValueError, TypeError):
        return 'N/A'


def format_datetime(date_str: str) -> str:
    """Formatear string de fecha a formato legible"""
    if not date_str or date_str == 'N/A':
        return 'N/A'

    try:
        # Manejar diferentes formatos de fecha
        if 'T' in date_str:
            if '.' in date_str:
                # Formato con microsegundos: 2025-06-12T18:38:45.446834
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                # Formato sin microsegundos: 2025-06-09T10:00:00
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            # Formato solo fecha: 2025-06-09
            dt = datetime.strptime(date_str, '%Y-%m-%d')

        # Formatear a español
        months = [
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ]
        days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

        day_name = days[dt.weekday()]
        month_name = months[dt.month - 1]

        return f"{day_name}, {dt.day} de {month_name} {dt.year}"

    except (ValueError, TypeError, AttributeError):
        return date_str  # Retornar el string original si no se puede formatear


def format_percentage(value: float, decimals: int = 1) -> str:
    """Formatear valor como porcentaje"""
    if value is None or value == 'N/A':
        return 'N/A'
    try:
        return f"{value:.{decimals}f}%"
    except (ValueError, TypeError):
        return 'N/A'


def get_delivery_status_badge(metodo: str) -> str:
    """Obtener badge HTML para método de entrega"""
    if not metodo or metodo == 'N/A':
        return '<span class="badge badge-secondary">N/A</span>'

    # Mapeo de métodos a colores y iconos
    method_styles = {
        'EDT FLASH': '<span style="background: #10b981; color: white; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600;">🚀 EDT FLASH</span>',
        'FLOTA LIVERPOOL': '<span style="background: #3b82f6; color: white; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600;">🚛 FLOTA LIVERPOOL</span>',
        'MENSAJERIA EXTERNA': '<span style="background: #f59e0b; color: white; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600;">📦 MENSAJERÍA EXTERNA</span>',
        'SAME DAY': '<span style="background: #ef4444; color: white; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600;">⚡ SAME DAY</span>'
    }

    return method_styles.get(metodo.upper(),
                             f'<span style="background: #6b7280; color: white; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600;">{metodo}</span>')


def calculate_business_days(start_date: str, end_date: str) -> int:
    """Calcular días hábiles entre dos fechas"""
    if not start_date or not end_date:
        return 0

    try:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

        # Contar días hábiles (lunes a viernes)
        current = start.date()
        end_date_obj = end.date()
        business_days = 0

        while current <= end_date_obj:
            if current.weekday() < 5:  # 0-4 son lunes a viernes
                business_days += 1
            current = current.replace(day=current.day + 1)

        return business_days
    except:
        return 0


def get_priority_icon(score: float) -> str:
    """Obtener icono de prioridad basado en el score"""
    if score >= 0.8:
        return "🟢"  # Verde - Alta prioridad
    elif score >= 0.6:
        return "🟡"  # Amarillo - Media prioridad
    else:
        return "🔴"  # Rojo - Baja prioridad


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncar texto con elipsis"""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def safe_get(data: dict, key: str, default='N/A'):
    """Obtener valor de diccionario de forma segura"""
    try:
        return data.get(key, default) if data else default
    except (AttributeError, TypeError):
        return default