from datetime import datetime
import pandas as pd
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

## Modificación
def get_delivery_status_badge(delivery_type: str) -> str:
    """
    Obtener badge de tipo de entrega
    """
    delivery_type_upper = delivery_type.upper()
    badge_info = {
        "color": "#64748b", # Default gray
        "icon": "📋",
        "label": delivery_type
    }

    if "FLOTA LIVERPOOL" in delivery_type_upper:
        badge_info = {
            "color": "#FFC0CB",
            "icon": "🏠",
            "label": "FLOTA LIVERPOOL"
        }
    elif "MENSAJERIA EXTERNA" in delivery_type_upper:
        badge_info = {
            "color": "#ADD8E6",
            "icon": "🚚",
            "label": "MENSAJERIA EXTERNA"
        }
    elif "EDT" in delivery_type_upper or "PROGRAMADA" in delivery_type_upper:
        badge_info = {
            "color": "#90EE90",
            "icon": "🗓️",
            "label": delivery_type
        }

    return f'''
    <span style="
        background: {badge_info["color"]};
        color: black; /* Changed to black for better contrast on light backgrounds */
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

def render_comprehensive_evaluation_table(data: dict):
    """Renderizar tabla comprehensiva MEJORADA para todos los tipos de respuesta"""

    # DETECTAR TIPO DE RESPUESTA
    tipo_respuesta = data.get('tipo_respuesta', 'single_delivery_date')
    multiple_options = data.get('multiple_delivery_options', False)

    if multiple_options and data.get('delivery_options'):
        st.markdown("## 🔍 Evaluación Integral de Múltiples Opciones")
        render_multiple_options_comprehensive_analysis(data)
        return

    # RESPUESTA SIMPLE - ANÁLISIS MEJORADO
    st.markdown("## 🔍 Evaluación Integral Completa")

    eval_tab1, eval_tab2= st.tabs([
        "🏪 Análisis Liverpool",
        "🏆 Ganador Final"
    ])

    with eval_tab1:
        render_liverpool_analysis_enhanced(data)

    with eval_tab2:
        render_winner_analysis_enhanced(data)

def render_multiple_options_comprehensive_analysis(data: dict):
    """Análisis comprehensivo para múltiples opciones de entrega"""

    delivery_options = data.get('delivery_options', [])
    recommendation = data.get('recommendation', {})
    total_options = data.get('total_options', len(delivery_options))
    split_reason = data.get('split_reason', 'N/A')

    # INFORMACIÓN GENERAL
    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        border: 2px solid #0ea5e9;
    '>
        <h3 style='color: #0c4a6e; margin: 0 0 1rem 0;'>📊 Resumen de Múltiples Opciones</h3>
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;'>
            <div><strong>🔢 Total Opciones:</strong> {total_options}</div>
            <div><strong>🏆 Recomendada:</strong> {recommendation.get('opcion', 'N/A').replace('_', ' ').title()}</div>
            <div><strong>🔄 Razón División:</strong> {split_reason}</div>
            <div><strong>📦 Consolidación:</strong> {'✅ Disponible' if data.get('consolidation_available', False) else '❌ No disponible'}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # TABS POR CADA OPCIÓN
    if delivery_options:
        tab_names = []
        for i, opt in enumerate(delivery_options):
            opcion_name = opt.get('opcion', f'Opción {i + 1}').replace('_', ' ').title()
            is_recommended = opt.get('opcion') == recommendation.get('opcion')
            icon = '🏆' if is_recommended else '📦'
            tab_names.append(f"{icon} {opcion_name}")

        tabs = st.tabs(tab_names)

        for i, (tab, option) in enumerate(zip(tabs, delivery_options)):
            with tab:
                is_recommended = option.get('opcion') == recommendation.get('opcion')
                render_single_option_detailed_analysis(option, data, is_recommended, i)

    # COMPARACIÓN CONSOLIDADA
    render_cross_option_analysis(delivery_options, recommendation, data)

def render_single_option_detailed_analysis(option: dict, full_data: dict, is_recommended: bool, option_index: int):
    """Análisis detallado de una opción específica"""

    opcion_name = option.get('opcion', 'Opción').replace('_', ' ').title()

    if is_recommended:
        st.success(f"🏆 **OPCIÓN RECOMENDADA:** {opcion_name}")
    else:
        st.info(f"📦 **Opción Alternativa:** {opcion_name}")

    # MÉTRICAS PRINCIPALES
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("💰 Costo", f"${option.get('costo_envio', 0):,.2f}")

    with col2:
        st.metric("📈 Probabilidad", f"{option.get('probabilidad_cumplimiento', 0):.1%}")

    with col3:
        fecha = option.get('fecha_entrega', 'N/A')
        fecha_display = fecha.split('T')[0] if 'T' in str(fecha) else str(fecha)
        st.metric("📅 Entrega", fecha_display)

    with col4:
        tiempo = option.get('logistica', {}).get('tiempo_total_h', 0)
        st.metric("⏱️ Tiempo", f"{tiempo:.1f}h")

    # ANÁLISIS POR SECCIONES
    opt_tab1, opt_tab2, opt_tab3, opt_tab4 = st.tabs([
        "🏪 Tiendas Origen",
        "🚚 Logística",
        "📊 Métricas",
        "🔍 Detalles"
    ])

    with opt_tab1:
        render_option_stores_analysis(option, full_data)

    with opt_tab2:
        render_option_logistics_analysis(option, full_data)

    with opt_tab3:
        render_option_metrics_analysis(option, full_data)

    with opt_tab4:
        render_option_details_analysis(option, full_data)

def render_option_stores_analysis(option: dict, full_data: dict):
    """Análisis de tiendas origen para una opción específica"""

    import pandas as pd

    st.markdown("#### 🏪 Tiendas Origen de esta Opción")

    tiendas_origen = option.get('tiendas_origen', [])

    if tiendas_origen:
        # Obtener información detallada de las tiendas desde el análisis completo
        stock_analysis = full_data.get('evaluacion_detallada', {}).get('stock_analysis', {})
        stock_encontrado = stock_analysis.get('stock_encontrado', [])
        tiendas_cercanas = stock_analysis.get('tiendas_cercanas', [])

        stores_data = []
        for i, tienda_nombre in enumerate(tiendas_origen):
            # Buscar información detallada de la tienda
            tienda_info = None

            # Buscar en stock encontrado
            for stock_tienda in stock_encontrado:
                if tienda_nombre in stock_tienda.get('nombre_tienda', ''):
                    tienda_info = stock_tienda
                    break

            # Buscar en tiendas cercanas si no se encontró
            if not tienda_info:
                for cercana in tiendas_cercanas:
                    if tienda_nombre in cercana.get('nombre', ''):
                        tienda_info = cercana
                        break

            if tienda_info:
                stores_data.append({
                    '#': i + 1,
                    'Tienda Liverpool': tienda_nombre,
                    'Stock Disponible': tienda_info.get('stock_disponible', 'N/A'),
                    'Distancia (km)': f"{tienda_info.get('distancia_km', 0):.1f}",
                    'Estado': tienda_info.get('estado', 'N/A'),
                    'Zona Seguridad': tienda_info.get('zona_seguridad', 'N/A'),
                    'Precio Unitario': f"${tienda_info.get('precio_tienda', 0):,.2f}" if tienda_info.get(
                        'precio_tienda') else 'N/A',
                    'Es Local': '🟢 Sí' if tienda_info.get('es_local', False) else '🔴 No'
                })
            else:
                stores_data.append({
                    '#': i + 1,
                    'Tienda Liverpool': tienda_nombre,
                    'Stock Disponible': 'N/A',
                    'Distancia (km)': 'N/A',
                    'Estado': 'N/A',
                    'Zona Seguridad': 'N/A',
                    'Precio Unitario': 'N/A',
                    'Es Local': 'N/A'
                })

        df_stores = pd.DataFrame(stores_data)
        st.dataframe(df_stores, use_container_width=True)

        # Métricas de las tiendas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🏪 Total Tiendas", len(tiendas_origen))
        with col2:
            locales = sum(1 for item in stores_data if item.get('Es Local') == '🟢 Sí')
            st.metric("🏠 Tiendas Locales", locales)
        with col3:
            nacionales = len(tiendas_origen) - locales
            st.metric("🌍 Tiendas Nacionales", nacionales)
    else:
        st.warning("⚠️ No se encontraron tiendas origen para esta opción")

def render_option_logistics_analysis(option: dict, full_data: dict):
    """Análisis logístico detallado por opción"""

    st.markdown("#### 🚚 Análisis Logístico Detallado")

    logistica = option.get('logistica', {})

    # Información básica
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🛣️ Información de Ruta**")
        tipo_ruta = logistica.get('tipo_ruta', 'N/A')
        flota = logistica.get('flota', 'N/A')
        tiempo_total = logistica.get('tiempo_total_h', 0)

        st.info(f"""
        **Tipo de Ruta:** {tipo_ruta}

        **Flota:** {flota}

        **Tiempo Total:** {tiempo_total:.1f} horas

        **Segmentos:** {logistica.get('segmentos', 1)}
        """)

    with col2:
        st.markdown("**🏭 Infraestructura**")

        hub_consolidacion = logistica.get('hub_consolidacion')
        cedis_intermedio = logistica.get('cedis_intermedio')

        if hub_consolidacion:
            st.success(f"🏭 **Hub Consolidación:** {hub_consolidacion}")

        if cedis_intermedio:
            st.success(f"🏭 **CEDIS Intermedio:** {cedis_intermedio}")

        if not hub_consolidacion and not cedis_intermedio:
            st.info("🚚 **Ruta Directa** - Sin infraestructura intermedia")

    # Análisis de complejidad
    st.markdown("#### 📊 Análisis de Complejidad")

    # Determinar complejidad
    complejidad_score = 1
    factores_complejidad = []

    if 'consolidada' in tipo_ruta:
        complejidad_score += 2
        factores_complejidad.append("Consolidación múltiple")

    if cedis_intermedio:
        complejidad_score += 2
        factores_complejidad.append("Paso por CEDIS")

    if logistica.get('segmentos', 1) > 2:
        complejidad_score += 1
        factores_complejidad.append("Múltiples segmentos")

    if 'FE' in flota:
        complejidad_score += 1
        factores_complejidad.append("Flota externa")

    # Mostrar complejidad
    if complejidad_score <= 2:
        st.success(f"🟢 **Complejidad Baja** (Score: {complejidad_score})")
    elif complejidad_score <= 4:
        st.warning(f"🟡 **Complejidad Media** (Score: {complejidad_score})")
    else:
        st.error(f"🔴 **Complejidad Alta** (Score: {complejidad_score})")

    if factores_complejidad:
        st.markdown("**Factores de Complejidad:**")
        for factor in factores_complejidad:
            st.markdown(f"• {factor}")

def render_option_metrics_analysis(option: dict, full_data: dict):
    """Análisis de métricas detallado por opción"""

    st.markdown("#### 📊 Métricas Operacionales")

    # Métricas principales
    costo = option.get('costo_envio', 0)
    probabilidad = option.get('probabilidad_cumplimiento', 0)
    tiempo = option.get('logistica', {}).get('tiempo_total_h', 0)
    tipo_entrega = option.get('tipo_entrega', 'STANDARD')

    # Análisis de costo
    st.markdown("##### 💰 Análisis de Costo")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("💳 Costo Total", f"${costo:,.2f}")

        if costo < 100:
            st.success("💰 Costo muy eficiente")
        elif costo < 500:
            st.info("💰 Costo moderado")
        else:
            st.warning("💰 Costo elevado")

    with col2:
        # Costo por hora
        costo_hora = costo / max(tiempo, 1)
        st.metric("⏱️ Costo/Hora", f"${costo_hora:.2f}")

    with col3:
        # Eficiencia
        if probabilidad > 0:
            eficiencia = (probabilidad * 100) / max(costo, 1)
            st.metric("📈 Eficiencia", f"{eficiencia:.2f}")

    # Análisis de riesgo
    st.markdown("##### ⚠️ Análisis de Riesgo")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("🎯 Probabilidad Éxito", f"{probabilidad:.1%}")

        if probabilidad >= 0.85:
            st.success("🟢 Riesgo muy bajo")
        elif probabilidad >= 0.7:
            st.info("🟡 Riesgo moderado")
        else:
            st.error("🔴 Riesgo alto")

    with col2:
        # Calcular índice de riesgo
        riesgo = (1 - probabilidad) * 100
        st.metric("⚠️ Índice Riesgo", f"{riesgo:.1f}%")

    # Análisis temporal
    st.markdown("##### ⏰ Análisis Temporal")

    fecha_entrega = option.get('fecha_entrega', '')
    ventana = option.get('ventana_entrega', {})

    if fecha_entrega:
        from datetime import datetime
        try:
            fecha_dt = datetime.fromisoformat(fecha_entrega.replace('Z', '+00:00'))
            fecha_compra = full_data.get('request', {}).get('fecha_compra', '')

            if fecha_compra:
                compra_dt = datetime.fromisoformat(fecha_compra.replace('Z', '+00:00'))
                dias_diferencia = (fecha_dt - compra_dt).days

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("📅 Días para Entrega", dias_diferencia)

                with col2:
                    st.metric("🕐 Ventana", f"{ventana.get('inicio', 'N/A')} - {ventana.get('fin', 'N/A')}")

                with col3:
                    st.metric("📦 Tipo", tipo_entrega)

                    if tipo_entrega == 'EXPRESS':
                        st.success("⚡ Entrega rápida")
                    elif tipo_entrega == 'STANDARD':
                        st.info("📦 Entrega estándar")
                    else:
                        st.warning("🗓️ Entrega programada")
        except:
            st.info("📅 Información temporal no disponible")

def render_option_details_analysis(option: dict, full_data: dict):
    """Análisis de detalles específicos por opción"""

    st.markdown("#### 🔍 Detalles Específicos")

    import pandas as pd

    # Crear tabla de detalles
    details_data = [
        {"Campo": "Opción", "Valor": option.get('opcion', 'N/A').replace('_', ' ').title()},
        {"Campo": "Descripción", "Valor": option.get('descripcion', 'N/A')},
        {"Campo": "Tipo Entrega", "Valor": option.get('tipo_entrega', 'N/A')},
        {"Campo": "Fecha Entrega", "Valor": option.get('fecha_entrega', 'N/A')},
        {"Campo": "Costo Envío", "Valor": f"${option.get('costo_envio', 0):,.2f}"},
        {"Campo": "Probabilidad", "Valor": f"{option.get('probabilidad_cumplimiento', 0):.1%}"},
        {"Campo": "Tiendas Origen", "Valor": ', '.join(option.get('tiendas_origen', []))},
    ]

    # Agregar detalles logísticos
    logistica = option.get('logistica', {})
    for key, value in logistica.items():
        if key != 'tiempo_total_h':  # Ya se muestra arriba
            field_name = key.replace('_', ' ').title()
            details_data.append({
                "Campo": f"Logística - {field_name}",
                "Valor": str(value)
            })

    df_details = pd.DataFrame(details_data)
    st.dataframe(df_details, use_container_width=True)

    # Ventana de entrega detallada
    ventana = option.get('ventana_entrega', {})
    if ventana:
        st.markdown("#### 🕐 Ventana de Entrega")
        st.info(f"**Horario:** {ventana.get('inicio', 'N/A')} - {ventana.get('fin', 'N/A')}")

def render_cross_option_analysis(delivery_options: list, recommendation: dict, full_data: dict):
    """Análisis cruzado y comparativo entre todas las opciones"""

    st.markdown("---")
    st.markdown("## 🔄 Análisis Comparativo Cruzado")

    import pandas as pd

    # TABLA COMPARATIVA COMPLETA
    st.markdown("### 📊 Matriz Comparativa Completa")

    comparison_data = []
    for i, option in enumerate(delivery_options):
        is_recommended = option.get('opcion') == recommendation.get('opcion')
        logistica = option.get('logistica', {})

        comparison_data.append({
            'Ranking': '🏆 1' if is_recommended else f"📦 {i + 1}",
            'Opción': option.get('opcion', f'Opción {i + 1}').replace('_', ' ').title(),
            'Descripción': option.get('descripcion', 'N/A'),
            'Tipo': option.get('tipo_entrega', 'N/A'),
            'Fecha': option.get('fecha_entrega', 'N/A').split('T')[0] if 'T' in str(
                option.get('fecha_entrega', '')) else option.get('fecha_entrega', 'N/A'),
            'Costo ($)': f"{option.get('costo_envio', 0):,.2f}",
            'Prob. (%)': f"{option.get('probabilidad_cumplimiento', 0):.1%}",
            'Tiempo (h)': f"{logistica.get('tiempo_total_h', 0):.1f}",
            'Tiendas': len(option.get('tiendas_origen', [])),
            'Complejidad': _calculate_option_complexity(option),
            'Score Riesgo': f"{(1 - option.get('probabilidad_cumplimiento', 0)) * 100:.1f}%"
        })

    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True)

    # ANÁLISIS DE RANGOS
    st.markdown("### 📈 Análisis de Rangos")

    costos = [opt.get('costo_envio', 0) for opt in delivery_options]
    probabilidades = [opt.get('probabilidad_cumplimiento', 0) for opt in delivery_options]
    tiempos = [opt.get('logistica', {}).get('tiempo_total_h', 0) for opt in delivery_options]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("💰 Costo Min-Max", f"${min(costos):,.0f} - ${max(costos):,.0f}")
        st.metric("📊 Variación", f"{((max(costos) - min(costos)) / max(costos, 1) * 100):.1f}%")

    with col2:
        st.metric("📈 Prob. Min-Max", f"{min(probabilidades):.0%} - {max(probabilidades):.0%}")
        st.metric("📊 Diferencia", f"{(max(probabilidades) - min(probabilidades)) * 100:.1f} pts")

    with col3:
        st.metric("⏱️ Tiempo Min-Max", f"{min(tiempos):.1f}h - {max(tiempos):.1f}h")
        st.metric("📊 Variación", f"{((max(tiempos) - min(tiempos)) / max(tiempos, 1) * 100):.1f}%")

    with col4:
        st.metric("📦 Total Opciones", len(delivery_options))
        recomendada = recommendation.get('opcion', 'N/A').replace('_', ' ').title()
        st.metric("🏆 Recomendada", recomendada)

    # RECOMENDACIÓN FINAL
    st.markdown("### 🎯 Justificación de la Recomendación")

    recomendada_option = None
    for opt in delivery_options:
        if opt.get('opcion') == recommendation.get('opcion'):
            recomendada_option = opt
            break

    if recomendada_option:
        st.success(f"""
        **🏆 Opción Recomendada:** {recommendation.get('opcion', 'N/A').replace('_', ' ').title()}

        **💰 Costo:** ${recomendada_option.get('costo_envio', 0):,.2f}

        **📈 Probabilidad:** {recomendada_option.get('probabilidad_cumplimiento', 0):.1%}

        **📅 Entrega:** {recomendada_option.get('fecha_entrega', 'N/A').split('T')[0] if 'T' in str(recomendada_option.get('fecha_entrega', '')) else recomendada_option.get('fecha_entrega', 'N/A')}

        **🏪 Tiendas:** {', '.join(recomendada_option.get('tiendas_origen', []))}

        **🎯 Razón:** {_generate_recommendation_reason(recomendada_option, delivery_options)}
        """)

def _calculate_option_complexity(option: dict) -> str:
    """Calcular nivel de complejidad de una opción"""

    logistica = option.get('logistica', {})
    score = 1

    if 'consolidada' in logistica.get('tipo_ruta', ''):
        score += 2

    if logistica.get('cedis_intermedio'):
        score += 2

    if logistica.get('segmentos', 1) > 2:
        score += 1

    if 'FE' in logistica.get('flota', ''):
        score += 1

    if score <= 2:
        return "🟢 Baja"
    elif score <= 4:
        return "🟡 Media"
    else:
        return "🔴 Alta"

def _generate_recommendation_reason(recommended: dict, all_options: list) -> str:
    """Generar razón de por qué se recomienda una opción"""

    costos = [opt.get('costo_envio', 0) for opt in all_options]
    probabilidades = [opt.get('probabilidad_cumplimiento', 0) for opt in all_options]

    rec_costo = recommended.get('costo_envio', 0)
    rec_prob = recommended.get('probabilidad_cumplimiento', 0)

    reasons = []

    # Análisis de costo
    if rec_costo == min(costos):
        reasons.append("menor costo")
    elif rec_costo <= sum(costos) / len(costos):
        reasons.append("costo competitivo")

    # Análisis de probabilidad
    if rec_prob == max(probabilidades):
        reasons.append("mayor probabilidad de éxito")
    elif rec_prob >= 0.8:
        reasons.append("alta confiabilidad")

    # Análisis de descripción
    descripcion = recommended.get('descripcion', '')
    if 'consolidada' in descripcion:
        reasons.append("eficiencia de consolidación")

    return ', '.join(reasons) if reasons else "balance óptimo de factores"

def render_winner_analysis_enhanced(data: dict):
    """Análisis del ganador MEJORADO con justificación completa"""
    st.markdown("### 🏆 Análisis del Ganador Final")

    # MAPA DE DECISIÓN
    st.markdown("#### 🗺️ Mapa de la Decisión Final")

    plan_asignacion = data.get('evaluacion_detallada', {}).get('stock_analysis', {}).get('asignacion_detallada',
                                                                                         {}).get('plan_asignacion', [])
    resultado_final = data.get('resultado_final', {})
    logistica = data.get('logistica_entrega', {})

    if plan_asignacion:
        ganador = plan_asignacion[0]

        # Flujo de decisión
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #d1fae5, #a7f3d0);
            padding: 2rem;
            border-radius: 15px;
            margin: 1.5rem 0;
            border: 2px solid #10b981;
        '>
            <h4 style='color: #065f46; margin: 0 0 1rem 0;'>🎯 Flujo de Decisión Ganadora</h4>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem;'>
                <div>
                    <strong>🏪 Tienda Seleccionada</strong><br>
                    {ganador.get('nombre_tienda', 'N/A')}<br>
                    <em>Score: {ganador.get('score_total', 0):.3f}</em>
                </div>
                <div>
                    <strong>🚚 Ruta Definida</strong><br>
                    {logistica.get('tipo_ruta', 'N/A')}<br>
                    <em>{logistica.get('carrier', 'N/A')} - {logistica.get('flota', 'N/A')}</em>
                </div>
                <div>
                    <strong>💰 Optimización Costo</strong><br>
                    ${resultado_final.get('costo_mxn', 0):,.2f}<br>
                    <em>Eficiencia: {ganador.get('distancia_km', 0):.1f}km</em>
                </div>
                <div>
                    <strong>📈 Resultado Final</strong><br>
                    {resultado_final.get('probabilidad_exito', 0):.1%} éxito<br>
                    <em>{resultado_final.get('tipo_entrega', 'N/A')}</em>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def extract_key_insights(data: dict) -> list:
    """Extraer insights ejecutivos MEJORADOS para todos los tipos de respuesta"""
    insights = []

    # DETECTAR TIPO DE RESPUESTA
    multiple_options = data.get('multiple_delivery_options', False)

    if multiple_options:
        # INSIGHTS PARA MÚLTIPLES OPCIONES
        delivery_options = data.get('delivery_options', [])
        recommendation = data.get('recommendation', {})

        insights.append(f"🔄 {len(delivery_options)} opciones evaluadas")

        # Análisis de costos
        costos = [opt.get('costo_envio', 0) for opt in delivery_options]
        if costos:
            if max(costos) / min(costos) > 2:
                insights.append(f"💰 Gran variación de costos")
            else:
                insights.append(f"💰 Costos similares")

        # Recomendación
        rec_name = recommendation.get('opcion', 'N/A').replace('_', ' ').title()
        insights.append(f"🏆 Recomendada: {rec_name}")

        # Consolidación
        if data.get('consolidation_available', False):
            insights.append("📦 Consolidación disponible")

        # Complejidad
        for opt in delivery_options:
            if 'consolidada' in opt.get('descripcion', ''):
                insights.append("🏭 Requiere consolidación")
                break

    else:
        # INSIGHTS PARA RESPUESTA SIMPLE (código actual)
        logistica = data.get('logistica_entrega', {})
        resultado = data.get('resultado_final', {})

        tiempo = logistica.get('tiempo_total_h', 0)
        if tiempo <= 24:
            insights.append(f"⚡ Entrega rápida: {tiempo:.1f}h")
        elif tiempo <= 48:
            insights.append(f"📅 Entrega estándar: {tiempo:.1f}h")
        else:
            insights.append(f"🐌 Entrega extendida: {tiempo:.1f}h")

        costo = resultado.get('costo_mxn', 0)
        if costo > 0:
            if costo <= 100:
                insights.append(f"💰 Costo eficiente: ${costo:,.0f}")
            elif costo <= 300:
                insights.append(f"💰 Costo moderado: ${costo:,.0f}")
            else:
                insights.append(f"💰 Costo elevado: ${costo:,.0f}")

        probabilidad = resultado.get('probabilidad_exito', 0)
        if probabilidad >= 0.9:
            insights.append(f"🎯 Éxito muy probable: {probabilidad:.0%}")
        elif probabilidad >= 0.7:
            insights.append(f"📈 Éxito probable: {probabilidad:.0%}")
        else:
            insights.append(f"⚠️ Riesgo elevado: {probabilidad:.0%}")

        # Factores adicionales
        factores = data.get('factores_externos', {})
        factor_demanda = factores.get('factor_demanda', 1.0)
        if factor_demanda > 1.5:
            insights.append(f"📊 Alta demanda (×{factor_demanda:.1f})")

        tipo_ruta = logistica.get('tipo_ruta', '')
        if 'cedis' in tipo_ruta.lower():
            insights.append("🏭 Ruta vía CEDIS")
        else:
            insights.append("🚚 Ruta directa")

    return insights[:5]  # Máximo 5 insights

## Análisis completo de Tiendas Liverpool

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

def render_liverpool_analysis_enhanced(data: dict):
    """Análisis Liverpool MEJORADO con mejor mapeo de relaciones"""
    st.markdown("### 🏪 Análisis Completo de Tiendas Liverpool")

    stock_analysis = data.get('evaluacion_detallada', {}).get('stock_analysis', {})
    request_data = data.get('request', {})
    codigo_postal = request_data.get('codigo_postal', 'N/A')

    # MAPA DE RELACIONES CP → TIENDAS
    st.markdown(f"#### 🗺️ Mapeo de Relaciones: CP {codigo_postal} → Tiendas Liverpool")

    # Información de conectividad
    tiendas_cercanas = stock_analysis.get('tiendas_cercanas', [])
    stock_encontrado = stock_analysis.get('stock_encontrado', [])
    tiendas_autorizadas = stock_analysis.get('tiendas_autorizadas', [])

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📍 CP Destino", codigo_postal)
        zona_cp = data.get('factores_externos', {}).get('zona_seguridad', 'N/A')
        st.metric("🛡️ Zona CP", zona_cp)

    with col2:
        st.metric("🏪 Tiendas Cercanas", len(tiendas_cercanas))
        st.metric("📦 Con Stock", len(stock_encontrado))

    with col3:
        st.metric("🌍 Autorizadas Nacional", len(tiendas_autorizadas))
        tipo_stock = stock_analysis.get('resumen_stock', {}).get('tipo_stock', 'N/A')
        st.metric("📋 Tipo Stock", tipo_stock)

    with col4:
        total_disponible = stock_analysis.get('resumen_stock', {}).get('total_disponible', 0)
        requerido = stock_analysis.get('resumen_stock', {}).get('requerido', 0)
        st.metric("📊 Stock Total", total_disponible)
        st.metric("📋 Requerido", requerido)

    # Resto del análisis actual...
    render_liverpool_analysis_corrected(data)


def render_prediction_results(data: dict):
    """
    Renderizar los resultados completos de la predicción de entrega,
    adaptándose si hay un split en la entrega.
    """
    st.subheader("📊 Resultados de la Predicción de Entrega")

    # Sección principal de métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**🛣️ Información de ruta**")
        st.metric("📦 ID Trazo", data.get('id_trazo', 'N/A'))
        st.metric("📍 Tienda", data.get('tienda', 'N/A'))
        st.metric("🚚 Método", data.get('metodo', 'N/A'))
    with col2:
        st.markdown("**🗓️Fechas importantes**")
        st.metric("⏳ Días Estimados", data.get('dias', 'N/A'))
        st.metric("🗓️ Fecha Entrega", format_datetime(data.get('fecha_entrega', '')))
    with col3:
        st.markdown("**💲Desglose de costos**")
        st.metric("🛒 Cantidad Total", data.get('cantidad_total', 'N/A'))
        st.metric("💰 Costo Unitario", format_currency(data.get('costo_unitario', 0)))
        st.metric("💲 Costo Total", format_currency(data.get('costo', 0)))
    with col4:
        st.markdown("**⚙️ Detalles técnicos**")
        st.metric("⏱️ Tiempo de procesamiento", f"{data.get('tiempo_proceso_ms', 0):.2f} ms")
        st.metric("✨ Score", format_percentage(data.get('score', 0)))

    st.markdown("---")
    st.subheader("🔍 Información Detallada de la Entrega")

    # Tipo de Entrega
    tipo_entrega = data.get('tipo_entrega', {})
    if tipo_entrega:
        st.markdown(f"**Tipo de Entrega:** {tipo_entrega.get('icono', '')} {tipo_entrega.get('nombre', 'N/A')}")
        st.info(f"Descripción: {tipo_entrega.get('descripcion', 'N/A')}")
        st.info(f"Criterios: {tipo_entrega.get('criterios', 'N/A')}")
        st.info(f"Ventana de Tiempo: {tipo_entrega.get('ventana_tiempo', 'N/A')}")
    else:
        st.info("ℹ️ No se encontró información detallada del tipo de entrega.")

    st.markdown("---")
    st.subheader("🗺️ Contexto Geográfico")
    geo_context = data.get('contexto_geografico', {})
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🌍 Rango CP", geo_context.get('rango_cp', 'N/A'))
        st.metric("🏘️ Estado/Alcaldía", geo_context.get('estado_alcaldia', 'N/A'))
        st.metric("🏬 Cobertura Liverpool", "✅ Sí" if geo_context.get('cobertura_liverpool', False) else "❌ No")
    with col2:
        st.metric("🚨 Zona Seguridad", geo_context.get('zona_seguridad', 'N/A'))
        st.metric("🏙️ Tipo de Zona", geo_context.get('tipo_zona', 'N/A'))
    with col3:
        st.metric("⏳ Tiempo Entrega Base (horas)", geo_context.get('tiempo_entrega_base_horas', 'N/A'))
        st.metric("📝 Observaciones", geo_context.get('observaciones', 'N/A'))

    st.markdown("---")
    st.subheader("☁️ Contexto Climático")
    clim_context = data.get('contexto_climatico', {})
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📍 Región", clim_context.get('region_nombre', 'N/A'))
        st.metric("🗺️ Estado Principal", clim_context.get('estado_principal', 'N/A'))
    with col2:
        st.metric("☀️ Clima Actual", clim_context.get('clima_actual', 'N/A'))
        st.metric("🌡️ Temperatura (Min/Max)",
                  f"{clim_context.get('temperatura_min', 'N/A')}°C / {clim_context.get('temperatura_max', 'N/A')}°C")
    with col3:
        st.metric("⛰️ Altitud (msnm)", clim_context.get('altitud_msnm', 'N/A'))
        st.metric("💧 Precipitación Anual", f"{clim_context.get('precipitacion_anual', 'N/A')} mm")
        st.metric("⚡ Factores Especiales", clim_context.get('factores_especiales', 'N/A'))

    st.markdown("---")
    st.subheader("⚙️ Ajustes Aplicados")
    ajustes = data.get('ajustes_aplicados', {})
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("➕ Tiempo Extra (horas)", ajustes.get('tiempo_extra_horas', 'N/A'))
    with col2:
        st.metric("✖️ Multiplicador Costo", ajustes.get('multiplicador_costo', 'N/A'))
    with col3:
        st.metric("🚀 Entrega Rápida Viable", "✅ Sí" if ajustes.get('entrega_rapida_viable', False) else "❌ No")

    st.markdown("---")
    st.subheader("⚖️ Pesos Aplicados y Decisión")
    decision_info = data.get('decision_info', {})
    pesos_aplicados = data.get('pesos_aplicados', {})

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Criterios de Decisión:**")
        st.info(f"Criterio Principal: {decision_info.get('criterio_principal', 'N/A')}")
        st.info(f"Temporada Aplicada: {decision_info.get('temporada_aplicada', 'N/A')}")
        st.info(f"Pesos Origen: {decision_info.get('pesos_origen', 'N/A')}")
        if 'razon_split' in decision_info and decision_info['razon_split']:
            st.info(f"Motivo del Split: {decision_info['razon_split']} 💡")
    with col2:
        st.write("**Pesos Utilizados:**")
        if pesos_aplicados:
            for key, value in pesos_aplicados.items():
                st.info(f"{key.replace('_', ' ').title()}: {format_percentage(value)}")
        else:
            st.info("ℹ️ No se encontraron pesos aplicados.")

def render_candidates(data):
    """
    Despliega las rutas candidatas que fueron evaluadas,
    coloreando las filas seleccionadas.
    """
    st.subheader("🏆 Principales candidatos")
    alternatives = data.get('alternativas', [])
    if alternatives:
        df_alternatives = pd.DataFrame(alternatives)

        styled_df = df_alternatives.style.apply(highlight_selected_row, axis=1)

        if 'costo' in df_alternatives.columns:
            df_alternatives['costo'] = df_alternatives['costo'].apply(format_currency)
        if 'score' in df_alternatives.columns:
            df_alternatives['score'] = df_alternatives['score'].apply(format_percentage)

        column_configuration = {
            "selected": st.column_config.CheckboxColumn(
                "✅ Seleccionada",
                help="Indica si esta ruta fue seleccionada para la entrega",
                default=False,
                width="small"
            )
        }

        st.dataframe(styled_df, use_container_width=True, column_config=column_configuration)
    else:
        st.info("No se encontraron alternativas. 🤷‍♀️")

    st.markdown("---")
    st.subheader("ℹ️ Información Adicional")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📊 Total de opciones evaluadas", data.get('opciones_evaluadas', 'N/A'))
    with col2:
        es_split = data.get('es_split', False)
        st.metric("📦 ¿Es Split?", "✅ Sí" if es_split else "❌ No")

    if es_split:
        st.subheader("📦 Detalles de las Rutas del Split")
        split_info = data.get('split_info', {})
        if split_info:
            st.write(f"Número de rutas seleccionadas: **{split_info.get('rutas_seleccionadas', 'N/A')}**")
            st.write(f"Tiempo total (días): **{split_info.get('tiempo_total', 'N/A')}**")
            st.write(f"Costo total: **{format_currency(split_info.get('costo_total', 0))}**")
            st.write(f"Costo unitario promedio: **{format_currency(split_info.get('costo_unitario_promedio', 0))}**")
            st.write(f"Cantidad total: **{split_info.get('cantidad_total', 'N/A')}**")

            detalle_rutas = split_info.get('detalle_rutas', [])
            if detalle_rutas:
                st.markdown("---")
                st.write("**Desglose por Ruta:**")
                for i, ruta in enumerate(detalle_rutas):
                    st.markdown(f"**Ruta {i + 1}:**")
                    col_r1, col_r2, col_r3 = st.columns(3)
                    with col_r1:
                        st.metric("🆔 ID Trazo", ruta.get('id_trazo', 'N/A'))
                        st.metric("🏪 Tienda", ruta.get('tienda', 'N/A'))
                        st.metric("🔢 Cantidad", ruta.get('cantidad', 'N/A'))
                    with col_r2:
                        st.metric("➡️ Método", ruta.get('metodo', 'N/A'))
                        st.metric("📅 Días", ruta.get('dias', 'N/A'))
                        st.metric("💲 Costo Unitario", format_currency(ruta.get('costo_unitario', 0)))
                    with col_r3:
                        st.metric("💸 Costo Total Ruta", format_currency(ruta.get('costo_total_ruta', 0)))
                        st.metric("📦 Inventario Disponible", ruta.get('inventario_disponible', 'N/A'))
                        st.metric("✨ Score", format_percentage(ruta.get('score', 0)))
                    st.markdown("---")
            else:
                st.info("⚠️ No se encontraron detalles de rutas para el split.")
        else:
            st.info("ℹ️ No se encontró información detallada del split.")

def highlight_selected_row(row):
    """
    Define el estilo para resaltar las filas donde 'selected' es True.
    """
    if row['selected']:
        return ['background-color: #d4edda'] * len(row)
    return [''] * len(row)