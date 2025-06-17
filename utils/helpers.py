from datetime import datetime
import streamlit as st


def init_session_state():
    """Inicializar el estado de la sesión"""
    if 'prediction_data' not in st.session_state:
        st.session_state.prediction_data = None
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False
    if 'hora_compra' not in st.session_state:
        st.session_state.hora_compra = datetime.now().time()
    if 'fecha_compra' not in st.session_state:
        st.session_state.fecha_compra = datetime.now().date()


def format_currency(amount: float) -> str:
    """Formatear cantidad como moneda mexicana"""
    return f"${amount:,.2f}"


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
    """Obtener badge de tipo de entrega"""
    badges = {
        "EXPRESS": {
            "color": "#10b981",
            "icon": "⚡",
            "label": "EXPRESS"
        },
        "STANDARD": {
            "color": "#3b82f6",
            "icon": "📦",
            "label": "STANDARD"
        },
        "PREMIUM": {
            "color": "#8b5cf6",
            "icon": "👑",
            "label": "PREMIUM"
        }
    }

    badge_info = badges.get(tipo_entrega, {
        "color": "#64748b",
        "icon": "📋",
        "label": tipo_entrega
    })

    return f'''
    <span style="
        background: {badge_info["color"]};
        color: white;
        padding: 0.375rem 0.875rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        font-family: Inter, system-ui, sans-serif;
        letter-spacing: 0.025em;
    ">
        {badge_info["icon"]} {badge_info["label"]}
    </span>
    '''


def get_risk_level_color(probability: float) -> str:
    """Obtener color basado en probabilidad de cumplimiento"""
    if probability >= 0.8:
        return "#10b981"  #  Green
    elif probability >= 0.6:
        return "#f59e0b"  #  Amber
    else:
        return "#ef4444"  #  Red


def get_priority_badge(priority: str) -> str:
    """Obtener badge de prioridad """
    priorities = {
        "ALTA": {"color": "#ef4444", "icon": "🔴"},
        "MEDIA": {"color": "#f59e0b", "icon": "🟡"},
        "BAJA": {"color": "#10b981", "icon": "🟢"},
        "CRITICA": {"color": "#8b5cf6", "icon": "🟣"}
    }

    priority_info = priorities.get(priority.upper(), {
        "color": "#64748b",
        "icon": "⚪"
    })

    return f'''
    <span style="
        background: {priority_info["color"]};
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        font-family: Inter, system-ui, sans-serif;
    ">
        {priority_info["icon"]} {priority}
    </span>
    '''


def extract_key_insights(data: dict) -> list:
    """Extraer insights ejecutivos del API response"""
    insights = []
    ruta = data.get('ruta_seleccionada', {})

    if ruta:
        tiempo = ruta.get('tiempo_total_horas', 0)
        if tiempo <= 24:
            insights.append(f"⚡ Entrega rápida: {tiempo:.1f}h")
        elif tiempo <= 48:
            insights.append(f"📅 Entrega estándar: {tiempo:.1f}h")
        else:
            insights.append(f"🐌 Entrega extendida: {tiempo:.1f}h")

    costo = data.get('costo_envio_mxn', 0)
    if costo > 0:
        if costo <= 100:
            insights.append(f"💰 Costo eficiente: ${costo:,.0f}")
        elif costo <= 300:
            insights.append(f"💰 Costo moderado: ${costo:,.0f}")
        else:
            insights.append(f"💰 Costo elevado: ${costo:,.0f}")

    probabilidad = data.get('probabilidad_cumplimiento', 0)
    if probabilidad >= 0.9:
        insights.append(f"🎯 Éxito muy probable: {probabilidad:.0%}")
    elif probabilidad >= 0.7:
        insights.append(f"📈 Éxito probable: {probabilidad:.0%}")
    else:
        insights.append(f"⚠️ Riesgo elevado: {probabilidad:.0%}")

    factores = data.get('explicabilidad', {}).get('factores_externos', {})

    if factores.get('es_temporada_alta'):
        factor_demanda = factores.get('factor_demanda', 1.0)
        insights.append(f"📊 Alta demanda (×{factor_demanda:.1f})")

    zona = factores.get('zona_seguridad')
    if zona == 'Roja':
        insights.append("🔴 Zona alto riesgo")
    elif zona == 'Verde':
        insights.append("🟢 Zona segura")

    eventos = factores.get('eventos_detectados', [])
    if eventos:
        insights.append(f"🎉 Eventos: {len(eventos)} detectados")

    segmentos = ruta.get('segmentos', [])
    if len(segmentos) > 2:
        insights.append("🏭 Ruta multi-segmento")
    else:
        insights.append("🚚 Ruta directa")

    return insights[:5]  # Máximo 5 insights para mantener claridad


def render_executive_metric(title: str, value: str, delta: str = None, icon: str = "📊"):
    """Renderizar métrica con diseño ejecutivo"""
    delta_html = ""
    if delta:
        delta_html = f'<div style="color: #64748b; font-size: 0.875rem; margin-top: 0.25rem;">{delta}</div>'

    st.markdown(f"""
    <div style="
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
        text-align: center;
    " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.1)'" 
       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 4px rgba(0,0,0,0.05)'">
        <div style="color: #3b82f6; font-size: 1.5rem; margin-bottom: 0.5rem;">{icon}</div>
        <div style="color: #64748b; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.5rem; font-family: Inter, system-ui, sans-serif;">{title}</div>
        <div style="color: #1e293b; font-size: 1.5rem; font-weight: 700; font-family: Inter, system-ui, sans-serif;">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_status_indicator(status: str, message: str):
    """Renderizar indicador de estatus """
    status_config = {
        "success": {"color": "#10b981", "icon": "✅", "bg": "#ecfdf5"},
        "warning": {"color": "#f59e0b", "icon": "⚠️", "bg": "#fffbeb"},
        "error": {"color": "#ef4444", "icon": "❌", "bg": "#fef2f2"},
        "info": {"color": "#3b82f6", "icon": "ℹ️", "bg": "#eff6ff"}
    }

    config = status_config.get(status, status_config["info"])

    st.markdown(f"""
    <div style="
        background: {config['bg']};
        border: 1px solid {config['color']};
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-family: Inter, system-ui, sans-serif;
    ">
        <span style="font-size: 1.25rem;">{config['icon']}</span>
        <span style="color: #1e293b; font-weight: 500;">{message}</span>
    </div>
    """, unsafe_allow_html=True)