import streamlit as st
from datetime import datetime
from config.settings import Config
from services.api_client import APIClient
from components.layout import render_header


def render_prediction_form():
    """Renderizar formulario de predicción mejorado"""
    render_header(
        f"🚚 {Config.APP_TITLE}",
        "Sistema inteligente de predicción de entregas para Liverpool"
    )
    st.markdown("""
    <div style='
        max-width: 800px;
        margin: 0 auto;
        padding: 0 1rem;
    '>
    """, unsafe_allow_html=True)
    with st.container():
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            padding: 3rem 2.5rem;
            border-radius: 24px;
            box-shadow: 0 20px 60px -10px rgba(0,0,0,0.1);
            border: 1px solid #e2e8f0;
            margin: 2rem 0;
        '>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center; margin-bottom: 3rem;'>
            <div style='
                background: linear-gradient(135deg, #2D5016, #8B4513);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-size: 2.5rem;
                font-weight: 800;
                font-family: "Poppins", sans-serif;
                margin-bottom: 0.5rem;
            '>
                📋 Nueva Predicción
            </div>
            <p style='
                color: #64748b; 
                font-size: 1.1rem;
                margin: 0;
                font-weight: 400;
            '>
                Complete la información del pedido para obtener una predicción inteligente
            </p>
        </div>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.markdown("""
            <div style='margin-bottom: 2rem;'>
                <h4 style='
                    color: #2D5016; 
                    font-weight: 600; 
                    margin-bottom: 0.5rem;
                    font-family: "Poppins", sans-serif;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                '>
                    📍 Destino de Entrega
                </h4>
                <p style='color: #64748b; font-size: 0.9rem; margin-bottom: 1rem;'>
                    Código postal donde se realizará la entrega
                </p>
            </div>
            """, unsafe_allow_html=True)

            codigo_postal = st.text_input(
                "Código Postal",
                value="",
                help="Ingrese el código postal de 5 dígitos",
                placeholder="76000",
                label_visibility="collapsed"
            )
            st.markdown("""
            <div style='margin-bottom: 2rem; margin-top: 2rem;'>
                <h4 style='
                    color: #2D5016; 
                    font-weight: 600; 
                    margin-bottom: 0.5rem;
                    font-family: "Poppins", sans-serif;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                '>
                    🏷️ Información del Producto
                </h4>
                <p style='color: #64748b; font-size: 0.9rem; margin-bottom: 1rem;'>
                    SKU del producto a entregar
                </p>
            </div>
            """, unsafe_allow_html=True)

            sku_id = st.text_input(
                "SKU",
                value="",
                help="Identificador único del producto (ej: LIV-001)",
                placeholder="LIV-001",
                label_visibility="collapsed"
            )

        with col2:
            st.markdown("""
            <div style='margin-bottom: 2rem;'>
                <h4 style='
                    color: #2D5016; 
                    font-weight: 600; 
                    margin-bottom: 0.5rem;
                    font-family: "Poppins", sans-serif;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                '>
                    📦 Cantidad
                </h4>
                <p style='color: #64748b; font-size: 0.9rem; margin-bottom: 1rem;'>
                    Número de unidades a entregar
                </p>
            </div>
            """, unsafe_allow_html=True)

            cantidad = st.number_input(
                "Cantidad",
                min_value=1,
                max_value=100,
                value=1,
                help="Cantidad de productos (máximo 100)",
                label_visibility="collapsed"
            )
            st.markdown("""
            <div style='margin-bottom: 2rem; margin-top: 2rem;'>
                <h4 style='
                    color: #2D5016; 
                    font-weight: 600; 
                    margin-bottom: 0.5rem;
                    font-family: "Poppins", sans-serif;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                '>
                    📅 Fecha y Hora de Compra
                </h4>
                <p style='color: #64748b; font-size: 0.9rem; margin-bottom: 1rem;'>
                    Cuándo se realizó el pedido (puede simular cualquier fecha/hora)
                </p>
            </div>
            """, unsafe_allow_html=True)
            from datetime import datetime, timedelta

            col_fecha, col_hora = st.columns(2)
            with col_fecha:
                fecha_compra = st.date_input(
                    "Fecha",
                    value=datetime.now().date(),
                    min_value=datetime.now().date() - timedelta(days=365),  # Permite hasta 1 año atrás
                    max_value=datetime.now().date() + timedelta(days=365),  # Permite hasta 1 año adelante
                    help="Seleccione cualquier fecha para simular diferentes escenarios",
                    label_visibility="collapsed"
                )

            with col_hora:
                hora_compra = st.time_input(
                    "Hora",
                    value=datetime.now().time(),  # TODO -> RECORDATORIO Cambiar esta parte para que se cambie la hora
                    help="Seleccione cualquier hora del día",
                    label_visibility="collapsed"
                )
            if fecha_compra != datetime.now().date():
                st.markdown(f"""
                            <div style='
                                background: #e7f3ff; 
                                padding: 0.8rem; 
                                border-radius: 8px; 
                                border-left: 4px solid #0066cc;
                                margin: 1rem 0;
                                font-size: 0.9rem;
                            '>
                                ℹ️ <strong>Simulación:</strong> Fecha seleccionada es diferente a hoy ({datetime.now().strftime('%d/%m/%Y')}). 
                                Esto simula un pedido realizado en esa fecha.
                            </div>
                            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='margin-top: 3rem; text-align: center;'>", unsafe_allow_html=True)
        predict_clicked = st.button(
            "🔮 Generar Predicción Inteligente",
            type="primary",
            help="Analizar los datos y generar predicción de entrega optimizada",
            use_container_width=False
        )

        st.markdown("</div>", unsafe_allow_html=True)
        with st.expander("ℹ️ ¿Cómo funciona la predicción?", expanded=False):
            st.markdown("""
            <div style='padding: 1rem 0;'>
                <p style='margin-bottom: 1rem; color: #4a5568;'>
                    Nuestro sistema utiliza inteligencia artificial avanzada para:
                </p>
                <ul style='color: #4a5568; line-height: 1.8;'>
                    <li><strong>🏪 Optimizar tiendas:</strong> Selecciona las ubicaciones con mejor stock y distancia</li>
                    <li><strong>🚚 Evaluar rutas:</strong> Compara opciones directas vs multi-segmento</li>
                    <li><strong>🌡️ Considerar factores:</strong> Clima, tráfico, seguridad y demanda</li>
                    <li><strong>⚡ Decidir inteligentemente:</strong> Combina LightGBM y análisis Gemini</li>
                    <li><strong>📊 Predecir resultados:</strong> Tiempo, costo y probabilidad de éxito</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        if predict_clicked:
            if not validate_form_inputs(codigo_postal, sku_id):
                return

            process_prediction(codigo_postal, sku_id, cantidad, fecha_compra, hora_compra)
    st.markdown("</div>", unsafe_allow_html=True)


def validate_form_inputs(codigo_postal: str, sku_id: str) -> bool:
    """Validar entradas del formulario"""
    errors = []

    if not codigo_postal:
        errors.append("📍 El código postal es obligatorio")
    elif len(codigo_postal) < 5:
        errors.append("📍 El código postal debe tener al menos 5 dígitos")
    elif not codigo_postal.isdigit():
        errors.append("📍 El código postal debe contener solo números")

    if not sku_id:
        errors.append("🏷️ El SKU del producto es obligatorio")
    elif len(sku_id) < 3:
        errors.append("🏷️ El SKU debe tener al menos 3 caracteres")

    if errors:
        for error in errors:
            st.error(error)
        with st.expander("💡 Ejemplos válidos", expanded=True):
            st.markdown("""
            **Códigos postales válidos:**
            - `76000` (Querétaro)
            - `05050` (Ciudad de México)
            - `44100` (Guadalajara)

            **SKUs válidos:**
            - `LIV-001`
            - `LIV-004`
            - `PROD-123`
            """)
        return False

    return True


def process_prediction(codigo_postal: str, sku_id: str, cantidad: int, fecha_compra, hora_compra):
    """Procesar la predicción con mejor manejo de errores"""
    try:
        fecha_hora_compra = datetime.combine(fecha_compra, hora_compra)
        fecha_str = fecha_hora_compra.strftime("%Y-%m-%dT%H:%M:%S")

        with st.status("🔄 Procesando predicción...", expanded=True) as status:
            st.write("📋 Validando datos de entrada...")
            st.write("🏪 Buscando tiendas disponibles...")
            st.write("🚚 Evaluando rutas óptimas...")
            st.write("🧠 Ejecutando algoritmos de IA...")

            api_client = APIClient()
            result, error = api_client.predict_delivery(codigo_postal, sku_id, cantidad, fecha_str)

            if result:
                st.write("✅ Predicción completada exitosamente!")
                status.update(label="✅ Predicción generada", state="complete", expanded=False)
                st.session_state.prediction_data = result
                st.session_state.show_results = True
                with st.success("🎉 ¡Predicción generada exitosamente!"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("⏱️ Tiempo",
                                  f"{result.get('ruta_seleccionada', {}).get('tiempo_total_horas', 0):.1f}h")
                    with col2:
                        st.metric("💰 Costo", f"${result.get('costo_envio_mxn', 0):,.2f}")
                    with col3:
                        st.metric("📈 Probabilidad", f"{result.get('probabilidad_cumplimiento', 0) * 100:.1f}%")

                st.balloons()
                st.rerun()

            else:
                st.write("❌ Error en el procesamiento")
                status.update(label="❌ Error en predicción", state="error", expanded=False)
                st.error(f"🚫 {error}")
                show_error_suggestions(error)

    except Exception as e:
        st.error(f"❌ Error inesperado: {str(e)}")
        st.info("💡 Si el problema persiste, contacte al soporte técnico.")


def show_error_suggestions(error: str):
    """Mostrar sugerencias específicas basadas en el error"""
    with st.expander("🛠️ Soluciones sugeridas", expanded=True):
        if "conexión" in error.lower() or "connection" in error.lower():
            st.markdown("""
            **Error de conexión detectado:**
            - ✅ Verificar conexión a internet
            - ✅ Comprobar que el servidor esté activo en `http://0.0.0.0:8000`
            - ✅ Revisar configuración de firewall
            - ✅ Intentar nuevamente en unos segundos
            """)
        elif "timeout" in error.lower() or "tiempo" in error.lower():
            st.markdown("""
            **Tiempo de espera agotado:**
            - ✅ El servidor está procesando, intente con datos más simples
            - ✅ Verifique la estabilidad de la conexión
            - ✅ Reduzca la cantidad de productos si es muy alta
            """)
        elif "404" in error or "500" in error:
            st.markdown("""
            **Error del servidor:**
            - ✅ Verificar que el código postal sea válido
            - ✅ Confirmar que el SKU existe en el sistema
            - ✅ Contactar al administrador del sistema
            """)
        else:
            st.markdown("""
            **Soluciones generales:**
            - ✅ Verificar que todos los campos estén completos
            - ✅ Validar formato de código postal (solo números)
            - ✅ Confirmar que el SKU sea correcto
            - ✅ Revisar la conexión del servidor
            - ✅ Contactar soporte técnico si persiste
            """)