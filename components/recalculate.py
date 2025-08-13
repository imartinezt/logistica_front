import streamlit as st
from services.api_client import APIClient
from utils.helpers import format_currency, format_datetime
from datetime import datetime

def render_recalculo_comparison(data: dict):
    """Mostrar comparación del recálculo"""
    st.markdown("### 🔄 Resultados del Recálculo")

    tienda_rechazada = data.get('tienda_rechazada', 'N/A')

    # Caso split
    es_split = data.get('es_split', False)

    if es_split:
        tienda_rechazada = st.session_state.tienda_rechazada


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
        st.info(f"**Tienda(s) Rechazada(s):** {tienda_rechazada}")

        rutas_descartadas = data.get('rutas_descartadas', [])
        rutas_text = ', '.join(rutas_descartadas) if rutas_descartadas else 'Ninguna'
        st.info(f"**Rutas Descartadas:** {rutas_text}")

    st.markdown("---")


def render_recalculate_section(data: dict, original_request: dict):
    """
    Sección de recálculo con campos completamente editables.
    """
    st.subheader("⚙️ Configuración para el Recálculo de Entrega")

    # Extracción de valores iniciales del request original
    fecha_entrega_promesa = data.get('fecha_entrega', '')
    tienda_rechazada = data.get('tienda', 0)
    alternativas = data.get('alternativas', [])
    rutas_seleccionadas = [alt.get('id', '') for alt in alternativas if alt.get('selected', False)]
    codigo_postal = original_request.get('codigo_postal', '')
    sku_id = original_request.get('sku_id', '')

    can_recalculate = bool(
        original_request.get('codigo_postal') and
        original_request.get('sku_id') and
        fecha_entrega_promesa and
        tienda_rechazada
    )

    if not can_recalculate:
        st.warning("⚠️ No se pueden realizar recálculos. Faltan datos del request original.")
        return

    st.markdown("**Modifica los datos que se utilizarán para el recálculo:**")

    # Si `tienda_rechazada` es un conjunto, lo convertimos a cadena
    tienda_rechazada_str = ", ".join(tienda_rechazada) if isinstance(tienda_rechazada, set) else str(tienda_rechazada)

    # Creamos un estado de sesión para las rutas rechazadas si no existe
    if 'rutas_rechazadas_str' not in st.session_state:
        st.session_state.rutas_rechazadas_str = ', '.join(rutas_seleccionadas)

    col1, col2, col3 = st.columns(3)

    with col1:
        # Campos de entrada para los datos del request original
        st.session_state.codigo_postal = st.text_input(
            "Código Postal",
            value=codigo_postal,
            placeholder="Ej: 14650",
            key="cp_input",
            help="Código postal de destino"
        )
        st.session_state.sku_id = st.text_input(
            "SKU ID",
            value=sku_id,
            placeholder="Ej: 1159567954",
            key="sku_input",
            help="Identificador único del producto"
        )

        temporada = st.selectbox(
            "Selecciona la temporada",
            ("TEMPORADA_BAJA", "TEMPORADA_ALTA")

        )

    with col2:

        st.session_state.fecha_compra = st.date_input(
            "Fecha de Compra",
            value=datetime.now().date(),
            key="fecha_compra_input",
            help="Fecha cuando se realizó la compra"
        )

        st.session_state.fecha_entrega = st.date_input(
            "Fecha de Entrega",
            value=datetime.now().date(),
            key="fecha_entrega_input",
            help="Fecha de entrega estimada"
        )

    with col3:
        # Campo para editar las rutas a rechazar
        rutas_rechazadas_rq = st.text_input(
            "Rutas a Rechazar",
            value=st.session_state.rutas_rechazadas_str,
            key="rutas_rechazadas_input",
            help="Ingresa las rutas a rechazar, separadas por comas."
        )

        st.session_state.rutas_rechazadas = [r.strip() for r in rutas_rechazadas_rq.split(',')]

        # Campo para editar las tiendas a rechazar
        st.session_state.tienda_rechazada = st.text_input(
            "Tienda(s) a Rechazar",
            value=tienda_rechazada_str,
            key="tienda_rechazada_input",
            help="Ingresa el ID de la tienda o múltiples IDs separados por comas."
        )

        # Checkbox para la prioridad de la fecha de entrega
        st.session_state.priorizar_fecha_promesa = st.checkbox(
            "Priorizar Fecha Promesa",
            help="Si está activado, priorizará mantener la fecha promesa original"
        )


    if st.checkbox("📋 Ver datos que se enviarán al API", value=False):
        # Usar los valores del estado de sesión para el request
        request_data = {
            "codigo_postal": st.session_state.get('codigo_postal'),
            "sku_id": st.session_state.get('sku_id'),
            "cantidad": original_request.get('cantidad', 1),
            "fecha_compra_original": st.session_state.get('fecha_compra').strftime('%Y-%m-%d'),
            "fecha_entrega_promesa": st.session_state.get('fecha_entrega').strftime('%Y-%m-%d'),
            "tienda_rechazada": st.session_state.get('tienda_rechazada'),
            "temporada": original_request.get('temporada', 'TEMPORADA_BAJA'),
            "rutas_rechazadas": st.session_state.get('rutas_rechazadas'),
            "priorizar_fecha_promesa": st.session_state.get('priorizar_fecha_promesa', False)
        }
        st.json(request_data)

    if st.button("🔄 Ejecutar Recálculo", type="secondary", use_container_width=True):
        priorizar = st.session_state.get('priorizar_fecha_promesa', False)
        rutas_finales = st.session_state.get('rutas_rechazadas', [])
        st.session_state.show_results = True
        execute_recalculation(data, original_request, priorizar, rutas_finales, temporada)

def execute_recalculation(data: dict, original_request: dict, priorizar_fecha_promesa: bool, rutas_rechazadas: list, temporada: str):
    """Ejecutar recálculo"""
    try:
        codigo_postal = original_request.get('codigo_postal', '')
        sku_id = original_request.get('sku_id', '')
        cantidad = original_request.get('cantidad', 1)
        fecha_compra_original = original_request.get('fecha_compra', '')
        temporada = temporada.upper()

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