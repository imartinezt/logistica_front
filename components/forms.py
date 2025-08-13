import streamlit as st
from datetime import datetime
from config.settings import Config
from services.api_client import APIClient


def render_prediction_form():
    """Formulario de predicción """
    st.markdown("""
        <div class="main-header">
            <h1>📦 Fecha de Entrega Estimada</h1>
            <p class="subtitle">Plataforma de predicción de entregas</p>
        </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="form-container">', unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            st.markdown("#### 📍 Información del Pedido")
            codigo_postal = st.text_input(
                "Código Postal",
                value=Config.DEFAULT_CP,
                placeholder="Ej: 14650",
                key="cp_input",
                help="Código postal de destino"
            )

            sku_id = st.text_input(
                "SKU ID",
                value=Config.DEFAULT_SKU,
                placeholder="Ej: 1159567954",
                key="sku_input",
                help="Identificador único del producto"
            )

            cantidad = st.number_input(
                "Cantidad",
                min_value=1,
                max_value=Config.MAX_QUANTITY,
                value=Config.DEFAULT_QUANTITY,
                key="qty_input",
                help="Cantidad de productos a enviar"
            )

        with col2:
            st.markdown("#### ⚙️ Configuración")
            temporada = st.selectbox(
                "Temporada",
                Config.TEMPORADAS,
                index=0,
                key="temporada_input",
                help="Temporada comercial que afecta la logística"
            )

            fecha_compra = st.date_input(
                "Fecha de Compra",
                value=datetime.now().date(),
                key="fecha_input",
                help="Fecha cuando se realizó la compra"
            )

            hora_compra = st.time_input(
                "Hora de Compra",
                value=datetime.now().time(),
                key="hora_input",
                help="Hora específica de la compra"
            )

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Calcular Fecha de Entrega", type="primary", use_container_width=True):
                if validate_inputs(codigo_postal, sku_id):
                    process_prediction(codigo_postal, sku_id, cantidad, temporada, fecha_compra, hora_compra)


def validate_inputs(codigo_postal: str, sku_id: str) -> bool:
    """Validar entradas del formulario"""
    if not codigo_postal or len(codigo_postal) < Config.MIN_CP_LENGTH:
        st.error(f"❌ Código postal requerido (mínimo {Config.MIN_CP_LENGTH} dígitos)")
        return False

    if not sku_id or len(sku_id) < Config.MIN_SKU_LENGTH:
        st.error(f"❌ SKU ID requerido (mínimo {Config.MIN_SKU_LENGTH} caracteres)")
        return False

    return True


def process_prediction(codigo_postal: str, sku_id: str, cantidad: int, temporada: str, fecha_compra, hora_compra):
    """Procesar predicción con indicadores visuales"""
    try:
        fecha_hora_compra = datetime.combine(fecha_compra, hora_compra)
        fecha_str = fecha_hora_compra.strftime("%Y-%m-%dT%H:%M:%S.%f")

        with st.status("🔄 Procesando predicción...", expanded=True) as status:
            st.write("📡 Enviando solicitud al servidor...")
            st.write(f"📍 CP: {codigo_postal} | 📦 SKU: {sku_id} | 🔢 Qty: {cantidad}")

            api_client = APIClient()
            result, error = api_client.predict_delivery(
                codigo_postal, sku_id, cantidad, temporada, fecha_str
            )

            if result:
                st.write("✅ Predicción completada exitosamente")
                status.update(label="✅ Completado", state="complete", expanded=False)

                st.session_state.prediction_data = result
                st.session_state.original_request = {
                    "codigo_postal": codigo_postal,
                    "sku_id": sku_id,
                    "cantidad": cantidad,
                    "temporada": temporada,
                    "fecha_compra": fecha_str
                }
                st.session_state.show_results = True
                st.rerun()
            else:
                st.write("❌ Error en el procesamiento")
                status.update(label="❌ Error", state="error", expanded=False)
                st.error(f"🚫 {error}")

    except Exception as e:
        st.error(f"❌ Error inesperado: {str(e)}")