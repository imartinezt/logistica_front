import streamlit as st
from datetime import datetime, timedelta, time
import datetime as dt
from config.settings import Config
from services.api_client import APIClient
from components.layout import render_header


def render_prediction_form():
    """Formulario de predicción simplificado"""
    render_header(
        f"🚀 {Config.APP_TITLE}",
        "Plataforma de predicción de entregas"
    )

    with st.container():
        st.markdown("### 📊 Análisis de Entrega")

        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            st.markdown("**📍 Información del Pedido**")
            codigo_postal = st.text_input(
                "Código Postal",
                value=Config.DEFAULT_CP,
                placeholder=Config.DEFAULT_CP,
                key="cp_input"
            )

            sku_id = st.text_input(
                "SKU ID",
                value=Config.DEFAULT_SKU,
                placeholder=Config.DEFAULT_SKU,
                key="sku_input"
            )

            cantidad = st.number_input(
                "Cantidad",
                min_value=1,
                max_value=Config.MAX_QUANTITY,
                value=Config.DEFAULT_QUANTITY,
                key="qty_input"
            )

        with col2:
            st.markdown("**⏰ Configuración Temporal**")

            temporada = st.selectbox(
                "Temporada",
                Config.TEMPORADAS,
                index=0,
                key="temporada_input"
            )

            date_testing = dt.date(2024, 7, 2)
            fecha_compra = st.date_input(
                "Fecha de Compra",
                value=datetime.now().date(),
                key="fecha_input"
            )

            time_testing = dt.time(10, 0, 0)
            hora_compra = st.time_input(
                "Hora de Compra",
                value=datetime.now().time(),
                key="hora_input"
            )

        st.markdown("---")

        predict_clicked = st.button(
            "🎯 Ejecutar Predicción",
            type="primary",
            use_container_width=True,
            key="predict_btn"
        )

        if predict_clicked:
            if validate_inputs(codigo_postal, sku_id):
                process_prediction(codigo_postal, sku_id, cantidad, temporada, fecha_compra, hora_compra)

def validate_inputs(codigo_postal: str, sku_id: str) -> bool:
    """Validar entradas básicas"""
    if not codigo_postal or len(codigo_postal) < Config.MIN_CP_LENGTH:
        st.error(f"📍 Código postal requerido (mínimo {Config.MIN_CP_LENGTH} dígitos)")
        return False

    if not sku_id or len(sku_id) < Config.MIN_SKU_LENGTH:
        st.error(f"📦 SKU ID requerido (mínimo {Config.MIN_SKU_LENGTH} caracteres)")
        return False

    return True

def process_prediction(codigo_postal: str, sku_id: str, cantidad: int, temporada: str, fecha_compra, hora_compra):
    """Procesar predicción"""
    try:
        fecha_hora_compra = datetime.combine(fecha_compra, hora_compra)
        fecha_str = fecha_hora_compra.strftime("%Y-%m-%dT%H:%M:%S.%f")

        with st.status("🔄 Procesando predicción...", expanded=True) as status:
            st.write("🔍 Enviando solicitud...")

            api_client = APIClient()
            result, error = api_client.predict_delivery(
                codigo_postal, sku_id, cantidad, temporada, fecha_str
            )

            if result:
                st.write("✅ Predicción completada")
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
        st.error(f"❌ Error: {str(e)}")