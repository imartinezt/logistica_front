import streamlit as st
from datetime import datetime, timedelta, time
from config.settings import Config
from services.api_client import APIClient
from components.layout import render_header

from typing import List


def render_section_header(icon: str, title: str, subtitle: str):
    """Renderiza un encabezado de sección con ícono, título y subtítulo."""
    st.markdown(f"""
    <div style='margin-bottom: 1rem;'>
        <h4 style='
            color: #1e293b;
            font-weight: 600;
            margin-bottom: 0.25rem;
            font-family: "Inter", system-ui, sans-serif;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 1rem;
            letter-spacing: -0.025em;
        '>
            <span style='color: #3b82f6;'>{icon}</span> {title}
        </h4>
        <p style='
            color: #64748b;
            font-size: 0.875rem;
            margin: 0;
            line-height: 1.5;
        '>
            {subtitle}
        </p>
    </div>
    """, unsafe_allow_html=True)

# Cambiar por variables de sesion
def render_datetime_section():
    """Renderiza la sección de entrada de fecha y hora del pedido."""
    fecha_compra = st.date_input(
        "Fecha del Pedido",
        value = st.session_state.fecha_compra,
        min_value=datetime.now().date() - timedelta(days=365),
        max_value=datetime.now().date() + timedelta(days=365),
        help="Fecha en que se realizó el pedido para el análisis.",
        key="fecha_input"
    )

    if 'hora_compra' not in st.session_state:
        st.session_state.hora_compra = datetime.now().time()

    tiempo_options = []
    for h in range(24):
        for m in range(0, 60, 15):
            tiempo_options.append(f"{h:02d}:{m:02d}")

    hora_actual = datetime.now().hour
    min_actual = (datetime.now().minute // 15) * 15
    tiempo_actual = f"{hora_actual:02d}:{min_actual:02d}"

    try:
        indice_actual = tiempo_options.index(tiempo_actual)
    except ValueError:
        indice_actual = 0 # Si la hora actual no está en las opciones exactas, selecciona la primera

    tiempo_seleccionado = st.selectbox(
        "Hora del Pedido",
        tiempo_options,
        index=indice_actual,
        help="Seleccione la hora exacta en que se realizó el pedido.",
        key="tiempo_sel"
    )
    hora_parts = tiempo_seleccionado.split(":")
    st.session_state.hora_compra = time(int(hora_parts[0]), int(hora_parts[1]))
    st.session_state.fecha_compra = fecha_compra

    if fecha_compra != datetime.now().date():
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #dbeafe 0%, #e0f2fe 100%);
            padding: 0.75rem 1rem;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
            margin: 1rem 0;
            font-size: 0.875rem;
        '>
            <strong style='color: #1e40af;'>💼 Modo Simulación:</strong>
            <span style='color: #374151;'>Análisis basado en {fecha_compra.strftime('%d/%m/%Y')} a las {st.session_state.hora_compra.strftime('%H:%M')}</span>
        </div>
        """, unsafe_allow_html=True)


def render_methodology_panel():
    """Renderiza el panel de metodología del análisis."""
    st.markdown("""
    <div style='padding: 1.5rem 0;'>
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem;'>
            <div style='
                background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                padding: 1.5rem;
                border-radius: 12px;
                border-left: 4px solid #0ea5e9;
            '>
                <h5 style='color: #0c4a6e; margin: 0 0 0.5rem 0; font-weight: 600;'>🎯 Optimización Inteligente</h5>
                <p style='color: #475569; margin: 0; font-size: 0.875rem; line-height: 1.5;'>
                    Algoritmos de Machine Learning evalúan múltiples rutas considerando inventario, distancias y restricciones operativas.
                </p>
            </div>
            <div style='
                background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
                padding: 1.5rem;
                border-radius: 12px;
                border-left: 4px solid #22c55e;
            '>
                <h5 style='color: #14532d; margin: 0 0 0.5rem 0; font-weight: 600;'>📊 Análisis Predictivo</h5>
                <p style='color: #475569; margin: 0; font-size: 0.875rem; line-height: 1.5;'>
                    LightGBM y análisis Gemini procesan factores externos: clima, tráfico, demanda y seguridad zonal.
                </p>
            </div>
            <div style='
                background: linear-gradient(135deg, #fef7ff 0%, #f3e8ff 100%);
                padding: 1.5rem;
                border-radius: 12px;
                border-left: 4px solid #a855f7;
            '>
                <h5 style='color: #581c87; margin: 0 0 0.5rem 0; font-weight: 600;'>⚡ Decisión en Tiempo Real</h5>
                <p style='color: #475569; margin: 0; font-size: 0.875rem; line-height: 1.5;'>
                    Evaluación instantánea de probabilidades de éxito, costos y tiempos de entrega optimizados.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def validate_form_inputs(codigo_postal: str, sku_id: str) -> bool:
    """Valida las entradas principales del formulario."""
    errors = []

    if not codigo_postal:
        errors.append("📍 Código postal requerido.")
    elif len(codigo_postal) < 5:
        errors.append("📍 Código postal incompleto (mínimo 5 dígitos).")
    elif not codigo_postal.isdigit():
        errors.append("📍 Código postal debe ser numérico.")

    if not sku_id:
        errors.append("📦 SKU del producto requerido.")
    elif len(sku_id) < 3:
        errors.append("📦 SKU incompleto (mínimo 3 caracteres).")

    if errors:
        for error in errors:
            st.error(error)
        render_examples_panel()
        return False

    return True


def render_examples_panel():
    """Renderiza un panel con ejemplos de entradas válidas."""
    with st.expander("💼 Ejemplos de Referencia", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **🗺️ Códigos Postales Válidos:**
            ```
            76000  → Querétaro Centro
            05050  → Ciudad de México
            44100  → Guadalajara Centro
            64000  → Monterrey Centro
            ```
            """)
        with col2:
            st.markdown("""
            **📦 SKUs de Ejemplo:**
            ```
            LIV-001  → Producto Liverpool
            LIV-004  → Artículo Especial
            PROD-123 → SKU Genérico
            ```
            """)


def process_prediction(codigo_postal: str, sku_id: str, cantidad: int,
                       fecha_entrega_promesa: datetime.date, tienda_rechazada: int,
                       temporada: str, rutas_rechazadas: List[str], priorizar_fecha_promesa: bool):
    """
    Procesa la predicción de entrega, interactúa con la API
    y muestra el feedback al usuario.
    """
    try:
        # Combina fecha y hora de compra para enviarlo a la API
        fecha_hora_compra = datetime.combine(
            st.session_state.fecha_compra,
            st.session_state.hora_compra
        )
        fecha_str = fecha_hora_compra.strftime("%Y-%m-%dT%H:%M:%S")

        # Combina la fecha de promesa con una hora por defecto (medianoche)
        # Si necesitas una hora específica para la promesa, podrías añadir otro st.time_input
        fecha_entrega_promesa_dt = datetime.combine(fecha_entrega_promesa, time(0, 0, 0))
        fecha_entrega_promesa_str = fecha_entrega_promesa_dt.strftime("%Y-%m-%dT%H:%M:%S")


        with st.status("🔄 Ejecutando Análisis Inteligente...", expanded=True) as status:
            st.write("🔍 Validando parámetros de entrada...")
            st.write("🏪 Identificando ubicaciones con inventario...")
            st.write("🛣️ Calculando rutas óptimas...")
            st.write("🤖 Procesando con algoritmos de IA...")
            st.write("📊 Generando insights predictivos...")

            api_client = APIClient() # Instancia tu cliente API real aquí
            result, error = api_client.recalculate_delivery(
                codigo_postal,
                sku_id,
                cantidad,
                fecha_str,
                fecha_entrega_promesa_str,
                tienda_rechazada,
                temporada,
                rutas_rechazadas,
                priorizar_fecha_promesa
            )

            if result:
                st.write("✅ Análisis completado exitosamente")
                status.update(label="✅ Análisis Completado", state="complete", expanded=False)

                st.session_state.prediction_data_recalculate = result
                st.session_state.show_results_recalculate = True

                # Guarda las variables para posible recálculo o visualización posterior
                st.session_state.codigo_postal = codigo_postal
                st.session_state.sku_id = sku_id
                st.session_state.cantidad = cantidad
                st.session_state.fecha_entrega_promesa = fecha_entrega_promesa
                st.session_state.tienda_rechazada = tienda_rechazada
                st.session_state.temporada = temporada
                st.session_state.rutas_rechazadas = rutas_rechazadas
                st.session_state.priorizar_fecha_promesa = priorizar_fecha_promesa


                render_success_summary(result)
                st.balloons()
                # st.rerun() # Descomentar si quieres que la página se recargue completamente al mostrar resultados
            else:
                st.write("❌ Error en el procesamiento")
                status.update(label="❌ Error en Análisis", state="error", expanded=False)
                st.error(f"🚫 {error}")
                render_error_guidance(error)

    except Exception as e:
        st.error(f"❌ Error crítico del sistema: {str(e)}")
        st.info("💼 Contacte al equipo de soporte técnico para asistencia inmediata.")


def render_success_summary(result: dict):
    """Renderiza un resumen ejecutivo de los resultados exitosos."""
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #10b981;
        margin: 1.5rem 0;
    '>
    """, unsafe_allow_html=True)

    st.markdown("""
    <h3 style='color: #065f46; margin: 0 0 1rem 0; font-weight: 600;'>
        ✅ Análisis Completado Exitosamente
    </h3>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        tiempo = result.get('ruta_seleccionada', {}).get('tiempo_total_horas', 0)
        st.metric("⏱️ Tiempo Estimado", f"{tiempo:.1f} horas")
    with col2:
        costo = result.get('costo_envio_mxn', 0)
        st.metric("💰 Costo Total", f"${costo:,.2f}")
    with col3:
        prob = result.get('probabilidad_cumplimiento', 0)
        st.metric("📈 Probabilidad Éxito", f"{prob * 100:.1f}%")

    st.markdown("</div>", unsafe_allow_html=True)


def render_error_guidance(error: str):
    """Renderiza una guía de resolución de errores basada en el mensaje de error."""
    with st.expander("🛠️ Guía de Resolución", expanded=True):
        if "conexión" in error.lower() or "connection" in error.lower():
            st.error("**🔌 Error de Conectividad**")
            st.info("Verificar conexión de red y disponibilidad del sistema backend.")
        elif "timeout" in error.lower():
            st.error("**⏰ Tiempo de Respuesta Excedido**")
            st.info("El sistema está procesando. Reintentar con parámetros simplificados.")
        elif "404" in error or "500" in error:
            st.error("**🏥 Error del Sistema**")
            st.info("Contactar al equipo de TI para verificación del servicio.")
        else:
            st.error("**❓ Error No Identificado**")
            st.info("Revisar parámetros de entrada y contactar soporte técnico si persiste.")


def render_prediction_form():
    """
    Renderiza el formulario completo de predicción de entrega con todos
    los campos de entrada requeridos y adicionales.
    """

    data = st.session_state.prediction_data

    st.markdown("""
    <div style='max-width: 900px; margin: 0 auto; padding: 0 1rem;'>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("""
        <div style='
            background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
            padding: 3rem;
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border: 1px solid #e2e8f0;
            margin: 2rem 0;
        '>
        """, unsafe_allow_html=True)

        # Header ejecutivo del formulario
        st.markdown("""
        <div style='text-align: center; margin-bottom: 3rem;'>
            <h1 style='
                color: #1e293b;
                font-size: 2.25rem;
                font-weight: 700;
                font-family: "Inter", system-ui, sans-serif;
                margin-bottom: 0.75rem;
                letter-spacing: -0.025em;
            '>
                 📈 Recálculo de Fecha Promesa de Entrega
            </h1>
            <p style='
                color: #64748b;
                font-size: 1.125rem;
                margin: 0;
                font-weight: 400;
                line-height: 1.6;
            '>
                Evaluación de escenarios con IA avanzada
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Sección de campos principales (Código Postal, SKU, Cantidad, Fecha/Hora)
        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            render_section_header("📍", "Destino", "Ubicación de entrega final")
            codigo_postal = st.text_input(
                "Código Postal",
                value=st.session_state.codigo_postal, # Código postal de prueba (5 unidades caso split)
                help="Código postal de 5 dígitos del destino.",
                placeholder=st.session_state.codigo_postal,
                label_visibility="collapsed",
                key="cp_input"
            )

            render_section_header("📦", "Producto", "Información del SKU")
            sku_id = st.text_input(
                "SKU",
                value=st.session_state.sku_id, # SKU de prueba (30 unidades caso split)
                help="Identificador único del producto.",
                placeholder=st.session_state.sku_id,
                label_visibility="collapsed",
                key="sku_input"
            )

        with col2:
            render_section_header("📊", "Cantidad", "Unidades requeridas")
            cantidad = st.number_input(
                "Cantidad",
                min_value=1,
                max_value=100,
                value=data.get('cantidad_total', ''),
                help="Número de unidades a entregar.",
                label_visibility="collapsed",
                key="qty_input"
            )

            render_section_header("⏰", "Temporización", "Fecha y hora del pedido")
            render_datetime_section()

        # Separador visual para la nueva sección
        st.markdown("<hr style='margin: 3rem 0; border-top: 1px dashed #e2e8f0;'>", unsafe_allow_html=True)

        # Sección de Parámetros Adicionales
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h2 style='
                color: #1e293b;
                font-size: 1.75rem;
                font-weight: 700;
                font-family: "Inter", system-ui, sans-serif;
                margin-bottom: 0.5rem;
                letter-spacing: -0.025em;
            '>
                ⚙️ Parámetros Adicionales
            </h2>
            <p style='
                color: #64748b;
                font-size: 1rem;
                margin: 0;
                font-weight: 400;
                line-height: 1.5;
            '>
                Ajusta opciones avanzadas para un análisis más preciso.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col3, col4 = st.columns([1, 1], gap="large")

        with col3:
            render_section_header("🗓️", "Fecha Promesa", "Fecha de entrega prometida al cliente")
            fecha_entrega_promesa = st.date_input(
                "Fecha de Entrega Promesa",
                value=data.get('fecha_entrega', ''), # Por defecto, 7 días a partir de hoy
                min_value=datetime.now().date(), # No se puede prometer una fecha en el pasado
                help="Fecha en la que se prometió la entrega al cliente.",
                key="fecha_entrega_promesa_input"
            )

            render_section_header("🚫", "Tienda Rechazada", "ID de tienda a excluir del análisis")
            tienda_rechazada = st.number_input(
                "Tienda Rechazada",
                min_value=0, # Asumiendo 0 significa que no hay tienda rechazada
                value=data.get('tienda', ''),
                help="ID numérico de la tienda que debe ser excluida de las opciones de envío. Ingrese 0 si no aplica.",
                key="tienda_rechazada_input"
            )

        with col4:
            render_section_header("🍂", "Temporada", "Temporada actual del año")
            temporada = st.selectbox(
                data.get('temporada', ''),
                options=["TEMPORADA_BAJA", "TEMPORADA_MEDIA", "TEMPORADA_ALTA"],
                index=0, # Por defecto a TEMPORADA_BAJA
                help="Seleccione la temporada actual para influir en la predicción de la demanda y capacidad.",
                key="temporada_input"
            )

            render_section_header("❌", "Rutas Rechazadas", "IDs de rutas a excluir (separar por comas)")
            rutas_rechazadas_str = st.text_input(
                "Rutas Rechazadas (ej: R11677, R11678)",
                value=data.get('id_trazo', ''),
                help="Introduzca los IDs de las rutas que deben ser excluidas del análisis, separados por comas. Opcional.",
                placeholder="R11677, R11678",
                key="rutas_rechazadas_input"
            )
            # Convierte la cadena separada por comas en una lista de strings
            rutas_rechazadas = [r.strip() for r in rutas_rechazadas_str.split(',') if r.strip()]

            render_section_header("⭐", "Priorizar Promesa", "¿Priorizar fecha de entrega prometida?")
            priorizar_fecha_promesa = st.checkbox(
                "Priorizar la fecha de entrega prometida sobre otros factores de optimización",
                value=False,
                help="Marque esta casilla para dar prioridad a la fecha de entrega prometida en el cálculo de la ruta óptima.",
                key="priorizar_fecha_promesa_checkbox"
            )


        st.markdown("</div>", unsafe_allow_html=True) # Cierra el div del formulario con estilo
        st.markdown("<div style='text-align: center; margin-top: 2.5rem;'>", unsafe_allow_html=True)
        predict_clicked = st.button(
            "🎯 Ejecutar Análisis Predictivo",
            type="primary",
            help="Iniciar el análisis de inteligencia logística con los parámetros especificados.",
            use_container_width=False,
            key="predict_btn"
        )
        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("💡 Metodología del Análisis", expanded=False):
            render_methodology_panel()

        if predict_clicked:
            # Realiza la validación de los campos principales
            if not validate_form_inputs(codigo_postal, sku_id):
                return

            # Procesa la predicción con todos los parámetros
            process_prediction(
                codigo_postal,
                sku_id,
                cantidad,
                fecha_entrega_promesa,
                tienda_rechazada,
                temporada,
                rutas_rechazadas,
                priorizar_fecha_promesa
            )

    st.markdown("</div>", unsafe_allow_html=True) # Cierra el div principal de max-width