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


# AGREGAR ESTA FUNCIÓN PRINCIPAL A utils/helpers.py

def render_comprehensive_evaluation_table(data: dict):
    """Renderizar tabla comprehensiva CORREGIDA con datos reales del response"""
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
        render_liverpool_analysis_corrected(data)

    with eval_tab2:
        render_cedis_analysis_corrected(data)

    with eval_tab3:
        render_external_factors_analysis_corrected(data)

    with eval_tab4:
        render_cost_analysis_corrected(data)

    with eval_tab5:
        render_winner_analysis_corrected(data)

    # NUEVA SECCIÓN: Tabla consolidada del ganador
    st.markdown("---")
    render_consolidated_winner_table(data)


def render_liverpool_analysis_corrected(data: dict):
    """Análisis Liverpool CORREGIDO con lógica correcta de tiendas"""
    st.markdown("### 🏪 Análisis Completo de Tiendas Liverpool")

    import pandas as pd

    stock_analysis = data.get('evaluacion_detallada', {}).get('stock_analysis', {})

    # 1. TIENDAS CON STOCK DISPONIBLE - DATOS REALES
    stock_encontrado = stock_analysis.get('stock_encontrado', [])
    if stock_encontrado:
        st.markdown("#### ✅ Tiendas Liverpool con Stock Disponible")

        stock_data = []
        for i, tienda in enumerate(stock_encontrado):
            # Determinar si es local o nacional
            es_local = tienda.get('es_local', False)
            categoria = "🏠 Local" if es_local else "🌍 Nacional"

            stock_data.append({
                '#': i + 1,
                'Tienda Liverpool': tienda.get('nombre_tienda', 'N/A'),
                'Categoría': categoria,
                'Stock Disponible': tienda.get('stock_disponible', 0),
                'Distancia (km)': f"{tienda.get('distancia_km', 0):.1f}",
                'Precio Unitario': f"${tienda.get('precio_tienda', 0):,.2f}",
                'Precio Total (3 und)': f"${tienda.get('precio_total', 0):,.2f}",
                'Tienda ID': tienda.get('tienda_id', 'N/A')
            })

        df_stock = pd.DataFrame(stock_data)
        st.dataframe(df_stock, use_container_width=True)

        # Métricas resumen REALES
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
            precio_unitario = stock_encontrado[0].get('precio_tienda', 0) if stock_encontrado else 0
            st.metric("💰 Precio Unitario", f"${precio_unitario:,.2f}")

    # 2. TIENDAS CERCANAS SIN STOCK - LÓGICA CORREGIDA
    tiendas_cercanas = stock_analysis.get('tiendas_cercanas', [])

    # Obtener IDs de tiendas que SÍ tienen stock
    tienda_ids_con_stock = {t.get('tienda_id') for t in stock_encontrado}

    # Filtrar tiendas cercanas que NO tienen stock
    tiendas_cercanas_sin_stock = [
        tienda for tienda in tiendas_cercanas
        if tienda.get('tienda_id') not in tienda_ids_con_stock
    ]

    if tiendas_cercanas_sin_stock:
        st.markdown("#### ❌ Tiendas Liverpool Cercanas (Sin Stock)")

        cercanas_data = []
        for i, tienda in enumerate(tiendas_cercanas_sin_stock):
            cercanas_data.append({
                '#': i + 1,
                'Tienda Liverpool': tienda.get('nombre', 'N/A'),
                'Distancia (km)': f"{tienda.get('distancia_km', 0):.1f}",
                'Estado': tienda.get('estado', 'N/A'),
                'Municipio': tienda.get('alcaldia_municipio', 'N/A'),
                'Zona Seguridad': tienda.get('zona_seguridad', 'N/A'),
                'Tienda ID': tienda.get('tienda_id', 'N/A'),
                'Razón Sin Stock': 'Inventario insuficiente para este SKU'
            })

        df_cercanas = pd.DataFrame(cercanas_data)
        st.dataframe(df_cercanas, use_container_width=True)
        st.metric("🏪 Liverpool Cercanas (Sin Stock)", len(cercanas_data))

    # 3. TIENDAS AUTORIZADAS NACIONALES - NUEVA SECCIÓN
    tiendas_autorizadas = stock_analysis.get('tiendas_autorizadas', [])

    if tiendas_autorizadas:
        st.markdown("#### 🌍 Tiendas Liverpool Autorizadas Nacionales")

        # Separar autorizadas con y sin stock
        autorizadas_con_stock = [
            tienda for tienda in tiendas_autorizadas
            if tienda.get('tienda_id') in tienda_ids_con_stock
        ]

        autorizadas_sin_stock = [
            tienda for tienda in tiendas_autorizadas
            if tienda.get('tienda_id') not in tienda_ids_con_stock
        ]

        if autorizadas_con_stock:
            st.markdown("##### ✅ Con Stock Disponible")

            auth_stock_data = []
            for i, tienda in enumerate(autorizadas_con_stock):
                # Buscar el stock real de esta tienda
                stock_info = next((s for s in stock_encontrado if s.get('tienda_id') == tienda.get('tienda_id')), {})

                auth_stock_data.append({
                    '#': i + 1,
                    'Tienda Liverpool': tienda.get('nombre', 'N/A'),
                    'Stock Disponible': stock_info.get('stock_disponible', 0),
                    'Distancia (km)': f"{tienda.get('distancia_km', 0):.1f}",
                    'Estado': tienda.get('estado', 'N/A'),
                    'Municipio': tienda.get('alcaldia_municipio', 'N/A'),
                    'Zona Seguridad': tienda.get('zona_seguridad', 'N/A'),
                    'Tienda ID': tienda.get('tienda_id', 'N/A')
                })

            df_auth_stock = pd.DataFrame(auth_stock_data)
            st.dataframe(df_auth_stock, use_container_width=True)

        if autorizadas_sin_stock:
            st.markdown("##### ❌ Sin Stock")

            auth_no_stock_data = []
            for i, tienda in enumerate(autorizadas_sin_stock[:5]):  # Mostrar solo las primeras 5
                auth_no_stock_data.append({
                    '#': i + 1,
                    'Tienda Liverpool': tienda.get('nombre', 'N/A'),
                    'Distancia (km)': f"{tienda.get('distancia_km', 0):.1f}",
                    'Estado': tienda.get('estado', 'N/A'),
                    'Zona Seguridad': tienda.get('zona_seguridad', 'N/A'),
                    'Razón Sin Stock': 'No disponible en inventario'
                })

            df_auth_no_stock = pd.DataFrame(auth_no_stock_data)
            st.dataframe(df_auth_no_stock, use_container_width=True)

    # 4. PLAN DE ASIGNACIÓN FINAL - DATOS REALES
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
                'Distancia (km)': f"{asign.get('distancia_km', 0):.1f}",
                'Tiempo Total (h)': f"{asign.get('tiempo_total_h', 0):.1f}",
                'Costo Total': f"${asign.get('costo_total_mxn', 0):,.2f}",
                'Score': f"{asign.get('score_total', 0):.3f}",
                'Flota': asign.get('fleet_type', 'N/A'),
                'Carrier': asign.get('carrier', 'N/A'),
                'Precio Producto': f"${asign.get('precio_total', 0):,.2f}",
                'Razón Selección': asign.get('razon_seleccion', 'N/A')
            })

        df_asignacion = pd.DataFrame(asignacion_data)
        st.dataframe(df_asignacion, use_container_width=True)

        # Totales de asignación REALES
        total_cantidad = sum(a.get('cantidad_asignada', 0) for a in plan_asignacion)
        total_costo = sum(a.get('costo_total_mxn', 0) for a in plan_asignacion)
        total_tiempo_prep = sum(a.get('tiempo_total_h', 0) for a in plan_asignacion)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📦 Total Asignado", total_cantidad)
        with col2:
            st.metric("💰 Costo Logístico", f"${total_costo:,.2f}")
        with col3:
            st.metric("⏱️ Tiempo Total", f"{total_tiempo_prep:.1f}h")


def render_cedis_analysis_corrected(data: dict):
    """Análisis CEDIS CORREGIDO con manejo seguro de None"""
    st.markdown("### 🏭 Análisis Completo de CEDIS")

    import pandas as pd

    # MANEJO SEGURO DE CEDIS
    cedis_analysis = data.get('evaluacion_detallada', {}).get('cedis_analysis')

    if not cedis_analysis or not isinstance(cedis_analysis, dict):
        st.info("ℹ️ Esta ruta no requiere CEDIS (entrega directa)")
        return

    # 1. CEDIS EVALUADOS - DATOS REALES
    cedis_evaluados = cedis_analysis.get('cedis_evaluados', [])
    if cedis_evaluados:
        st.markdown("#### 📊 CEDIS Evaluados")

        cedis_data = []
        for i, cedis in enumerate(cedis_evaluados):
            cedis_data.append({
                '#': i + 1,
                'CEDIS': cedis.get('nombre', 'N/A'),
                'Score': f"{cedis.get('score', 0):.2f}",
                'Cobertura Estados': cedis.get('cobertura_estados', 'N/A'),
                'Dist. Origen-CEDIS (km)': f"{cedis.get('distancia_origen_cedis_km', 0):.1f}",
                'Dist. CEDIS-Destino (km)': f"{cedis.get('distancia_cedis_destino_km', 0):.1f}",
                'Distancia Total (km)': f"{cedis.get('distancia_total_km', 0):.1f}",
                'Tiempo Proc. (h)': f"{cedis.get('tiempo_procesamiento_h', 0):.1f}",
                'Cobertura Específica': '✅ Sí' if cedis.get('cobertura_especifica', False) else '❌ No',
                'CEDIS ID': cedis.get('cedis_id', 'N/A')
            })

        df_cedis = pd.DataFrame(cedis_data)
        st.dataframe(df_cedis, use_container_width=True)

        # Métricas CEDIS REALES
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🏭 CEDIS Evaluados", len(cedis_evaluados))
        with col2:
            avg_score = sum(c.get('score', 0) for c in cedis_evaluados) / len(cedis_evaluados)
            st.metric("📊 Score Promedio", f"{avg_score:.2f}")
        with col3:
            avg_tiempo = sum(c.get('tiempo_procesamiento_h', 0) for c in cedis_evaluados) / len(cedis_evaluados)
            st.metric("⏱️ Tiempo Proc. Promedio", f"{avg_tiempo:.1f}h")

    # 2. CEDIS SELECCIONADO - DATOS REALES
    cedis_seleccionado = cedis_analysis.get('cedis_seleccionado', {})
    if cedis_seleccionado:
        st.markdown("#### 🏆 CEDIS Seleccionado")

        st.success(f"""
        **🏭 CEDIS Ganador:** {cedis_seleccionado.get('nombre', 'N/A')}

        **📊 Score Final:** {cedis_seleccionado.get('score', 0):.2f}

        **🎯 Razón de Selección:** {cedis_seleccionado.get('razon_seleccion', 'N/A')}

        **📏 Distancia Total:** {cedis_seleccionado.get('distancia_total_km', 0):.1f} km

        **⏱️ Tiempo de Procesamiento:** {cedis_seleccionado.get('tiempo_procesamiento_h', 0):.1f} horas

        **🌍 Cobertura Específica:** {'✅ Sí' if cedis_seleccionado.get('cobertura_especifica', False) else '❌ No'}

        **🆔 CEDIS ID:** {cedis_seleccionado.get('cedis_id', 'N/A')}
        """)

    # 3. CEDIS DESCARTADOS - DATOS REALES
    cedis_descartados = cedis_analysis.get('cedis_descartados', [])
    if cedis_descartados:
        st.markdown("#### ❌ CEDIS Descartados")

        descartados_data = []
        for i, cedis in enumerate(cedis_descartados[:10]):  # Top 10
            descartados_data.append({
                '#': i + 1,
                'CEDIS': cedis.get('nombre', 'N/A'),
                'Cobertura Estados': cedis.get('cobertura_estados', 'N/A'),
                'Cubre Destino': '✅ Sí' if cedis.get('cubre_destino', False) else '❌ No',
                'Razón Descarte': cedis.get('razon_descarte', 'N/A'),
                'CEDIS ID': cedis.get('cedis_id', 'N/A')
            })

        df_descartados = pd.DataFrame(descartados_data)
        st.dataframe(df_descartados, use_container_width=True)


def render_external_factors_analysis_corrected(data: dict):
    """Análisis factores externos CORREGIDO con datos reales"""
    st.markdown("### 🌍 Análisis Completo de Factores Externos")

    factores = data.get('factores_externos', {})
    request_data = data.get('request', {})

    # 1. INFORMACIÓN DEL PEDIDO
    st.markdown("#### 📋 Información del Pedido")
    col1, col2, col3 = st.columns(3)

    with col1:
        fecha_compra = request_data.get('fecha_compra', 'N/A')
        st.metric("📅 Fecha de Compra", fecha_compra.split('T')[0] if 'T' in fecha_compra else fecha_compra)

    with col2:
        evento = factores.get('evento_detectado', 'Normal')
        st.metric("🎉 Evento Detectado", evento)
        if evento != 'Normal':
            st.warning(f"🎄 Evento especial: {evento}")

    with col3:
        temporada_alta = factores.get('es_temporada_alta', False)
        st.metric("📈 Temporada Alta", '✅ Sí' if temporada_alta else '❌ No')

    # 2. FACTORES CLIMÁTICOS - DATOS REALES
    st.markdown("#### 🌤️ Condiciones Climáticas")
    col1, col2, col3 = st.columns(3)

    with col1:
        clima = factores.get('condicion_clima', 'N/A')
        st.metric("🌡️ Condición Climática", clima)

        if 'Frio' in clima:
            st.info("❄️ Condiciones de invierno - puede afectar tiempos")
        elif 'Lluvia' in clima:
            st.warning("🌧️ Condiciones lluviosas")
        else:
            st.success("☀️ Condiciones climáticas favorables")

    with col2:
        criticidad = factores.get('criticidad_logistica', 'N/A')
        st.metric("⚠️ Criticidad Logística", criticidad)

        if criticidad == 'Alta':
            st.error("🚨 Criticidad logística alta")
        elif criticidad == 'Media':
            st.warning("⚠️ Criticidad moderada")
        else:
            st.success("✅ Criticidad baja")

    with col3:
        fuente_datos = factores.get('fuente_datos', 'N/A')
        st.metric("📊 Fuente de Datos", fuente_datos)

    # 3. FACTORES DE TRÁFICO Y SEGURIDAD - DATOS REALES
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

    # 4. FACTORES DE DEMANDA - DATOS REALES
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
        rango_cp = factores.get('rango_cp_afectado', 'N/A')
        st.metric("📮 Rango CP Afectado", rango_cp)

    with col3:
        codigo_postal = request_data.get('codigo_postal', 'N/A')
        st.metric("📍 Código Postal Destino", codigo_postal)


def render_cost_analysis_corrected(data: dict):
    """Análisis de costos CORREGIDO con datos reales"""
    st.markdown("### 💰 Análisis Detallado de Costos")

    import pandas as pd

    # 1. DESGLOSE DE COSTOS PRINCIPALES - DATOS REALES
    resultado = data.get('resultado_final', {})
    logistica = data.get('logistica_entrega', {})

    st.markdown("#### 💳 Desglose de Costos")

    costo_total = resultado.get('costo_mxn', 0)
    desglose_costos = logistica.get('desglose_costos_mxn', {})

    # Si no hay desglose, calcular aproximado
    if not desglose_costos:
        # Obtener precio del producto
        stock_analysis = data.get('evaluacion_detallada', {}).get('stock_analysis', {})
        plan_asignacion = stock_analysis.get('asignacion_detallada', {}).get('plan_asignacion', [])

        precio_producto = 0
        if plan_asignacion:
            precio_producto = plan_asignacion[0].get('precio_total', 0)

        # Estimar desglose
        costo_logistico = costo_total - precio_producto
        desglose_costos = {
            'producto': precio_producto,
            'transporte': costo_logistico * 0.7,
            'preparacion': costo_logistico * 0.2,
            'contingencia': costo_logistico * 0.1
        }

    # Crear tabla de costos REAL
    costos_data = []

    for concepto, costo in desglose_costos.items():
        porcentaje = (costo / max(costo_total, 1)) * 100
        categoria_map = {
            'producto': 'Producto',
            'transporte': 'Logística',
            'preparacion': 'Operación',
            'contingencia': 'Buffer'
        }

        costos_data.append({
            'Concepto': concepto.title(),
            'Monto': f"${costo:,.2f}",
            'Porcentaje': f"{porcentaje:.1f}%",
            'Categoría': categoria_map.get(concepto, 'Otros')
        })

    df_costos = pd.DataFrame(costos_data)
    st.dataframe(df_costos, use_container_width=True)

    # 2. MÉTRICAS DE COSTO REALES
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("💰 Costo Total", f"${costo_total:,.2f}")

    with col2:
        distancia = logistica.get('distancia_km', 1)
        costo_por_km = costo_total / max(distancia, 1)
        st.metric("📏 Costo por KM", f"${costo_por_km:.2f}")

    with col3:
        tiempo = logistica.get('tiempo_total_h', 1)
        costo_por_hora = costo_total / max(tiempo, 1)
        st.metric("⏱️ Costo por Hora", f"${costo_por_hora:.2f}")

    with col4:
        cantidad = data.get('request', {}).get('cantidad', 1)
        costo_por_unidad = costo_total / max(cantidad, 1)
        st.metric("📦 Costo por Unidad", f"${costo_por_unidad:.2f}")


def render_winner_analysis_corrected(data: dict):
    """Análisis del ganador CORREGIDO con datos reales"""
    st.markdown("### 🏆 Análisis del Ganador Final")

    # Datos del ganador desde el response real
    ganador_evaluacion = data.get('evaluacion', {}).get('ganador', {})
    resultado_final = data.get('resultado_final', {})
    logistica = data.get('logistica_entrega', {})
    plan_asignacion = data.get('evaluacion_detallada', {}).get('stock_analysis', {}).get('asignacion_detallada',
                                                                                         {}).get('plan_asignacion', [])

    if not ganador_evaluacion and not plan_asignacion:
        st.warning("⚠️ No se encontró información del ganador")
        return

    # 1. INFORMACIÓN DEL GANADOR REAL
    st.markdown("#### 🥇 Tienda/Ruta Ganadora")

    if plan_asignacion:
        ganador_real = plan_asignacion[0]  # El primer elemento del plan es el ganador

        col1, col2 = st.columns([1, 1])

        with col1:
            st.success(f"""
            **🏪 Tienda Seleccionada:** {ganador_real.get('nombre_tienda', 'N/A')}

            **📊 Score Final:** {ganador_real.get('score_total', 0):.3f}

            **💰 Costo Logístico:** ${ganador_real.get('costo_total_mxn', 0):,.2f}

            **💳 Costo Producto:** ${ganador_real.get('precio_total', 0):,.2f}

            **📏 Distancia:** {ganador_real.get('distancia_km', 0):.1f} km

            **⏱️ Tiempo Total:** {ganador_real.get('tiempo_total_h', 0):.1f} horas

            **🚚 Flota:** {ganador_real.get('fleet_type', 'N/A')}

            **📦 Carrier:** {ganador_real.get('carrier', 'N/A')}
            """)

        with col2:
            # Razón de selección REAL
            razon_seleccion = ganador_real.get('razon_seleccion', 'N/A')
            st.markdown("**🎯 Razón de Selección:**")
            st.info(razon_seleccion)

            # Datos adicionales del CSV
            datos_csv = ganador_evaluacion.get('datos_csv', {})
            if datos_csv:
                st.markdown("**📊 Datos del Sistema:**")
                st.markdown(f"🛡️ **Zona Seguridad:** {datos_csv.get('zona_seguridad', 'N/A')}")
                st.markdown(f"🏭 **CEDIS:** {datos_csv.get('cedis_asignado', 'N/A')}")
                st.markdown(f"🚚 **Carrier:** {datos_csv.get('carrier_seleccionado', 'N/A')}")

    # 2. DETALLES DE LA RUTA FINAL
    st.markdown("#### 🗺️ Detalles de la Ruta Final")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**🛣️ Información de Ruta**")
        tipo_ruta = logistica.get('tipo_ruta', 'N/A')
        ruta_descripcion = logistica.get('ruta', 'N/A')

        st.info(f"""
        **Tipo:** {tipo_ruta}

        **Descripción:** {ruta_descripcion}

        **Distancia Total:** {logistica.get('distancia_km', 0):.1f} km

        **CEDIS Intermedio:** {logistica.get('cedis_intermedio', 'No aplica')}
        """)

    with col2:
        st.markdown("**⏰ Desglose de Tiempos**")
        desglose_tiempos = logistica.get('desglose_tiempos_h', {})

        tiempo_prep = desglose_tiempos.get('preparacion', 0)
        tiempo_viaje = desglose_tiempos.get('viaje', 0)
        tiempo_factores = desglose_tiempos.get('factores_externos', 0)
        tiempo_contingencia = desglose_tiempos.get('contingencia', 0)

        st.info(f"""
        **Preparación:** {tiempo_prep:.1f}h

        **Viaje:** {tiempo_viaje:.1f}h

        **Factores Externos:** {tiempo_factores:.1f}h

        **Contingencia:** {tiempo_contingencia:.1f}h
        """)

    with col3:
        st.markdown("**📈 Métricas de Éxito**")
        probabilidad_exito = resultado_final.get('probabilidad_exito', 0)
        confianza = resultado_final.get('confianza_prediccion', 0)
        fecha_entrega = resultado_final.get('fecha_entrega_estimada', 'N/A')

        st.info(f"""
        **Prob. Éxito:** {probabilidad_exito:.1%}

        **Confianza:** {confianza:.1%}

        **Fecha Entrega:** {fecha_entrega.split('T')[0] if 'T' in str(fecha_entrega) else fecha_entrega}

        **Tipo Entrega:** {resultado_final.get('tipo_entrega', 'N/A')}
        """)


def render_consolidated_winner_table(data: dict):
    """Tabla consolidada del ganador con manejo seguro de CEDIS None"""
    st.markdown("## 🎯 Resumen Ejecutivo - Decisión Final")

    import pandas as pd

    # Extraer todos los datos relevantes
    ganador_evaluacion = data.get('evaluacion', {}).get('ganador', {})
    resultado_final = data.get('resultado_final', {})
    logistica = data.get('logistica_entrega', {})
    factores = data.get('factores_externos', {})
    request_data = data.get('request', {})
    plan_asignacion = data.get('evaluacion_detallada', {}).get('stock_analysis', {}).get('asignacion_detallada',
                                                                                         {}).get('plan_asignacion', [])

    # MANEJO SEGURO DE CEDIS - puede ser None
    cedis_analysis = data.get('evaluacion_detallada', {}).get('cedis_analysis')
    cedis_seleccionado = {}
    if cedis_analysis and isinstance(cedis_analysis, dict):
        cedis_seleccionado = cedis_analysis.get('cedis_seleccionado', {})

    if not plan_asignacion:
        st.warning("⚠️ No hay datos de asignación disponibles")
        return

    ganador_real = plan_asignacion[0]

    # Crear tabla consolidada
    consolidated_data = [
        # Información básica del pedido
        {"Categoría": "📋 PEDIDO", "Campo": "SKU", "Valor": request_data.get('sku_id', 'N/A')},
        {"Categoría": "📋 PEDIDO", "Campo": "Cantidad", "Valor": f"{request_data.get('cantidad', 0)} unidades"},
        {"Categoría": "📋 PEDIDO", "Campo": "Código Postal Destino", "Valor": request_data.get('codigo_postal', 'N/A')},
        {"Categoría": "📋 PEDIDO", "Campo": "Fecha Compra",
         "Valor": request_data.get('fecha_compra', 'N/A').split('T')[0] if 'T' in str(
             request_data.get('fecha_compra', '')) else request_data.get('fecha_compra', 'N/A')},

        # Información del ganador
        {"Categoría": "🏆 GANADOR", "Campo": "Tienda Seleccionada", "Valor": ganador_real.get('nombre_tienda', 'N/A')},
        {"Categoría": "🏆 GANADOR", "Campo": "Score Final", "Valor": f"{ganador_real.get('score_total', 0):.3f}"},
        {"Categoría": "🏆 GANADOR", "Campo": "Distancia", "Valor": f"{ganador_real.get('distancia_km', 0):.1f} km"},
        {"Categoría": "🏆 GANADOR", "Campo": "Stock Disponible",
         "Valor": f"{ganador_real.get('stock_disponible', 0)} unidades"},
        {"Categoría": "🏆 GANADOR", "Campo": "Razón Selección", "Valor": ganador_real.get('razon_seleccion', 'N/A')},

        # Información logística
        {"Categoría": "🚚 LOGÍSTICA", "Campo": "Tipo de Ruta", "Valor": logistica.get('tipo_ruta', 'N/A')},
        {"Categoría": "🚚 LOGÍSTICA", "Campo": "Flota", "Valor": ganador_real.get('fleet_type', 'N/A')},
        {"Categoría": "🚚 LOGÍSTICA", "Campo": "Carrier", "Valor": ganador_real.get('carrier', 'N/A')},
        {"Categoría": "🚚 LOGÍSTICA", "Campo": "Tiempo Total",
         "Valor": f"{ganador_real.get('tiempo_total_h', 0):.1f} horas"},

        # Información de CEDIS (MANEJO SEGURO)
        {"Categoría": "🏭 CEDIS", "Campo": "CEDIS Intermedio", "Valor": logistica.get('cedis_intermedio', 'No aplica')},
        {"Categoría": "🏭 CEDIS", "Campo": "Score CEDIS",
         "Valor": f"{cedis_seleccionado.get('score', 0):.2f}" if cedis_seleccionado else "N/A"},
        {"Categoría": "🏭 CEDIS", "Campo": "Tiempo Procesamiento",
         "Valor": f"{cedis_seleccionado.get('tiempo_procesamiento_h', 0):.1f}h" if cedis_seleccionado else "N/A"},

        # Costos
        {"Categoría": "💰 COSTOS", "Campo": "Costo Producto", "Valor": f"${ganador_real.get('precio_total', 0):,.2f}"},
        {"Categoría": "💰 COSTOS", "Campo": "Costo Logístico",
         "Valor": f"${ganador_real.get('costo_total_mxn', 0):,.2f}"},
        {"Categoría": "💰 COSTOS", "Campo": "Costo Total Final",
         "Valor": f"${resultado_final.get('costo_mxn', 0):,.2f}"},

        # Factores externos
        {"Categoría": "🌍 FACTORES", "Campo": "Evento Detectado", "Valor": factores.get('evento_detectado', 'Normal')},
        {"Categoría": "🌍 FACTORES", "Campo": "Factor Demanda", "Valor": f"{factores.get('factor_demanda', 1.0):.2f}x"},
        {"Categoría": "🌍 FACTORES", "Campo": "Zona Seguridad", "Valor": factores.get('zona_seguridad', 'N/A')},
        {"Categoría": "🌍 FACTORES", "Campo": "Clima", "Valor": factores.get('condicion_clima', 'N/A')},
        {"Categoría": "🌍 FACTORES", "Campo": "Tiempo Extra",
         "Valor": f"{factores.get('impacto_tiempo_extra_horas', 0):.1f}h"},

        # Resultado final
        {"Categoría": "📈 RESULTADO", "Campo": "Probabilidad Éxito",
         "Valor": f"{resultado_final.get('probabilidad_exito', 0):.1%}"},
        {"Categoría": "📈 RESULTADO", "Campo": "Confianza Predicción",
         "Valor": f"{resultado_final.get('confianza_prediccion', 0):.1%}"},
        {"Categoría": "📈 RESULTADO", "Campo": "Fecha Entrega",
         "Valor": resultado_final.get('fecha_entrega_estimada', 'N/A').split('T')[0] if 'T' in str(
             resultado_final.get('fecha_entrega_estimada', '')) else resultado_final.get('fecha_entrega_estimada',
                                                                                         'N/A')},
        {"Categoría": "📈 RESULTADO", "Campo": "Ventana Entrega",
         "Valor": f"{resultado_final.get('ventana_entrega', {}).get('inicio', 'N/A')} - {resultado_final.get('ventana_entrega', {}).get('fin', 'N/A')}"},
        {"Categoría": "📈 RESULTADO", "Campo": "Tipo Entrega", "Valor": resultado_final.get('tipo_entrega', 'N/A')}
    ]

    # Mostrar tabla consolidada
    df_consolidated = pd.DataFrame(consolidated_data)
    st.dataframe(df_consolidated, use_container_width=True, height=800)

    # Métricas finales en tarjetas
    st.markdown("### 📊 Métricas Clave de la Decisión")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "🏆 Score Ganador",
            f"{ganador_real.get('score_total', 0):.3f}",
            help="Score final de optimización tiempo-costo-stock"
        )

    with col2:
        st.metric(
            "💰 Costo Total",
            f"${resultado_final.get('costo_mxn', 0):,.0f}",
            help="Costo total incluyendo producto y logística"
        )

    with col3:
        st.metric(
            "⏱️ Tiempo Total",
            f"{ganador_real.get('tiempo_total_h', 0):.1f}h",
            help="Tiempo total estimado de entrega"
        )

    with col4:
        st.metric(
            "📈 Prob. Éxito",
            f"{resultado_final.get('probabilidad_exito', 0):.0%}",
            help="Probabilidad de cumplir con la entrega"
        )

    with col5:
        st.metric(
            "📏 Distancia",
            f"{ganador_real.get('distancia_km', 0):.0f} km",
            help="Distancia total de la ruta"
        )

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


def render_liverpool_analysis_corrected(data: dict):
    """Análisis Liverpool CORREGIDO con lógica correcta de tiendas"""
    st.markdown("### 🏪 Análisis Completo de Tiendas Liverpool")

    import pandas as pd

    stock_analysis = data.get('evaluacion_detallada', {}).get('stock_analysis', {})

    # 1. TIENDAS CON STOCK DISPONIBLE - DATOS REALES
    stock_encontrado = stock_analysis.get('stock_encontrado', [])
    if stock_encontrado:
        st.markdown("#### ✅ Tiendas Liverpool con Stock Disponible")

        stock_data = []
        for i, tienda in enumerate(stock_encontrado):
            # Determinar si es local o nacional
            es_local = tienda.get('es_local', False)
            categoria = "🏠 Local" if es_local else "🌍 Nacional"

            stock_data.append({
                '#': i + 1,
                'Tienda Liverpool': tienda.get('nombre_tienda', 'N/A'),
                'Categoría': categoria,
                'Stock Disponible': tienda.get('stock_disponible', 0),
                'Distancia (km)': f"{tienda.get('distancia_km', 0):.1f}",
                'Precio Unitario': f"${tienda.get('precio_tienda', 0):,.2f}",
                'Precio Total (3 und)': f"${tienda.get('precio_total', 0):,.2f}",
                'Tienda ID': tienda.get('tienda_id', 'N/A')
            })

        df_stock = pd.DataFrame(stock_data)
        st.dataframe(df_stock, use_container_width=True)

        # Métricas resumen REALES
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
            precio_unitario = stock_encontrado[0].get('precio_tienda', 0) if stock_encontrado else 0
            st.metric("💰 Precio Unitario", f"${precio_unitario:,.2f}")

    # 2. TIENDAS CERCANAS SIN STOCK - LÓGICA CORREGIDA
    tiendas_cercanas = stock_analysis.get('tiendas_cercanas', [])

    # Obtener IDs de tiendas que SÍ tienen stock
    tienda_ids_con_stock = {t.get('tienda_id') for t in stock_encontrado}

    # Filtrar tiendas cercanas que NO tienen stock
    tiendas_cercanas_sin_stock = [
        tienda for tienda in tiendas_cercanas
        if tienda.get('tienda_id') not in tienda_ids_con_stock
    ]

    if tiendas_cercanas_sin_stock:
        st.markdown("#### ❌ Tiendas Liverpool Cercanas (Sin Stock)")

        cercanas_data = []
        for i, tienda in enumerate(tiendas_cercanas_sin_stock):
            cercanas_data.append({
                '#': i + 1,
                'Tienda Liverpool': tienda.get('nombre', 'N/A'),
                'Distancia (km)': f"{tienda.get('distancia_km', 0):.1f}",
                'Estado': tienda.get('estado', 'N/A'),
                'Municipio': tienda.get('alcaldia_municipio', 'N/A'),
                'Zona Seguridad': tienda.get('zona_seguridad', 'N/A'),
                'Tienda ID': tienda.get('tienda_id', 'N/A'),
                'Razón Sin Stock': 'Inventario insuficiente para este SKU'
            })

        df_cercanas = pd.DataFrame(cercanas_data)
        st.dataframe(df_cercanas, use_container_width=True)
        st.metric("🏪 Liverpool Cercanas (Sin Stock)", len(cercanas_data))

    # 3. TIENDAS AUTORIZADAS NACIONALES - NUEVA SECCIÓN
    tiendas_autorizadas = stock_analysis.get('tiendas_autorizadas', [])

    if tiendas_autorizadas:
        st.markdown("#### 🌍 Tiendas Liverpool Autorizadas Nacionales")

        # Separar autorizadas con y sin stock
        autorizadas_con_stock = [
            tienda for tienda in tiendas_autorizadas
            if tienda.get('tienda_id') in tienda_ids_con_stock
        ]

        autorizadas_sin_stock = [
            tienda for tienda in tiendas_autorizadas
            if tienda.get('tienda_id') not in tienda_ids_con_stock
        ]

        if autorizadas_con_stock:
            st.markdown("##### ✅ Con Stock Disponible")

            auth_stock_data = []
            for i, tienda in enumerate(autorizadas_con_stock):
                # Buscar el stock real de esta tienda
                stock_info = next((s for s in stock_encontrado if s.get('tienda_id') == tienda.get('tienda_id')), {})

                auth_stock_data.append({
                    '#': i + 1,
                    'Tienda Liverpool': tienda.get('nombre', 'N/A'),
                    'Stock Disponible': stock_info.get('stock_disponible', 0),
                    'Distancia (km)': f"{tienda.get('distancia_km', 0):.1f}",
                    'Estado': tienda.get('estado', 'N/A'),
                    'Municipio': tienda.get('alcaldia_municipio', 'N/A'),
                    'Zona Seguridad': tienda.get('zona_seguridad', 'N/A'),
                    'Tienda ID': tienda.get('tienda_id', 'N/A')
                })

            df_auth_stock = pd.DataFrame(auth_stock_data)
            st.dataframe(df_auth_stock, use_container_width=True)

        if autorizadas_sin_stock:
            st.markdown("##### ❌ Sin Stock")

            auth_no_stock_data = []
            for i, tienda in enumerate(autorizadas_sin_stock[:5]):  # Mostrar solo las primeras 5
                auth_no_stock_data.append({
                    '#': i + 1,
                    'Tienda Liverpool': tienda.get('nombre', 'N/A'),
                    'Distancia (km)': f"{tienda.get('distancia_km', 0):.1f}",
                    'Estado': tienda.get('estado', 'N/A'),
                    'Zona Seguridad': tienda.get('zona_seguridad', 'N/A'),
                    'Razón Sin Stock': 'No disponible en inventario'
                })

            df_auth_no_stock = pd.DataFrame(auth_no_stock_data)
            st.dataframe(df_auth_no_stock, use_container_width=True)

    # 4. PLAN DE ASIGNACIÓN FINAL - DATOS REALES (sin cambios)
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
                'Distancia (km)': f"{asign.get('distancia_km', 0):.1f}",
                'Tiempo Total (h)': f"{asign.get('tiempo_total_h', 0):.1f}",
                'Costo Total': f"${asign.get('costo_total_mxn', 0):,.2f}",
                'Score': f"{asign.get('score_total', 0):.3f}",
                'Flota': asign.get('fleet_type', 'N/A'),
                'Carrier': asign.get('carrier', 'N/A'),
                'Precio Producto': f"${asign.get('precio_total', 0):,.2f}",
                'Razón Selección': asign.get('razon_seleccion', 'N/A')
            })

        df_asignacion = pd.DataFrame(asignacion_data)
        st.dataframe(df_asignacion, use_container_width=True)

        # Totales de asignación REALES
        total_cantidad = sum(a.get('cantidad_asignada', 0) for a in plan_asignacion)
        total_costo = sum(a.get('costo_total_mxn', 0) for a in plan_asignacion)
        total_tiempo_prep = sum(a.get('tiempo_total_h', 0) for a in plan_asignacion)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📦 Total Asignado", total_cantidad)
        with col2:
            st.metric("💰 Costo Logístico", f"${total_costo:,.2f}")
        with col3:
            st.metric("⏱️ Tiempo Total", f"{total_tiempo_prep:.1f}h")


def render_cedis_analysis_corrected(data: dict):
    """Análisis CEDIS CORREGIDO con manejo seguro de None"""
    st.markdown("### 🏭 Análisis Completo de CEDIS")

    import pandas as pd

    # MANEJO SEGURO DE CEDIS
    cedis_analysis = data.get('evaluacion_detallada', {}).get('cedis_analysis')

    if not cedis_analysis or not isinstance(cedis_analysis, dict):
        st.info("ℹ️ Esta ruta no requiere CEDIS (entrega directa)")
        return

    # 1. CEDIS EVALUADOS - DATOS REALES
    cedis_evaluados = cedis_analysis.get('cedis_evaluados', [])
    if cedis_evaluados:
        st.markdown("#### 📊 CEDIS Evaluados")

        cedis_data = []
        for i, cedis in enumerate(cedis_evaluados):
            cedis_data.append({
                '#': i + 1,
                'CEDIS': cedis.get('nombre', 'N/A'),
                'Score': f"{cedis.get('score', 0):.2f}",
                'Cobertura Estados': cedis.get('cobertura_estados', 'N/A'),
                'Dist. Origen-CEDIS (km)': f"{cedis.get('distancia_origen_cedis_km', 0):.1f}",
                'Dist. CEDIS-Destino (km)': f"{cedis.get('distancia_cedis_destino_km', 0):.1f}",
                'Distancia Total (km)': f"{cedis.get('distancia_total_km', 0):.1f}",
                'Tiempo Proc. (h)': f"{cedis.get('tiempo_procesamiento_h', 0):.1f}",
                'Cobertura Específica': '✅ Sí' if cedis.get('cobertura_especifica', False) else '❌ No',
                'CEDIS ID': cedis.get('cedis_id', 'N/A')
            })

        df_cedis = pd.DataFrame(cedis_data)
        st.dataframe(df_cedis, use_container_width=True)

        # Métricas CEDIS REALES
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🏭 CEDIS Evaluados", len(cedis_evaluados))
        with col2:
            avg_score = sum(c.get('score', 0) for c in cedis_evaluados) / len(cedis_evaluados)
            st.metric("📊 Score Promedio", f"{avg_score:.2f}")
        with col3:
            avg_tiempo = sum(c.get('tiempo_procesamiento_h', 0) for c in cedis_evaluados) / len(cedis_evaluados)
            st.metric("⏱️ Tiempo Proc. Promedio", f"{avg_tiempo:.1f}h")

    # 2. CEDIS SELECCIONADO - DATOS REALES
    cedis_seleccionado = cedis_analysis.get('cedis_seleccionado', {})
    if cedis_seleccionado:
        st.markdown("#### 🏆 CEDIS Seleccionado")

        st.success(f"""
        **🏭 CEDIS Ganador:** {cedis_seleccionado.get('nombre', 'N/A')}

        **📊 Score Final:** {cedis_seleccionado.get('score', 0):.2f}

        **🎯 Razón de Selección:** {cedis_seleccionado.get('razon_seleccion', 'N/A')}

        **📏 Distancia Total:** {cedis_seleccionado.get('distancia_total_km', 0):.1f} km

        **⏱️ Tiempo de Procesamiento:** {cedis_seleccionado.get('tiempo_procesamiento_h', 0):.1f} horas

        **🌍 Cobertura Específica:** {'✅ Sí' if cedis_seleccionado.get('cobertura_especifica', False) else '❌ No'}

        **🆔 CEDIS ID:** {cedis_seleccionado.get('cedis_id', 'N/A')}
        """)

    # 3. CEDIS DESCARTADOS - DATOS REALES
    cedis_descartados = cedis_analysis.get('cedis_descartados', [])
    if cedis_descartados:
        st.markdown("#### ❌ CEDIS Descartados")

        descartados_data = []
        for i, cedis in enumerate(cedis_descartados[:10]):  # Top 10
            descartados_data.append({
                '#': i + 1,
                'CEDIS': cedis.get('nombre', 'N/A'),
                'Cobertura Estados': cedis.get('cobertura_estados', 'N/A'),
                'Cubre Destino': '✅ Sí' if cedis.get('cubre_destino', False) else '❌ No',
                'Razón Descarte': cedis.get('razon_descarte', 'N/A'),
                'CEDIS ID': cedis.get('cedis_id', 'N/A')
            })

        df_descartados = pd.DataFrame(descartados_data)
        st.dataframe(df_descartados, use_container_width=True)


def _create_logistics_route_from_response_with_distances(logistica: dict, cedis_analysis, stock_nodes: list,
                                                         destination_node_name: str):
    """Crear ruta logística CON DISTANCIAS en los enlaces - para charts.py"""
    nodes = []
    links = []

    if not stock_nodes:
        return nodes, links

    try:
        current_node = stock_nodes[0]['name']
        tipo_ruta = logistica.get('tipo_ruta', '')
        carrier = logistica.get('carrier', 'N/A')
        flota = logistica.get('flota', 'N/A')
        distancia_total = logistica.get('distancia_km', 0)

        # CASO 1: RUTA VÍA CEDIS
        if 'cedis' in tipo_ruta.lower() and cedis_analysis and isinstance(cedis_analysis, dict):
            cedis_seleccionado = cedis_analysis.get('cedis_seleccionado', {})

            if cedis_seleccionado:
                cedis_nombre = cedis_seleccionado.get('nombre', 'CEDIS')
                dist_origen_cedis = cedis_seleccionado.get('distancia_origen_cedis_km', 0)
                dist_cedis_destino = cedis_seleccionado.get('distancia_cedis_destino_km', 0)

                # Crear nodo CEDIS
                cedis_node = {
                    "name": f"🏭 {cedis_nombre}",
                    "value": 80,
                    "symbolSize": 85,
                    "category": 4,
                    "itemStyle": {
                        "color": "#6366f1",
                        "borderWidth": 4,
                        "borderColor": "#ffffff"
                    },
                    "label": {"show": True, "fontSize": 12, "fontWeight": "bold"},
                    "tooltip": f"🏭 CENTRO DE DISTRIBUCIÓN\\nNombre: {cedis_nombre}\\nScore: {cedis_seleccionado.get('score', 0):.2f}"
                }
                nodes.append(cedis_node)

                # Enlace tienda → CEDIS CON DISTANCIA
                links.append({
                    "source": current_node,
                    "target": f"🏭 {cedis_nombre}",
                    "lineStyle": {"color": "#6366f1", "width": 6},
                    "label": {"show": True, "formatter": f"📦 {dist_origen_cedis:.0f}km", "fontSize": 11}
                })

                current_node = f"🏭 {cedis_nombre}"
                distancia_restante = dist_cedis_destino
        else:
            # Ruta directa
            distancia_restante = distancia_total

        # CASO 2: CREAR NODO DE FLOTA/CARRIER
        flota_icon = "🚚" if 'FI' in flota else "🚛"
        flota_color = "#3b82f6" if 'FI' in flota else "#8b5cf6"
        flota_category = 5 if 'FI' in flota else 6

        flota_node = {
            "name": f"{flota_icon} {carrier}",
            "value": 90,
            "symbolSize": 80,
            "category": flota_category,
            "itemStyle": {
                "color": flota_color,
                "borderWidth": 4,
                "borderColor": "#ffffff"
            },
            "label": {"show": True, "fontSize": 12, "fontWeight": "bold"},
            "tooltip": f"{flota_icon} FLOTA\\nCarrier: {carrier}\\nTipo: {flota}\\nTiempo: {logistica.get('tiempo_total_h', 0):.1f}h"
        }
        nodes.append(flota_node)

        # Enlaces finales CON DISTANCIAS
        links.append({
            "source": current_node,
            "target": f"{flota_icon} {carrier}",
            "lineStyle": {"color": flota_color, "width": 7},
            "label": {"show": True, "formatter": "🚚 Recogida", "fontSize": 10}
        })

        links.append({
            "source": f"{flota_icon} {carrier}",
            "target": destination_node_name,
            "lineStyle": {
                "color": "#1e40af",
                "width": 10,
                "shadowBlur": 15,
                "shadowColor": "rgba(30, 64, 175, 0.4)"
            },
            "label": {
                "show": True,
                "formatter": f"🎯 {distancia_restante:.0f}km",
                "fontSize": 13,
                "fontWeight": "bold",
                "color": "#1e40af"
            }
        })

    except Exception as e:
        st.error(f"Error creando ruta logística: {str(e)}")

    return nodes, links


def render_external_factors_analysis_corrected(data: dict):
    """Análisis factores externos CORREGIDO con datos reales"""
    st.markdown("### 🌍 Análisis Completo de Factores Externos")

    factores = data.get('factores_externos', {})
    request_data = data.get('request', {})

    # 1. INFORMACIÓN DEL PEDIDO
    st.markdown("#### 📋 Información del Pedido")
    col1, col2, col3 = st.columns(3)

    with col1:
        fecha_compra = request_data.get('fecha_compra', 'N/A')
        st.metric("📅 Fecha de Compra", fecha_compra.split('T')[0] if 'T' in fecha_compra else fecha_compra)

    with col2:
        evento = factores.get('evento_detectado', 'Normal')
        st.metric("🎉 Evento Detectado", evento)
        if evento != 'Normal':
            st.warning(f"🎄 Evento especial: {evento}")

    with col3:
        temporada_alta = factores.get('es_temporada_alta', False)
        st.metric("📈 Temporada Alta", '✅ Sí' if temporada_alta else '❌ No')

    # 2. FACTORES CLIMÁTICOS - DATOS REALES
    st.markdown("#### 🌤️ Condiciones Climáticas")
    col1, col2, col3 = st.columns(3)

    with col1:
        clima = factores.get('condicion_clima', 'N/A')
        st.metric("🌡️ Condición Climática", clima)

        if 'Frio' in clima:
            st.info("❄️ Condiciones de invierno - puede afectar tiempos")
        elif 'Lluvia' in clima:
            st.warning("🌧️ Condiciones lluviosas")
        else:
            st.success("☀️ Condiciones climáticas favorables")

    with col2:
        criticidad = factores.get('criticidad_logistica', 'N/A')
        st.metric("⚠️ Criticidad Logística", criticidad)

        if criticidad == 'Alta':
            st.error("🚨 Criticidad logística alta")
        elif criticidad == 'Media':
            st.warning("⚠️ Criticidad moderada")
        else:
            st.success("✅ Criticidad baja")

    with col3:
        fuente_datos = factores.get('fuente_datos', 'N/A')
        st.metric("📊 Fuente de Datos", fuente_datos)

    # 3. FACTORES DE TRÁFICO Y SEGURIDAD - DATOS REALES
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

    # 4. FACTORES DE DEMANDA - DATOS REALES
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
        rango_cp = factores.get('rango_cp_afectado', 'N/A')
        st.metric("📮 Rango CP Afectado", rango_cp)

    with col3:
        codigo_postal = request_data.get('codigo_postal', 'N/A')
        st.metric("📍 Código Postal Destino", codigo_postal)


def render_cost_analysis_corrected(data: dict):
    """Análisis de costos CORREGIDO con datos reales"""
    st.markdown("### 💰 Análisis Detallado de Costos")

    import pandas as pd

    # 1. DESGLOSE DE COSTOS PRINCIPALES - DATOS REALES
    resultado = data.get('resultado_final', {})
    logistica = data.get('logistica_entrega', {})

    st.markdown("#### 💳 Desglose de Costos")

    costo_total = resultado.get('costo_mxn', 0)
    desglose_costos = logistica.get('desglose_costos_mxn', {})

    # Si no hay desglose, calcular aproximado
    if not desglose_costos:
        # Obtener precio del producto
        stock_analysis = data.get('evaluacion_detallada', {}).get('stock_analysis', {})
        plan_asignacion = stock_analysis.get('asignacion_detallada', {}).get('plan_asignacion', [])

        precio_producto = 0
        if plan_asignacion:
            precio_producto = plan_asignacion[0].get('precio_total', 0)

        # Estimar desglose
        costo_logistico = costo_total - precio_producto
        desglose_costos = {
            'producto': precio_producto,
            'transporte': costo_logistico * 0.7,
            'preparacion': costo_logistico * 0.2,
            'contingencia': costo_logistico * 0.1
        }

    # Crear tabla de costos REAL
    costos_data = []

    for concepto, costo in desglose_costos.items():
        porcentaje = (costo / max(costo_total, 1)) * 100
        categoria_map = {
            'producto': 'Producto',
            'transporte': 'Logística',
            'preparacion': 'Operación',
            'contingencia': 'Buffer'
        }

        costos_data.append({
            'Concepto': concepto.title(),
            'Monto': f"${costo:,.2f}",
            'Porcentaje': f"{porcentaje:.1f}%",
            'Categoría': categoria_map.get(concepto, 'Otros')
        })

    df_costos = pd.DataFrame(costos_data)
    st.dataframe(df_costos, use_container_width=True)

    # 2. MÉTRICAS DE COSTO REALES
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("💰 Costo Total", f"${costo_total:,.2f}")

    with col2:
        distancia = logistica.get('distancia_km', 1)
        costo_por_km = costo_total / max(distancia, 1)
        st.metric("📏 Costo por KM", f"${costo_por_km:.2f}")

    with col3:
        tiempo = logistica.get('tiempo_total_h', 1)
        costo_por_hora = costo_total / max(tiempo, 1)
        st.metric("⏱️ Costo por Hora", f"${costo_por_hora:.2f}")

    with col4:
        cantidad = data.get('request', {}).get('cantidad', 1)
        costo_por_unidad = costo_total / max(cantidad, 1)
        st.metric("📦 Costo por Unidad", f"${costo_por_unidad:.2f}")


def render_winner_analysis_corrected(data: dict):
    """Análisis del ganador CORREGIDO con datos reales"""
    st.markdown("### 🏆 Análisis del Ganador Final")

    # Datos del ganador desde el response real
    ganador_evaluacion = data.get('evaluacion', {}).get('ganador', {})
    resultado_final = data.get('resultado_final', {})
    logistica = data.get('logistica_entrega', {})
    plan_asignacion = data.get('evaluacion_detallada', {}).get('stock_analysis', {}).get('asignacion_detallada',
                                                                                         {}).get('plan_asignacion', [])

    if not ganador_evaluacion and not plan_asignacion:
        st.warning("⚠️ No se encontró información del ganador")
        return

    # 1. INFORMACIÓN DEL GANADOR REAL
    st.markdown("#### 🥇 Tienda/Ruta Ganadora")

    if plan_asignacion:
        ganador_real = plan_asignacion[0]  # El primer elemento del plan es el ganador

        col1, col2 = st.columns([1, 1])

        with col1:
            st.success(f"""
            **🏪 Tienda Seleccionada:** {ganador_real.get('nombre_tienda', 'N/A')}

            **📊 Score Final:** {ganador_real.get('score_total', 0):.3f}

            **💰 Costo Logístico:** ${ganador_real.get('costo_total_mxn', 0):,.2f}

            **💳 Costo Producto:** ${ganador_real.get('precio_total', 0):,.2f}

            **📏 Distancia:** {ganador_real.get('distancia_km', 0):.1f} km

            **⏱️ Tiempo Total:** {ganador_real.get('tiempo_total_h', 0):.1f} horas

            **🚚 Flota:** {ganador_real.get('fleet_type', 'N/A')}

            **📦 Carrier:** {ganador_real.get('carrier', 'N/A')}
            """)

        with col2:
            # Razón de selección REAL
            razon_seleccion = ganador_real.get('razon_seleccion', 'N/A')
            st.markdown("**🎯 Razón de Selección:**")
            st.info(razon_seleccion)

            # Datos adicionales del CSV
            datos_csv = ganador_evaluacion.get('datos_csv', {})
            if datos_csv:
                st.markdown("**📊 Datos del Sistema:**")
                st.markdown(f"🛡️ **Zona Seguridad:** {datos_csv.get('zona_seguridad', 'N/A')}")
                st.markdown(f"🏭 **CEDIS:** {datos_csv.get('cedis_asignado', 'N/A')}")
                st.markdown(f"🚚 **Carrier:** {datos_csv.get('carrier_seleccionado', 'N/A')}")

    # 2. DETALLES DE LA RUTA FINAL
    st.markdown("#### 🗺️ Detalles de la Ruta Final")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**🛣️ Información de Ruta**")
        tipo_ruta = logistica.get('tipo_ruta', 'N/A')
        ruta_descripcion = logistica.get('ruta', 'N/A')

        st.info(f"""
        **Tipo:** {tipo_ruta}

        **Descripción:** {ruta_descripcion}

        **Distancia Total:** {logistica.get('distancia_km', 0):.1f} km

        **CEDIS Intermedio:** {logistica.get('cedis_intermedio', 'No aplica')}
        """)

    with col2:
        st.markdown("**⏰ Desglose de Tiempos**")
        desglose_tiempos = logistica.get('desglose_tiempos_h', {})

        tiempo_prep = desglose_tiempos.get('preparacion', 0)
        tiempo_viaje = desglose_tiempos.get('viaje', 0)
        tiempo_factores = desglose_tiempos.get('factores_externos', 0)
        tiempo_contingencia = desglose_tiempos.get('contingencia', 0)

        st.info(f"""
        **Preparación:** {tiempo_prep:.1f}h

        **Viaje:** {tiempo_viaje:.1f}h

        **Factores Externos:** {tiempo_factores:.1f}h

        **Contingencia:** {tiempo_contingencia:.1f}h
        """)

    with col3:
        st.markdown("**📈 Métricas de Éxito**")
        probabilidad_exito = resultado_final.get('probabilidad_exito', 0)
        confianza = resultado_final.get('confianza_prediccion', 0)
        fecha_entrega = resultado_final.get('fecha_entrega_estimada', 'N/A')

        st.info(f"""
        **Prob. Éxito:** {probabilidad_exito:.1%}

        **Confianza:** {confianza:.1%}

        **Fecha Entrega:** {fecha_entrega.split('T')[0] if 'T' in str(fecha_entrega) else fecha_entrega}

        **Tipo Entrega:** {resultado_final.get('tipo_entrega', 'N/A')}
        """)


def render_consolidated_winner_table(data: dict):
    """Tabla consolidada del ganador con manejo seguro de CEDIS None"""
    st.markdown("## 🎯 Resumen Ejecutivo - Decisión Final")

    import pandas as pd

    # Extraer todos los datos relevantes
    ganador_evaluacion = data.get('evaluacion', {}).get('ganador', {})
    resultado_final = data.get('resultado_final', {})
    logistica = data.get('logistica_entrega', {})
    factores = data.get('factores_externos', {})
    request_data = data.get('request', {})
    plan_asignacion = data.get('evaluacion_detallada', {}).get('stock_analysis', {}).get('asignacion_detallada',
                                                                                         {}).get('plan_asignacion', [])

    # MANEJO SEGURO DE CEDIS - puede ser None
    cedis_analysis = data.get('evaluacion_detallada', {}).get('cedis_analysis')
    cedis_seleccionado = {}
    if cedis_analysis and isinstance(cedis_analysis, dict):
        cedis_seleccionado = cedis_analysis.get('cedis_seleccionado', {})

    if not plan_asignacion:
        st.warning("⚠️ No hay datos de asignación disponibles")
        return

    ganador_real = plan_asignacion[0]

    # Crear tabla consolidada
    consolidated_data = [
        # Información básica del pedido
        {"Categoría": "📋 PEDIDO", "Campo": "SKU", "Valor": request_data.get('sku_id', 'N/A')},
        {"Categoría": "📋 PEDIDO", "Campo": "Cantidad", "Valor": f"{request_data.get('cantidad', 0)} unidades"},
        {"Categoría": "📋 PEDIDO", "Campo": "Código Postal Destino", "Valor": request_data.get('codigo_postal', 'N/A')},
        {"Categoría": "📋 PEDIDO", "Campo": "Fecha Compra",
         "Valor": request_data.get('fecha_compra', 'N/A').split('T')[0] if 'T' in str(
             request_data.get('fecha_compra', '')) else request_data.get('fecha_compra', 'N/A')},

        # Información del ganador
        {"Categoría": "🏆 GANADOR", "Campo": "Tienda Seleccionada", "Valor": ganador_real.get('nombre_tienda', 'N/A')},
        {"Categoría": "🏆 GANADOR", "Campo": "Score Final", "Valor": f"{ganador_real.get('score_total', 0):.3f}"},
        {"Categoría": "🏆 GANADOR", "Campo": "Distancia", "Valor": f"{ganador_real.get('distancia_km', 0):.1f} km"},
        {"Categoría": "🏆 GANADOR", "Campo": "Stock Disponible",
         "Valor": f"{ganador_real.get('stock_disponible', 0)} unidades"},
        {"Categoría": "🏆 GANADOR", "Campo": "Razón Selección", "Valor": ganador_real.get('razon_seleccion', 'N/A')},

        # Información logística
        {"Categoría": "🚚 LOGÍSTICA", "Campo": "Tipo de Ruta", "Valor": logistica.get('tipo_ruta', 'N/A')},
        {"Categoría": "🚚 LOGÍSTICA", "Campo": "Flota", "Valor": ganador_real.get('fleet_type', 'N/A')},
        {"Categoría": "🚚 LOGÍSTICA", "Campo": "Carrier", "Valor": ganador_real.get('carrier', 'N/A')},
        {"Categoría": "🚚 LOGÍSTICA", "Campo": "Tiempo Total",
         "Valor": f"{ganador_real.get('tiempo_total_h', 0):.1f} horas"},

        # Información de CEDIS (MANEJO SEGURO)
        {"Categoría": "🏭 CEDIS", "Campo": "CEDIS Intermedio", "Valor": logistica.get('cedis_intermedio', 'No aplica')},
        {"Categoría": "🏭 CEDIS", "Campo": "Score CEDIS",
         "Valor": f"{cedis_seleccionado.get('score', 0):.2f}" if cedis_seleccionado else "N/A"},
        {"Categoría": "🏭 CEDIS", "Campo": "Tiempo Procesamiento",
         "Valor": f"{cedis_seleccionado.get('tiempo_procesamiento_h', 0):.1f}h" if cedis_seleccionado else "N/A"},

        # Costos
        {"Categoría": "💰 COSTOS", "Campo": "Costo Producto", "Valor": f"${ganador_real.get('precio_total', 0):,.2f}"},
        {"Categoría": "💰 COSTOS", "Campo": "Costo Logístico",
         "Valor": f"${ganador_real.get('costo_total_mxn', 0):,.2f}"},
        {"Categoría": "💰 COSTOS", "Campo": "Costo Total Final",
         "Valor": f"${resultado_final.get('costo_mxn', 0):,.2f}"},

        # Factores externos
        {"Categoría": "🌍 FACTORES", "Campo": "Evento Detectado", "Valor": factores.get('evento_detectado', 'Normal')},
        {"Categoría": "🌍 FACTORES", "Campo": "Factor Demanda", "Valor": f"{factores.get('factor_demanda', 1.0):.2f}x"},
        {"Categoría": "🌍 FACTORES", "Campo": "Zona Seguridad", "Valor": factores.get('zona_seguridad', 'N/A')},
        {"Categoría": "🌍 FACTORES", "Campo": "Clima", "Valor": factores.get('condicion_clima', 'N/A')},
        {"Categoría": "🌍 FACTORES", "Campo": "Tiempo Extra",
         "Valor": f"{factores.get('impacto_tiempo_extra_horas', 0):.1f}h"},

        # Resultado final
        {"Categoría": "📈 RESULTADO", "Campo": "Probabilidad Éxito",
         "Valor": f"{resultado_final.get('probabilidad_exito', 0):.1%}"},
        {"Categoría": "📈 RESULTADO", "Campo": "Confianza Predicción",
         "Valor": f"{resultado_final.get('confianza_prediccion', 0):.1%}"},
        {"Categoría": "📈 RESULTADO", "Campo": "Fecha Entrega",
         "Valor": resultado_final.get('fecha_entrega_estimada', 'N/A').split('T')[0] if 'T' in str(
             resultado_final.get('fecha_entrega_estimada', '')) else resultado_final.get('fecha_entrega_estimada',
                                                                                         'N/A')},
        {"Categoría": "📈 RESULTADO", "Campo": "Ventana Entrega",
         "Valor": f"{resultado_final.get('ventana_entrega', {}).get('inicio', 'N/A')} - {resultado_final.get('ventana_entrega', {}).get('fin', 'N/A')}"},
        {"Categoría": "📈 RESULTADO", "Campo": "Tipo Entrega", "Valor": resultado_final.get('tipo_entrega', 'N/A')}
    ]

    # Mostrar tabla consolidada
    df_consolidated = pd.DataFrame(consolidated_data)
    st.dataframe(df_consolidated, use_container_width=True, height=800)

    # Métricas finales en tarjetas
    st.markdown("### 📊 Métricas Clave de la Decisión")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "🏆 Score Ganador",
            f"{ganador_real.get('score_total', 0):.3f}",
            help="Score final de optimización tiempo-costo-stock"
        )

    with col2:
        st.metric(
            "💰 Costo Total",
            f"${resultado_final.get('costo_mxn', 0):,.0f}",
            help="Costo total incluyendo producto y logística"
        )

    with col3:
        st.metric(
            "⏱️ Tiempo Total",
            f"{ganador_real.get('tiempo_total_h', 0):.1f}h",
            help="Tiempo total estimado de entrega"
        )

    with col4:
        st.metric(
            "📈 Prob. Éxito",
            f"{resultado_final.get('probabilidad_exito', 0):.0%}",
            help="Probabilidad de cumplir con la entrega"
        )

    with col5:
        st.metric(
            "📏 Distancia",
            f"{ganador_real.get('distancia_km', 0):.0f} km",
            help="Distancia total de la ruta"
        )




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