import streamlit as st
import pandas as pd

from components.layout import render_header, render_back_button
from services.api_client import APIClient
from utils.helpers import format_currency, format_datetime, get_delivery_status_badge, format_percentage

from utils.helpers import generate_comparison_table
from services.bigquery_service import get_bigquery_client, execute_bigquery_query

from streamlit_calendar import calendar
from datetime import datetime

def render_results_dashboard():
    """Renderizar dashboard completo de resultados"""

    data = st.session_state.prediction_data
    original_request = st.session_state.get('original_request', {})

    render_back_button()
    render_header(
        "📊 Análisis de Predicción",
        "Resultados del análisis de ruta y predicción de entrega"
    )

    es_recalculo = data.get('es_recalculo', False)

    if es_recalculo:

        render_recalculo_comparison(data)
        render_main_results(data, original_request, recalculate=True)
        # render_context_info(data)
        render_all_options(data, original_request, recalculate=True)

    else:

        # Resultados principales
        render_main_results(data, original_request, recalculate=False)

        # Enriquecimiento
        # render_context_info(data)

        # Visualizaciones
        # render_interactive_charts(data, original_request)

        tab1, tab2 = st.tabs([f"Información general", "Recálculo"])

        with tab1:
            # Información extraída directamente de BigQuery para el SKU y CP seleccionados
            render_all_options(data, original_request, recalculate=False)

        with tab2:
            # Recálculo
            render_recalculate_section(data, original_request)

def render_main_results(data: dict, original_request: dict, recalculate: bool = False):
    """Renderizar los resultados principales"""

    # Fecha promesa destacada
    render_delivery_promise(data)

    # Desglose de pedido del cliente
    render_transaction_details(original_request)

    # Desglose de fechas importantes
    render_delivery_dates(data, original_request)

    # Desglose de detalles de entrega
    render_delivery_details(data)

    # Detalles técnicos
    render_technical_details(data)

    # Calendario para visualización de fechas importantes
    render_delivery_calendar_view(data, original_request, recalculate)


    # Enriquecimiento del código postal destino
    # render_context_info(data)

def render_recalculo_comparison(data: dict):
    """Mostrar comparación del recálculo"""
    st.markdown("### 🔄 Comparación del Recálculo")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "📅 Fecha de Entrega Original",
            format_datetime(data.get('fecha_entrega_original', 'N/A')),
            help="Fecha de entrega de la predicción original"
        )

    with col2:
        st.metric(
            "🎯 Fecha Entrega Recálculo",
            format_datetime(data.get('fecha_entrega', 'N/A')),
            help="Nueva fecha de entrega después del recálculo"
        )

    with col3:
        dias_diff = data.get('dias_diferencia', 'N/A')
        delta_color = "normal"
        if isinstance(dias_diff, (int, float)):
            delta_color = "inverse" if dias_diff > 0 else "normal"

        st.metric(
            "📊 Diferencia",
            f"{dias_diff} días" if dias_diff != 'N/A' else 'N/A',
            delta=f"{dias_diff} días" if isinstance(dias_diff, (int, float)) else None,
            delta_color=delta_color
        )

    st.markdown("**📋 Detalles del Recálculo:**")

    col1, col2 = st.columns(2)

    with col1:
        fecha_promesa_mantenida = data.get('fecha_promesa_mantenida', False)
        status_promesa = "✅ Mantenida" if fecha_promesa_mantenida else "❌ No mantenida"
        st.info(f"**Fecha Promesa:** {status_promesa}")

        costo_diff = data.get('costo_diferencia', 0)
        st.info(f"**Diferencia de Costo:** {format_currency(costo_diff)}")

    with col2:
        tienda_rechazada = data.get('tienda_rechazada', 'N/A')
        st.info(f"**Tienda Rechazada:** {tienda_rechazada}")

        rutas_descartadas = data.get('rutas_descartadas', [])
        rutas_text = ', '.join(rutas_descartadas) if rutas_descartadas else 'Ninguna'
        st.info(f"**Rutas Descartadas:** {rutas_text}")

    st.markdown("---")


def render_alternatives_table(data: dict):
    """Tabla de alternativas"""
    st.subheader("📋 Alternativas Evaluadas")

    alternativas = data.get('alternativas', [])

    if alternativas:
        for i, alt in enumerate(alternativas):
            is_selected = alt.get('selected', False)

            if is_selected:
                st.success(f"""
                **🏆 SELECCIONADA - Rank {alt.get('rank', 'N/A')}**
                - **ID Trazo:** {alt.get('id', 'N/A')}
                - **Tienda:** {alt.get('tienda', 'N/A')}
                - **Método:** {alt.get('metodo', 'N/A')}
                - **Días:** {alt.get('dias', 'N/A')}
                - **Costo:** {format_currency(alt.get('costo', 0))}
                - **Inventario:** {alt.get('inventario', 'N/A')}
                - **Score:** {alt.get('score', 0):.3f}
                """)
            else:
                st.info(f"""
                **Rank {alt.get('rank', 'N/A')}**
                - **ID Trazo:** {alt.get('id', 'N/A')}
                - **Tienda:** {alt.get('tienda', 'N/A')}
                - **Método:** {alt.get('metodo', 'N/A')}
                - **Días:** {alt.get('dias', 'N/A')}
                - **Costo:** {format_currency(alt.get('costo', 0))}
                - **Inventario:** {alt.get('inventario', 'N/A')}
                - **Score:** {alt.get('score', 0):.3f}
                """)

        total_opciones = len(alternativas)
        seleccionadas = sum(1 for alt in alternativas if alt.get('selected', False))

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total Opciones", total_opciones)
        with col2:
            st.metric("✅ Seleccionadas", seleccionadas)
        with col3:
            tiempo_proceso = data.get('tiempo_proceso_ms', 0)
            st.metric("⏱️ Tiempo Proceso", f"{tiempo_proceso:.2f} ms")

        st.markdown("**📋 Información Adicional:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📦 Inventario Total", data.get('inventario_total_disponible', 'N/A'))
        with col2:
            st.metric("🏪 Tiendas con Inventario", data.get('tiendas_con_inventario', 'N/A'))
        with col3:
            st.metric("🔢 Opciones Evaluadas", data.get('opciones_evaluadas', 'N/A'))
    else:
        st.info("No se encontraron alternativas")

# Recalculo
def render_recalculate_section(data: dict, original_request: dict):
    """Sección de recálculo"""
    st.subheader("⚙️ Configuración para el Recálculo de Entrega")

    fecha_entrega_promesa = data.get('fecha_entrega', '')
    tienda_rechazada = data.get('tienda', 0)
    alternativas = data.get('alternativas', [])
    rutas_seleccionadas = [alt.get('id', '') for alt in alternativas if alt.get('selected', False)]
    can_recalculate = bool(
        original_request.get('codigo_postal') and
        original_request.get('sku_id') and
        fecha_entrega_promesa and
        tienda_rechazada
    )

    if not can_recalculate:
        st.warning("⚠️ No se pueden realizar recálculos. Faltan datos del request original.")
        return

    st.markdown("**Datos del recálculo (extraídos automáticamente):**")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(f"**Código postal:** {original_request.get('codigo_postal', '')}")
        st.info(f"**SKU:** {original_request.get('sku_id', '')}")

    with col2:
        st.info(f"**Fecha Compra Original:** {format_datetime(original_request.get('fecha_compra', ''))}")
        st.info(f"**Fecha Entrega Promesa:** {format_datetime(fecha_entrega_promesa)}")

    with col3:
        st.info(f"**Tienda a Rechazar:** {tienda_rechazada}")
        st.info(f"**Rutas a Rechazar:** {', '.join(rutas_seleccionadas) if rutas_seleccionadas else 'Ninguna'}")

        priorizar_fecha_promesa = st.checkbox(
            "Priorizar Fecha Promesa",
            help="Si está activado, priorizará mantener la fecha promesa original"
        )
        st.session_state.priorizar_fecha_promesa = priorizar_fecha_promesa

    if st.checkbox("📋 Ver datos que se enviarán al API", value=False):
        request_data = {
            "codigo_postal": original_request.get('codigo_postal', ''),
            "sku_id": original_request.get('sku_id', ''),
            "cantidad": original_request.get('cantidad', 1),
            "fecha_compra_original": original_request.get('fecha_compra', ''),
            "fecha_entrega_promesa": fecha_entrega_promesa,
            "tienda_rechazada": tienda_rechazada,
            "temporada": original_request.get('temporada', 'TEMPORADA_BAJA'),
            "rutas_rechazadas": rutas_seleccionadas,
            "priorizar_fecha_promesa": st.session_state.get('priorizar_fecha_promesa', False)
        }
        st.json(request_data)

    if st.button("🔄 Ejecutar Recálculo", type="secondary", use_container_width=True):
        priorizar = st.session_state.get('priorizar_fecha_promesa', False)
        st.session_state.show_results = True
        execute_recalculation(data, original_request, priorizar, rutas_seleccionadas)

def execute_recalculation(data: dict, original_request: dict, priorizar_fecha_promesa: bool, rutas_rechazadas: list):
    """Ejecutar recálculo"""
    try:
        codigo_postal = original_request.get('codigo_postal', '')
        sku_id = original_request.get('sku_id', '')
        cantidad = original_request.get('cantidad', 1)
        fecha_compra_original = original_request.get('fecha_compra', '')
        temporada = original_request.get('temporada', 'TEMPORADA_BAJA')

        fecha_entrega_promesa = data.get('fecha_entrega', '')
        tienda_rechazada = data.get('tienda', 0)

        if not codigo_postal or not sku_id or not fecha_compra_original:
            st.error("❌ Faltan datos del request original para el recálculo")
            return

        if not fecha_entrega_promesa or not tienda_rechazada:
            st.error("❌ Faltan datos de la respuesta original para el recálculo")
            return

        result_placeholder = st.empty()

        with st.status("🔄 Ejecutando recálculo...", expanded=True) as status:
            st.write("🔍 Preparando datos del recálculo...")
            st.write(f"📍 CP: {codigo_postal} | SKU: {sku_id} | Cantidad: {cantidad}")
            st.write(f"🏪 Rechazando tienda: {tienda_rechazada}")
            st.write(f"🚫 Rechazando rutas: {', '.join(rutas_rechazadas) if rutas_rechazadas else 'Ninguna'}")

            api_client = APIClient()
            result, error = api_client.recalculate_delivery(
                codigo_postal=codigo_postal,
                sku_id=sku_id,
                cantidad=cantidad,
                fecha_compra_original=fecha_compra_original,
                fecha_entrega_promesa=fecha_entrega_promesa,
                tienda_rechazada=tienda_rechazada,
                temporada=temporada,
                rutas_rechazadas=rutas_rechazadas,
                priorizar_fecha_promesa=priorizar_fecha_promesa
            )

            if result:
                st.write("✅ Recálculo completado exitosamente")
                status.update(label="✅ Recálculo Completado", state="complete", expanded=False)

                st.session_state.prediction_data = result
                st.session_state.show_results = True

                with result_placeholder.container():
                    st.success("🎉 **Recálculo completado exitosamente!**")

                    if result.get('es_recalculo', False):
                        st.rerun()

                    if st.button("🔄 Ver Resultados Completos en Pestañas", type="primary", key="refresh_results"):
                        st.rerun()

                    st.info(
                        "💡 **Tip:** Haz clic en el botón de arriba para ver los resultados completos organizados en pestañas.")

            else:
                st.write("❌ Error en el recálculo")
                status.update(label="❌ Error en Recálculo", state="error", expanded=False)

                with result_placeholder.container():
                    st.error(f"🚫 **Error en el recálculo:** {error}")

                    with st.expander("🔍 Detalles del Error", expanded=False):
                        st.write("**Datos enviados:**")
                        st.json({
                            "codigo_postal": codigo_postal,
                            "sku_id": sku_id,
                            "cantidad": cantidad,
                            "fecha_compra_original": fecha_compra_original,
                            "fecha_entrega_promesa": fecha_entrega_promesa,
                            "tienda_rechazada": tienda_rechazada,
                            "temporada": temporada,
                            "rutas_rechazadas": rutas_rechazadas,
                            "priorizar_fecha_promesa": priorizar_fecha_promesa
                        })
                        st.write(f"**Error recibido:** {error}")

    except Exception as e:
        st.error(f"❌ Error en recálculo: {str(e)}")
        st.write(f"**Detalles del error:** {str(e)}")

# Código de prueba
def render_delivery_promise(data: dict):
    """Renderizar fecha promesa de entrega adaptada al nuevo response"""
    fecha_entrega_str = data.get('fecha_entrega', '')

    if fecha_entrega_str:
        # fecha (sin hora)
        fecha_entrega = format_datetime(fecha_entrega_str)

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
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ No se encontró fecha de entrega estimada")

def render_transaction_details(original_request: dict):
    """
    Muestra los detalles del pedido del cliente
    """

    codigo_postal = original_request.get('codigo_postal', '')
    sku_id = original_request.get('sku_id', '')
    cantidad = original_request.get('cantidad', '')

    # Main summary box (sin cambios, ya estaba bien)
    st.markdown(f"""
           <div style='
               background: linear-gradient(135deg, #CFEDE6, #E8DCCF);
               padding: 2rem;
               border-radius: 15px;
               margin: 1.5rem 0;
               border: 2px solid #C8B8A1;
               box-shadow: 0 8px 25px rgba(0,0,0,0.1);
           '>
               <h3 style='color: #6B5B73; text-align: center; margin-bottom: 2rem;'>💰 Detalles de transacción</h3>
               <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; text-align: center;'>
                   <div>
                       <h4 style='color: #6B5B73; margin: 0; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;'>🏠 Código Postal Destino</h4>
                       <p style='color: #4A4A4A; font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0;'>{codigo_postal}</p>
                   </div>
                   <div>
                       <h4 style='color: #6B5B73; margin: 0; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;'>📦 Clave SKU</h4>
                       <p style='color: #4A4A4A; font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0;'>{sku_id}</p>
                   </div>                
                   <div>
                       <h4 style='color: #6B5B73; margin: 0; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;'>📊 Cantidad seleccionada</h4>
                       <p style='color: #4A4A4A; font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0;'>{cantidad}</p>
                   </div>          
               </div>
           </div>
           """, unsafe_allow_html=True)

def render_delivery_dates(data: dict, original_request: dict):
    """
    Muestra fechas importantes en el cálculo como la Fecha de compra y Fecha estimada de entrega.
    """

    fecha_compra = original_request.get('fecha_compra', '')
    fecha_entrega = data.get('fecha_entrega', '')
    tipo_entrega = data.get('tipo_entrega', {})

    if not fecha_compra and 'fecha_compra' in st.session_state:
        fecha_compra = str(st.session_state.fecha_compra)

    dias_diferencia = calculate_relative_arrival(fecha_compra, fecha_entrega)
    ventana_horaria = data.get('tipo_entrega', {}).get('ventana_tiempo', 'N/A')

    # Main summary box (sin cambios, ya estaba bien)
    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg, #F2E9E4, #E8DCCF);
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        border: 2px solid #C8B8A1;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    '>
        <h3 style='color: #6B5B73; text-align: center; margin-bottom: 2rem;'>🎯 Fechas importantes</h3>
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; text-align: center;'>
            <div>
                <h4 style='color: #6B5B73; margin: 0; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;'>📅 Fecha de Compra</h4>
                <p style='color: #4A4A4A; font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0;'>{format_datetime(fecha_compra)}</p>
            </div>
            <div>
                <h4 style='color: #6B5B73; margin: 0; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;'>🎯 Fecha de Entrega</h4>
                <p style='color: #4A4A4A; font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0;'>{format_datetime(fecha_entrega)}</p>
            </div>
            <div>
                <h4 style='color: #6B5B73; margin: 0; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;'>⏰ Llega en</h4>
                <p style='color: #E07A5F; font-size: 1.3rem; font-weight: 700; margin: 0.5rem 0;'>{dias_diferencia}</p>
            </div>
            <div>
                <h4 style='color: #6B5B73; margin: 0; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;'>📦 Tipo de Entrega</h4>
                <p style='color: #4A4A4A; font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0;'>{tipo_entrega.get('icono', '')} {tipo_entrega.get('nombre', 'N/A')}</p>
            </div>              
            <div>
                <h4 style='color: #6B5B73; margin: 0; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;'>🕐 Ventana Horaria</h4>
                <p style='color: #4A4A4A; font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0;'>{ventana_horaria}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_delivery_details(data: dict):
    """
    Muestra detalles para llevar a cabo la entrega
    """
    ruta_seleccionada = data.get('id_trazo', 'N/A')

    es_split = data.get("es_split", False)

    if not es_split:

        tiendas_asignadas = data.get('tienda', 'N/A')

    else:

        split_info = data.get('split_info', {})

        # Obtenemos el total de tiendas involucradas
        rutas_info = split_info.get('detalle_rutas', {})
        tiendas_asignadas = set()

        for ruta in rutas_info:
            tiendas_asignadas.add(ruta['tienda'])

    metodo = data.get('metodo', 'N/A')
    score = f"{data.get('score', 0):.3f}"
    costo_total = format_currency(data.get('costo', 0))

    # Main summary box (sin cambios, ya estaba bien)
    st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #CFEDE6, #E8DCCF);
            padding: 2rem;
            border-radius: 15px;
            margin: 1.5rem 0;
            border: 2px solid #C8B8A1;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        '>
            <h3 style='color: #6B5B73; text-align: center; margin-bottom: 2rem;'>🧿️ Detalles logísticos</h3>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; text-align: center;'>
                <div>
                    <h4 style='color: #6B5B73; margin: 0; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;'>🏪 Tienda(s) Asignada(s)</h4>
                    <p style='color: #4A4A4A; font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0;'>{tiendas_asignadas}</p>
                </div>
                <div>
                    <h4 style='color: #6B5B73; margin: 0; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;'>🗺️ Ruta Seleccionada</h4>
                    <p style='color: #4A4A4A; font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0;'>{ruta_seleccionada}</p>
                </div>                
                <div>
                    <h4 style='color: #6B5B73; margin: 0; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;'>📊 Score</h4>
                    <p style='color: #4A4A4A; font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0;'>{score}</p>
                </div>
                <div>
                    <h4 style='color: #6B5B73; margin: 0; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;'>🚚 Método de Entrega</h4>
                    <p style='margin: 0.5rem 0;'>{get_delivery_status_badge(metodo)}</p>
                </div>
                <div>
                    <h4 style='color: #6B5B73; margin: 0; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;'>💰 Costo Total</h4>
                    <p style='color: #4A4A4A; font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0;'>{costo_total}</p>
                </div>              
            </div>
        </div>
        """, unsafe_allow_html=True)

    render_split_elements(data)

def render_split_elements(data: dict):
    """
    Muestra una tabla con las tiendas involucradas en el split
    """

    es_split = data.get('es_split', False)

    if es_split:
        split_info = data.get('split_info', {})
        if split_info:

            # Obtenemos el total de tiendas usadas
            rutas_info = split_info.get('detalle_rutas', {})
            tiendas_seleccionadas = set()

            for ruta in rutas_info:

                tiendas_seleccionadas.add(ruta['tienda'])

            split_html_content = f"""
                <div style='
                    background-color: #FFF3E0;
                    padding: 1rem;
                    border-radius: 10px;
                    margin-top: 1.5rem;
                    border: 1px solid #FFCC80;
                    color: #FB8C00;
                '>
                    <h4 style='color: #FB8C00; margin: 0 0 0.5rem 0;'>📦 ENTREGA DIVIDIDA (SPLIT)</h4>
                    <ul style='list-style-position: inside; padding-left: 0;'>
                        <li style='margin-bottom: 0.3rem;'><strong>Rutas Seleccionadas:</strong> {split_info.get('rutas_seleccionadas', 'N/A')}</li>
                        <li style='margin-bottom: 0.3rem;'><strong>Tiendas Seleccionadas:</strong> {len(tiendas_seleccionadas)}</li>
                        <li style='margin-bottom: 0.3rem;'><strong>Cantidad Total:</strong> {split_info.get('cantidad_total', 'N/A')}</li>
                        <li style='margin-bottom: 0.3rem;'><strong>Costo Total:</strong> {format_currency(split_info.get('costo_total', 0))}</li>
                        <li style='margin-bottom: 0.3rem;'><strong>Tiempo Total:</strong> {split_info.get('tiempo_total', 'N/A')} días</li>
                        <li style='margin-bottom: 0.3rem;'><strong>Algoritmo:</strong> {split_info.get('algoritmo_optimizacion', 'N/A')}</li>
                    </ul>
                </div>
                """

            detalle_rutas = split_info.get('detalle_rutas', [])
            if detalle_rutas:
                split_html_content += "<h4 style='color: #4A4A4A; margin-top: 2rem;'>🔄 Detalles de Rutas del Split:</h4>"

                table_header = """
                    <table style="width: 100%; border-collapse: collapse; margin: 10px 0; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
                        <thead style="background-color: #E3F2FD;">
                            <tr>
                                <th style="padding: 12px; border: 1px solid #BBDEFB; text-align: center; color: #3F51B5;">Ruta</th>
                                <th style="padding: 12px; border: 1px solid #BBDEFB; text-align: center; color: #3F51B5;">ID Trazo</th>
                                <th style="padding: 12px; border: 1px solid #BBDEFB; text-align: center; color: #3F51B5;">Tienda</th>
                                <th style="padding: 12px; border: 1px solid #BBDEFB; text-align: center; color: #3F51B5;">Inventario</th>
                                <th style="padding: 12px; border: 1px solid #BBDEFB; text-align: center; color: #3F51B5;">Cantidad</th>
                                <th style="padding: 12px; border: 1px solid #BBDEFB; text-align: center; color: #3F51B5;">Tiempo</th>
                                <th style="padding: 12px; border: 1px solid #BBDEFB; text-align: center; color: #3F51B5;">Costo</th>
                                <th style="padding: 12px; border: 1px solid #BBDEFB; text-align: center; color: #3F51B5;">Método</th>
                                <th style="padding: 12px; border: 1px solid #BBDEFB; text-align: center; color: #3F51B5;">Capacidad_ME</th>
                                <th style="padding: 12px; border: 1px solid #BBDEFB; text-align: center; color: #3F51B5;">Score</th>
                                
                                
                            </tr>
                        </thead>
                        <tbody>
                    """
                table_rows = ""
                for i, ruta in enumerate(detalle_rutas):
                    row_color = "#f9f9f9" if i % 2 == 0 else "#ffffff"
                    table_rows += f"""
                        <tr style="background-color: {row_color};">
                            <td style="padding: 10px; border: 1px solid #E0E0E0; text-align: center;">Ruta {i + 1}</td>
                            <td style="padding: 10px; border: 1px solid #E0E0E0; text-align: center;">{ruta.get('id_trazo', 'N/A')}</td>
                            <td style="padding: 10px; border: 1px solid #E0E0E0; text-align: center;">{ruta.get('tienda', 'N/A')}</td>
                            <td style="padding: 10px; border: 1px solid #E0E0E0; text-align: center;">{ruta.get('inventario_disponible', 'N/A')}</td>
                            <td style="padding: 10px; border: 1px solid #E0E0E0; text-align: center;">{ruta.get('cantidad', 'N/A')}</td>
                            <td style="padding: 10px; border: 1px solid #E0E0E0; text-align: center;">{ruta.get('dias', 'N/A')}</td>
                            <td style="padding: 10px; border: 1px solid #E0E0E0; text-align: center;">{format_currency(ruta.get('costo_total_ruta', 0))}</td>
                            <td style="padding: 10px; border: 1px solid #E0E0E0; text-align: center;">{ruta.get('metodo', 'N/A')}</td>
                            <td style="padding: 10px; border: 1px solid #E0E0E0; text-align: center;">{ruta.get('capacidad_me', 0):.3f}</td>
                            <td style="padding: 10px; border: 1px solid #E0E0E0; text-align: center;">{ruta.get('score', 'N/A')}</td>
                        </tr>
                        """
                table_footer = "</tbody></table>"

                split_html_content += table_header + table_rows + table_footer

            st.html(split_html_content)

def render_all_options(data: dict, original_request: dict, recalculate: bool = False):
    """
    Consulta a Bigquery y despliega los resultados de la consulta del request
    """
    df_bigquery = pd.DataFrame()
    bq_client = get_bigquery_client() # Mandar la service account

    if bq_client:
        df_bigquery = execute_bigquery_query(bq_client, original_request)

        if not df_bigquery.empty and data:
            generate_comparison_table(df_bigquery, data, original_request, recalculate)

    else:
        st.warning("Ocurrió un error al consultar BigQuery, por favor revisa tu conexión.")


def render_context_info(data: dict):
    """
    Muestra información contextual sobre el request original
    """
    st.subheader("🗺️ Información Contextual")

    geo_context = data.get('contexto_geografico', {})
    clima_context = data.get('contexto_climatico', {})

    st.subheader("📍️ Contexto Geográfico")
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
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📍 Región", clima_context.get('region_nombre', 'N/A'))
        st.metric("🗺️ Estado Principal", clima_context.get('estado_principal', 'N/A'))
    with col2:
        st.metric("☀️ Clima Actual", clima_context.get('clima_actual', 'N/A'))
        st.metric("🌡️ Temperatura (Min/Max)",
                  f"{clima_context.get('temperatura_min', 'N/A')}°C / {clima_context.get('temperatura_max', 'N/A')}°C")
    with col3:
        st.metric("⛰️ Altitud (msnm)", clima_context.get('altitud_msnm', 'N/A'))
        st.metric("💧 Precipitación Anual", f"{clima_context.get('precipitacion_anual', 'N/A')} mm")
        st.metric("⚡ Factores Especiales", clima_context.get('factores_especiales', 'N/A'))

def render_technical_details(data: dict):
    """
    Muestra detalles relacionados con el procesamiento del sistema
    """

    st.subheader("️⚙️ Detalles técnicos")

    tiempo_procesamiento = data.get('tiempo_proceso_ms', 'N/A')

    st.metric("🕐 Tiempo de procesamiento (ms)", tiempo_procesamiento)


def render_interactive_charts(data: dict, original_request):
    """Renderizar gráficos interactivos"""
    # render_delivery_route_graph(data)
    # render_delivery_summary(data, original_request)

    return

def render_delivery_calendar_view(data: dict, original_request: dict, is_recalculation: bool):
    """
    Muestra un calendario visual para resaltar fechas importantes en el trazo logistico.
    Adapta las fechas mostradas si es un recálculo.
    """
    st.subheader("🗓️ Calendario de Fechas Importantes")

    events = []
    initial_date = None # Initialize initial_date here

    # --- Common: Fecha de Compra (always present in original_request) ---
    fecha_compra_str = original_request.get('fecha_compra', '')
    if fecha_compra_str:
        try:
            fecha_compra_date = datetime.fromisoformat(fecha_compra_str.replace('Z', '+00:00')).date()
            events.append({
                "title": "Fecha de Compra",
                "start": fecha_compra_date.isoformat(),
                "color": "#1E88E5", # Blue for purchase date
                "borderColor": "#1565C0"
            })
            initial_date = fecha_compra_date.isoformat() # Set initial_date if purchase date is available
        except ValueError:
            st.warning(f"Advertencia: Formato de Fecha de Compra inválido: {fecha_compra_str}")

    # --- Conditional Logic for Recalculation ---
    if is_recalculation:
        st.info("Mostrando fechas para Recálculo.")
        fecha_original_str = data.get('fecha_entrega_original', '') # Assuming 'fecha_entrega_original' exists in 'data'
        fecha_nueva_str = data.get('fecha_entrega', '') # 'fecha_entrega' is the new one after recalculation

        # Event: Fecha Original
        if fecha_original_str:
            try:
                fecha_original_date = datetime.fromisoformat(fecha_original_str.replace('Z', '+00:00')).date()
                events.append({
                    "title": "Fecha Original",
                    "start": fecha_original_date.isoformat(),
                    "color": "#E57373", # Amber/Orange for original date
                    "borderColor": "#D32F2F"
                })
                # Prioritize original date for initial view if recalculation
                if not initial_date:
                    initial_date = fecha_original_date.isoformat()
            except ValueError:
                st.warning(f"Advertencia: Formato de Fecha Original inválido: {fecha_original_str}")

        # Event: Fecha Nueva (the recalculated delivery date)
        if fecha_nueva_str:
            try:
                fecha_nueva_date = datetime.fromisoformat(fecha_nueva_str.replace('Z', '+00:00')).date()
                events.append({
                    "title": "Fecha Nueva",
                    "start": fecha_nueva_date.isoformat(),
                    "color": "#4CAF50", # Green for new delivery date
                    "borderColor": "#388E3C"
                })
                # Prioritize new date for initial view if recalculation
                if not initial_date:
                    initial_date = fecha_nueva_date.isoformat()
            except ValueError:
                st.warning(f"Advertencia: Formato de Fecha Nueva inválido: {fecha_nueva_str}")

    else: # Not a recalculation (original prediction)
        st.info("Mostrando fechas para Predicción Original.")
        fecha_entrega_str = data.get('fecha_entrega', '') # This is the delivery date for original prediction

        # Event: Fecha de Entrega (for original prediction)
        if fecha_entrega_str:
            try:
                fecha_entrega_date = datetime.fromisoformat(fecha_entrega_str.replace('Z', '+00:00')).date()
                events.append({
                    "title": "Fecha de Entrega",
                    "start": fecha_entrega_date.isoformat(),
                    "color": "#4CAF50", # Green for delivery date
                    "borderColor": "#388E3C"
                })
                # Prioritize delivery date for initial view
                if not initial_date:
                    initial_date = fecha_entrega_date.isoformat()
            except ValueError:
                st.warning(f"Advertencia: Formato de Fecha de Entrega inválido: {fecha_entrega_str}")

    calendar_options = {
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth"
        },
        "initialView": "dayGridMonth",
        "editable": False,
        "selectable": False,
        "height": "auto",
        "contentHeight": "auto",
        "locale": "es" # Idioma del calendario

    }

    # --- Custom CSS (keeping your light theme) ---
    custom_css = """
        .fc {
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            font-size: 0.85em;
            background-color: #F8F9FA;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        .fc .fc-toolbar-title {
            color: #333333;
            font-size: 1.4em;
        }
        .fc .fc-button {
            background-color: #E0E0E0;
            border: 1px solid #CCCCCC;
            color: #444444;
            border-radius: 5px;
            padding: 6px 10px;
            margin: 0 3px;
            font-size: 0.8em;
        }
        .fc .fc-button:hover {
            background-color: #D5D5D5;
            color: #222222;
            border-color: #BBBBBB;
        }
        .fc .fc-button:focus {
            box-shadow: none;
            outline: none;
        }
        .fc-daygrid-event {
            font-size: 0.7em;
            padding: 2px 4px;
            border-radius: 3px;
            margin-bottom: 1px;
            font-weight: bold;
            color: #FFFFFF !important;
        }
        .fc-daygrid-day-number {
            color: #555555;
            font-size: 0.9em;
            font-weight: 500;
            padding-top: 2px;
        }
        .fc-day-other .fc-daygrid-day-number {
            color: #AAAAAA;
        }
        .fc-col-header-cell-cushion {
            color: #444444;
            font-weight: bold;
            text-transform: uppercase;
            font-size: 0.8em;
            padding-top: 5px;
            padding-bottom: 5px;
        }
        .fc-view-harness {
            background-color: #FFFFFF;
            border-radius: 8px;
            overflow: hidden;
        }
        .fc-scrollgrid-sync-table {
            background-color: #FFFFFF;
        }
        .fc-theme-standard td, .fc-theme-standard th {
            border-color: #E0E0E0;
        }
        .fc-daygrid-body-unbalanced .fc-daygrid-day-events {
            margin-top: 0;
        }
        .fc-daygrid-body-unbalanced .fc-daygrid-day-frame {
            padding-bottom: 0;
        }
        .fc-daygrid-day.fc-day-today {
            background-color: #FFFFFF !important; /* Set to white to remove yellow */
            /* You can keep or remove the border as per your design preference */
            border: 1px solid #E0E0E0 !important;
        }
        .fc-daygrid-day {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            min-height: 70px;
        }
    """

    # Render the calendar
    calendar(
        events=events,
        options=calendar_options,
        custom_css=custom_css,
        key="delivery_calendar_conditional"
    )

# Métodos auxiliares para el correcto renderizado
def calculate_relative_arrival(fecha_compra_str: str, fecha_entrega_str: str) -> str:
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