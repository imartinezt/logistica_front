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
        return "#10b981"  # Green
    elif probability >= 0.6:
        return "#f59e0b"  # Amber
    else:
        return "#ef4444"  # Red


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
    """Extraer insights ejecutivos del API response - CORREGIDO PARA NUEVO RESPONSE"""
    insights = []

    # ADAPTADO AL NUEVO RESPONSE
    logistica = data.get('logistica_entrega', {})
    resultado = data.get('resultado_final', {})

    if logistica:
        tiempo = logistica.get('tiempo_total_h', 0)
        if tiempo <= 24:
            insights.append(f"⚡ Entrega rápida: {tiempo:.1f}h")
        elif tiempo <= 48:
            insights.append(f"📅 Entrega estándar: {tiempo:.1f}h")
        else:
            insights.append(f"🐌 Entrega extendida: {tiempo:.1f}h")

    # ADAPTADO AL NUEVO RESPONSE
    costo = resultado.get('costo_mxn', 0)
    if costo > 0:
        if costo <= 100:
            insights.append(f"💰 Costo eficiente: ${costo:,.0f}")
        elif costo <= 300:
            insights.append(f"💰 Costo moderado: ${costo:,.0f}")
        else:
            insights.append(f"💰 Costo elevado: ${costo:,.0f}")

    # ADAPTADO AL NUEVO RESPONSE
    probabilidad = resultado.get('probabilidad_exito', 0)
    if probabilidad >= 0.9:
        insights.append(f"🎯 Éxito muy probable: {probabilidad:.0%}")
    elif probabilidad >= 0.7:
        insights.append(f"📈 Éxito probable: {probabilidad:.0%}")
    else:
        insights.append(f"⚠️ Riesgo elevado: {probabilidad:.0%}")

    # ADAPTADO AL NUEVO RESPONSE
    factores = data.get('factores_externos', {})

    factor_demanda = factores.get('factor_demanda', 1.0)
    if factor_demanda > 1.5:
        insights.append(f"📊 Alta demanda (×{factor_demanda:.1f})")

    zona = factores.get('zona_seguridad')
    if zona == 'Roja':
        insights.append("🔴 Zona alto riesgo")
    elif zona == 'Verde':
        insights.append("🟢 Zona segura")

    evento = factores.get('evento_detectado', 'Normal')
    if evento != 'Normal':
        insights.append(f"🎉 Evento: {evento}")

    # ADAPTADO AL NUEVO RESPONSE
    tipo_ruta = logistica.get('tipo_ruta', '')
    if 'cedis' in tipo_ruta.lower():
        insights.append("🏭 Ruta via CEDIS")
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


def render_comprehensive_evaluation_table(data: dict):
    """Renderizar tabla comprehensiva de evaluación con TODOS los detalles solicitados"""
    st.markdown("## 🔍 Evaluación Integral Completa")

    # Tab principal de evaluación
    eval_tab1, eval_tab2, eval_tab3, eval_tab4, eval_tab5 = st.tabs([
        "🏪 Análisis Liverpool",
        "🏭 Evaluación CEDIS",
        "🌍 Factores Externos",
        "💰 Análisis de Costos",
        "🏆 Ganador Final"
    ])

    with eval_tab1:
        render_liverpool_analysis(data)

    with eval_tab2:
        render_cedis_analysis(data)

    with eval_tab3:
        render_external_factors_analysis(data)

    with eval_tab4:
        render_cost_analysis(data)

    with eval_tab5:
        render_winner_analysis(data)


def render_liverpool_analysis(data: dict):
    """Análisis completo de todas las tiendas Liverpool"""
    st.markdown("### 🏪 Análisis Completo de Tiendas Liverpool")

    import pandas as pd

    # Obtener datos de evaluación
    stock_analysis = data.get('evaluacion_detallada', {}).get('stock_analysis', {})

    # 1. TIENDAS CON STOCK DISPONIBLE
    stock_encontrado = stock_analysis.get('stock_encontrado', [])
    if stock_encontrado:
        st.markdown("#### ✅ Tiendas Liverpool con Stock Disponible")

        stock_data = []
        for i, tienda in enumerate(stock_encontrado):
            stock_data.append({
                '#': i + 1,
                'Tienda Liverpool': tienda.get('nombre_tienda', 'N/A'),
                'Stock Disponible': tienda.get('stock_disponible', 0),
                'Stock Requerido': tienda.get('stock_requerido', 0),
                'Distancia (km)': f"{tienda.get('distancia_km', 0):.1f}",
                'Precio Unitario': f"${tienda.get('precio_unitario', 0):,.2f}",
                'Precio Total': f"${tienda.get('precio_total', 0):,.2f}",
                'Es Local': '🟢 Sí' if tienda.get('es_local', False) else '🔴 No',
                'Score Tienda': f"{tienda.get('score_tienda', 0):.3f}",
                'Estado': tienda.get('estado', 'N/A'),
                'Municipio': tienda.get('alcaldia_municipio', 'N/A'),
                'Zona Seguridad': tienda.get('zona_seguridad', 'N/A')
            })

        df_stock = pd.DataFrame(stock_data)
        st.dataframe(df_stock, use_container_width=True)

        # Métricas resumen
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏪 Liverpool con Stock", len(stock_encontrado))
        with col2:
            total_stock = sum(t.get('stock_disponible', 0) for t in stock_encontrado)
            st.metric("📦 Stock Total", total_stock)
        with col3:
            avg_distance = sum(t.get('distancia_km', 0) for t in stock_encontrado) / len(
                stock_encontrado) if stock_encontrado else 0
            st.metric("📏 Distancia Promedio", f"{avg_distance:.1f} km")
        with col4:
            avg_price = sum(t.get('precio_total', 0) for t in stock_encontrado) / len(
                stock_encontrado) if stock_encontrado else 0
            st.metric("💰 Precio Promedio", f"${avg_price:,.2f}")

    # 2. TIENDAS CERCANAS SIN STOCK
    tiendas_cercanas = stock_analysis.get('tiendas_cercanas', [])
    if tiendas_cercanas:
        st.markdown("#### ❌ Tiendas Liverpool Cercanas (Sin Stock)")

        cercanas_data = []
        for i, tienda in enumerate(tiendas_cercanas):
            cercanas_data.append({
                '#': i + 1,
                'Tienda Liverpool': tienda.get('nombre', 'N/A'),
                'Distancia (km)': f"{tienda.get('distancia_km', 0):.1f}",
                'Estado': tienda.get('estado', 'N/A'),
                'Municipio': tienda.get('alcaldia_municipio', 'N/A'),
                'Zona Seguridad': tienda.get('zona_seguridad', 'N/A'),
                'Horario': tienda.get('horario_operacion', 'N/A'),
                'Capacidad Procesamiento': tienda.get('capacidad_procesamiento', 'N/A'),
                'Razón Sin Stock': 'Inventario insuficiente'
            })

        df_cercanas = pd.DataFrame(cercanas_data)
        st.dataframe(df_cercanas, use_container_width=True)

        st.metric("🏪 Liverpool Cercanas (Sin Stock)", len(tiendas_cercanas))

    # 3. PLAN DE ASIGNACIÓN DETALLADO
    asignacion_detallada = stock_analysis.get('asignacion_detallada', {})
    plan_asignacion = asignacion_detallada.get('plan_asignacion', [])

    if plan_asignacion:
        st.markdown("#### 📋 Plan de Asignación Final")

        asignacion_data = []
        for i, asign in enumerate(plan_asignacion):
            asignacion_data.append({
                '#': i + 1,
                'Tienda Asignada': asign.get('nombre_tienda', 'N/A'),
                'Cantidad Asignada': asign.get('cantidad_asignada', 0),
                'Stock Disponible': asign.get('stock_disponible', 0),
                'Costo Unitario': f"${asign.get('costo_unitario', 0):,.2f}",
                'Costo Total': f"${asign.get('costo_total', 0):,.2f}",
                'Tiempo Prep (h)': f"{asign.get('tiempo_preparacion_h', 0):.1f}",
                'Prioridad': asign.get('prioridad', 'N/A'),
                'Estado Asignación': '✅ Confirmada'
            })

        df_asignacion = pd.DataFrame(asignacion_data)
        st.dataframe(df_asignacion, use_container_width=True)

        # Totales de asignación
        total_cantidad = sum(a.get('cantidad_asignada', 0) for a in plan_asignacion)
        total_costo = sum(a.get('costo_total', 0) for a in plan_asignacion)
        total_tiempo_prep = sum(a.get('tiempo_preparacion_h', 0) for a in plan_asignacion)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📦 Total Asignado", total_cantidad)
        with col2:
            st.metric("💰 Costo Total Asignación", f"${total_costo:,.2f}")
        with col3:
            st.metric("⏱️ Tiempo Prep Total", f"{total_tiempo_prep:.1f}h")


def render_cedis_analysis(data: dict):
    """Análisis completo de CEDIS"""
    st.markdown("### 🏭 Análisis Completo de CEDIS")

    import pandas as pd

    cedis_analysis = data.get('evaluacion_detallada', {}).get('cedis_analysis', {})

    if not cedis_analysis:
        st.warning("⚠️ No se encontró evaluación de CEDIS en este caso")
        return

    # 1. CEDIS EVALUADOS
    cedis_evaluados = cedis_analysis.get('cedis_evaluados', [])
    if cedis_evaluados:
        st.markdown("#### 📊 CEDIS Evaluados")

        cedis_data = []
        for i, cedis in enumerate(cedis_evaluados):
            cedis_data.append({
                '#': i + 1,
                'CEDIS': cedis.get('nombre', 'N/A'),
                'Score': f"{cedis.get('score', 0):.3f}",
                'Distancia Total (km)': f"{cedis.get('distancia_total_km', 0):.1f}",
                'Tiempo Proc. (h)': f"{cedis.get('tiempo_procesamiento_h', 0):.1f}",
                'Capacidad': cedis.get('capacidad_procesamiento', 'N/A'),
                'Cobertura Específica': '✅ Sí' if cedis.get('cobertura_especifica', False) else '❌ No',
                'Estados Cubiertos': cedis.get('cobertura_estados', 'N/A'),
                'Horario Operación': cedis.get('horario_operacion', 'N/A'),
                'Estado': cedis.get('estado', 'N/A')
            })

        df_cedis = pd.DataFrame(cedis_data)
        st.dataframe(df_cedis, use_container_width=True)

        # Métricas CEDIS
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🏭 CEDIS Evaluados", len(cedis_evaluados))
        with col2:
            avg_score = sum(c.get('score', 0) for c in cedis_evaluados) / len(cedis_evaluados)
            st.metric("📊 Score Promedio", f"{avg_score:.3f}")
        with col3:
            avg_tiempo = sum(c.get('tiempo_procesamiento_h', 0) for c in cedis_evaluados) / len(cedis_evaluados)
            st.metric("⏱️ Tiempo Proc. Promedio", f"{avg_tiempo:.1f}h")

    # 2. CEDIS SELECCIONADO
    cedis_seleccionado = cedis_analysis.get('cedis_seleccionado', {})
    if cedis_seleccionado:
        st.markdown("#### 🏆 CEDIS Seleccionado")

        st.success(f"""
        **🏭 CEDIS Ganador:** {cedis_seleccionado.get('nombre', 'N/A')}

        **📊 Score Final:** {cedis_seleccionado.get('score', 0):.3f}

        **🎯 Razón de Selección:** {cedis_seleccionado.get('razon_seleccion', 'N/A')}

        **📏 Distancia:** {cedis_seleccionado.get('distancia_total_km', 0):.1f} km

        **⏱️ Tiempo de Procesamiento:** {cedis_seleccionado.get('tiempo_procesamiento_h', 0):.1f} horas

        **🗺️ Cobertura:** {cedis_seleccionado.get('cobertura_estados', 'N/A')}
        """)

        # Ventajas del CEDIS seleccionado
        ventajas = cedis_seleccionado.get('ventajas', [])
        if ventajas:
            st.markdown("**✅ Ventajas Clave:**")
            for ventaja in ventajas:
                st.markdown(f"• {ventaja}")


def render_external_factors_analysis(data: dict):
    """Análisis completo de factores externos"""
    st.markdown("### 🌍 Análisis Completo de Factores Externos")

    factores = data.get('factores_externos', {})

    # 1. FACTORES CLIMÁTICOS
    st.markdown("#### 🌤️ Condiciones Climáticas")
    col1, col2, col3 = st.columns(3)

    with col1:
        clima = factores.get('condicion_clima', 'N/A')
        st.metric("🌡️ Condición Climática", clima)

        if 'Frio' in clima:
            st.warning("❄️ Condiciones frías pueden afectar tiempos de entrega")
        elif 'Lluvia' in clima:
            st.warning("🌧️ Lluvia puede impactar logística")
        else:
            st.success("☀️ Condiciones climáticas favorables")

    with col2:
        temp = factores.get('temperatura_celsius', 0)
        st.metric("🌡️ Temperatura", f"{temp}°C")

        if temp < 10:
            st.warning("🥶 Temperatura baja")
        elif temp > 35:
            st.warning("🥵 Temperatura alta")
        else:
            st.success("🌡️ Temperatura óptima")

    with col3:
        lluvia = factores.get('probabilidad_lluvia', 0)
        st.metric("☔ Prob. Lluvia", f"{lluvia}%")

        if lluvia > 70:
            st.error("🌧️ Alta probabilidad de lluvia")
        elif lluvia > 30:
            st.warning("🌦️ Posible lluvia")
        else:
            st.success("☀️ Cielo despejado")

    # 2. FACTORES DE TRÁFICO Y SEGURIDAD
    st.markdown("#### 🚦 Tráfico y Seguridad")
    col1, col2, col3 = st.columns(3)

    with col1:
        trafico = factores.get('trafico_nivel', 'N/A')
        st.metric("🚗 Nivel de Tráfico", trafico)

        if trafico == 'Alto':
            st.warning("🚗 Tráfico intenso esperado")
        elif trafico == 'Moderado':
            st.info("🚙 Tráfico moderado")
        else:
            st.success("🛣️ Tráfico fluido")

    with col2:
        zona_seguridad = factores.get('zona_seguridad', 'N/A')
        st.metric("🛡️ Zona de Seguridad", zona_seguridad)

        if zona_seguridad == 'Roja':
            st.error("🔴 Zona de alto riesgo")
        elif zona_seguridad == 'Amarilla':
            st.warning("🟡 Zona de precaución")
        else:
            st.success("🟢 Zona segura")

    with col3:
        tiempo_extra = factores.get('impacto_tiempo_extra_horas', 0)
        st.metric("⏱️ Tiempo Extra", f"{tiempo_extra:.1f}h")

        if tiempo_extra > 2:
            st.warning(f"⏰ +{tiempo_extra:.1f}h por factores externos")
        elif tiempo_extra > 0:
            st.info(f"⏱️ +{tiempo_extra:.1f}h impacto menor")
        else:
            st.success("✅ Sin impacto en tiempo")

    # 3. FACTORES DE DEMANDA
    st.markdown("#### 📈 Análisis de Demanda")
    col1, col2, col3 = st.columns(3)

    with col1:
        factor_demanda = factores.get('factor_demanda', 1.0)
        st.metric("📊 Factor de Demanda", f"{factor_demanda:.2f}x")

        if factor_demanda > 2.0:
            st.error("📈 Demanda extremadamente alta")
        elif factor_demanda > 1.5:
            st.warning("📊 Demanda alta")
        else:
            st.success("📉 Demanda normal")

    with col2:
        evento = factores.get('evento_detectado', 'Normal')
        st.metric("🎉 Evento Especial", evento)

        if evento != 'Normal':
            st.info(f"🎊 Evento detectado: {evento}")
        else:
            st.success("📅 Día normal")

    with col3:
        temporada = "Alta" if factor_demanda > 1.5 else "Normal"
        st.metric("🗓️ Temporada", temporada)

        if temporada == "Alta":
            st.warning("🎄 Temporada alta - mayor demanda")
        else:
            st.success("📅 Temporada normal")


def render_cost_analysis(data: dict):
    """Análisis completo de costos"""
    st.markdown("### 💰 Análisis Detallado de Costos")

    import pandas as pd

    # 1. DESGLOSE DE COSTOS PRINCIPALES
    resultado = data.get('resultado_final', {})
    logistica = data.get('logistica_entrega', {})

    st.markdown("#### 💳 Desglose de Costos")

    costo_total = resultado.get('costo_mxn', 0)
    desglose_costos = logistica.get('desglose_costos_mxn', {})

    # Crear tabla de costos
    costos_data = [
        {
            'Concepto': 'Costo Base Producto',
            'Monto': f"${desglose_costos.get('producto', 0):,.2f}",
            'Porcentaje': f"{(desglose_costos.get('producto', 0) / max(costo_total, 1)) * 100:.1f}%",
            'Categoría': 'Producto'
        },
        {
            'Concepto': 'Transporte',
            'Monto': f"${desglose_costos.get('transporte', 0):,.2f}",
            'Porcentaje': f"{(desglose_costos.get('transporte', 0) / max(costo_total, 1)) * 100:.1f}%",
            'Categoría': 'Logística'
        },
        {
            'Concepto': 'Preparación',
            'Monto': f"${desglose_costos.get('preparacion', 0):,.2f}",
            'Porcentaje': f"{(desglose_costos.get('preparacion', 0) / max(costo_total, 1)) * 100:.1f}%",
            'Categoría': 'Operación'
        },
        {
            'Concepto': 'Contingencia',
            'Monto': f"${desglose_costos.get('contingencia', 0):,.2f}",
            'Porcentaje': f"{(desglose_costos.get('contingencia', 0) / max(costo_total, 1)) * 100:.1f}%",
            'Categoría': 'Buffer'
        }
    ]

    df_costos = pd.DataFrame(costos_data)
    st.dataframe(df_costos, use_container_width=True)

    # 2. MÉTRICAS DE COSTO
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("💰 Costo Total", f"${costo_total:,.2f}")

    with col2:
        costo_por_km = costo_total / max(logistica.get('distancia_km', 1), 1)
        st.metric("📏 Costo por KM", f"${costo_por_km:.2f}")

    with col3:
        costo_por_hora = costo_total / max(logistica.get('tiempo_total_h', 1), 1)
        st.metric("⏱️ Costo por Hora", f"${costo_por_hora:.2f}")

    with col4:
        # Calcular cantidad desde asignación
        cantidad = data.get('request', {}).get('cantidad', 1)
        costo_por_unidad = costo_total / max(cantidad, 1)
        st.metric("📦 Costo por Unidad", f"${costo_por_unidad:.2f}")

    # 3. COMPARACIÓN CON ALTERNATIVAS (si existe)
    evaluacion = data.get('evaluacion', {})
    candidatos = evaluacion.get('candidatos_evaluados', [])

    if len(candidatos) > 1:
        st.markdown("#### 🔄 Comparación de Costos con Alternativas")

        comparacion_data = []
        for i, candidato in enumerate(candidatos[:5]):  # Top 5
            asignacion = candidato.get('asignacion', {})
            comparacion_data.append({
                'Ranking': i + 1,
                'Tienda': candidato.get('tienda', 'N/A'),
                'Costo Total': f"${asignacion.get('costo_total_mxn', 0):,.2f}",
                'Score': f"{candidato.get('score_final', 0):.3f}",
                'Distancia (km)': f"{asignacion.get('distancia_km', 0):.1f}",
                'Tiempo (h)': f"{asignacion.get('tiempo_total_h', 0):.1f}",
                'Seleccionado': '🏆 SÍ' if i == 0 else '❌ No'
            })

        df_comparacion = pd.DataFrame(comparacion_data)
        st.dataframe(df_comparacion, use_container_width=True)


def render_winner_analysis(data: dict):
    """Análisis completo del ganador"""
    st.markdown("### 🏆 Análisis del Ganador Final")

    ganador = data.get('evaluacion', {}).get('ganador', {})

    if not ganador:
        st.warning("⚠️ No se encontró información del ganador")
        return

    # 1. INFORMACIÓN DEL GANADOR
    st.markdown("#### 🥇 Tienda Ganadora")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.success(f"""
        **🏪 Tienda Seleccionada:** {ganador.get('tienda', 'N/A')}

        **📊 Score Final:** {ganador.get('score_final', 0):.3f}

        **🎯 Ranking:** #{ganador.get('ranking', 1)}

        **💰 Costo Total:** ${ganador.get('asignacion', {}).get('costo_total_mxn', 0):,.2f}

        **📏 Distancia:** {ganador.get('asignacion', {}).get('distancia_km', 0):.1f} km

        **⏱️ Tiempo Total:** {ganador.get('asignacion', {}).get('tiempo_total_h', 0):.1f} horas
        """)

    with col2:
        # Ventajas del ganador
        ventajas = ganador.get('ventajas', [])
        if ventajas:
            st.markdown("**✅ Ventajas Clave:**")
            for ventaja in ventajas:
                st.markdown(f"• {ventaja}")

        # Desventajas si existen
        desventajas = ganador.get('desventajas', [])
        if desventajas:
            st.markdown("**⚠️ Consideraciones:**")
            for desventaja in desventajas:
                st.markdown(f"• {desventaja}")

    # 2. TRAZADO COMPLETO DE LA RUTA GANADORA
    st.markdown("#### 🗺️ Trazado Completo de la Ruta Ganadora")

    logistica = data.get('logistica_entrega', {})

    # Información de ruta
    st.info(f"""
    **🛣️ Tipo de Ruta:** {logistica.get('tipo_ruta', 'N/A')}

    **🚚 Carrier:** {logistica.get('carrier', 'N/A')}

    **🚛 Flota:** {logistica.get('flota', 'N/A')}

    **📏 Distancia Total:** {logistica.get('distancia_km', 0):.1f} km

    **⏱️ Tiempo Total:** {logistica.get('tiempo_total_h', 0):.1f} horas
    """)

    # Desglose de tiempos
    st.markdown("#### ⏰ Desglose Temporal de la Ruta")

    desglose_tiempos = logistica.get('desglose_tiempos_h', {})

    import pandas as pd

    tiempo_data = [
        {
            'Etapa': 'Preparación en Tienda',
            'Tiempo (h)': f"{desglose_tiempos.get('preparacion', 0):.2f}",
            'Descripción': 'Picking, empaque y preparación del pedido',
            'Responsable': 'Tienda Liverpool'
        },
        {
            'Etapa': 'Viaje/Transporte',
            'Tiempo (h)': f"{desglose_tiempos.get('viaje', 0):.2f}",
            'Descripción': 'Transporte desde origen hasta destino',
            'Responsable': logistica.get('carrier', 'N/A')
        },
        {
            'Etapa': 'Contingencia',
            'Tiempo (h)': f"{desglose_tiempos.get('contingencia', 0):.2f}",
            'Descripción': 'Buffer para imprevistos y demoras',
            'Responsable': 'Sistema'
        }
    ]

    df_tiempo = pd.DataFrame(tiempo_data)
    st.dataframe(df_tiempo, use_container_width=True)

    # 3. RAZONES DE LA SELECCIÓN
    st.markdown("#### 🎯 Razones de la Selección")

    razon_seleccion = ganador.get('razon_seleccion', '')
    if razon_seleccion:
        st.success(f"🎯 **Razón Principal:** {razon_seleccion}")

    # Análisis de pesos utilizados
    pesos = data.get('evaluacion', {}).get('pesos', {})
    if pesos:
        st.markdown("**⚖️ Pesos Utilizados en la Evaluación:**")

        pesos_data = []
        for criterio, peso in pesos.items():
            pesos_data.append({
                'Criterio': criterio.title(),
                'Peso': f"{peso:.2f}",
                'Porcentaje': f"{peso * 100:.1f}%",
                'Impacto': 'Alto' if peso > 0.3 else 'Medio' if peso > 0.15 else 'Bajo'
            })

        df_pesos = pd.DataFrame(pesos_data)
        st.dataframe(df_pesos, use_container_width=True)

    # 4. RESULTADO FINAL
    st.markdown("#### 🎉 Resultado Final")

    resultado = data.get('resultado_final', {})

    col1, col2, col3 = st.columns(3)

    with col1:
        prob_exito = resultado.get('probabilidad_exito', 0)
        st.metric("🎯 Probabilidad de Éxito", f"{prob_exito:.1%}")

        if prob_exito >= 0.9:
            st.success("🎯 Muy alta probabilidad de éxito")
        elif prob_exito >= 0.7:
            st.info("📈 Buena probabilidad de éxito")
        else:
            st.warning("⚠️ Probabilidad moderada")

    with col2:
        confianza = resultado.get('confianza_prediccion', 0)
        st.metric("🔮 Confianza Predicción", f"{confianza:.1%}")

        if confianza >= 0.85:
            st.success("🔮 Predicción muy confiable")
        elif confianza >= 0.7:
            st.info("📊 Predicción confiable")
        else:
            st.warning("⚠️ Predicción con reservas")

    with col3:
        fecha_entrega = resultado.get('fecha_entrega_estimada', '')
        if fecha_entrega:
            st.metric("📅 Fecha Entrega", format_datetime(fecha_entrega))
            st.success("✅ Fecha confirmada")
        else:
            st.metric("📅 Fecha Entrega", "N/A")
            st.warning("⚠️ Fecha pendiente")