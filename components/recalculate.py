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
    Renderiza un formulario para ejecutar el recálculo de la ultima EDD calculada
    """
    st.subheader("⚙️ Configuración para el Recálculo de Entrega")

    # Extracción de valores iniciales del request original
    fecha_entrega_promesa_init = data.get('fecha_entrega', '')
    tienda_rechazada_init = data.get('tienda', 0)
    codigo_postal_init = original_request.get('codigo_postal', '')
    sku_id_init = original_request.get('sku_id', '')
    cantidad_init = original_request.get('cantidad', 1)
    fecha_compra_init = original_request.get('fecha_compra', '')

    can_recalculate = bool(
        codigo_postal_init and
        sku_id_init and
        fecha_entrega_promesa_init and
        tienda_rechazada_init
    )

    if not can_recalculate:
        st.warning("⚠️ No se pueden realizar recálculos. Faltan datos del request original.")
        return

    st.markdown("**Modifica los datos que se utilizarán para el recálculo:**")

    with st.form(key="recalculation_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("##### 📦 Datos del Pedido")
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
            cantidad_rq = st.number_input(
                "Cantidad",
                min_value=1,
                max_value=100,
                value=int(cantidad_init),
                help="Cantidad de productos"
            )

        with col2:
            st.markdown("##### 📅 Fechas y Tiendas")
            # Fechas importantes
            try:
                fecha_compra_default = datetime.fromisoformat(
                    fecha_compra_init.replace('Z', '+00:00')).date() if fecha_compra_init else datetime.now().date()
            except:
                fecha_compra_default = datetime.now().date()

            fecha_compra_rq = st.date_input(
                "Fecha de Compra Original",
                value=fecha_compra_default,
                help="Fecha cuando se realizó la compra"
            )

            try:
                fecha_promesa_default = datetime.fromisoformat(fecha_entrega_promesa_init.replace('Z',
                                                                                                  '+00:00')).date() if fecha_entrega_promesa_init else datetime.now().date()
            except:
                fecha_promesa_default = datetime.now().date()

            fecha_entrega_promesa_rq = st.date_input(
                "Fecha Entrega Promesa",
                value=fecha_promesa_default,
                help="Fecha promesa de entrega original"
            )

            tienda_rechazada_rq = st.number_input(
                "Tienda a Rechazar",
                min_value=1,
                max_value=9999,
                value=int(tienda_rechazada_init),
                help="ID de la tienda a rechazar"
            )

        with col3:
            st.markdown("##### ⚙️ Configuración Avanzada")

            # Slider para tipo de impacto
            tipo_impacto_valor = st.slider(
                "Tipo de Impacto",
                min_value=1,
                max_value=3,
                value=1,
                help="1 = BAJA, 2 = MEDIANA, 3 = ALTA"
            )

            # Mapear el valor del slider a texto
            tipo_impacto_map = {1: "BAJA", 2: "MEDIANA", 3: "ALTA"}
            tipo_impacto_text = tipo_impacto_map[tipo_impacto_valor]

            # Mostrar el valor seleccionado
            impacto_colors = {
                "BAJA": "🟢",
                "MEDIANA": "🟡",
                "ALTA": "🔴"
            }
            st.markdown(f"**Nivel seleccionado:** {impacto_colors[tipo_impacto_text]} {tipo_impacto_text}")

            # Checkbox para permitir split
            permitir_split = st.checkbox(
                "Permitir Split",
                value=True,
                help="Permitir dividir la orden en múltiples tiendas si es necesario"
            )

        # Separador visual
        st.markdown("---")

        # Checkbox para ver datos que se enviarán
        ver_datos = st.checkbox("📋 Ver datos que se enviarán al API", value=False)
        if ver_datos:
            request_preview = {
                "codigo_postal": codigo_postal_rq,
                "sku_id": sku_id_rq,
                "cantidad": cantidad_rq,
                "fecha_compra_original": fecha_compra_rq.strftime('%Y-%m-%dT%H:%M:%S.%f'),
                "fecha_entrega_promesa": fecha_entrega_promesa_rq.strftime('%Y-%m-%dT%H:%M:%S.%f'),
                "tienda_rechazada": tienda_rechazada_rq,
                "tipo_impacto": tipo_impacto_text,
                "permitir_split": permitir_split,
            }
            st.json(request_preview)

        # Botón de envío del formulario
        submitted = st.form_submit_button(
            "🔄 Ejecutar Recálculo",
            type="primary",
            use_container_width=True
        )

        if submitted:
            # Validaciones básicas
            if not codigo_postal_rq or not sku_id_rq:
                st.error("❌ Código postal y SKU son requeridos")
                return

            # Crear el diccionario de datos del request
            request_data = {
                "codigo_postal": codigo_postal_rq,
                "sku_id": sku_id_rq,
                "cantidad": cantidad_rq,
                "fecha_compra_original": fecha_compra_rq.strftime('%Y-%m-%dT%H:%M:%S.%f'),
                "fecha_entrega_promesa": fecha_entrega_promesa_rq.strftime('%Y-%m-%dT%H:%M:%S.%f'),
                "tienda_rechazada": tienda_rechazada_rq,
                "tipo_impacto": tipo_impacto_text,
                "permitir_split": permitir_split
            }

            execute_recalculation(request_data)


def execute_recalculation(request_data: dict):
    """Ejecutar recálculo con los datos recibidos del formulario."""
    try:
        # Extraer valores para logging
        codigo_postal = request_data.get('codigo_postal')
        sku_id = request_data.get('sku_id')
        cantidad = request_data.get('cantidad')
        tienda_rechazada = request_data.get('tienda_rechazada')
        tipo_impacto = request_data.get('tipo_impacto')

        if not codigo_postal or not sku_id:
            st.error("❌ Faltan datos requeridos para el recálculo")
            return

        result_placeholder = st.empty()

        with st.status("🔄 Ejecutando recálculo...", expanded=True) as status:
            st.write("🔍 Preparando datos del recálculo...")
            st.write(f"📍 CP: {codigo_postal} | 📦 SKU: {sku_id} | 🔢 Cantidad: {cantidad}")
            st.write(f"🏪 Rechazando tienda: {tienda_rechazada}")
            st.write(f"⚡ Tipo de impacto: {tipo_impacto}")

            api_client = APIClient()
            result, error = api_client.recalculate_delivery(**request_data)

            if result:
                st.write("✅ Recálculo completado exitosamente")
                status.update(label="✅ Recálculo Completado", state="complete", expanded=False)

                # Guardar resultado en session state
                st.session_state.prediction_data = result
                st.session_state.show_results = True

                with result_placeholder.container():
                    st.success("🎉 **Recálculo completado exitosamente!**")

                    # Mostrar resumen rápido del resultado
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📅 Nueva Fecha", format_datetime(result.get('fecha_entrega', 'N/A')))
                    with col2:
                        st.metric("💰 Nuevo Costo", format_currency(result.get('costo', 0)))
                    with col3:
                        dias_diff = result.get('dias_diferencia', 0)
                        st.metric("📊 Diferencia", f"{dias_diff} días")

                # Esperar un momento antes de rerun
                import time
                time.sleep(1)
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
        st.error(f"❌ Error inesperado en recálculo: {str(e)}")
        st.write(f"**Detalles del error:** {str(e)}")

        # Mostrar traceback para debugging si es necesario
        import traceback
        with st.expander("🐛 Traceback completo", expanded=False):
            st.code(traceback.format_exc())