from datetime import datetime

import streamlit as st


def init_session_state():
    """Inicializar el estado de la sesión"""
    if 'prediction_data' not in st.session_state:
        st.session_state.prediction_data = None
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False


def format_currency(amount: float) -> str:
    """Formatear cantidad como moneda mexicana"""
    return f"${amount:,.2f} MXN"


def format_percentage(value: float) -> str:
    """Formatear como porcentaje"""
    return f"{value * 100:.1f}%"


def format_datetime(datetime_str: str) -> str:
    """Formatear datetime string"""
    try:
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        return dt.strftime('%d/%m/%Y')
    except:
        return "N/A"


def format_datetime_with_time(datetime_str: str) -> str:
    """Formatear datetime string con hora"""
    try:
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        return dt.strftime('%d/%m/%Y a las %H:%M')
    except:
        return "N/A"


def get_delivery_status_badge(tipo_entrega: str) -> str:
    """tipo de entrega"""
    if tipo_entrega == "EXPRESS":
        return f'<span style="background: linear-gradient(135deg, #1B4332, #0F2419); color: white; padding: 0.4rem 1rem; border-radius: 50px; font-size: 0.875rem; font-weight: 600;">⚡ {tipo_entrega}</span>'
    elif tipo_entrega == "STANDARD":
        return f'<span style="background: linear-gradient(135deg, #6D4C41, #5D4037); color: white; padding: 0.4rem 1rem; border-radius: 50px; font-size: 0.875rem; font-weight: 600;">📦 {tipo_entrega}</span>'
    else:
        return f'<span style="background: linear-gradient(135deg, #2D5016, #1A3A0E); color: white; padding: 0.4rem 1rem; border-radius: 50px; font-size: 0.875rem; font-weight: 600;">📋 {tipo_entrega}</span>'


def get_risk_level_color(probability: float) -> str:
    """probabilidad de cumplimiento"""
    if probability >= 0.8:
        return "#1B4332"  # Verde Oscuro (success)
    elif probability >= 0.6:
        return "#6D4C41"  # Marrón Medio (warning)
    else:
        return "#4A148C"  # Púrpura Profundo (danger)


def extract_key_insights(data: dict) -> list:
    """ Extraer insights dinámicos del API response"""
    insights = []
    ruta = data.get('ruta_seleccionada', {})
    if ruta:
        tiempo = ruta.get('tiempo_total_horas', 0)
        insights.append(f"⏱️ Tiempo estimado: {tiempo:.1f} horas")

    costo = data.get('costo_envio_mxn', 0)
    if costo > 0:
        insights.append(f"💰 Costo: ${costo:,.2f} MXN")

    probabilidad = data.get('probabilidad_cumplimiento', 0)
    if probabilidad > 0:
        insights.append(f"📈 Probabilidad éxito: {probabilidad:.1%}")

    factores = data.get('explicabilidad', {}).get('factores_externos', {})

    if factores.get('es_temporada_alta'):
        factor_demanda = factores.get('factor_demanda', 1.0)
        insights.append(f"🎄 Alta demanda (x{factor_demanda}) - Temporada especial")

    zona = factores.get('zona_seguridad')
    if zona == 'Roja':
        insights.append("🔴 Zona de alto riesgo - Tiempo y costo incrementados")
    elif zona == 'Amarilla':
        insights.append("🟡 Zona de riesgo moderado")
    elif zona == 'Verde':
        insights.append("🟢 Zona de bajo riesgo")

    eventos = factores.get('eventos_detectados', [])
    if eventos:
        insights.append(f"🎉 Eventos especiales: {', '.join(eventos)}")

    segmentos = ruta.get('segmentos', [])
    if len(segmentos) > 2:
        insights.append("🏭 Ruta compleja via CEDIS")
    elif len(segmentos) <= 2:
        insights.append("🚚 Ruta directa optimizada")

    return insights