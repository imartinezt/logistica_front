import streamlit as st
from streamlit_echarts import st_echarts

from components.layout import render_header, render_back_button
from config.settings import Config
from utils.helpers import (
    format_currency, format_percentage, format_datetime, get_delivery_status_badge, extract_key_insights
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

    # Insights clave
    render_key_insights(data)

    # Visualizaciones interactivas
    render_interactive_charts(data)

    # Detalles técnicos
    render_technical_details(data)


def render_main_metrics(data: dict):
    """Renderizar métricas principales"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        costo = data.get('costo_envio_mxn', 0)
        st.metric(
            label="💰 Costo Total",
            value=format_currency(costo),
            delta=None
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        prob = data.get('probabilidad_cumplimiento', 0)
        st.metric(
            label="📈 Probabilidad Éxito",
            value=format_percentage(prob),
            delta=f"Confianza: {format_percentage(data.get('confianza_prediccion', 0))}"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        ruta = data.get('ruta_seleccionada', {})
        tiempo = ruta.get('tiempo_total_horas', 0)
        st.metric(
            label="⏱️ Tiempo Total",
            value=f"{tiempo:.1f} horas",
            delta=f"Distancia: {ruta.get('distancia_total_km', 0):.0f} km"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col4:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        tipo_entrega = data.get('tipo_entrega', 'N/A')
        carrier = data.get('carrier_principal', 'N/A')
        st.markdown("**🚚 Tipo de Entrega**")
        st.markdown(get_delivery_status_badge(tipo_entrega), unsafe_allow_html=True)
        st.markdown(f"**Carrier:** {carrier}")
        st.markdown("</div>", unsafe_allow_html=True)


def render_delivery_promise(data: dict):
    """Renderizar fecha promesa de entrega"""
    fecha_entrega_str = data.get('fecha_entrega_estimada', '')

    if fecha_entrega_str:
        # fecha (sin hora)
        fecha_entrega = format_datetime(fecha_entrega_str)
        rango = data.get('rango_horario', {})

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
    """Crear red dinámica centrada en el código postal destino como nodo principal"""
    st.markdown("#### 🎯 Red Logística Centrada en Destino")
    render_delivery_summary(data)

    request_data = data.get('explicabilidad', {}).get('request_procesado', {})
    factores_externos = data.get('explicabilidad', {}).get('factores_externos', {})
    ruta_seleccionada = data.get('ruta_seleccionada', {})
    analisis_tiendas = data.get('explicabilidad_extendida', {}).get('analisis_tiendas', {})
    datos_geograficos = data.get('explicabilidad_extendida', {}).get('datos_geograficos', {})
    nodes = []
    links = []

    categories = _get_graph_categories()

    # 1. NODO CENTRAL: CÓDIGO POSTAL DESTINO (CORAZÓN DEL GRAFO)
    codigo_postal = request_data.get('codigo_postal', 'N/A')
    destination_node = _create_central_destination_node(codigo_postal, datos_geograficos)
    nodes.append(destination_node)
    destination_node_name = destination_node['name']

    # 2. NODO PRODUCTO/SKU con cantidad requerida
    product_node = _create_product_node(request_data)
    nodes.append(product_node)

    # 3. TIENDAS CERCANAS AL CÓDIGO POSTAL DESTINO (con y sin stock)
    tiendas_destino_nodes, tiendas_destino_links = _create_destination_area_stores(
        datos_geograficos, codigo_postal, destination_node_name
    )
    nodes.extend(tiendas_destino_nodes)
    links.extend(tiendas_destino_links)

    # 4. TIENDA(S) CON STOCK DISPONIBLE (pueden estar lejos)
    tiendas_stock_nodes, tiendas_stock_links = _create_stock_available_stores(
        ruta_seleccionada, product_node['name'], request_data
    )
    nodes.extend(tiendas_stock_nodes)
    links.extend(tiendas_stock_links)

    # 5. MAPEO DINÁMICO DE RUTA LOGÍSTICA COMPLETA
    route_nodes, route_links = _create_complete_logistics_route(
        ruta_seleccionada, tiendas_stock_nodes, destination_node_name
    )
    nodes.extend(route_nodes)
    links.extend(route_links)

    # 6. FACTORES EXTERNOS QUE IMPACTAN AL DESTINO
    factor_nodes, factor_links = _create_destination_impact_factors(
        factores_externos, destination_node_name
    )
    nodes.extend(factor_nodes)
    links.extend(factor_links)

    # 7. CANDIDATOS ALTERNATIVOS (si existen)
    candidate_nodes, candidate_links = _create_alternative_routes(
        data.get('explicabilidad', {}).get('candidatos_lightgbm', []),
        destination_node_name
    )
    nodes.extend(candidate_nodes)
    links.extend(candidate_links)

    option = _build_logistics_graph_config(nodes, links, categories, data, codigo_postal)
    st_echarts(option, height="900px", key="logistics_network_centered")
    _render_logistics_summary_metrics(data, analisis_tiendas, ruta_seleccionada, codigo_postal)


def _get_graph_categories():
    """Categorías con paleta ejecutiva profesional"""
    return [
        {"name": "🎯 Destino", "itemStyle": {"color": "#1e40af"}},        # Corporate Blue
        {"name": "📦 Producto", "itemStyle": {"color": "#0ea5e9"}},       # Sky Blue
        {"name": "🏪 Con Inventario", "itemStyle": {"color": "#10b981"}}, # Professional Green
        {"name": "🏪 Sin Inventario", "itemStyle": {"color": "#94a3b8"}}, # Light Gray
        {"name": "🏭 CEDIS", "itemStyle": {"color": "#6366f1"}},          # Indigo
        {"name": "🚚 Flota Interna", "itemStyle": {"color": "#3b82f6"}},  # Bright Blue
        {"name": "🚛 Flota Externa", "itemStyle": {"color": "#8b5cf6"}},  # Purple
        {"name": "⚠️ Factores", "itemStyle": {"color": "#f59e0b"}},       # Executive Amber
        {"name": "🔄 Alternativas", "itemStyle": {"color": "#64748b"}}    # Medium Gray
    ]


def _create_central_destination_node(codigo_postal: str, datos_geograficos: dict):
    """Crear el nodo central del destino con diseño ejecutivo"""
    destino_coords = datos_geograficos.get('destino', {}).get('coordenadas', {})

    return {
        "name": f"🎯 {codigo_postal}",
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
            "color": "#ffffff",
            "fontFamily": "Inter, system-ui, sans-serif"
        },
        "tooltip": f"🎯 DESTINO PRINCIPAL\\nCódigo Postal: {codigo_postal}\\nLat: {destino_coords.get('lat', 'N/A')}\\nLon: {destino_coords.get('lon', 'N/A')}\\n\\n📍 Ubicación de entrega final"
    }


def _create_product_node(request_data: dict):
    """Crear nodo del producto con estilo ejecutivo"""
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
            "fontWeight": "600",
            "fontFamily": "Inter, system-ui, sans-serif"
        },
        "tooltip": f"📦 PRODUCTO REQUERIDO\\nSKU: {sku_id}\\nCantidad: {cantidad} unidades\\n\\n🛒 Artículo solicitado"
    }



def _create_destination_area_stores(datos_geograficos: dict, codigo_postal: str, destination_node_name: str):
    """Crear tiendas cercanas al código postal destino (con y sin stock)"""
    nodes = []
    links = []

    tiendas_geograficas = datos_geograficos.get('tiendas', [])

    for tienda in tiendas_geograficas:
        nombre = tienda.get('nombre', 'Tienda')
        distancia = tienda.get('distancia_km', 0)
        coords = tienda.get('coordenadas', {})
        seleccionada = tienda.get('seleccionada', False)

        # Tienda cercana al destino (normalmente SIN stock, por eso no fue seleccionada)
        if not seleccionada:
            # Nodo de tienda sin stock (transparente)
            store_node = {
                "name": f"🏪 {nombre}",
                "value": distancia,
                "symbolSize": 60,
                "category": 3,
                "itemStyle": {
                    "color": "#9AA0A6",
                    "opacity": 0.4,
                    "borderColor": "#666",
                    "borderWidth": 2
                },
                "label": {
                    "show": True,
                    "fontSize": 11,
                    "color": "#666"
                },
                "tooltip": f"🏪 TIENDA CERCANA AL DESTINO\\nNombre: {nombre}\\nDistancia al CP {codigo_postal.replace('CP ', '')}: {distancia:.1f} km\\n❌ Sin stock disponible\\nLat: {coords.get('lat', 'N/A')}\\nLon: {coords.get('lon', 'N/A')}"
            }
            nodes.append(store_node)

            # Enlace punteado Tienda sin stock → Destino (proximidad)
            proximity_link = {
                "source": f"🏪 {nombre}",
                "target": destination_node_name,
                "lineStyle": {
                    "color": "#9AA0A6",
                    "width": 3,
                    "type": "dashed",
                    "opacity": 0.5
                },
                "label": {
                    "show": True,
                    "formatter": f"📍 {distancia:.1f}km",
                    "color": "#666"
                }
            }
            links.append(proximity_link)

    return nodes, links


def _create_stock_available_stores(ruta_seleccionada: dict, product_node_name: str, request_data: dict):
    """Crear tiendas con inventario disponible - estilo ejecutivo"""
    nodes = []
    links = []

    ubicaciones = ruta_seleccionada.get('split_inventory', {}).get('ubicaciones', [])

    for ubicacion in ubicaciones:
        nombre_tienda = ubicacion.get('nombre_ubicacion', 'Tienda')
        stock_disponible = ubicacion.get('stock_disponible', 0)
        stock_reservado = ubicacion.get('stock_reservado', 0)
        coords = ubicacion.get('coordenadas', {})
        horario = ubicacion.get('horario_operacion', 'N/A')
        tiempo_prep = ubicacion.get('tiempo_preparacion_horas', 0)

        # Nodo de tienda con inventario
        store_with_stock_node = {
            "name": f"🏪 {nombre_tienda}",
            "value": stock_disponible * 12,
            "symbolSize": 80,
            "category": 2,
            "itemStyle": {
                "color": "#10b981",
                "borderColor": "#ffffff",
                "borderWidth": 4,
                "shadowBlur": 10,
                "shadowColor": "rgba(16, 185, 129, 0.3)"
            },
            "label": {
                "show": True,
                "fontSize": 12,
                "fontWeight": "600",
                "fontFamily": "Inter, system-ui, sans-serif"
            },
            "tooltip": f"🏪 TIENDA CON INVENTARIO\\nUbicación: {nombre_tienda}\\n✅ Stock disponible: {stock_disponible}\\n🔒 Stock reservado: {stock_reservado}\\n⏱️ Tiempo prep: {tiempo_prep}h\\n🕐 Horario: {horario}\\nCoordenadas: {coords.get('lat', 'N/A')}, {coords.get('lon', 'N/A')}"
        }
        nodes.append(store_with_stock_node)

        # Enlace producto → tienda con inventario
        product_to_stock_link = {
            "source": product_node_name,
            "target": f"🏪 {nombre_tienda}",
            "value": request_data.get('cantidad', 0),
            "lineStyle": {
                "color": "#10b981",
                "width": 8,
                "shadowBlur": 6,
                "shadowColor": "rgba(16, 185, 129, 0.2)"
            },
            "label": {
                "show": True,
                "formatter": f"✅ {stock_disponible} disponibles",
                "fontSize": 11,
                "fontWeight": "600",
                "color": "#10b981",
                "fontFamily": "Inter, system-ui, sans-serif"
            }
        }
        links.append(product_to_stock_link)

    return nodes, links


def _create_complete_logistics_route(ruta_seleccionada: dict, tiendas_stock_nodes: list, destination_node_name: str):
    """Mapear la ruta logística completa desde tienda con stock hasta destino"""
    nodes = []
    links = []

    segmentos = ruta_seleccionada.get('segmentos', [])
    ruta_id = ruta_seleccionada.get('ruta_id', '')
    es_ruta_directa = ('direct_' in ruta_id) and (len(segmentos) == 1)
    current_node = None

    # Encontrar la tienda de origen (con stock)
    if tiendas_stock_nodes:
        current_node = tiendas_stock_nodes[0]['name']

    for i, segmento in enumerate(segmentos):
        origen_nombre = segmento.get('origen_nombre', 'Origen')
        destino_nombre = segmento.get('destino_nombre', 'Destino')
        distancia = segmento.get('distancia_km', 0)
        tiempo = segmento.get('tiempo_viaje_horas', 0)
        carrier = segmento.get('carrier', 'Carrier')
        tipo_flota = segmento.get('tipo_flota', 'N/A')

        # CASO ESPECIAL: Ruta Directa (Tienda → Cliente)
        if es_ruta_directa and destino_nombre.lower() in ['cliente', 'cliente final']:
            flota_icon = "🚚" if tipo_flota == "FI" else "🚛"
            flota_label = tipo_flota  # Usar FI/FE directamente
            flota_color = "#C7D3DD" if tipo_flota == "FI" else "#A3A5A8"
            flota_category = 5 if tipo_flota == "FI" else 6

            # (entrega directa)
            flota_directa_node = {
                "name": f"{flota_icon} {carrier} ({flota_label})",
                "value": 90,
                "symbolSize": 80,
                "category": flota_category,
                "itemStyle": {
                    "color": flota_color,
                    "borderWidth": 4,
                    "borderColor": "#888B8D"
                },
                "label": {"show": True, "fontSize": 12, "fontWeight": "bold"},
                "tooltip": f"{flota_icon} FLOTA {flota_label} (ENTREGA DIRECTA)\\nCarrier: {carrier}\\nTipo: {tipo_flota}\\nDistancia: {distancia:.1f}km\\nTiempo: {tiempo:.1f}h\\nEntrega directa desde tienda"
            }
            nodes.append(flota_directa_node)

            # Enlaces: Tienda → Flota → Destino final
            if current_node:
                links.append({
                    "source": current_node,
                    "target": f"{flota_icon} {carrier} ({flota_label})",
                    "lineStyle": {"color": flota_color, "width": 7},
                    "label": {"show": True, "formatter": "Recogida"}
                })

                links.append({ # todo verificar ( duplicado de esta linea factoizar -> nex update )
                    "source": f"{flota_icon} {carrier} ({flota_label})",
                    "target": destination_node_name,
                    "lineStyle": {
                        "color": "#888B8D",
                        "width": 10,
                        "shadowBlur": 15,
                        "shadowColor": "rgba(136,139,141,0.4)"
                    },
                    "label": {
                        "show": True,
                        "formatter": f"🎯 ENTREGA DIRECTA | {tiempo:.1f}h",
                        "fontSize": 13,
                        "fontWeight": "bold",
                        "color": "#888B8D"
                    }
                })

            continue  # Saltar al siguiente segmento

        # CASO 1: Tienda → CEDIS (usar tipo_flota del API)
        elif 'CEDIS' in destino_nombre or 'cedis' in destino_nombre.lower():
            cedis_node = {
                "name": f"🏭 {destino_nombre}",
                "value": 80,
                "symbolSize": 85,
                "category": 4,  # CEDIS
                "itemStyle": {
                    "color": "#B4B7BA",
                    "borderWidth": 4,
                    "borderColor": "#888B8D"
                },
                "label": {"show": True, "fontSize": 12, "fontWeight": "bold"},
                "tooltip": f"🏭 CENTRO DE DISTRIBUCIÓN\\nNombre: {destino_nombre}\\nDistancia desde tienda: {distancia:.1f}km\\nTiempo de traslado: {tiempo:.1f}h\\nCarrier: {carrier}"
            }
            nodes.append(cedis_node)

            flota_icon = "🚚" if tipo_flota == "FI" else "🚛"
            flota_label = tipo_flota  #  FI/FE directamente
            flota_color = "#C7D3DD" if tipo_flota == "FI" else "#A3A5A8"
            flota_category = 5 if tipo_flota == "FI" else 6

            flota_node = {
                "name": f"{flota_icon} {carrier} ({flota_label})",
                "value": 60,
                "symbolSize": 70,
                "category": flota_category,
                "itemStyle": {"color": flota_color, "borderWidth": 3, "borderColor": "#888B8D"},
                "label": {"show": True, "fontSize": 11},
                "tooltip": f"{flota_icon} FLOTA {flota_label}\\nCarrier: {carrier}\\nTipo: {tipo_flota}\\nSegmento: Tienda → CEDIS"
            }
            nodes.append(flota_node)

            # Enlaces: Tienda → Flota → CEDIS
            if current_node:
                links.append({
                    "source": current_node,
                    "target": f"{flota_icon} {carrier} ({flota_label})",
                    "lineStyle": {"color": flota_color, "width": 6},
                    "label": {"show": True, "formatter": "Recogida"}
                })

                links.append({
                    "source": f"{flota_icon} {carrier} ({flota_label})",
                    "target": f"🏭 {destino_nombre}",
                    "lineStyle": {"color": flota_color, "width": 6},
                    "label": {"show": True, "formatter": f"{distancia:.1f}km | {tiempo:.1f}h"}
                })

            current_node = f"🏭 {destino_nombre}"

        # CASO 2: CEDIS → Tienda local (cerca del destino)
        elif 'Liverpool' in destino_nombre and current_node and '🏭' in current_node:
            # Esta es la tienda local cerca del destino
            tienda_local_node = {
                "name": f"🏪 {destino_nombre} (Local)",
                "value": 40,
                "symbolSize": 75,
                "category": 3,  # Sin Stock (es punto de distribución local)
                "itemStyle": {
                    "color": "#D6DBD9",
                    "borderWidth": 3,
                    "borderColor": "#B4B7BA"
                },
                "label": {"show": True, "fontSize": 11},
                "tooltip": f"🏪 TIENDA LOCAL (DISTRIBUCIÓN)\\nNombre: {destino_nombre}\\nFunción: Punto de distribución local\\nTiempo desde CEDIS: {tiempo:.1f}h"
            }
            nodes.append(tienda_local_node)

            # Enlace CEDIS → Tienda Local
            links.append({
                "source": current_node,
                "target": f"🏪 {destino_nombre} (Local)",
                "lineStyle": {"color": "#B4B7BA", "width": 5},
                "label": {"show": True, "formatter": f"Distribución | {tiempo:.1f}h"}
            })

            current_node = f"🏪 {destino_nombre} (Local)"

        # CASO 3: Último tramo complejo → Cliente final (usar tipo_flota del API)
        elif destino_nombre.lower() in ['cliente', 'cliente final'] and not es_ruta_directa:
            flota_icon = "🚚" if tipo_flota == "FI" else "🚛"
            flota_label = tipo_flota
            flota_color = "#C7D3DD" if tipo_flota == "FI" else "#A3A5A8"
            flota_category = 5 if tipo_flota == "FI" else 6

            # Crear nodo de Flota (última milla)
            flota_final_node = {
                "name": f"{flota_icon} {carrier} ({flota_label})",
                "value": 90,
                "symbolSize": 80,
                "category": flota_category,
                "itemStyle": {
                    "color": flota_color,
                    "borderWidth": 4,
                    "borderColor": "#888B8D"
                },
                "label": {"show": True, "fontSize": 12, "fontWeight": "bold"},
                "tooltip": f"{flota_icon} FLOTA {flota_label} (ÚLTIMA MILLA)\\nCarrier: {carrier}\\nTipo: {tipo_flota}\\nTiempo entrega: {tiempo:.1f}h\\nResponsable entrega final"
            }
            nodes.append(flota_final_node)

            # Enlaces: Punto actual → Flota → Destino final
            if current_node:
                links.append({
                    "source": current_node,
                    "target": f"{flota_icon} {carrier} ({flota_label})",
                    "lineStyle": {"color": flota_color, "width": 7},
                    "label": {"show": True, "formatter": "Handoff"}
                })

                links.append({
                    "source": f"{flota_icon} {carrier} ({flota_label})",
                    "target": destination_node_name,
                    "lineStyle": {
                        "color": "#888B8D",
                        "width": 10,
                        "shadowBlur": 15,
                        "shadowColor": "rgba(136,139,141,0.4)"
                    },
                    "label": {
                        "show": True,
                        "formatter": f"🎯 ENTREGA FINAL | {tiempo:.1f}h",
                        "fontSize": 13,
                        "fontWeight": "bold",
                        "color": "#888B8D"
                    }
                })

    return nodes, links


def _create_destination_impact_factors(factores_externos: dict, destination_node_name: str):
    """Crear factores externos que impactan específicamente al destino"""
    nodes = []
    links = []

    temperatura = factores_externos.get('temperatura_celsius', 0)
    lluvia = factores_externos.get('probabilidad_lluvia', 0)
    trafico = factores_externos.get('trafico_nivel', 'N/A')
    zona_seguridad = factores_externos.get('zona_seguridad', 'N/A')
    factor_demanda = factores_externos.get('factor_demanda', 1.0)
    eventos = factores_externos.get('eventos_detectados', [])
    tiempo_extra = factores_externos.get('impacto_tiempo_extra_horas', 0)
    relevant_factors = []

    if lluvia > 20:
        relevant_factors.append({
            "name": f"🌧️ Lluvia {lluvia}%",
            "value": lluvia,
            "color": "#C7D3DD",
            "impact": f"☔ {lluvia}% probabilidad lluvia\\nImpacto: +{tiempo_extra:.1f}h entrega"
        })

    if trafico in ['Alto', 'Crítico']:
        relevant_factors.append({
            "name": f"🚦 Tráfico {trafico}",
            "value": 80,
            "color": "#A3A5A8",
            "impact": f"🚗 Tráfico {trafico}\\nImpacto en última milla"
        })

    if zona_seguridad in ['Amarilla', 'Roja']:
        color = "#B4B7BA" if zona_seguridad == 'Amarilla' else "#A3A5A8"
        relevant_factors.append({
            "name": f"🛡️ Zona {zona_seguridad}",
            "value": 70,
            "color": color,
            "impact": f"⚠️ Zona de seguridad {zona_seguridad}\\nRequiere precauciones especiales"
        })

    if factor_demanda > 1.5:
        relevant_factors.append({
            "name": f"📈 Alta Demanda x{factor_demanda}",
            "value": factor_demanda * 30,
            "color": "#C0C0C0",
            "impact": f"📊 Factor demanda: {factor_demanda}x\\nTemporada alta detectada"
        })

    for evento in eventos:
        relevant_factors.append({
            "name": f"🎉 {evento}",
            "value": 85,
            "color": "#C7D3DD",
            "impact": f"🎄 Evento especial: {evento}\\nAumento demanda y restricciones"
        })

    for factor in relevant_factors:
        factor_node = {
            "name": factor["name"],
            "value": factor["value"],
            "symbolSize": 55,
            "category": 7,
            "itemStyle": {"color": factor["color"]},
            "label": {"show": True, "fontSize": 10},
            "tooltip": factor["impact"]
        }
        nodes.append(factor_node)

        impact_link = {
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
                "color": factor["color"]
            }
        }
        links.append(impact_link)

    return nodes, links


def _create_alternative_routes(candidatos: list, destination_node_name: str):
    """Crear candidatos alternativos (si existen múltiples opciones)"""
    nodes = []
    links = []

    if len(candidatos) <= 1:
        return nodes, links

    top_alternatives = candidatos[1:4]

    for i, candidato in enumerate(top_alternatives):
        ruta = candidato.get('ruta', {})
        score = candidato.get('score_lightgbm', 0)
        ranking = candidato.get('ranking_position', i + 2)
        tiempo = ruta.get('tiempo_total_horas', 0)
        costo = ruta.get('costo_total_mxn', 0)

        # Nodo de ruta alternativa
        alt_node = {
            "name": f"🏆 Alternativa #{ranking}",
            "value": score * 60,
            "symbolSize": 45,
            "category": 8,  # Alternativas
            "itemStyle": {"color": "#B4B7BA", "opacity": 0.6},
            "label": {"show": True, "fontSize": 9},
            "tooltip": f"🏆 RUTA ALTERNATIVA #{ranking}\\nScore: {score:.3f}\\nTiempo: {tiempo:.1f}h\\nCosto: ${costo:.2f}\\nEstado: No seleccionada"
        }
        nodes.append(alt_node)

        # Enlace punteado alternativa → destino
        alt_link = {
            "source": f"🏆 Alternativa #{ranking}",
            "target": destination_node_name,
            "lineStyle": {
                "color": "#B4B7BA",
                "width": 2,
                "type": "dashed",
                "opacity": 0.4
            },
            "label": {"show": False}
        }
        links.append(alt_link)

    return nodes, links


def _build_logistics_graph_config(nodes: list, links: list, categories: list, data: dict, codigo_postal: str):
    """Configuración del gráfico con diseño ejecutivo"""
    return {
        "title": {
            "text": f"🎯 Red Logística → {codigo_postal}",
            "subtext": f"Análisis de flujo operacional | {len(nodes)} nodos | {len(links)} conexiones",
            "top": "15px",
            "left": "center",
            "textStyle": {
                "fontSize": 20,
                "fontWeight": "600",
                "color": "#1e293b",
                "fontFamily": "Inter, system-ui, sans-serif"
            },
            "subtextStyle": {
                "fontSize": 12,
                "color": "#64748b",
                "fontFamily": "Inter, system-ui, sans-serif"
            }
        },
        "tooltip": {
            "trigger": "item",
            "backgroundColor": "#ffffff",
            "borderColor": "#e2e8f0",
            "borderWidth": 1,
            "borderRadius": 8,
            "textStyle": {"color": "#1e293b", "fontSize": 12, "fontFamily": "Inter, system-ui, sans-serif"},
            "formatter": """
            function(params) {
                if (params.dataType === 'node') {
                    let info = '<div style="max-width: 300px; font-family: Inter, system-ui, sans-serif;">';
                    info += '<strong style="color: #1e40af; font-size: 14px; font-weight: 600;">' + params.data.name + '</strong><br/>';
                    if (params.data.tooltip) {
                        info += '<div style="color: #64748b; margin-top: 8px; line-height: 1.5; font-size: 12px;">' + params.data.tooltip.replace(/\\\\n/g, '<br/>') + '</div>';
                    }
                    info += '</div>';
                    return info;
                } else if (params.dataType === 'edge') {
                    return '<div style="font-family: Inter, system-ui, sans-serif;"><strong>' + params.data.source + '</strong><br/>➡️<br/><strong>' + params.data.target + '</strong></div>';
                }
            }
            """
        },
        "legend": {
            "data": [cat["name"] for cat in categories],
            "top": "60px",
            "orient": "horizontal",
            "textStyle": {
                "fontSize": 11,
                "color": "#1e293b",
                "fontFamily": "Inter, system-ui, sans-serif"
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


def _build_graph_config(nodes: list, links: list, categories: list, data: dict, codigo_postal: str):
    """Configuración optimizada del gráfico centrado en destino"""
    return {
        "title": {
            "text": f"🎯 Red Logística → CP {codigo_postal}",
            "subtext": f"Flujo completo desde tienda con stock hasta destino final | {len(nodes)} nodos | {len(links)} conexiones",
            "top": "10px",
            "left": "center",
            "textStyle": {"fontSize": 22, "fontWeight": "bold", "color": "#FF0000"}
        },
        "tooltip": {
            "trigger": "item",
            "backgroundColor": "rgba(255,255,255,0.98)",
            "borderColor": "#FF0000",
            "borderWidth": 3,
            "textStyle": {"color": "#333", "fontSize": 12},
            "formatter": """
            function(params) {
                if (params.dataType === 'node') {
                    let info = '<div style="max-width: 300px;">';
                    info += '<strong style="color: #FF0000; font-size: 14px;">' + params.data.name + '</strong><br/>';
                    if (params.data.tooltip) {
                        info += '<div style="color: #666; margin-top: 8px; line-height: 1.5;">' + params.data.tooltip.replace(/\\\\n/g, '<br/>') + '</div>';
                    }
                    info += '</div>';
                    return info;
                } else if (params.dataType === 'edge') {
                    return '<strong>' + params.data.source + '</strong><br/>➡️<br/><strong>' + params.data.target + '</strong>';
                }
            }
            """
        },
        "legend": {
            "data": [cat["name"] for cat in categories],
            "top": "60px",
            "orient": "horizontal",
            "textStyle": {"fontSize": 11, "color": "#333"}
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
                "repulsion": 2000,
                "gravity": 0.2,
                "edgeLength": [100, 400],
                "layoutAnimation": True
            },
            "emphasis": {
                "focus": "adjacency",
                "lineStyle": {"width": 15, "opacity": 1},
                "itemStyle": {
                    "shadowBlur": 25,
                    "shadowColor": "rgba(255,0,0,0.6)",
                    "borderWidth": 6,
                    "borderColor": "#FFD700"
                }
            },
            "lineStyle": {
                "curveness": 0.3,
                "opacity": 0.9
            }
        }],
        "animationDuration": 4000,
        "animationEasingUpdate": "cubicOut"
    }


def _render_logistics_summary_metrics(data: dict, analisis_tiendas: dict, ruta_seleccionada: dict, codigo_postal: str):
    """Mostrar métricas enfocadas en el destino y la logística"""
    st.markdown(f"### 📊 Resumen Logístico → CP {codigo_postal}")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("**🎯 Destino**")
        st.info(f"**CP:** {codigo_postal}")

        zona_seguridad = data.get('explicabilidad', {}).get('factores_externos', {}).get('zona_seguridad', 'N/A')
        color = "🟢" if zona_seguridad == 'Verde' else "🟡" if zona_seguridad == 'Amarilla' else "🔴"
        st.info(f"**Zona:** {color} {zona_seguridad}")

    with col2:
        st.markdown("**🏪 Tiendas**")
        total_tiendas = analisis_tiendas.get('total_consideradas', 0)
        tiendas_con_stock = analisis_tiendas.get('total_seleccionadas', 0)
        st.info(f"**Con stock:** {tiendas_con_stock}")
        st.info(f"**Evaluadas:** {total_tiendas}")

    with col3:
        st.markdown("**🚚 Logística**")
        segmentos = ruta_seleccionada.get('segmentos', [])
        st.info(f"**Segmentos:** {len(segmentos)}")

        # hay CEDIS??
        hay_cedis = any('CEDIS' in seg.get('destino_nombre', '') for seg in segmentos)
        st.info(f"**Vía CEDIS:** {'✅ Sí' if hay_cedis else '❌ No'}")

    with col4:
        st.markdown("**📈 Resultados**")
        tiempo_total = ruta_seleccionada.get('tiempo_total_horas', 0)
        probabilidad = data.get('probabilidad_cumplimiento', 0)
        st.info(f"**Tiempo:** {tiempo_total:.1f}h")
        st.info(f"**Éxito:** {probabilidad:.1%}")

    st.markdown("### 🛣️ Flujo Logístico Completo")

    factores = data.get('explicabilidad', {}).get('factores_externos', {})
    eventos = factores.get('eventos_detectados', [])
    factor_demanda = factores.get('factor_demanda', 1.0)

    timeline_info = "**Proceso:** "
    for i, segmento in enumerate(segmentos, 1):
        origen = segmento.get('origen_nombre', 'Origen')
        destino = segmento.get('destino_nombre', 'Destino')
        carrier = segmento.get('carrier', 'Carrier')
        tiempo = segmento.get('tiempo_viaje_horas', 0)

        if i > 1:
            timeline_info += " → "

        if 'CEDIS' in destino:
            timeline_info += f"🏭 **{destino}** ({tiempo:.1f}h)"
        elif destino.lower() == 'cliente':
            timeline_info += f"🎯 **CP {codigo_postal}** ({carrier} - {tiempo:.1f}h)"
        else:
            timeline_info += f"🏪 **{destino}** ({tiempo:.1f}h)"

    st.markdown(timeline_info)

    if eventos or factor_demanda > 1.5:
        st.markdown("### ⚠️ Factores de Impacto")
        if eventos:
            st.warning(f"🎉 **Eventos especiales:** {', '.join(eventos)} - Mayor demanda y restricciones")
        if factor_demanda > 1.5:
            st.warning(f"📈 **Alta demanda:** Factor {factor_demanda}x - Temporada especial detectada")



def _create_destination_node(request_data: dict, datos_geograficos: dict):
    """NUEVA FUNCIÓN - Crear nodo del código postal destino"""
    codigo_postal = request_data.get('codigo_postal', 'N/A')
    destino_coords = datos_geograficos.get('destino', {}).get('coordenadas', {})

    return {
        "name": f"📍 CP: {codigo_postal}",
        "value": int(codigo_postal) if codigo_postal.isdigit() else 0,
        "symbolSize": 100,
        "category": 8,  # Ubicación
        "itemStyle": {
            "color": "#E91E63",
            "borderColor": "#FFD700",
            "borderWidth": 5
        },
        "label": {"show": True, "fontSize": 16, "fontWeight": "bold"},
        "tooltip": f"Destino: {codigo_postal}\\nLat: {destino_coords.get('lat', 'N/A')}\\nLon: {destino_coords.get('lon', 'N/A')}"
    }




def render_delivery_summary(data: dict):
    """Renderizar resumen de información de entrega con lógica de fechas corregida"""
    request_data = data.get('explicabilidad', {}).get('request_procesado', {})
    fecha_compra_str = request_data.get('fecha_compra', '')
    fecha_entrega_str = data.get('fecha_entrega_estimada', '')
    rango_horario = data.get('rango_horario', {})
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


def render_performance_metrics_chart(data: dict):
    """Renderizar gráfico de métricas con diseño ejecutivo"""
    st.markdown("#### 📊 Indicadores de Rendimiento")

    ruta = data.get('ruta_seleccionada', {})
    metrics_data = [
        {"name": "Tiempo", "value": ruta.get('score_tiempo', 0) * 100},
        {"name": "Costo", "value": ruta.get('score_costo', 0) * 100},
        {"name": "Confiabilidad", "value": ruta.get('score_confiabilidad', 0) * 100},
        {"name": "Cumplimiento", "value": data.get('probabilidad_cumplimiento', 0) * 100},
        {"name": "Confianza", "value": data.get('confianza_prediccion', 0) * 100}
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

    st_echarts(option, height=Config.METRICS_CHART_HEIGHT)


def render_process_timeline(data: dict):
    """Renderizar timeline del proceso con datos reales del API"""
    st.markdown("#### ⏰ Timeline - Proceso")

    explicabilidad_ext = data.get('explicabilidad_extendida', {})
    timeline_procesamiento = explicabilidad_ext.get('timeline_procesamiento', {})
    fee_calc = data.get('explicabilidad', {}).get('fee_calculation', {})
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("**🔄 Procesamiento del Sistema**")

        pasos_procesamiento = [
            {"paso": timeline_procesamiento.get('paso_1', '❓ Validación de datos'), "status": "✅"},
            {"paso": timeline_procesamiento.get('paso_2', '❓ Búsqueda de tiendas'), "status": "✅"},
            {"paso": timeline_procesamiento.get('paso_3', '❓ Verificación de stock'), "status": "✅"},
            {"paso": timeline_procesamiento.get('paso_4', '❓ Generación de candidatos'), "status": "✅"},
            {"paso": timeline_procesamiento.get('paso_5', '❓ Selección óptima'), "status": "✅"}
        ]

        for i, paso in enumerate(pasos_procesamiento):
            status_color = "#34A853" if "✅" in paso["status"] else "#EA4335"
            st.markdown(f"""
            <div style='
                display: flex;
                align-items: center;
                padding: 0.8rem;
                margin: 0.5rem 0;
                background: {"#f0f9ff" if "✅" in paso["status"] else "#fef2f2"};
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
                "duration": fee_calc.get('tiempo_preparacion', 1.0),
                "color": "#6D4C41",
                "description": "Picking y empaque en tienda"
            },
            {
                "name": "Tránsito",
                "duration": fee_calc.get('tiempo_transito', 2.7),
                "color": "#2D5016",
                "description": "Transporte hasta destino"
            },
            {
                "name": "Contingencia",
                "duration": fee_calc.get('tiempo_contingencia', 0.37),
                "color": "#4A148C",
                "description": "Tiempo de buffer"
            }
        ]
        option = {
            "title": {
                "text": "Distribución del Tiempo",
                "textStyle": {"fontSize": 14, "color": "#2D5016"}
            },
            "tooltip": {
                "trigger": "axis",
                "formatter": """
                function(params) {
                    let item = params[0];
                    return '<strong>' + item.name + '</strong><br/>' +
                           'Tiempo: <strong>' + item.value + ' horas</strong><br/>' +
                           'Descripción: ' + item.data.description;
                }
                """
            },
            "xAxis": {
                "type": "value",
                "name": "Horas",
                "axisLabel": {"formatter": "{value}h", "color": "#2D5016"},
                "axisLine": {"lineStyle": {"color": "#8B7355"}},
                "splitLine": {"lineStyle": {"color": "#F0ECE0"}}
            },
            "yAxis": {
                "type": "category",
                "data": [item["name"] for item in reversed(timeline_data)],
                "axisLabel": {"color": "#2D5016"},
                "axisLine": {"lineStyle": {"color": "#8B7355"}}
            },
            "series": [{
                "type": "bar",
                "data": [
                    {
                        "value": item["duration"],
                        "itemStyle": {"color": item["color"]},
                        "description": item["description"]
                    } for item in reversed(timeline_data)
                ],
                "label": {
                    "show": True,
                    "position": "right",
                    "formatter": "{c}h",
                    "color": "#2D5016",
                    "fontWeight": "bold"
                },
                "barWidth": "60%"
            }]
        }

        st_echarts(option, height="250px")
        tiempo_total = sum(item["duration"] for item in timeline_data)
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #f8fafc, #e2e8f0);
            padding: 1rem;
            border-radius: 8px;
            margin-top: 1rem;
            text-align: center;
        '>
            <strong style='color: #2D5016; font-size: 1.1rem;'>
                ⏱️ Tiempo Total Estimado: {tiempo_total:.1f} horas
            </strong>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")

    debug_info = data.get('explicabilidad', {}).get('debug_info', {})

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_candidatos = debug_info.get('total_candidates_generated', 0)
        st.metric("🏆 Candidatos", total_candidatos)

    with col2:
        metodo_opt = debug_info.get('optimization_method', 'N/A')
        st.metric("🧠 Método", metodo_opt.replace('_', ' ').title())

    with col3:
        data_source = debug_info.get('data_source', 'N/A')
        st.metric("💾 Fuente", data_source.replace('_', ' ').title())

    with col4:
        scope = debug_info.get('search_scope', 'N/A')
        st.metric("🔍 Alcance", scope.title())

    candidatos = data.get('explicabilidad', {}).get('candidatos_lightgbm', [])
    if candidatos and len(candidatos) > 1:
        st.markdown("### 🔄 Proceso de Evaluación de Candidatos")
        candidatos_timeline = []
        for i, candidato in enumerate(candidatos[:5]):  # 5 para visualización
            ruta = candidato.get('ruta', {})
            score = candidato.get('score_lightgbm', 0)
            ranking = candidato.get('ranking_position', i + 1)

            candidatos_timeline.append({
                "name": f"Candidato #{ranking}",
                "value": [i, score * 100, score],
                "itemStyle": {"color": "#34A853" if ranking == 1 else "#64748B"}
            })

        timeline_option = {
            "title": {
                "text": "Evaluación de Candidatos",
                "textStyle": {"fontSize": 16, "color": "#2D5016"}
            },
            "tooltip": {
                "trigger": "item",
                "formatter": "Candidato: {b}<br/>Score: {c}%"
            },
            "xAxis": {
                "type": "category",
                "data": [f"#{i + 1}" for i in range(len(candidatos_timeline))],
                "name": "Orden de Evaluación"
            },
            "yAxis": {
                "type": "value",
                "name": "Score (%)",
                "max": 100
            },
            "series": [{
                "type": "line",
                "data": candidatos_timeline,
                "smooth": True,
                "lineStyle": {"width": 3, "color": "#2D5016"},
                "markPoint": {
                    "data": [{"type": "max", "name": "Mejor Score"}]
                },
                "areaStyle": {
                    "color": {
                        "type": "linear",
                        "x": 0, "y": 0, "x2": 0, "y2": 1,
                        "colorStops": [
                            {"offset": 0, "color": "rgba(45, 80, 22, 0.3)"},
                            {"offset": 1, "color": "rgba(45, 80, 22, 0.05)"}
                        ]
                    }
                }
            }]
        }

        st_echarts(timeline_option, height="300px")


def render_factors_analysis(data: dict):
    """Renderizar análisis de factores con paleta ejecutiva"""
    st.markdown("#### 🎯 Análisis de Variables Externas")

    factores = data.get('explicabilidad', {}).get('factores_externos', {})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🌍 Condiciones Operacionales**")
        zona_seguridad = factores.get('zona_seguridad', 'N/A')
        clima = factores.get('condicion_clima', 'N/A')
        trafico = factores.get('trafico_nivel', 'N/A')

        factor_data = [
            {"name": "Demanda", "value": factores.get('factor_demanda', 1) * 100},
            {"name": "Clima", "value": 85 if clima == 'Templado_Seco' else 60},
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
        costo_extra = factores.get('impacto_costo_extra_pct', 0)

        st.metric("⏰ Tiempo Adicional", f"{tiempo_extra:.1f} horas")
        st.metric("💰 Incremento Costo", f"{costo_extra:.1f}%")

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
    """Renderizar detalles técnicos"""
    with st.expander("🔍 Detalles Técnicos del Análisis", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**🛣️ Información de Ruta**")
            ruta = data.get('ruta_seleccionada', {})
            st.text(f"ID de Ruta: {ruta.get('ruta_id', 'N/A')}")
            st.text(f"Distancia Total: {ruta.get('distancia_total_km', 0):.2f} km")
            st.text(f"Score LightGBM: {ruta.get('score_lightgbm', 0):.3f}")
            st.text(f"Estado: {ruta.get('estado', 'N/A')}")

            st.markdown("**🏪 Inventario Split**")
            split_inv = ruta.get('split_inventory', {})
            st.text(f"Total Requerido: {split_inv.get('cantidad_total_requerida', 0)}")
            st.text(f"Total Disponible: {split_inv.get('cantidad_total_disponible', 0)}")
            st.text(f"Split Factible: {'✅ Sí' if split_inv.get('es_split_factible') else '❌ No'}")

        with col2:
            st.markdown("**🧠 Algoritmo y Decisión**")
            explicabilidad = data.get('explicabilidad_extendida', {})
            insights = explicabilidad.get('insights_algoritmo', {})
            st.text(f"Modelo: {insights.get('modelo_utilizado', 'N/A')}")
            st.text(f"Score Final: {insights.get('score_final', 0):.3f}")
            st.text(f"Ranking: #{insights.get('ranking_obtenido', 'N/A')}")

            st.markdown("**📍 Datos Geográficos**")
            geo_data = explicabilidad.get('datos_geograficos', {})
            destino = geo_data.get('destino', {})
            st.text(f"CP Destino: {destino.get('codigo_postal', 'N/A')}")
            coords = destino.get('coordenadas', {})
            st.text(f"Coordenadas: {coords.get('lat', 0):.4f}, {coords.get('lon', 0):.4f}")
