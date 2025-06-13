# components/charts.py
import streamlit as st
from streamlit_echarts import st_echarts

from components.layout import render_header, render_back_button
from config.settings import Config
from utils.helpers import (
    format_currency, format_percentage, format_datetime, get_delivery_status_badge, extract_key_insights
)


def render_results_dashboard():
    """Renderizar dashboard completo de resultados"""
    data = st.session_state.prediction_data

    # Botón de regreso
    render_back_button()

    # Header
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
    if 'fecha_entrega_estimada' in data:
        fecha_entrega = format_datetime(data['fecha_entrega_estimada'])
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


def render_key_insights(data: dict):
    """Renderizar insights clave"""
    insights = extract_key_insights(data)

    if insights:
        st.markdown("### 💡 Puntos Clave del Análisis")

        cols = st.columns(len(insights))
        colors = ["#2D5016", "#8B4513", "#1B4332", "#6D4C41", "#4A148C"]  # Paleta contrastante

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
    # Tabs para diferentes visualizaciones
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
    """Crear y mostrar el grafo de ruta de entrega estilo Force Layout completo"""
    st.markdown("#### 🚚 Red Completa de Factores de Decisión")

    # Mostrar información de resumen primero
    render_delivery_summary(data)

    # Obtener todos los datos del API
    ruta = data.get('ruta_seleccionada', {})
    factores = data.get('explicabilidad', {}).get('factores_externos', {})
    request_data = data.get('explicabilidad', {}).get('request_procesado', {})
    analisis_tiendas = data.get('explicabilidad_extendida', {}).get('analisis_tiendas', {})
    split_inventory = ruta.get('split_inventory', {})
    ubicaciones_seleccionadas = split_inventory.get('ubicaciones', [])

    # Crear nodos y enlaces
    nodes = []
    links = []

    # Definir categorías completas con colores distintos
    categories = [
        {"name": "A: Producto", "itemStyle": {"color": "#4285F4"}},  # Azul Google
        {"name": "B: Tiendas", "itemStyle": {"color": "#34A853"}},  # Verde Google
        {"name": "C: Flota", "itemStyle": {"color": "#FBBC04"}},  # Amarillo Google
        {"name": "D: Destino", "itemStyle": {"color": "#EA4335"}},  # Rojo Google
        {"name": "E: Clima", "itemStyle": {"color": "#9AA0A6"}},  # Gris Google
        {"name": "F: Eventos", "itemStyle": {"color": "#9C27B0"}},  # Púrpura Material
        {"name": "G: Seguridad", "itemStyle": {"color": "#FF5722"}},  # Deep Orange
        {"name": "H: Demanda", "itemStyle": {"color": "#607D8B"}},  # Blue Grey
        {"name": "I: Métricas", "itemStyle": {"color": "#795548"}}  # Brown
    ]

    # A: PRODUCTO/SKU
    sku_id = request_data.get('sku_id', 'N/A')
    cantidad = request_data.get('cantidad', 0)
    nodes.append({
        "name": f"SKU: {sku_id}",
        "value": cantidad,
        "symbolSize": 60,
        "category": 0,
        "itemStyle": {"color": "#4285F4"},
        "label": {"show": True, "fontSize": 12, "fontWeight": "bold"}
    })

    # B: TODAS LAS TIENDAS (seleccionadas y no seleccionadas)
    tiendas_detalle = analisis_tiendas.get('tiendas_detalle', [])

    # Tienda seleccionada
    for ubicacion in ubicaciones_seleccionadas:
        nombre_tienda = ubicacion.get('nombre_ubicacion', 'Tienda')
        stock = ubicacion.get('stock_disponible', 0)
        nodes.append({
            "name": nombre_tienda,
            "value": stock,
            "symbolSize": 80,
            "category": 1,
            "selected": True,
            "itemStyle": {"color": "#34A853", "borderColor": "#FFD700", "borderWidth": 3},
            "label": {"show": True, "fontSize": 12, "fontWeight": "bold"}
        })

        # SKU → Tienda seleccionada
        links.append({
            "source": f"SKU: {sku_id}",
            "target": nombre_tienda,
            "lineStyle": {"color": "#4285F4", "width": 4}
        })

    # Tiendas consideradas pero no seleccionadas
    for tienda in tiendas_detalle:
        if not tienda.get('seleccionada', False):
            nombre = tienda.get('nombre', 'Tienda')
            distancia = tienda.get('distancia_km', 0)
            nodes.append({
                "name": nombre,
                "value": distancia,
                "symbolSize": 50,
                "category": 1,
                "selected": False,
                "itemStyle": {"color": "#34A853", "opacity": 0.6},
                "label": {"show": True, "fontSize": 10}
            })

            # SKU → Tiendas no seleccionadas (línea punteada)
            links.append({
                "source": f"SKU: {sku_id}",
                "target": nombre,
                "lineStyle": {"color": "#34A853", "width": 2, "type": "dashed", "opacity": 0.5}
            })

    # C: FLOTA/CARRIER
    carrier = data.get('carrier_principal', 'Carrier')
    segmentos = ruta.get('segmentos', [])
    tipo_flota = segmentos[0].get('tipo_flota', 'N/A') if segmentos else 'N/A'

    flota_nombre = f"{carrier} ({tipo_flota})"
    nodes.append({
        "name": flota_nombre,
        "symbolSize": 70,
        "category": 2,
        "itemStyle": {"color": "#FBBC04"},
        "label": {"show": True, "fontSize": 12, "fontWeight": "bold"}
    })

    # Tienda seleccionada → Flota
    for ubicacion in ubicaciones_seleccionadas:
        links.append({
            "source": ubicacion.get('nombre_ubicacion'),
            "target": flota_nombre,
            "lineStyle": {"color": "#34A853", "width": 5}
        })

    # D: DESTINO/CLIENTE
    cp_destino = request_data.get('codigo_postal', 'N/A')
    cliente_nombre = f"Cliente CP: {cp_destino}"
    nodes.append({
        "name": cliente_nombre,
        "symbolSize": 90,
        "category": 3,
        "itemStyle": {"color": "#EA4335", "borderColor": "#FFD700", "borderWidth": 3},
        "label": {"show": True, "fontSize": 14, "fontWeight": "bold"}
    })

    # Flota → Cliente
    distancia = ruta.get('distancia_total_km', 0)
    links.append({
        "source": flota_nombre,
        "target": cliente_nombre,
        "value": distancia,
        "lineStyle": {"color": "#FBBC04", "width": 6},
        "label": {"show": True, "formatter": f"{distancia:.0f} km"}
    })

    # E: FACTORES CLIMÁTICOS
    clima = factores.get('condicion_clima', 'N/A')
    temperatura = factores.get('temperatura_celsius', 0)
    lluvia = factores.get('probabilidad_lluvia', 0)
    viento = factores.get('viento_kmh', 0)

    nodo_clima = f"🌡️ {clima}\n{temperatura}°C"
    nodes.append({
        "name": nodo_clima,
        "value": temperatura,
        "symbolSize": 55,
        "category": 4,
        "itemStyle": {"color": "#9AA0A6"},
        "label": {"show": True, "fontSize": 10}
    })

    nodes.append({
        "name": f"🌧️ Lluvia {lluvia}%",
        "value": lluvia,
        "symbolSize": 45,
        "category": 4,
        "itemStyle": {"color": "#9AA0A6"},
        "label": {"show": True, "fontSize": 10}
    })

    nodes.append({
        "name": f"💨 Viento {viento}km/h",
        "value": viento,
        "symbolSize": 45,
        "category": 4,
        "itemStyle": {"color": "#9AA0A6"},
        "label": {"show": True, "fontSize": 10}
    })

    # Factores climáticos → Cliente
    for factor_clima in [nodo_clima, f"🌧️ Lluvia {lluvia}%", f"💨 Viento {viento}km/h"]:
        links.append({
            "source": factor_clima,
            "target": cliente_nombre,
            "lineStyle": {"color": "#9AA0A6", "width": 2, "type": "dashed", "opacity": 0.7}
        })

    # F: EVENTOS/TEMPORALIDAD
    eventos = factores.get('eventos_detectados', [])
    es_temporada_alta = factores.get('es_temporada_alta', False)

    for evento in eventos:
        nodes.append({
            "name": f"🎄 {evento}",
            "symbolSize": 50,
            "category": 5,
            "itemStyle": {"color": "#9C27B0"},
            "label": {"show": True, "fontSize": 10}
        })

        # Evento → Cliente
        links.append({
            "source": f"🎄 {evento}",
            "target": cliente_nombre,
            "lineStyle": {"color": "#9C27B0", "width": 3, "type": "dashed"}
        })

    if es_temporada_alta:
        nodes.append({
            "name": "📈 Temporada Alta",
            "symbolSize": 55,
            "category": 5,
            "itemStyle": {"color": "#9C27B0"},
            "label": {"show": True, "fontSize": 11, "fontWeight": "bold"}
        })

        links.append({
            "source": "📈 Temporada Alta",
            "target": cliente_nombre,
            "lineStyle": {"color": "#9C27B0", "width": 4}
        })

    # G: FACTORES DE SEGURIDAD/ZONA
    zona_seguridad = factores.get('zona_seguridad', 'N/A')
    criticidad = factores.get('criticidad_logistica', 'N/A')
    trafico = factores.get('trafico_nivel', 'N/A')

    nodes.append({
        "name": f"🛡️ Zona {zona_seguridad}",
        "symbolSize": 60,
        "category": 6,
        "itemStyle": {"color": "#FF5722"},
        "label": {"show": True, "fontSize": 11, "fontWeight": "bold"}
    })

    nodes.append({
        "name": f"🚨 {criticidad}",
        "symbolSize": 55,
        "category": 6,
        "itemStyle": {"color": "#FF5722"},
        "label": {"show": True, "fontSize": 10}
    })

    nodes.append({
        "name": f"🚦 Tráfico {trafico}",
        "symbolSize": 50,
        "category": 6,
        "itemStyle": {"color": "#FF5722"},
        "label": {"show": True, "fontSize": 10}
    })

    # Factores de seguridad → Cliente
    for factor_seg in [f"🛡️ Zona {zona_seguridad}", f"🚨 {criticidad}", f"🚦 Tráfico {trafico}"]:
        links.append({
            "source": factor_seg,
            "target": cliente_nombre,
            "lineStyle": {"color": "#FF5722", "width": 3}
        })

    # H: FACTORES DE DEMANDA
    factor_demanda = factores.get('factor_demanda', 1)
    tiempo_extra = factores.get('impacto_tiempo_extra_horas', 0)
    costo_extra = factores.get('impacto_costo_extra_pct', 0)

    nodes.append({
        "name": f"📊 Demanda x{factor_demanda}",
        "value": factor_demanda,
        "symbolSize": 65,
        "category": 7,
        "itemStyle": {"color": "#607D8B"},
        "label": {"show": True, "fontSize": 11, "fontWeight": "bold"}
    })

    nodes.append({
        "name": f"⏰ +{tiempo_extra}h",
        "value": tiempo_extra,
        "symbolSize": 50,
        "category": 7,
        "itemStyle": {"color": "#607D8B"},
        "label": {"show": True, "fontSize": 10}
    })

    nodes.append({
        "name": f"💰 +{costo_extra:.1f}%",
        "value": costo_extra,
        "symbolSize": 55,
        "category": 7,
        "itemStyle": {"color": "#607D8B"},
        "label": {"show": True, "fontSize": 10}
    })

    # Factores de demanda → Flota
    for factor_dem in [f"📊 Demanda x{factor_demanda}", f"⏰ +{tiempo_extra}h", f"💰 +{costo_extra:.1f}%"]:
        links.append({
            "source": factor_dem,
            "target": flota_nombre,
            "lineStyle": {"color": "#607D8B", "width": 2, "type": "dashed"}
        })

    # I: MÉTRICAS DE DECISIÓN
    probabilidad = data.get('probabilidad_cumplimiento', 0)
    confianza = data.get('confianza_prediccion', 0)
    score_lightgbm = ruta.get('score_lightgbm', 0)
    tiempo_total = ruta.get('tiempo_total_horas', 0)

    nodes.append({
        "name": f"📈 Prob: {probabilidad * 100:.1f}%",
        "value": probabilidad,
        "symbolSize": 55,
        "category": 8,
        "itemStyle": {"color": "#795548"},
        "label": {"show": True, "fontSize": 10}
    })

    nodes.append({
        "name": f"🎯 Conf: {confianza * 100:.1f}%",
        "value": confianza,
        "symbolSize": 55,
        "category": 8,
        "itemStyle": {"color": "#795548"},
        "label": {"show": True, "fontSize": 10}
    })

    nodes.append({
        "name": f"🧠 Score: {score_lightgbm:.2f}",
        "value": score_lightgbm,
        "symbolSize": 60,
        "category": 8,
        "itemStyle": {"color": "#795548"},
        "label": {"show": True, "fontSize": 11, "fontWeight": "bold"}
    })

    # Métricas → Decisión final (Cliente)
    for metrica in [f"📈 Prob: {probabilidad * 100:.1f}%", f"🎯 Conf: {confianza * 100:.1f}%",
                    f"🧠 Score: {score_lightgbm:.2f}"]:
        links.append({
            "source": metrica,
            "target": cliente_nombre,
            "lineStyle": {"color": "#795548", "width": 2, "type": "dotted"}
        })

    # Configuración del grafo Force Layout
    option = {
        "title": {
            "text": "Red Completa de Factores de Decisión",
            "subtext": "Análisis integral de todos los elementos que influyen en la entrega",
            "top": "10px",
            "left": "center",
            "textStyle": {"fontSize": 18, "fontWeight": "bold", "color": "#2D5016"}
        },
        "tooltip": {
            "trigger": "item",
            "backgroundColor": "rgba(255,255,255,0.95)",
            "borderColor": "#2D5016",
            "borderWidth": 2,
            "textStyle": {"color": "#333"},
            "formatter": """
            function(params) {
                if (params.dataType === 'node') {
                    let info = '<strong style="color: #2D5016;">' + params.data.name + '</strong><br/>';
                    if (params.data.value !== undefined) {
                        info += '<span style="color: #666;">Valor: <strong>' + params.data.value + '</strong></span><br/>';
                    }
                    if (params.data.selected !== undefined) {
                        info += '<span style="color: ' + (params.data.selected ? '#34A853' : '#EA4335') + ';">';
                        info += params.data.selected ? '✅ Seleccionada' : '❌ No seleccionada';
                        info += '</span>';
                    }
                    return info;
                } else if (params.dataType === 'edge') {
                    let info = '<strong>' + params.data.source + '</strong> → <strong>' + params.data.target + '</strong>';
                    if (params.data.value !== undefined) {
                        info += '<br/><span style="color: #666;">Distancia: ' + params.data.value + ' km</span>';
                    }
                    return info;
                }
            }
            """
        },
        "legend": {
            "data": [cat["name"] for cat in categories],
            "top": "50px",
            "orient": "horizontal",
            "textStyle": {"fontSize": 11, "color": "#2D5016"},
            "selected": {
                "A: Producto": True,
                "B: Tiendas": True,
                "C: Flota": True,
                "D: Destino": True,
                "E: Clima": True,
                "F: Eventos": True,
                "G: Seguridad": True,
                "H: Demanda": True,
                "I: Métricas": True
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
                "repulsion": 1000,
                "gravity": 0.1,
                "edgeLength": [50, 200],
                "layoutAnimation": True
            },
            "emphasis": {
                "focus": "adjacency",
                "lineStyle": {"width": 8, "opacity": 1},
                "itemStyle": {
                    "shadowBlur": 20,
                    "shadowColor": "rgba(0,0,0,0.5)",
                    "borderWidth": 3,
                    "borderColor": "#FFD700"
                }
            },
            "lineStyle": {
                "curveness": 0.1,
                "opacity": 0.8
            }
        }],
        "animationDuration": 3000,
        "animationEasingUpdate": "cubicOut"
    }

    st_echarts(option, height="700px", key="complete_decision_network")

    # Información adicional
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"🏪 **Tiendas evaluadas:** {len(tiendas_detalle) + len(ubicaciones_seleccionadas)}")
        st.info(f"📊 **Factor demanda:** {factor_demanda}x")

    with col2:
        st.info(f"🎄 **Eventos activos:** {len(eventos)}")
        st.info(f"⚠️ **Criticidad:** {criticidad}")

    with col3:
        st.info(f"🎯 **Score final:** {score_lightgbm:.3f}")
        st.info(f"⏱️ **Tiempo total:** {tiempo_total:.1f}h")


def render_delivery_summary(data: dict):
    """Renderizar resumen de información de entrega"""
    # Obtener datos del request original y respuesta
    request_data = data.get('explicabilidad', {}).get('request_procesado', {})
    fecha_compra_str = request_data.get('fecha_compra', '')
    fecha_entrega_str = data.get('fecha_entrega_estimada', '')
    rango_horario = data.get('rango_horario', {})

    # Calcular días hasta entrega
    dias_entrega = "N/A"
    if fecha_compra_str and fecha_entrega_str:
        try:
            from datetime import datetime
            fecha_compra = datetime.fromisoformat(fecha_compra_str.replace('Z', '+00:00'))
            fecha_entrega = datetime.fromisoformat(fecha_entrega_str.replace('Z', '+00:00'))
            dias_diff = (fecha_entrega - fecha_compra).days
            dias_entrega = "HOY" if dias_diff == 0 else f"{dias_diff} días"
        except:
            dias_entrega = "N/A"

    # Crear card de resumen con estilo vintage
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
    """Renderizar gráfico de métricas de rendimiento"""
    st.markdown("#### 📊 Métricas de Rendimiento")

    ruta = data.get('ruta_seleccionada', {})

    # Datos para el gráfico radar
    metrics_data = [
        {"name": "Tiempo", "value": ruta.get('score_tiempo', 0) * 100},
        {"name": "Costo", "value": ruta.get('score_costo', 0) * 100},
        {"name": "Confiabilidad", "value": ruta.get('score_confiabilidad', 0) * 100},
        {"name": "Cumplimiento", "value": data.get('probabilidad_cumplimiento', 0) * 100},
        {"name": "Confianza", "value": data.get('confianza_prediccion', 0) * 100}
    ]

    option = {
        "title": {
            "text": "Scores de Rendimiento",
            "left": "center",
            "textStyle": {"fontSize": 18, "fontWeight": "bold", "color": "#2D5016"}
        },
        "tooltip": {
            "trigger": "axis",
            "formatter": "{b}: {c}%"
        },
        "radar": {
            "indicator": [{"name": item["name"], "max": 100} for item in metrics_data],
            "shape": "polygon",
            "splitNumber": 5,
            "axisName": {"color": "#2D5016"},
            "splitLine": {"lineStyle": {"color": "#8B7355"}},
            "splitArea": {"areaStyle": {"color": ["#F8F6F0", "#F0ECE0"]}}
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
                            {"offset": 0, "color": "rgba(45, 80, 22, 0.3)"},
                            {"offset": 1, "color": "rgba(139, 69, 19, 0.1)"}
                        ]
                    }
                },
                "lineStyle": {"color": "#2D5016", "width": 3},
                "itemStyle": {"color": "#8B4513"}
            }]
        }]
    }

    st_echarts(option, height=Config.METRICS_CHART_HEIGHT)


def render_process_timeline(data: dict):
    """Renderizar timeline del proceso"""
    st.markdown("#### ⏰ Timeline de Entrega")

    # Datos del timeline desde la respuesta del API
    fee_calc = data.get('explicabilidad', {}).get('fee_calculation', {})

    timeline_data = [
        {
            "name": "Preparación",
            "duration": fee_calc.get('tiempo_preparacion', 1),
            "color": "#6D4C41"  # Marrón Medio
        },
        {
            "name": "Tránsito",
            "duration": fee_calc.get('tiempo_transito', 13.5),
            "color": "#2D5016"  # Verde Bosque
        },
        {
            "name": "Contingencia",
            "duration": fee_calc.get('tiempo_contingencia', 1.75),
            "color": "#4A148C"  # Púrpura Profundo
        }
    ]

    option = {
        "title": {
            "text": "Distribución del Tiempo de Entrega",
            "left": "center",
            "textStyle": {"fontSize": 18, "fontWeight": "bold", "color": "#2D5016"}
        },
        "tooltip": {
            "trigger": "axis",
            "formatter": "{b}: {c} horas"
        },
        "xAxis": {
            "type": "category",
            "data": [item["name"] for item in timeline_data],
            "axisLabel": {"fontSize": 12, "color": "#2D5016"},
            "axisLine": {"lineStyle": {"color": "#8B7355"}}
        },
        "yAxis": {
            "type": "value",
            "name": "Horas",
            "axisLabel": {"formatter": "{value}h", "color": "#2D5016"},
            "axisLine": {"lineStyle": {"color": "#8B7355"}},
            "splitLine": {"lineStyle": {"color": "#F0ECE0"}}
        },
        "series": [{
            "type": "bar",
            "data": [
                {
                    "value": item["duration"],
                    "itemStyle": {"color": item["color"]}
                } for item in timeline_data
            ],
            "label": {
                "show": True,
                "position": "top",
                "formatter": "{c}h",
                "color": "#2D5016"
            },
            "barWidth": "50%"
        }]
    }

    st_echarts(option, height="350px")


def render_factors_analysis(data: dict):
    """Renderizar análisis de factores externos"""
    st.markdown("#### 🎯 Análisis de Factores")

    factores = data.get('explicabilidad', {}).get('factores_externos', {})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🌍 Condiciones Externas**")
        zona_seguridad = factores.get('zona_seguridad', 'N/A')
        clima = factores.get('condicion_clima', 'N/A')
        trafico = factores.get('trafico_nivel', 'N/A')

        # Gráfico de factores con paleta contrastante
        factor_data = [
            {"name": "Demanda", "value": factores.get('factor_demanda', 1) * 100},
            {"name": "Clima", "value": 85 if clima == 'Templado_Seco' else 60},
            {"name": "Tráfico", "value": 70 if trafico == 'Moderado' else 50},
            {"name": "Seguridad", "value": 40 if zona_seguridad == 'Roja' else 80}
        ]

        # Colores contrastantes para el pie chart
        contrast_pie_colors = ["#2D5016", "#8B4513", "#6D4C41", "#4A148C"]

        option = {
            "title": {
                "text": "Impacto de Factores",
                "textStyle": {"fontSize": 14, "color": "#2D5016"}
            },
            "tooltip": {"formatter": "{b}: {c}%"},
            "color": contrast_pie_colors,
            "series": [{
                "type": "pie",
                "radius": ["30%", "70%"],
                "data": factor_data,
                "emphasis": {"itemStyle": {"shadowBlur": 10}},
                "label": {"fontSize": 10, "color": "#2D5016"}
            }]
        }
        st_echarts(option, height="300px")

    with col2:
        st.markdown("**📊 Impactos Calculados**")
        tiempo_extra = factores.get('impacto_tiempo_extra_horas', 0)
        costo_extra = factores.get('impacto_costo_extra_pct', 0)

        st.metric("⏰ Tiempo Extra", f"{tiempo_extra:.1f} horas")
        st.metric("💰 Costo Extra", f"{costo_extra:.1f}%")

        # Información adicional con colores contrastantes
        st.markdown(f"""
        <div style='
            background: #F8F6F0; 
            padding: 1rem; 
            border-radius: 8px; 
            border-left: 4px solid #2D5016;
            margin: 0.5rem 0;
        '>
            🌡️ <strong>Clima:</strong> {clima}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style='
            background: #F8F6F0; 
            padding: 1rem; 
            border-radius: 8px; 
            border-left: 4px solid #8B4513;
            margin: 0.5rem 0;
        '>
            🚦 <strong>Tráfico:</strong> {trafico}
        </div>
        """, unsafe_allow_html=True)

        if zona_seguridad == 'Roja':
            st.markdown(f"""
            <div style='
                background: #F8F6F0; 
                padding: 1rem; 
                border-radius: 8px; 
                border-left: 4px solid #BF360C;
                margin: 0.5rem 0;
            '>
                🔴 <strong>Zona de Seguridad:</strong> {zona_seguridad}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='
                background: #F8F6F0; 
                padding: 1rem; 
                border-radius: 8px; 
                border-left: 4px solid #1B4332;
                margin: 0.5rem 0;
            '>
                🟢 <strong>Zona de Seguridad:</strong> {zona_seguridad}
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