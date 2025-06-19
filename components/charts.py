import streamlit as st
from streamlit_echarts import st_echarts

from components.layout import render_header, render_back_button
from utils.helpers import (
    format_currency, format_percentage, format_datetime, get_delivery_status_badge,
    extract_key_insights, render_comprehensive_evaluation_table
)


def calcular_llegada_relativa(fecha_compra_str: str, fecha_entrega_str: str) -> str:
    """Calcular cuándo llega el pedido de forma relativa a la fecha de compra"""
    if not fecha_compra_str or not fecha_entrega_str:
        return "N/A"

    try:
        from datetime import datetime

        fecha_compra = datetime.fromisoformat(fecha_compra_str.replace('Z', '+00:00'))
        fecha_entrega = datetime.fromisoformat(fecha_entrega_str.replace('Z', '+00:00'))
        dia_compra = fecha_compra.date()
        dia_entrega = fecha_entrega.date()
        diferencia_dias = (dia_entrega - dia_compra).days

        if diferencia_dias == 0:
            return "HOY"
        elif diferencia_dias == 1:
            return "MAÑANA"
        elif diferencia_dias > 0:
            return f"EN {diferencia_dias} DÍAS"
        else:
            return f"HACE {abs(diferencia_dias)} DÍAS"

    except Exception as e:
        return "N/A"


def render_results_dashboard():
    """Renderizar dashboard completo de resultados"""
    data = st.session_state.prediction_data

    render_back_button()
    render_header(
        "📊 Análisis de Predicción",
        "Resultados del análisis de ruta y predicción de entrega"
    )

    # Métricas principales
    render_main_metrics(data)

    # Fecha promesa destacada
    render_delivery_promise(data)

    # Insights
    render_key_insights(data)

    # Visualizaciones
    render_interactive_charts(data)

    # NUEVA SECCIÓN
    st.markdown("---")
    render_comprehensive_evaluation_table(data)

    # Detalles técnicos
    render_technical_details(data)


def render_main_metrics(data: dict):
    """Renderizar métricas principales adaptadas al nuevo response"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        costo = data.get('resultado_final', {}).get('costo_mxn', 0)
        st.metric(
            label="💰 Costo Total",
            value=format_currency(costo),
            delta=None
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        prob = data.get('resultado_final', {}).get('probabilidad_exito', 0)
        st.metric(
            label="📈 Probabilidad Éxito",
            value=format_percentage(prob),
            delta=f"Confianza: {format_percentage(data.get('resultado_final', {}).get('confianza_prediccion', 0))}"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        logistica = data.get('logistica_entrega', {})
        tiempo = logistica.get('tiempo_total_h', 0)
        st.metric(
            label="⏱️ Tiempo Total",
            value=f"{tiempo:.1f} horas",
            delta=f"Distancia: {logistica.get('distancia_km', 0):.0f} km"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col4:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        tipo_entrega = data.get('resultado_final', {}).get('tipo_entrega', 'N/A')
        carrier = data.get('logistica_entrega', {}).get('carrier', 'N/A')
        st.markdown("**🚚 Tipo de Entrega**")
        st.markdown(get_delivery_status_badge(tipo_entrega), unsafe_allow_html=True)
        st.markdown(f"**Carrier:** {carrier}")
        st.markdown("</div>", unsafe_allow_html=True)


def render_delivery_promise(data: dict):
    """Renderizar fecha promesa de entrega adaptada al nuevo response"""
    fecha_entrega_str = data.get('resultado_final', {}).get('fecha_entrega_estimada', '')

    if fecha_entrega_str:
        # fecha (sin hora)
        fecha_entrega = format_datetime(fecha_entrega_str)
        rango = data.get('resultado_final', {}).get('ventana_entrega', {})

        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #2D5016, #1B4332);
            color: white;
            padding: 2.5rem;
            border-radius: 20px;
            margin: 2rem 0;
            box-shadow: 0 15px 35px rgba(45, 80, 22, 0.3);
            border: 3px solid #4CAF50;
        '>
            <div style='text-align: center;'>
                <h3 style='margin: 0; font-size: 1.2rem; opacity: 0.9;'>🎯 Fecha Promesa de Entrega</h3>
                <h1 style='font-size: 2.8rem; margin: 1rem 0; font-weight: 800; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>{fecha_entrega}</h1>
                <div style='font-size: 1.3rem; opacity: 0.9; background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin-top: 1rem;'>
                    🕐 Ventana de entrega: <strong>{rango.get('inicio', 'N/A')} - {rango.get('fin', 'N/A')}</strong>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ No se encontró fecha de entrega estimada")


def render_key_insights(data: dict):
    """Renderizar insights clave"""
    insights = extract_key_insights(data)

    if insights:
        st.markdown("### 💡 Puntos Clave del Análisis")

        cols = st.columns(len(insights))
        colors = ["#2D5016", "#8B4513", "#1B4332", "#6D4C41", "#4A148C"]

        for i, insight in enumerate(insights):
            with cols[i]:
                color = colors[i % len(colors)]
                st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, #F8F6F0, #F0ECE0);
                    padding: 1.5rem;
                    border-radius: 12px;
                    border-left: 4px solid {color};
                    margin: 0.5rem 0;
                    text-align: center;
                    font-weight: 500;
                    color: #2D5016;
                    box-shadow: 0 4px 15px rgba(45, 80, 22, 0.1);
                '>
                    {insight}
                </div>
                """, unsafe_allow_html=True)


def render_interactive_charts(data: dict):
    """Renderizar gráficos interactivos"""
    tab1, tab2, tab3, tab4 = st.tabs([
        "🗺️ Ruta de Entrega",
        "📊 Métricas de Rendimiento",
        "⏰ Timeline de Proceso",
        "🎯 Análisis de Factores"
    ])

    with tab1:
        render_delivery_route_graph(data)

    with tab2:
        render_performance_metrics_chart(data)

    with tab3:
        render_process_timeline(data)

    with tab4:
        render_factors_analysis(data)


def render_delivery_route_graph(data: dict):
    """Crear red dinámica ADAPTADA AL NUEVO RESPONSE - VERSION MEJORADA PARA TODOS LOS TIPOS"""
    st.markdown("#### 🎯 Red Logística Centrada en Destino")

    tipo_respuesta = data.get('tipo_respuesta', 'single_delivery_date')
    multiple_options = data.get('multiple_delivery_options', False)

    if multiple_options and data.get('delivery_options'):
        render_multiple_delivery_options_graph(data)
        return

    render_delivery_summary(data)

    try:
        request_data = data.get('request', {})
        factores_externos = data.get('factores_externos', {})
        logistica = data.get('logistica_entrega', {})
        evaluacion_detallada = data.get('evaluacion_detallada', {})
        stock_analysis = evaluacion_detallada.get('stock_analysis', {})
        cedis_analysis = evaluacion_detallada.get('cedis_analysis')

        nodes = []
        links = []
        categories = _get_graph_categories()

        # 1. NODO CENTRAL: CÓDIGO POSTAL DESTINO
        codigo_postal = request_data.get('codigo_postal', 'N/A')
        destination_node = _create_central_destination_node(codigo_postal)
        nodes.append(destination_node)
        destination_node_name = destination_node['name']

        # 2. NODO PRODUCTO/SKU
        product_node = _create_product_node(request_data)
        nodes.append(product_node)

        # 3. TIENDAS CON STOCK DISPONIBLE
        stock_nodes, stock_links = _create_stock_stores_from_response(stock_analysis, product_node['name'])
        nodes.extend(stock_nodes)
        links.extend(stock_links)

        # 4. TIENDAS CERCANAS SIN STOCK
        nearby_nodes, nearby_links = _create_nearby_stores_from_response(stock_analysis, destination_node_name)
        nodes.extend(nearby_nodes)
        links.extend(nearby_links)

        # 5. RUTA LOGÍSTICA (MEJORADA)
        route_nodes, route_links = _create_logistics_route_enhanced(
            logistica, cedis_analysis, stock_nodes, destination_node_name, data
        )
        nodes.extend(route_nodes)
        links.extend(route_links)

        # 6. FACTORES EXTERNOS (MEJORADOS)
        factor_nodes, factor_links = _create_external_factors_enhanced(
            factores_externos, destination_node_name, request_data
        )
        nodes.extend(factor_nodes)
        links.extend(factor_links)

        # Verificar datos suficientes
        if len(nodes) < 2:
            st.warning("⚠️ Datos insuficientes para generar el gráfico de red")
            render_debug_info(data)
            return

        option = _build_graph_config(nodes, links, categories, codigo_postal)
        st_echarts(option, height="900px", key="logistics_network_centered")
        _render_summary_metrics(data, stock_analysis, logistica, codigo_postal)

    except Exception as e:
        st.error(f"Error generando gráfico de red: {str(e)}")
        render_debug_info(data)
        render_simple_fallback_graph(data)


def render_multiple_delivery_options_graph(data: dict):
    """Renderizar gráfico para múltiples opciones de entrega"""
    st.markdown("### 🔄 Análisis de Múltiples Opciones de Entrega")

    delivery_options = data.get('delivery_options', [])
    recommendation = data.get('recommendation', {})
    total_options = data.get('total_options', len(delivery_options))

    # Información general
    st.info(
        f"📊 **{total_options} opciones** de entrega evaluadas | **Recomendación:** {recommendation.get('opcion', 'N/A').title()}")

    # Crear tabs para cada opción
    if delivery_options:
        tab_names = []
        for i, opt in enumerate(delivery_options):
            opcion_name = opt.get('opcion', f'Opción {i + 1}').replace('_', ' ').title()
            is_recommended = opt.get('opcion') == recommendation.get('opcion')
            tab_names.append(f"{'🏆' if is_recommended else '📦'} {opcion_name}")

        tabs = st.tabs(tab_names)

        for i, (tab, option) in enumerate(zip(tabs, delivery_options)):
            with tab:
                is_recommended = option.get('opcion') == recommendation.get('opcion')
                render_single_delivery_option_graph(option, data, is_recommended, i)

    # Comparación consolidada
    render_delivery_options_comparison(delivery_options, recommendation)


def render_single_delivery_option_graph(option: dict, full_data: dict, is_recommended: bool, option_index: int):
    """Renderizar gráfico para una opción específica de entrega"""

    if is_recommended:
        st.success(f"🏆 **OPCIÓN RECOMENDADA:** {option.get('descripcion', 'N/A')}")
    else:
        st.info(f"📦 **Opción Alternativa:** {option.get('descripcion', 'N/A')}")

    try:
        request_data = full_data.get('request', {})
        factores_externos = full_data.get('factores_externos', {})

        nodes = []
        links = []
        categories = _get_graph_categories()

        # 1. NODO DESTINO
        codigo_postal = request_data.get('codigo_postal', 'N/A')
        destination_node = _create_central_destination_node(codigo_postal)
        nodes.append(destination_node)
        destination_node_name = destination_node['name']

        # 2. NODO PRODUCTO
        product_node = _create_product_node(request_data)
        nodes.append(product_node)

        # 3. TIENDAS ORIGEN (de la opción específica)
        tiendas_origen = option.get('tiendas_origen', [])
        origen_nodes, origen_links = _create_option_stores_nodes(tiendas_origen, product_node['name'])
        nodes.extend(origen_nodes)
        links.extend(origen_links)

        # 4. RUTA LOGÍSTICA DE LA OPCIÓN
        logistica_option = option.get('logistica', {})
        route_nodes, route_links = _create_option_logistics_route(
            logistica_option, origen_nodes, destination_node_name, option
        )
        nodes.extend(route_nodes)
        links.extend(route_links)

        # 5. FACTORES ESPECÍFICOS DE LA OPCIÓN
        factor_nodes, factor_links = _create_option_factors(
            factores_externos, destination_node_name, option
        )
        nodes.extend(factor_nodes)
        links.extend(factor_links)

        # Generar gráfico
        if len(nodes) >= 2:
            option_config = _build_option_graph_config(nodes, links, categories, option, codigo_postal)
            st_echarts(option_config, height="700px", key=f"option_graph_{option_index}")

            # Métricas de la opción
            _render_option_metrics(option, codigo_postal)
        else:
            st.warning("⚠️ Datos insuficientes para esta opción")

    except Exception as e:
        st.error(f"Error en gráfico de opción: {str(e)}")


def _create_option_stores_nodes(tiendas_origen: list, product_node_name: str):
    """Crear nodos de tiendas origen para una opción específica"""
    nodes = []
    links = []

    for i, tienda_nombre in enumerate(tiendas_origen):
        # Determinar tipo de tienda
        es_local = 'Santa Fe' in tienda_nombre or 'Centro' in tienda_nombre
        color = "#10b981" if es_local else "#3b82f6"

        store_node = {
            "name": f"🏪 {tienda_nombre}",
            "value": 80,
            "symbolSize": 80,
            "category": 2,
            "itemStyle": {
                "color": color,
                "borderColor": "#ffffff",
                "borderWidth": 4
            },
            "label": {"show": True, "fontSize": 12, "fontWeight": "600"},
            "tooltip": f"🏪 TIENDA ORIGEN\\nNombre: {tienda_nombre}\\n{'🏠 Local' if es_local else '🌍 Nacional'}"
        }
        nodes.append(store_node)

        # Enlace producto → tienda
        link = {
            "source": product_node_name,
            "target": f"🏪 {tienda_nombre}",
            "lineStyle": {"color": color, "width": 6},
            "label": {"show": True, "formatter": "📦 Stock", "fontSize": 11}
        }
        links.append(link)

    return nodes, links



def _create_option_logistics_route(logistica_option: dict, origen_nodes: list, destination_node_name: str,
                                   option: dict):
    """Crear ruta logística para una opción específica"""
    nodes = []
    links = []

    if not origen_nodes:
        return nodes, links

    try:
        tipo_ruta = logistica_option.get('tipo_ruta', '')
        flota = logistica_option.get('flota', 'N/A')
        tiempo_total = logistica_option.get('tiempo_total_h', 0)

        # HUB de consolidación si existe
        hub_consolidacion = logistica_option.get('hub_consolidacion')
        if hub_consolidacion:
            hub_node = {
                "name": f"🏭 {hub_consolidacion}",
                "value": 90,
                "symbolSize": 85,
                "category": 4,
                "itemStyle": {"color": "#6366f1", "borderWidth": 4, "borderColor": "#ffffff"},
                "label": {"show": True, "fontSize": 12, "fontWeight": "bold"},
                "tooltip": f"🏭 HUB CONSOLIDACIÓN\\nNombre: {hub_consolidacion}\\nTipo: {tipo_ruta}"
            }
            nodes.append(hub_node)

            # Enlaces tiendas → hub
            for origen_node in origen_nodes:
                link = {
                    "source": origen_node['name'],
                    "target": f"🏭 {hub_consolidacion}",
                    "lineStyle": {"color": "#6366f1", "width": 5},
                    "label": {"show": True, "formatter": "📦 Consolidar", "fontSize": 10}
                }
                links.append(link)

            current_node = f"🏭 {hub_consolidacion}"
        else:
            current_node = origen_nodes[0]['name'] if origen_nodes else "Origen"

        # CEDIS intermedio si existe
        cedis_intermedio = logistica_option.get('cedis_intermedio')
        if cedis_intermedio:
            cedis_node = {
                "name": f"🏭 {cedis_intermedio}",
                "value": 85,
                "symbolSize": 80,
                "category": 4,
                "itemStyle": {"color": "#8b5cf6", "borderWidth": 4, "borderColor": "#ffffff"},
                "label": {"show": True, "fontSize": 12, "fontWeight": "bold"},
                "tooltip": f"🏭 CEDIS INTERMEDIO\\nNombre: {cedis_intermedio}\\nSegmentos: {logistica_option.get('segmentos', 1)}"
            }
            nodes.append(cedis_node)

            link = {
                "source": current_node,
                "target": f"🏭 {cedis_intermedio}",
                "lineStyle": {"color": "#8b5cf6", "width": 6},
                "label": {"show": True, "formatter": "🚚 Vía CEDIS", "fontSize": 10}
            }
            links.append(link)
            current_node = f"🏭 {cedis_intermedio}"

        # Flota final
        flota_color = "#3b82f6" if 'FI' in flota else "#8b5cf6"
        flota_icon = "🚚" if 'FI' in flota else "🚛"

        flota_node = {
            "name": f"{flota_icon} {flota}",
            "value": 85,
            "symbolSize": 75,
            "category": 5,
            "itemStyle": {"color": flota_color, "borderWidth": 4, "borderColor": "#ffffff"},
            "label": {"show": True, "fontSize": 12, "fontWeight": "bold"},
            "tooltip": f"{flota_icon} FLOTA FINAL\\nTipo: {flota}\\nTiempo: {tiempo_total:.1f}h\\nCosto: ${option.get('costo_envio', 0):,.2f}"
        }
        nodes.append(flota_node)

        # Enlaces finales
        link = {
            "source": current_node,
            "target": f"{flota_icon} {flota}",
            "lineStyle": {"color": flota_color, "width": 7},
            "label": {"show": True, "formatter": "🚚 Recogida", "fontSize": 10}
        }
        links.append(link)

        link_final = {
            "source": f"{flota_icon} {flota}",
            "target": destination_node_name,
            "lineStyle": {"color": "#1e40af", "width": 10, "shadowBlur": 15},
            "label": {
                "show": True,
                "formatter": f"🎯 Entrega ({tiempo_total:.1f}h)",
                "fontSize": 13,
                "fontWeight": "bold",
                "color": "#1e40af"
            }
        }
        links.append(link_final)

    except Exception as e:
        st.error(f"Error creando ruta de opción: {str(e)}")

    return nodes, links


def _create_option_factors(factores_externos: dict, destination_node_name: str, option: dict):
    """Crear factores específicos para una opción"""
    nodes = []
    links = []

    try:
        probabilidad = option.get('probabilidad_cumplimiento', 0)
        costo = option.get('costo_envio', 0)
        tipo_entrega = option.get('tipo_entrega', 'STANDARD')

        # Factor de probabilidad
        prob_color = "#10b981" if probabilidad >= 0.8 else "#f59e0b" if probabilidad >= 0.6 else "#ef4444"
        prob_node = {
            "name": f"📊 Prob. {probabilidad:.0%}",
            "value": 60,
            "symbolSize": 60,
            "category": 7,
            "itemStyle": {"color": prob_color},
            "label": {"show": True, "fontSize": 10},
            "tooltip": f"📊 PROBABILIDAD CUMPLIMIENTO\\n{probabilidad:.1%} de éxito\\nTipo: {tipo_entrega}"
        }
        nodes.append(prob_node)

        link = {
            "source": f"📊 Prob. {probabilidad:.0%}",
            "target": destination_node_name,
            "lineStyle": {"color": prob_color, "width": 4, "type": "dashed"},
            "label": {"show": True, "formatter": "Riesgo", "fontSize": 9}
        }
        links.append(link)

        # Factor de costo si es relevante
        if costo > 1000:
            costo_node = {
                "name": f"💰 ${costo:,.0f}",
                "value": 55,
                "symbolSize": 55,
                "category": 7,
                "itemStyle": {"color": "#f59e0b"},
                "label": {"show": True, "fontSize": 10},
                "tooltip": f"💰 COSTO ELEVADO\\n${costo:,.2f}\\nImpacto financiero"
            }
            nodes.append(costo_node)

            link = {
                "source": f"💰 ${costo:,.0f}",
                "target": destination_node_name,
                "lineStyle": {"color": "#f59e0b", "width": 3, "type": "dashed"},
                "label": {"show": True, "formatter": "Costo", "fontSize": 9}
            }
            links.append(link)

    except Exception as e:
        st.error(f"Error creando factores de opción: {str(e)}")

    return nodes, links


def _create_logistics_route_enhanced(logistica: dict, cedis_analysis, stock_nodes: list, destination_node_name: str,
                                     full_data: dict):
    """Crear ruta logística MEJORADA con mejor detección de CEDIS"""
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
        cedis_intermedio = logistica.get('cedis_intermedio')

        # DETECTAR USO DE CEDIS (MEJORADO)
        usa_cedis = (
                'cedis' in tipo_ruta.lower() or
                cedis_intermedio is not None or
                'compleja' in tipo_ruta.lower() or
                (cedis_analysis and isinstance(cedis_analysis, dict) and cedis_analysis.get('cedis_seleccionado'))
        )

        # RUTA VÍA CEDIS
        if usa_cedis:
            cedis_info = None

            # Prioridad 1: CEDIS del análisis detallado
            if cedis_analysis and isinstance(cedis_analysis, dict):
                cedis_seleccionado = cedis_analysis.get('cedis_seleccionado', {})
                if cedis_seleccionado:
                    cedis_info = cedis_seleccionado

            # Prioridad 2: CEDIS de logística
            elif cedis_intermedio:
                cedis_info = {
                    'nombre': cedis_intermedio,
                    'distancia_origen_cedis_km': distancia_total * 0.6,
                    'distancia_cedis_destino_km': distancia_total * 0.4,
                    'score': 0,
                    'tiempo_procesamiento_h': 4.0
                }

            if cedis_info:
                cedis_nombre = cedis_info.get('nombre', 'CEDIS')
                dist_origen_cedis = cedis_info.get('distancia_origen_cedis_km', 0)
                dist_cedis_destino = cedis_info.get('distancia_cedis_destino_km', 0)

                # Crear nodo CEDIS
                cedis_node = {
                    "name": f"🏭 {cedis_nombre}",
                    "value": 80,
                    "symbolSize": 85,
                    "category": 4,
                    "itemStyle": {"color": "#6366f1", "borderWidth": 4, "borderColor": "#ffffff"},
                    "label": {"show": True, "fontSize": 12, "fontWeight": "bold"},
                    "tooltip": f"🏭 CENTRO DE DISTRIBUCIÓN\\nNombre: {cedis_nombre}\\nScore: {cedis_info.get('score', 0):.2f}\\nProcesamiento: {cedis_info.get('tiempo_procesamiento_h', 0):.1f}h"
                }
                nodes.append(cedis_node)

                # Enlace tienda → CEDIS
                links.append({
                    "source": current_node,
                    "target": f"🏭 {cedis_nombre}",
                    "lineStyle": {"color": "#6366f1", "width": 6},
                    "label": {"show": True, "formatter": f"📦 {dist_origen_cedis:.0f}km", "fontSize": 11}
                })

                current_node = f"🏭 {cedis_nombre}"
                distancia_restante = dist_cedis_destino
            else:
                distancia_restante = distancia_total
        else:
            # Ruta directa
            distancia_restante = distancia_total

        # CREAR NODO DE FLOTA/CARRIER
        flota_icon = "🚚" if 'FI' in flota else "🚛"
        flota_color = "#3b82f6" if 'FI' in flota else "#8b5cf6"
        flota_category = 5 if 'FI' in flota else 6

        flota_node = {
            "name": f"{flota_icon} {carrier}",
            "value": 90,
            "symbolSize": 80,
            "category": flota_category,
            "itemStyle": {"color": flota_color, "borderWidth": 4, "borderColor": "#ffffff"},
            "label": {"show": True, "fontSize": 12, "fontWeight": "bold"},
            "tooltip": f"{flota_icon} FLOTA\\nCarrier: {carrier}\\nTipo: {flota}\\nTiempo: {logistica.get('tiempo_total_h', 0):.1f}h\\nDistancia: {distancia_total:.1f}km"
        }
        nodes.append(flota_node)

        # Enlaces finales
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
        st.error(f"Error creando ruta logística mejorada: {str(e)}")

    return nodes, links


def _create_stock_stores_from_response(stock_analysis: dict, product_node_name: str):
    """Crear tiendas con stock disponible desde la respuesta del API"""
    nodes = []
    links = []

    stock_encontrado = stock_analysis.get('stock_encontrado', [])
    plan_asignacion = stock_analysis.get('asignacion_detallada', {}).get('plan_asignacion', [])

    # Usar plan de asignación si está disponible, sino usar stock encontrado
    tiendas_con_stock = plan_asignacion if plan_asignacion else stock_encontrado

    for tienda in tiendas_con_stock:
        nombre_tienda = tienda.get('nombre_tienda', 'Tienda')
        stock_disponible = tienda.get('stock_disponible', 0)
        distancia_km = tienda.get('distancia_km', 0)

        # Determinar si es local
        es_local = tienda.get('es_local', False) or distancia_km == 0

        # Nodo de tienda con inventario
        store_node = {
            "name": f"🏪 {nombre_tienda}",
            "value": stock_disponible * 12,
            "symbolSize": 85 if es_local else 75,
            "category": 2,
            "itemStyle": {
                "color": "#10b981" if es_local else "#3b82f6",
                "borderColor": "#ffffff",
                "borderWidth": 4,
                "shadowBlur": 10,
                "shadowColor": "rgba(16, 185, 129, 0.3)" if es_local else "rgba(59, 130, 246, 0.3)"
            },
            "label": {
                "show": True,
                "fontSize": 12,
                "fontWeight": "600"
            },
            "tooltip": f"🏪 TIENDA CON INVENTARIO\\nNombre: {nombre_tienda}\\n✅ Stock disponible: {stock_disponible}\\n📏 Distancia: {distancia_km:.1f}km\\n{'🏠 Local' if es_local else '🚚 Remota'}"
        }
        nodes.append(store_node)

        # Enlace producto → tienda con inventario
        link = {
            "source": product_node_name,
            "target": f"🏪 {nombre_tienda}",
            "lineStyle": {
                "color": "#10b981" if es_local else "#3b82f6",
                "width": 8,
                "shadowBlur": 6,
                "shadowColor": "rgba(16, 185, 129, 0.2)" if es_local else "rgba(59, 130, 246, 0.2)"
            },
            "label": {
                "show": True,
                "formatter": f"✅ {stock_disponible} disponibles",
                "fontSize": 11,
                "fontWeight": "600",
                "color": "#10b981" if es_local else "#3b82f6"
            }
        }
        links.append(link)

    return nodes, links


def _create_external_factors_enhanced(factores_externos: dict, destination_node_name: str, request_data: dict):
    """Crear factores externos MEJORADOS con mapeo específico del CP"""
    nodes = []
    links = []

    try:
        # Obtener CP específico
        codigo_postal = request_data.get('codigo_postal', destination_node_name.replace('🎯 CP ', ''))
        zona_seguridad = factores_externos.get('zona_seguridad', 'N/A')
        trafico = factores_externos.get('trafico_nivel', 'N/A')
        clima = factores_externos.get('condicion_clima', 'N/A')
        evento = factores_externos.get('evento_detectado', 'Normal')
        factor_demanda = factores_externos.get('factor_demanda', 1.0)

        # NODO CENTRAL DE FACTORES DEL CP
        cp_factors_node = {
            "name": f"📍 Factores CP {codigo_postal}",
            "value": 75,
            "symbolSize": 75,
            "category": 7,
            "itemStyle": {"color": "#f59e0b", "borderWidth": 3, "borderColor": "#ffffff"},
            "label": {"show": True, "fontSize": 11, "fontWeight": "600"},
            "tooltip": f"📍 FACTORES ESPECÍFICOS CP {codigo_postal}\\n🛡️ Zona: {zona_seguridad}\\n🚦 Tráfico: {trafico}\\n🌤️ Clima: {clima}\\n📊 Demanda: {factor_demanda}x\\n🎉 Evento: {evento}"
        }
        nodes.append(cp_factors_node)

        # Enlace principal factores → destino
        factor_link = {
            "source": f"📍 Factores CP {codigo_postal}",
            "target": destination_node_name,
            "lineStyle": {"color": "#f59e0b", "width": 8, "shadowBlur": 10},
            "label": {"show": True, "formatter": "Impacto Local", "fontSize": 12, "fontWeight": "bold"}
        }
        links.append(factor_link)

        # FACTORES ESPECÍFICOS RELEVANTES
        relevant_factors = []

        if trafico in ['Alto', 'Crítico']:
            relevant_factors.append({
                "name": f"🚦 Tráfico {trafico}",
                "color": "#f59e0b",
                "impact": f"🚗 Tráfico {trafico}\\nImpacto en tiempo de entrega"
            })

        if zona_seguridad in ['Amarilla', 'Roja']:
            color = "#f59e0b" if zona_seguridad == 'Amarilla' else "#ef4444"
            relevant_factors.append({
                "name": f"🛡️ Zona {zona_seguridad}",
                "color": color,
                "impact": f"⚠️ Zona {zona_seguridad}\\nRequiere precauciones especiales"
            })

        if factor_demanda > 1.5:
            relevant_factors.append({
                "name": f"📈 Demanda Alta",
                "color": "#8b5cf6",
                "impact": f"📊 Factor demanda: {factor_demanda}x\\nTemporada de alta demanda"
            })

        if evento != 'Normal':
            relevant_factors.append({
                "name": f"🎉 {evento}",
                "color": "#0ea5e9",
                "impact": f"🎄 Evento especial: {evento}\\nImpacto en operaciones"
            })

        if 'Lluvioso' in clima or 'Frio' in clima:
            relevant_factors.append({
                "name": f"🌤️ {clima}",
                "color": "#06b6d4",
                "impact": f"🌡️ Condición: {clima}\\nPuede afectar tiempos"
            })

        # Crear nodos y enlaces para factores relevantes
        for factor in relevant_factors:
            factor_node = {
                "name": factor["name"],
                "value": 50,
                "symbolSize": 50,
                "category": 7,
                "itemStyle": {"color": factor["color"], "borderWidth": 2, "borderColor": "#ffffff"},
                "label": {"show": True, "fontSize": 10},
                "tooltip": factor["impact"]
            }
            nodes.append(factor_node)

            # Enlace factor específico → factores del CP
            factor_link = {
                "source": factor["name"],
                "target": f"📍 Factores CP {codigo_postal}",
                "lineStyle": {"color": factor["color"], "width": 3, "type": "dashed", "opacity": 0.7},
                "label": {"show": True, "formatter": "Contribuye", "color": factor["color"], "fontSize": 8}
            }
            links.append(factor_link)

    except Exception as e:
        st.error(f"Error creando factores mejorados: {str(e)}")

    return nodes, links


def _build_option_graph_config(nodes: list, links: list, categories: list, option: dict, codigo_postal: str):
    """Configuración de gráfico para una opción específica"""
    opcion_name = option.get('opcion', 'Opción').replace('_', ' ').title()
    tipo_entrega = option.get('tipo_entrega', 'STANDARD')

    return {
        "title": {
            "text": f"🎯 {opcion_name} → CP {codigo_postal}",
            "subtext": f"Tipo: {tipo_entrega} | Costo: ${option.get('costo_envio', 0):,.0f} | Prob: {option.get('probabilidad_cumplimiento', 0):.0%}",
            "top": "15px",
            "left": "center",
            "textStyle": {"fontSize": 18, "fontWeight": "600", "color": "#1e293b"},
            "subtextStyle": {"fontSize": 11, "color": "#64748b"}
        },
        "tooltip": {
            "trigger": "item",
            "backgroundColor": "#ffffff",
            "borderColor": "#e2e8f0",
            "borderWidth": 1,
            "borderRadius": 8,
            "textStyle": {"color": "#1e293b", "fontSize": 12}
        },
        "legend": {
            "data": [cat["name"] for cat in categories],
            "top": "50px",
            "orient": "horizontal",
            "textStyle": {"fontSize": 10, "color": "#1e293b"}
        },
        "series": [{
            "type": "graph",
            "layout": "force",
            "data": nodes,
            "links": links,
            "categories": categories,
            "roam": True,
            "draggable": True,
            "symbol": "circle",
            "focusNodeAdjacency": True,
            "force": {
                "repulsion": 1500,
                "gravity": 0.2,
                "edgeLength": [100, 300],
                "layoutAnimation": True
            },
            "emphasis": {
                "focus": "adjacency",
                "lineStyle": {"width": 10, "opacity": 1},
                "itemStyle": {"shadowBlur": 15, "borderWidth": 4}
            },
            "lineStyle": {"curveness": 0.2, "opacity": 0.8}
        }],
        "animationDuration": 1500
    }


def _render_option_metrics(option: dict, codigo_postal: str):
    """Renderizar métricas específicas de una opción"""
    st.markdown(f"### 📊 Métricas - {option.get('opcion', 'Opción').replace('_', ' ').title()}")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        costo = option.get('costo_envio', 0)
        st.metric("💰 Costo Envío", f"${costo:,.2f}")

    with col2:
        prob = option.get('probabilidad_cumplimiento', 0)
        st.metric("📈 Probabilidad", f"{prob:.1%}")

    with col3:
        fecha_entrega = option.get('fecha_entrega', 'N/A')
        if 'T' in str(fecha_entrega):
            fecha_display = fecha_entrega.split('T')[0]
        else:
            fecha_display = str(fecha_entrega)
        st.metric("📅 Fecha Entrega", fecha_display)

    with col4:
        tiempo = option.get('logistica', {}).get('tiempo_total_h', 0)
        st.metric("⏱️ Tiempo Total", f"{tiempo:.1f}h")


def render_delivery_options_comparison(delivery_options: list, recommendation: dict):
    """Renderizar tabla comparativa de todas las opciones"""
    st.markdown("### 📊 Comparación de Opciones")

    import pandas as pd

    comparison_data = []
    for i, option in enumerate(delivery_options):
        is_recommended = option.get('opcion') == recommendation.get('opcion')

        comparison_data.append({
            'Opción': option.get('opcion', f'Opción {i + 1}').replace('_', ' ').title(),
            'Descripción': option.get('descripcion', 'N/A'),
            'Tipo Entrega': option.get('tipo_entrega', 'N/A'),
            'Fecha Entrega': option.get('fecha_entrega', 'N/A').split('T')[0] if 'T' in str(
                option.get('fecha_entrega', '')) else option.get('fecha_entrega', 'N/A'),
            'Costo ($)': f"{option.get('costo_envio', 0):,.2f}",
            'Probabilidad': f"{option.get('probabilidad_cumplimiento', 0):.1%}",
            'Tiempo (h)': f"{option.get('logistica', {}).get('tiempo_total_h', 0):.1f}",
            'Tiendas Origen': ', '.join(option.get('tiendas_origen', [])),
            'Recomendada': '🏆 SÍ' if is_recommended else '❌ No'
        })

    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True)

    # Métricas consolidadas
    st.markdown("#### 📈 Resumen Comparativo")
    col1, col2, col3 = st.columns(3)

    with col1:
        costos = [opt.get('costo_envio', 0) for opt in delivery_options]
        st.metric("💰 Rango de Costos", f"${min(costos):,.0f} - ${max(costos):,.0f}")

    with col2:
        probabilidades = [opt.get('probabilidad_cumplimiento', 0) for opt in delivery_options]
        st.metric("📊 Rango Probabilidades", f"{min(probabilidades):.0%} - {max(probabilidades):.0%}")

    with col3:
        st.metric("📦 Opción Recomendada", recommendation.get('opcion', 'N/A').replace('_', ' ').title())


def _create_nearby_stores_from_response(stock_analysis: dict, destination_node_name: str):
    """Crear tiendas cercanas sin stock"""
    nodes = []
    links = []

    tiendas_cercanas = stock_analysis.get('tiendas_cercanas', [])
    stock_encontrado_ids = {t.get('tienda_id') for t in stock_analysis.get('stock_encontrado', [])}

    for tienda in tiendas_cercanas:
        # Solo mostrar si NO tiene stock
        if tienda.get('tienda_id') not in stock_encontrado_ids:
            nombre = tienda.get('nombre', 'Tienda')
            distancia = tienda.get('distancia_km', 0)

            store_node = {
                "name": f"🏪 {nombre}",
                "value": 30,
                "symbolSize": 50,
                "category": 3,
                "itemStyle": {
                    "color": "#94a3b8",
                    "opacity": 0.6,
                    "borderColor": "#64748b",
                    "borderWidth": 2
                },
                "label": {
                    "show": True,
                    "fontSize": 10,
                    "color": "#64748b"
                },
                "tooltip": f"🏪 TIENDA CERCANA\\nNombre: {nombre}\\nDistancia: {distancia:.1f} km\\n❌ Sin stock disponible"
            }
            nodes.append(store_node)

            # Enlace punteado a destino
            link = {
                "source": f"🏪 {nombre}",
                "target": destination_node_name,
                "lineStyle": {
                    "color": "#94a3b8",
                    "width": 2,
                    "type": "dashed",
                    "opacity": 0.5
                },
                "label": {
                    "show": True,
                    "formatter": f"📍 {distancia:.1f}km",
                    "color": "#64748b",
                    "fontSize": 9
                }
            }
            links.append(link)

    return nodes, links


def _create_logistics_route_from_response(logistica: dict, cedis_analysis, stock_nodes: list,
                                          destination_node_name: str):
    """Crear ruta logística basada en la respuesta del API"""
    nodes = []
    links = []

    if not stock_nodes:
        return nodes, links

    try:
        current_node = stock_nodes[0]['name']
        tipo_ruta = logistica.get('tipo_ruta', '')
        carrier = logistica.get('carrier', 'N/A')
        flota = logistica.get('flota', 'N/A')

        # CASO 1: RUTA VÍA CEDIS
        if 'cedis' in tipo_ruta.lower() and cedis_analysis:
            cedis_seleccionado = cedis_analysis.get('cedis_seleccionado', {})

            if cedis_seleccionado:
                cedis_nombre = cedis_seleccionado.get('nombre', 'CEDIS')

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

                # Enlace tienda → CEDIS
                links.append({
                    "source": current_node,
                    "target": f"🏭 {cedis_nombre}",
                    "lineStyle": {"color": "#6366f1", "width": 6},
                    "label": {"show": True, "formatter": "📦 Envío a CEDIS"}
                })

                current_node = f"🏭 {cedis_nombre}"

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

        # Enlaces finales
        links.append({
            "source": current_node,
            "target": f"{flota_icon} {carrier}",
            "lineStyle": {"color": flota_color, "width": 7},
            "label": {"show": True, "formatter": "🚚 Recogida"}
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
                "formatter": "🎯 ENTREGA FINAL",
                "fontSize": 13,
                "fontWeight": "bold",
                "color": "#1e40af"
            }
        })

    except Exception as e:
        st.error(f"Error creando ruta logística: {str(e)}")

    return nodes, links


def _create_external_factors_from_response(factores_externos: dict, destination_node_name: str):
    """Crear factores externos basados en la respuesta"""
    nodes = []
    links = []

    try:
        zona_seguridad = factores_externos.get('zona_seguridad', 'N/A')
        trafico = factores_externos.get('trafico_nivel', 'N/A')
        clima = factores_externos.get('condicion_clima', 'N/A')
        evento = factores_externos.get('evento_detectado', 'Normal')
        factor_demanda = factores_externos.get('factor_demanda', 1.0)

        relevant_factors = []

        if trafico in ['Alto', 'Crítico']:
            relevant_factors.append({
                "name": f"🚦 Tráfico {trafico}",
                "color": "#f59e0b",
                "impact": f"🚗 Tráfico {trafico}\\nImpacto en entrega"
            })

        if zona_seguridad in ['Amarilla', 'Roja']:
            color = "#f59e0b" if zona_seguridad == 'Amarilla' else "#ef4444"
            relevant_factors.append({
                "name": f"🛡️ Zona {zona_seguridad}",
                "color": color,
                "impact": f"⚠️ Zona {zona_seguridad}\\nRequiere precauciones"
            })

        if factor_demanda > 1.5:
            relevant_factors.append({
                "name": f"📈 Demanda x{factor_demanda:.1f}",
                "color": "#8b5cf6",
                "impact": f"📊 Factor demanda: {factor_demanda}x\\nTemporada alta"
            })

        if evento != 'Normal':
            relevant_factors.append({
                "name": f"🎉 {evento}",
                "color": "#0ea5e9",
                "impact": f"🎄 Evento: {evento}\\nImpacto especial"
            })

        if 'Frio' in clima or 'Lluvia' in clima:
            relevant_factors.append({
                "name": f"🌤️ {clima}",
                "color": "#06b6d4",
                "impact": f"🌡️ Clima: {clima}\\nCondiciones especiales"
            })

        for factor in relevant_factors:
            factor_node = {
                "name": factor["name"],
                "value": 55,
                "symbolSize": 55,
                "category": 7,
                "itemStyle": {"color": factor["color"]},
                "label": {"show": True, "fontSize": 10},
                "tooltip": factor["impact"]
            }
            nodes.append(factor_node)

            factor_link = {
                "source": factor["name"],
                "target": destination_node_name,
                "lineStyle": {
                    "color": factor["color"],
                    "width": 4,
                    "type": "dashed",
                    "opacity": 0.8
                },
                "label": {
                    "show": True,
                    "formatter": "Impacto",
                    "color": factor["color"],
                    "fontSize": 9
                }
            }
            links.append(factor_link)

    except Exception as e:
        st.error(f"Error creando factores: {str(e)}")

    return nodes, links


def _build_graph_config(nodes: list, links: list, categories: list, codigo_postal: str):
    """Configuración del gráfico robusta"""
    return {
        "title": {
            "text": f"🎯 Red Logística → CP {codigo_postal}",
            "subtext": f"Análisis de flujo operacional | {len(nodes)} nodos | {len(links)} conexiones",
            "top": "15px",
            "left": "center",
            "textStyle": {
                "fontSize": 20,
                "fontWeight": "600",
                "color": "#1e293b"
            },
            "subtextStyle": {
                "fontSize": 12,
                "color": "#64748b"
            }
        },
        "tooltip": {
            "trigger": "item",
            "backgroundColor": "#ffffff",
            "borderColor": "#e2e8f0",
            "borderWidth": 1,
            "borderRadius": 8,
            "textStyle": {"color": "#1e293b", "fontSize": 12}
        },
        "legend": {
            "data": [cat["name"] for cat in categories],
            "top": "60px",
            "orient": "horizontal",
            "textStyle": {
                "fontSize": 11,
                "color": "#1e293b"
            }
        },
        "series": [{
            "type": "graph",
            "layout": "force",
            "data": nodes,
            "links": links,
            "categories": categories,
            "roam": True,
            "draggable": True,
            "symbol": "circle",
            "focusNodeAdjacency": True,
            "force": {
                "repulsion": 1800,
                "gravity": 0.15,
                "edgeLength": [120, 350],
                "layoutAnimation": True
            },
            "emphasis": {
                "focus": "adjacency",
                "lineStyle": {"width": 12, "opacity": 1},
                "itemStyle": {
                    "shadowBlur": 20,
                    "shadowColor": "rgba(30, 64, 175, 0.4)",
                    "borderWidth": 5,
                    "borderColor": "#ffffff"
                }
            },
            "lineStyle": {
                "curveness": 0.25,
                "opacity": 0.8
            }
        }],
        "animationDuration": 2000,
        "animationEasingUpdate": "cubicOut"
    }


def _render_summary_metrics(data: dict, stock_analysis: dict, logistica: dict, codigo_postal: str):
    """Métricas de resumen robustas"""
    st.markdown(f"### 📊 Resumen Logístico → CP {codigo_postal}")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("**🎯 Destino**")
        st.info(f"**CP:** {codigo_postal}")
        zona_seguridad = data.get('factores_externos', {}).get('zona_seguridad', 'N/A')
        color = "🟢" if zona_seguridad == 'Verde' else "🟡" if zona_seguridad == 'Amarilla' else "🔴"
        st.info(f"**Zona:** {color} {zona_seguridad}")

    with col2:
        st.markdown("**🏪 Tiendas**")
        tiendas_con_stock = len(stock_analysis.get('stock_encontrado', []))
        tiendas_cercanas = len(stock_analysis.get('tiendas_cercanas', []))
        st.info(f"**Con stock:** {tiendas_con_stock}")
        st.info(f"**Cercanas:** {tiendas_cercanas}")

    with col3:
        st.markdown("**🚚 Logística**")
        tipo_ruta = logistica.get('tipo_ruta', 'N/A')
        carrier = logistica.get('carrier', 'N/A')
        st.info(f"**Tipo:** {tipo_ruta}")
        st.info(f"**Carrier:** {carrier}")

    with col4:
        st.markdown("**📈 Resultados**")
        tiempo_total = logistica.get('tiempo_total_h', 0)
        probabilidad = data.get('resultado_final', {}).get('probabilidad_exito', 0)
        st.info(f"**Tiempo:** {tiempo_total:.1f}h")
        st.info(f"**Éxito:** {probabilidad:.1%}")


def render_debug_info(data: dict):
    """Mostrar información de debug cuando hay errores"""
    with st.expander("🔍 Debug - Información de datos", expanded=False):
        st.write("**Request:**", data.get('request', {}))
        st.write("**Logística:**", data.get('logistica_entrega', {}))
        st.write("**Stock Analysis:**", data.get('evaluacion_detallada', {}).get('stock_analysis', {}))
        st.write("**CEDIS Analysis:**", data.get('evaluacion_detallada', {}).get('cedis_analysis'))


def render_simple_fallback_graph(data: dict):
    """Gráfico simple como fallback si hay errores"""
    st.info("🔄 Mostrando versión simplificada del gráfico...")

    request_data = data.get('request', {})
    logistica = data.get('logistica_entrega', {})
    sku_id = request_data.get('sku_id', 'Producto')
    carrier = logistica.get('carrier', 'Carrier')
    codigo_postal = request_data.get('codigo_postal', 'Destino')

    simple_nodes = [
        {
            "name": f"📦 {sku_id}",
            "value": 50,
            "symbolSize": 60,
            "category": 0,
            "itemStyle": {"color": "#0ea5e9"}
        },
        {
            "name": f"🚚 {carrier}",
            "value": 70,
            "symbolSize": 80,
            "category": 1,
            "itemStyle": {"color": "#10b981"}
        },
        {
            "name": f"🎯 CP {codigo_postal}",
            "value": 100,
            "symbolSize": 90,
            "category": 2,
            "itemStyle": {"color": "#1e40af"}
        }
    ]

    simple_links = [
        {
            "source": f"📦 {sku_id}",
            "target": f"🚚 {carrier}",
            "lineStyle": {"color": "#10b981", "width": 5}
        },
        {
            "source": f"🚚 {carrier}",
            "target": f"🎯 CP {codigo_postal}",
            "lineStyle": {"color": "#1e40af", "width": 5}
        }
    ]

    simple_categories = [
        {"name": "Producto", "itemStyle": {"color": "#0ea5e9"}},
        {"name": "Transporte", "itemStyle": {"color": "#10b981"}},
        {"name": "Destino", "itemStyle": {"color": "#1e40af"}}
    ]

    simple_option = {
        "title": {"text": "Flujo Logístico Simplificado", "left": "center"},
        "tooltip": {"trigger": "item"},
        "legend": {"data": ["Producto", "Transporte", "Destino"], "top": "30px"},
        "series": [{
            "type": "graph",
            "layout": "force",
            "data": simple_nodes,
            "links": simple_links,
            "categories": simple_categories,
            "roam": True,
            "force": {"repulsion": 1000, "gravity": 0.2}
        }]
    }

    st_echarts(simple_option, height="400px")


def render_delivery_summary(data: dict):
    """Renderizar resumen adaptado al nuevo response"""
    request_data = data.get('request', {})
    fecha_compra_str = request_data.get('fecha_compra', '')
    fecha_entrega_str = data.get('resultado_final', {}).get('fecha_entrega_estimada', '')
    rango_horario = data.get('resultado_final', {}).get('ventana_entrega', {})
    dias_entrega = calcular_llegada_relativa(fecha_compra_str, fecha_entrega_str)

    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg, #F2E9E4, #E8DCCF);
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        border: 2px solid #C8B8A1;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    '>
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; text-align: center;'>
            <div>
                <h4 style='color: #6B5B73; margin: 0; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;'>📅 Fecha de Compra</h4>
                <p style='color: #4A4A4A; font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0;'>{format_datetime(fecha_compra_str) if fecha_compra_str else "N/A"}</p>
            </div>
            <div>
                <h4 style='color: #6B5B73; margin: 0; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;'>🎯 Fecha de Entrega</h4>
                <p style='color: #4A4A4A; font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0;'>{format_datetime(fecha_entrega_str) if fecha_entrega_str else "N/A"}</p>
            </div>
            <div>
                <h4 style='color: #6B5B73; margin: 0; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;'>⏰ Llega en</h4>
                <p style='color: #E07A5F; font-size: 1.3rem; font-weight: 700; margin: 0.5rem 0;'>{dias_entrega}</p>
            </div>
            <div>
                <h4 style='color: #6B5B73; margin: 0; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;'>🕐 Horario</h4>
                <p style='color: #4A4A4A; font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0;'>{rango_horario.get("inicio", "N/A")} - {rango_horario.get("fin", "N/A")}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def _get_graph_categories():
    """Categorías con paleta ejecutiva profesional"""
    return [
        {"name": "🎯 Destino", "itemStyle": {"color": "#1e40af"}},  # Corporate Blue
        {"name": "📦 Producto", "itemStyle": {"color": "#0ea5e9"}},  # Sky Blue
        {"name": "🏪 Con Inventario", "itemStyle": {"color": "#10b981"}},  # Professional Green
        {"name": "🏪 Sin Inventario", "itemStyle": {"color": "#94a3b8"}},  # Light Gray
        {"name": "🏭 CEDIS", "itemStyle": {"color": "#6366f1"}},  # Indigo
        {"name": "🚚 Flota Interna", "itemStyle": {"color": "#3b82f6"}},  # Bright Blue
        {"name": "🚛 Flota Externa", "itemStyle": {"color": "#8b5cf6"}},  # Purple
        {"name": "⚠️ Factores", "itemStyle": {"color": "#f59e0b"}},  # Executive Amber
        {"name": "🔄 Alternativas", "itemStyle": {"color": "#64748b"}}  # Medium Gray
    ]


def _create_central_destination_node(codigo_postal: str):
    """Crear el nodo central del destino"""
    return {
        "name": f"🎯 CP {codigo_postal}",
        "value": 100,
        "symbolSize": 90,
        "category": 0,
        "itemStyle": {
            "color": "#1e40af",
            "borderColor": "#ffffff",
            "borderWidth": 4,
            "shadowBlur": 12,
            "shadowColor": "rgba(30, 64, 175, 0.3)"
        },
        "label": {
            "show": True,
            "fontSize": 16,
            "fontWeight": "600",
            "color": "#ffffff"
        },
        "tooltip": f"🎯 DESTINO PRINCIPAL\\nCódigo Postal: {codigo_postal}\\n\\n📍 Ubicación de entrega final"
    }


def _create_product_node(request_data: dict):
    """Crear nodo del producto"""
    sku_id = request_data.get('sku_id', 'N/A')
    cantidad = request_data.get('cantidad', 0)

    return {
        "name": f"📦 {sku_id}",
        "value": cantidad * 15,
        "symbolSize": 75,
        "category": 1,
        "itemStyle": {
            "color": "#0ea5e9",
            "borderColor": "#ffffff",
            "borderWidth": 3,
            "shadowBlur": 8,
            "shadowColor": "rgba(14, 165, 233, 0.3)"
        },
        "label": {
            "show": True,
            "fontSize": 13,
            "fontWeight": "600"
        },
        "tooltip": f"📦 PRODUCTO REQUERIDO\\nSKU: {sku_id}\\nCantidad: {cantidad} unidades"
    }


def render_performance_metrics_chart(data: dict):
    """Renderizar gráfico de métricas adaptado"""
    st.markdown("#### 📊 Indicadores de Rendimiento")
    logistica = data.get('logistica_entrega', {})
    resultado = data.get('resultado_final', {})
    tiempo_score = min(100, (24 / max(logistica.get('tiempo_total_h', 24), 1)) * 100)
    costo_score = max(0, 100 - (resultado.get('costo_mxn', 1000) / 50))

    metrics_data = [
        {"name": "Tiempo", "value": tiempo_score},
        {"name": "Costo", "value": min(costo_score, 100)},
        {"name": "Disponibilidad", "value": 85},  # Valor por defecto
        {"name": "Cumplimiento", "value": resultado.get('probabilidad_exito', 0) * 100},
        {"name": "Confianza", "value": resultado.get('confianza_prediccion', 0) * 100}
    ]

    option = {
        "title": {
            "text": "Scores Operacionales",
            "left": "center",
            "textStyle": {
                "fontSize": 18,
                "fontWeight": "600",
                "color": "#1e293b",
                "fontFamily": "Inter, system-ui, sans-serif"
            }
        },
        "tooltip": {
            "trigger": "axis",
            "formatter": "{b}: {c}%",
            "backgroundColor": "#ffffff",
            "borderColor": "#e2e8f0",
            "borderWidth": 1,
            "textStyle": {"color": "#1e293b", "fontFamily": "Inter, system-ui, sans-serif"}
        },
        "radar": {
            "indicator": [{"name": item["name"], "max": 100} for item in metrics_data],
            "shape": "polygon",
            "splitNumber": 5,
            "axisName": {
                "color": "#1e293b",
                "fontFamily": "Inter, system-ui, sans-serif",
                "fontSize": 12
            },
            "splitLine": {"lineStyle": {"color": "#e2e8f0"}},
            "splitArea": {"areaStyle": {"color": ["#f8fafc", "#ffffff"]}}
        },
        "series": [{
            "type": "radar",
            "data": [{
                "value": [item["value"] for item in metrics_data],
                "name": "Scores",
                "areaStyle": {
                    "color": {
                        "type": "radial",
                        "x": 0.5, "y": 0.5, "r": 0.5,
                        "colorStops": [
                            {"offset": 0, "color": "rgba(30, 64, 175, 0.3)"},
                            {"offset": 1, "color": "rgba(59, 130, 246, 0.1)"}
                        ]
                    }
                },
                "lineStyle": {"color": "#1e40af", "width": 3},
                "itemStyle": {"color": "#3b82f6"}
            }]
        }]
    }

    st_echarts(option, height="400px")


def render_process_timeline(data: dict):
    """Timeline adaptado al nuevo response"""
    st.markdown("#### ⏰ Timeline - Proceso")
    logistica = data.get('logistica_entrega', {})
    desglose = logistica.get('desglose_tiempos_h', {})

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("**🔄 Procesamiento del Sistema**")

        pasos_procesamiento = [
            {"paso": "✅ Validación de datos", "status": "✅"},
            {"paso": "✅ Búsqueda de tiendas", "status": "✅"},
            {"paso": "✅ Verificación de stock", "status": "✅"},
            {"paso": "✅ Generación de candidatos", "status": "✅"},
            {"paso": "✅ Selección óptima", "status": "✅"}
        ]

        for paso in pasos_procesamiento:
            status_color = "#34A853"
            st.markdown(f"""
            <div style='
                display: flex;
                align-items: center;
                padding: 0.8rem;
                margin: 0.5rem 0;
                background: #f0f9ff;
                border-left: 4px solid {status_color};
                border-radius: 8px;
            '>
                <span style='font-size: 1.2rem; margin-right: 0.5rem;'>{paso["status"]}</span>
                <span style='color: #374151; font-weight: 500;'>{paso["paso"].replace("✅ ", "")}</span>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("**📦 Timeline de Entrega**")
        timeline_data = [
            {
                "name": "Preparación",
                "duration": desglose.get('preparacion', 1.0),
                "color": "#6D4C41",
                "description": "Picking y empaque en tienda"
            },
            {
                "name": "Tránsito",
                "duration": desglose.get('viaje', 2.7),
                "color": "#2D5016",
                "description": "Transporte hasta destino"
            },
            {
                "name": "Contingencia",
                "duration": desglose.get('contingencia', 0.37),
                "color": "#4A148C",
                "description": "Tiempo de buffer"
            }
        ]

        tiempo_total = sum(item["duration"] for item in timeline_data)
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #f8fafc, #e2e8f0);
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        '>
            <strong style='color: #2D5016; font-size: 1.1rem;'>
                ⏱️ Tiempo Total Estimado: {tiempo_total:.1f} horas
            </strong>
        </div>
        """, unsafe_allow_html=True)


def render_factors_analysis(data: dict):
    """Análisis de factores adaptado"""
    st.markdown("#### 🎯 Análisis de Variables Externas")
    factores = data.get('factores_externos', {})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🌍 Condiciones Operacionales**")
        zona_seguridad = factores.get('zona_seguridad', 'N/A')
        clima = factores.get('condicion_clima', 'N/A')
        trafico = factores.get('trafico_nivel', 'N/A')

        factor_data = [
            {"name": "Demanda", "value": factores.get('factor_demanda', 1) * 100},
            {"name": "Clima", "value": 85 if 'Frio' in clima else 70},
            {"name": "Tráfico", "value": 70 if trafico == 'Moderado' else 50},
            {"name": "Seguridad", "value": 40 if zona_seguridad == 'Roja' else 80}
        ]

        executive_colors = ["#1e40af", "#3b82f6", "#0ea5e9", "#10b981"]

        option = {
            "title": {
                "text": "Impacto Operacional",
                "textStyle": {
                    "fontSize": 16,
                    "color": "#1e293b",
                    "fontFamily": "Inter, system-ui, sans-serif",
                    "fontWeight": "600"
                }
            },
            "tooltip": {
                "formatter": "{b}: {c}%",
                "backgroundColor": "#ffffff",
                "borderColor": "#e2e8f0",
                "textStyle": {"color": "#1e293b", "fontFamily": "Inter, system-ui, sans-serif"}
            },
            "color": executive_colors,
            "series": [{
                "type": "pie",
                "radius": ["35%", "75%"],
                "data": factor_data,
                "emphasis": {"itemStyle": {"shadowBlur": 15, "shadowColor": "rgba(0,0,0,0.1)"}},
                "label": {
                    "fontSize": 11,
                    "color": "#1e293b",
                    "fontFamily": "Inter, system-ui, sans-serif",
                    "fontWeight": "500"
                }
            }]
        }
        st_echarts(option, height="300px")

    with col2:
        st.markdown("**📊 Impactos Cuantificados**")
        tiempo_extra = factores.get('impacto_tiempo_extra_horas', 0)

        st.metric("⏰ Tiempo Adicional", f"{tiempo_extra:.1f} horas")
        st.metric("📊 Factor Demanda", f"{factores.get('factor_demanda', 1.0):.1f}x")

        render_status_card("🌡️", "Clima", clima, "#3b82f6")
        render_status_card("🚦", "Tráfico", trafico, "#0ea5e9")

        if zona_seguridad == 'Roja':
            render_status_card("🔴", "Zona", zona_seguridad, "#ef4444")
        else:
            render_status_card("🟢", "Zona", zona_seguridad, "#10b981")


def render_status_card(icon: str, title: str, value: str, color: str):
    """Renderizar tarjeta de estado ejecutiva"""
    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg, {color}15, {color}08);
        padding: 1rem; 
        border-radius: 8px; 
        border-left: 4px solid {color};
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    '>
        <div style='display: flex; align-items: center; gap: 0.5rem;'>
            <span style='font-size: 1.125rem;'>{icon}</span>
            <strong style='color: #1e293b; font-family: Inter, system-ui, sans-serif;'>{title}:</strong>
            <span style='color: #64748b; font-family: Inter, system-ui, sans-serif;'>{value}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_technical_details(data: dict):
    """Detalles técnicos adaptados"""
    with st.expander("🔍 Detalles Técnicos del Análisis", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**🛣️ Información de Logística**")
            logistica = data.get('logistica_entrega', {})
            st.text(f"Tipo de Ruta: {logistica.get('tipo_ruta', 'N/A')}")
            st.text(f"Distancia: {logistica.get('distancia_km', 0):.2f} km")
            st.text(f"Tiempo Total: {logistica.get('tiempo_total_h', 0):.2f} h")
            st.text(f"Carrier: {logistica.get('carrier', 'N/A')}")

            st.markdown("**📦 Información del Producto**")
            producto = data.get('producto', {})
            st.text(f"Nombre: {producto.get('nombre', 'N/A')}")
            st.text(f"Marca: {producto.get('marca', 'N/A')}")
            st.text(f"Precio: ${producto.get('precio_unitario_mxn', 0):,.2f}")

        with col2:
            st.markdown("**🎯 Resultado Final**")
            resultado = data.get('resultado_final', {})
            st.text(f"Tipo Entrega: {resultado.get('tipo_entrega', 'N/A')}")
            st.text(f"Costo: ${resultado.get('costo_mxn', 0):,.2f}")
            st.text(f"Probabilidad: {resultado.get('probabilidad_exito', 0):.3f}")
            st.text(f"Confianza: {resultado.get('confianza_prediccion', 0):.3f}")

            st.markdown("**🏆 Ganador**")
            ganador = data.get('evaluacion', {}).get('ganador', {})
            st.text(f"Tienda: {ganador.get('tienda', 'N/A')}")
            st.text(f"Score: {ganador.get('score_final', 0):.3f}")

        # DEBUG -> PARA VER EL FK Request
        show_json = st.checkbox("📄 Mostrar Response Completo del API")
        if show_json:
            st.json(data)



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