import streamlit as st
from datetime import datetime
from config.settings import Config
from services.api_client import APIClient


def render_split_forms(data: dict, original_request: dict):
    """
    Renderiza un formulario para ejecutar un recalculo simple con split (sin tienda rechazada)
    """
    st.subheader("⚙️ Configuración Split")

    # Extracción de valores iniciales del request original
    codigo_postal_init = original_request.get('codigo_postal', '')
    sku_id_init = original_request.get('sku_id', '')
    cantidad_init = original_request.get('cantidad', 1)
    temporada_original = original_request.get('temporada', '')
    fecha_compra_init = original_request.get('fecha_compra', '')
    tiendas_inventario = data.get("tiendas_con_inventario", 0)

    can_recalculate = bool(
        codigo_postal_init and
        sku_id_init
    )

    if not can_recalculate:
        st.warning("⚠️ No se pueden realizar el recálculo. Faltan datos del request original.")
        return

    st.markdown("**Modifica los datos para solicitar un split**")

    col_config = st.columns(1)[0]
    with col_config:
        st.markdown("##### ✅ Selección Avanzada de Split")
        opcion_split = st.radio(
            "Selecciona el tipo de split",
            ("Split Inteligente", "Split Manual"),
            help="Elige entre dejar que el sistema decida o seleccionar un número de tiendas.",
            key="split_option_radio"
        )

        forzar_split_rq = None
        if opcion_split == "Split Manual":
            forzar_split_rq = st.slider(
                "Forzar Split entre tiendas",
                min_value=2,
                max_value=int(data.get("tiendas_con_inventario", 0)),
                value=2,
                help="Número de tiendas a considerar para el split."
            )

    with st.form(key="recalculation_split_form"):
        col1, col2 = st.columns(2)

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
            st.markdown("##### 📅 Fechas y Temporada")
            try:
                fecha_compra_default = datetime.fromisoformat(
                    fecha_compra_init.replace('Z', '+00:00')).date() if fecha_compra_init else datetime.now().date()
            except:
                fecha_compra_default = datetime.now().date()

            fecha_compra_rq = st.date_input(
                "Fecha de Compra",
                value=fecha_compra_default,
                key="fecha_input",
                help="Fecha cuando se realizó la compra"
            )

            temporada_rq = st.selectbox(
                "Temporada",
                Config.TEMPORADAS,
                index=0,
                key="temporada_input",
                help="Temporada comercial que afecta la logística"
            )

        # Botón de envío del formulario
        submitted = st.form_submit_button(
            "🔄 Ejecutar predicción",
            type="primary",
            use_container_width=True
        )

        if submitted:
            # Validaciones básicas
            if not codigo_postal_rq or not sku_id_rq:
                st.error("❌ Código postal y SKU son requeridos")
                return

            # Crear el diccionario de datos del request
            payload = {
                "codigo_postal": codigo_postal_rq,
                "sku_id": sku_id_rq,
                "cantidad": cantidad_rq,
                "fecha_compra": fecha_compra_rq.strftime('%Y-%m-%dT%H:%M:%S.%f'),
                "temporada": temporada_rq,
                "forzar_split_inteligente": opcion_split == "Split Inteligente",
                "forzar_split_tiendas": forzar_split_rq,
            }

            execute_split_prediction(payload, data)


def execute_split_prediction(payload: dict, data: dict):
    """
    Ejecuta un recalculo de FEE forzando split entre tiendas
    """
    try:
        # Extraer valores para logging
        codigo_postal = payload.get('codigo_postal')
        sku_id = payload.get('sku_id')
        cantidad = payload.get('cantidad')


        if not codigo_postal or not sku_id:
            st.error("❌ Faltan datos requeridos para el recálculo")
            return

        result_placeholder = st.empty()

        with st.status("🔄 Volviendo a calcular FEE con split...", expanded=True) as status:
            st.write("🔍 Preparando datos para la predicción...")
            st.write(f"📍 CP: {codigo_postal} | 📦 SKU: {sku_id} | 🔢 Cantidad: {cantidad}")

            api_client = APIClient()
            result, error = api_client.predict_delivery(payload)

            if result:
                st.write("✅ Predicción con Split completada exitosamente")
                status.update(label="✅ Predicción Completado", state="complete", expanded=False)

                # Guardar resultado en session state
                st.session_state.prediction_data = result
                st.session_state.show_results = True
                st.rerun()
            else:
                st.write("❌ Error en la predicción") # TODO: Mapear correctamente el error (inventario insuficiente, etc.)
                status.update(label="❌ Error en la predicción con split", state="error", expanded=False)

                with result_placeholder.containe():
                    st.error(f"🚫 **Error durante la predicción:** {error}")

                    with st.expander("🔍 Detalles del Error", expanded=False):
                        st.write("**Datos enviados:**")
                        st.json(payload)
                        st.write(f"**Error recibido:** {error}")

    except Exception as e:
        st.error(f"❌ Error inesperado en la predicción: {str(e)}")
        st.write(f"**Detalles del error:** {str(e)}")

        # Mostrar traceback para debugging si es necesario
        import traceback
        with st.expander("🐛 Traceback completo", expanded=False):
            st.code(traceback.format_exc())