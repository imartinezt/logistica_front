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


def render_recalculate_forms(data: dict, original_request: dict):
    """
    Renderiza un forms para ejecutar el recálculo de la ultima EDD calculada
    """
    st.subheader("⚙️ Configuración para el Recálculo de Entrega")

    # Extracción de valores iniciales del request original
    fecha_entrega_promesa_init = data.get('fecha_entrega', '')
    tienda_rechazada_init = data.get('tienda', 0)
    alternativas = data.get('alternativas', [])
    rutas_seleccionadas_init = [alt.get('id', '') for alt in alternativas if alt.get('selected', False)]
    codigo_postal_init = original_request.get('codigo_postal', '')
    sku_id_init = original_request.get('sku_id', '')

    can_recalculate = bool(
        original_request.get('codigo_postal') and
        original_request.get('sku_id') and
        fecha_entrega_promesa_init and
        tienda_rechazada_init
    )

    if not can_recalculate:
        st.warning("⚠️ No se pueden realizar recálculos. Faltan datos del request original.")
        return

    st.markdown("**Modifica los datos que se utilizarán para el recálculo:**")
    tienda_rechazada_str = ", ".join(tienda_rechazada_init) if isinstance(tienda_rechazada_init, set) else str(tienda_rechazada_init)

    # Creamos un estado de sesión para las rutas rechazadas si no existe
    if 'rutas_rechazadas_str' not in st.session_state:
        st.session_state.rutas_rechazadas_str = ', '.join(rutas_seleccionadas_init)

    with st.form(key="recalculation_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            # Datos del request original
            codigo_postal_rq = st.text_input(
                "Código Postal",
                value=codigo_postal_init,
                placeholder="Ej: 14650",
                help="Código postal de destino"
            )
            sku_id_rq = st.text_input(
                "SKU ID",
                value=sku_id_init,
                placeholder="Ej: 1159567954",
                help="Identificador único del producto"
            )
            temporada_rq = st.selectbox(
                "Selecciona la temporada",
                ("TEMPORADA_BAJA", "TEMPORADA_ALTA"),
            )

        with col2:
            # Fechas importantes
            fecha_compra_rq = st.date_input(
                "Fecha de Compra",
                value=datetime.now().date(),
                help="Fecha cuando se realizó la compra"
            )

            fecha_original_rq = st.date_input(
                "Fecha de Entrega",
                value=datetime.now().date(),
                help="Fecha de entrega estimada"
            )

        with col3:
            # Rutas y tiendas a rechazar
            rutas_rq = st.text_input(
                "Rutas a Rechazar",
                value=', '.join(rutas_seleccionadas_init),
                help="Ingresa las rutas a rechazar, separadas por comas."
            )

            tiendas_rq = st.text_input(
                "Tienda(s) a Rechazar",
                value=tienda_rechazada_str,
                help="Ingresa el ID de la tienda o múltiples IDs separados por comas."
            )

            # Checkbox para la prioridad de la fecha de entrega
            priorizar_fecha_promesa = st.checkbox(
                "Priorizar Fecha Promesa",
                help="Si está activado, priorizará mantener la fecha promesa original",
            )

        # Usar un checkbox fuera del formulario para visualizar los datos
        ver_datos = st.checkbox("📋 Ver datos que se enviarán al API", value=False)
        if ver_datos:
            st.json({
                "codigo_postal": codigo_postal_rq,
                "sku_id": sku_id_rq,
                "cantidad": original_request.get('cantidad', 1),
                "fecha_compra_original": fecha_compra_rq.strftime('%Y-%m-%d'),
                "fecha_entrega_promesa": fecha_original_rq.strftime('%Y-%m-%d'),
                "tienda_rechazada": tiendas_rq,
                "temporada": temporada_rq,
                "rutas_rechazadas": [r.strip() for r in rutas_rq.split(',')],
                "priorizar_fecha_promesa": priorizar_fecha_promesa,
            })

        # Botón de envío del formulario
        submitted = st.form_submit_button("🔄 Ejecutar Recálculo", type="secondary", use_container_width=True)

        if submitted:
            # Creamos el diccionario de datos del request
            request_data = {
                "codigo_postal": codigo_postal_rq,
                "sku_id": sku_id_rq,
                "cantidad": original_request.get('cantidad', 1),
                "fecha_compra_original": fecha_compra_rq.strftime('%Y-%m-%d'),
                "fecha_entrega_promesa": fecha_original_rq.strftime('%Y-%m-%d'),
                "tienda_rechazada": tiendas_rq,
                "temporada": temporada_rq,
                "rutas_rechazadas": [r.strip() for r in rutas_rq.split(',')],
                "priorizar_fecha_promesa": priorizar_fecha_promesa
            }

            execute_recalculation(request_data)


def execute_recalculation(request_data: dict):
    """Ejecutar recálculo con los datos recibidos del formulario."""
    try:
        # Extraemos los valores del diccionario
        codigo_postal = request_data.get('codigo_postal')
        sku_id = request_data.get('sku_id')
        cantidad = request_data.get('cantidad')
        fecha_compra_original = request_data.get('fecha_compra_original')
        fecha_entrega_promesa = request_data.get('fecha_entrega_promesa')
        tienda_rechazada = request_data.get('tienda_rechazada')
        temporada = request_data.get('temporada')
        rutas_rechazadas = request_data.get('rutas_rechazadas')
        priorizar_fecha_promesa = request_data.get('priorizar_fecha_promesa')

        if not codigo_postal or not sku_id or not fecha_compra_original:
            st.error("❌ Faltan datos del request original para el recálculo")
            return

        result_placeholder = st.empty()

        with st.status("🔄 Ejecutando recálculo...", expanded=True) as status:
            st.write("🔍 Preparando datos del recálculo...")
            st.write(f"📍 CP: {codigo_postal} | SKU: {sku_id} | Cantidad: {cantidad}")
            st.write(f"🏪 Rechazando tienda: {tienda_rechazada}")
            st.write(f"🚫 Rechazando rutas: {', '.join(rutas_rechazadas) if rutas_rechazadas else 'Ninguna'}")

            api_client = APIClient()
            result, error = api_client.recalculate_delivery(**request_data) # Desempaquetamos el diccionario

            if result:
                st.write("✅ Recálculo completado exitosamente")
                status.update(label="✅ Recálculo Completado", state="complete", expanded=False)
                st.session_state.prediction_data = result
                st.session_state.show_results = True
                with result_placeholder.container():
                    st.success("🎉 **Recálculo completado exitosamente!**")
                    st.rerun()
            else:
                st.write("❌ Error en el recálculo")
                status.update(label="❌ Error en Recálculo", state="error", expanded=False)
                with result_placeholder.container():
                    st.error(f"🚫 **Error en el recálculo:** {error}")
                    with st.expander("🔍 Detalles del Error", expanded=False):
                        st.write("**Datos enviados:**")
                        st.json(request_data)
                        st.write(f"**Error recibido:** {error}")
    except Exception as e:
        st.error(f"❌ Error en recálculo: {str(e)}")
        st.write(f"**Detalles del error:** {str(e)}")