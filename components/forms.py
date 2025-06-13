# components/forms.py
import streamlit as st
from datetime import datetime
from config.settings import Config
from services.api_client import APIClient
from components.layout import render_header


def render_prediction_form():
    """Renderizar formulario de predicción"""
    # Header
    render_header(
        f"🚚 {Config.APP_TITLE}",
        "Autor: Iván Martinez Trejo | Logistica Liverpool beta 1"
    )

    # Formulario principal
    with st.container():
        st.markdown("<div class='form-container'>", unsafe_allow_html=True)

        # Título del formulario
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h3 style='color: #1e293b; font-family: Poppins; font-weight: 600;'>
                📋 Información del Pedido
            </h3>
            <p style='color: #64748b; margin-top: 0.5rem;'>
                Complete los datos para generar una predicción precisa
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Campos del formulario en dos columnas
        col1, col2 = st.columns(2, gap="large")

        with col1:
            # Ubicación
            st.markdown("### 📍 Ubicación")
            codigo_postal = st.text_input(
                "Código Postal de Destino",
                value=Config.DEFAULT_CP,
                help="📮 Ingrese el código postal donde se realizará la entrega",
                placeholder="Ej: 05050"
            )

            # Producto
            st.markdown("### 🏷️ Producto")
            sku_id = st.text_input(
                "SKU del Producto",
                value=Config.DEFAULT_SKU,
                help="🏷️ Identificador único del producto",
                placeholder="Ej: LIV-004"
            )

        with col2:
            # Cantidad
            st.markdown("### 📦 Cantidad")
            cantidad = st.number_input(
                "Cantidad de Productos",
                min_value=1,
                max_value=100,
                value=Config.DEFAULT_QUANTITY,
                help="📦 Número de unidades a entregar"
            )

            # Fecha y hora
            st.markdown("### 📅 Fecha de Compra")
            col_fecha, col_hora = st.columns(2)

            with col_fecha:
                fecha_compra = st.date_input(
                    "Fecha",
                    value=datetime.now().date(),
                    help="📅 Fecha en que se realizó la compra"
                )

            with col_hora:
                hora_compra = st.time_input(
                    "Hora",
                    value=datetime.now().time(),
                    help="🕐 Hora en que se realizó la compra"
                )

        st.markdown("</div>", unsafe_allow_html=True)

        # Botón de predicción centrado
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])

        with col2:
            if st.button(
                    "🔮 Generar Predicción",
                    type="primary",
                    use_container_width=True,
                    help="Analizar los datos y generar predicción de entrega"
            ):
                # Validaciones
                if not codigo_postal or len(codigo_postal) < 5:
                    st.error("❌ Por favor ingrese un código postal válido (mínimo 5 dígitos)")
                    return

                if not sku_id:
                    st.error("❌ Por favor ingrese un SKU válido")
                    return

                # Procesar predicción
                process_prediction(codigo_postal, sku_id, cantidad, fecha_compra, hora_compra)


def process_prediction(codigo_postal: str, sku_id: str, cantidad: int, fecha_compra, hora_compra):
    """Procesar la predicción"""
    try:
        # Combinar fecha y hora
        fecha_hora_compra = datetime.combine(fecha_compra, hora_compra)
        fecha_str = fecha_hora_compra.strftime("%Y-%m-%dT%H:%M:%S")

        # Llamada al API
        api_client = APIClient()
        result, error = api_client.predict_delivery(codigo_postal, sku_id, cantidad, fecha_str)

        if result:
            # Guardar resultado y cambiar vista
            st.session_state.prediction_data = result
            st.session_state.show_results = True

            # Mostrar mensaje de éxito
            st.success("✅ ¡Predicción generada exitosamente!")
            st.balloons()

            # Recargar para mostrar resultados
            st.rerun()

        else:
            # Mostrar error
            st.error(f"❌ {error}")

            # Sugerencias de solución
            with st.expander("💡 Posibles soluciones"):
                st.markdown("""
                **Si el error persiste, intente:**
                - Verificar que el servidor esté ejecutándose en `http://0.0.0.0:8000`
                - Comprobar que el código postal sea válido
                - Validar que el SKU exista en el sistema
                - Revisar la conexión a internet
                - Contactar al administrador del sistema
                """)

    except Exception as e:
        st.error(f"❌ Error inesperado: {str(e)}")
        st.info("💡 Si el problema persiste, contacte al soporte técnico.")