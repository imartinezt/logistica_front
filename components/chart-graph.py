import streamlit as st

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