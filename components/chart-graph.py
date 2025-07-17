import streamlit as st
from utils.helpers import (
    format_currency, format_percentage, format_datetime, get_delivery_status_badge,
    extract_key_insights, render_comprehensive_evaluation_table
)
from streamlit_echarts import st_echarts


# Métodos principales para graficar la ruta de entrega
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


### Métodos auxiliares
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


def render_debug_info(data: dict):
    """Mostrar información de debug cuando hay errores"""
    with st.expander("🔍 Debug - Información de datos", expanded=False):
        st.write("**Request:**", data.get('request', {}))
        st.write("**Logística:**", data.get('logistica_entrega', {}))
        st.write("**Stock Analysis:**", data.get('evaluacion_detallada', {}).get('stock_analysis', {}))
        st.write("**CEDIS Analysis:**", data.get('evaluacion_detallada', {}).get('cedis_analysis'))


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


### Fallback
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