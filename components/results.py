from datetime import datetime

import pandas as pd
import streamlit as st
from streamlit_calendar import calendar

from components.recalculate import render_recalculate_forms
from components.split_prediction import render_split_forms
from utils.helpers import format_currency, format_datetime
from components.bigquery_table import render_bigquery_analysis, get_bigquery_results


def render_results_page():
    """Página de resultados minimalista y elegante"""
    data = st.session_state.prediction_data
    original_request = st.session_state.get('original_request', {})

    if 'show_recalculate_form' not in st.session_state:
        st.session_state.show_recalculate_form = False

    render_main_results(data, original_request)

    # Lógica para mostrar/ocultar los formularios de recálculo con un solo botón
    if st.session_state.show_recalculate_form:
        # Si el formulario está visible, el botón lo ocultará
        button_label = "❌ Ocultar opciones avanzadas"
        if st.button(button_label):
            st.session_state.show_recalculate_form = False
            st.rerun()
    else:
        # Si el formulario está oculto, el botón lo mostrará
        button_label = "🔄 Mostrar opciones avanzadas"
        if st.button(button_label):
            st.session_state.show_recalculate_form = True
            st.rerun()

    # Renderizar los tabs solo si la variable de estado es True
    if st.session_state.show_recalculate_form:
        tab1, tab2 = st.tabs(["❌ Recálculo", "📍Volver a calcular"])

        with tab1:
            # Asume que esta función ya está definida en otro lugar
            render_recalculate_forms(data, original_request)

        with tab2:
            # Asume que esta función ya está definida en otro lugar
            render_split_forms(data, original_request)

def render_main_results(data: dict, original_request: dict):
    """
    Desplegamos los resultados generales para el cálculo de una EDD
    """

    # Header de resultados
    render_results_header()

    # Botón de regreso
    render_back_button()

    # Cuadro principal de fecha promesa
    render_delivery_promise_card(data, original_request)

    # Layout de dos columnas: Calendario + Factores Externos con mejor alineación
    st.markdown("---")
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("""
            <div style="
                background: white; 
                padding: 1.5rem; 
                border-radius: 12px; 
                border: 1px solid #e5e7eb;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                height: 100%;
            ">
        """, unsafe_allow_html=True)
        render_delivery_calendar(data, original_request)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div style="
                background: white; 
                padding: 1.5rem; 
                border-radius: 12px; 
                border: 1px solid #e5e7eb;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                height: 100%;
            ">
        """, unsafe_allow_html=True)
        render_external_factors_table(data)
        st.markdown("</div>", unsafe_allow_html=True)

    # Análisis completo de datos vs algoritmo
    render_bigquery_analysis(data, original_request)

    # Detalles de las rutas split seleccionadas

    es_split = data.get("es_split")

    if es_split:
        render_split_elements(data=data)


def render_results_header():
    """Header de la página de resultados"""
    st.html("""
        <div class="main-header">
            <h1>📊 Resultados</h1>
            <p class="subtitle">Resultados del análisis de ruta y predicción de entrega</p>
        </div>
    """)


def render_back_button():
    """Botón de regreso elegante"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← Nuevo Análisis", type="secondary"):
            st.session_state.show_results = False
            st.rerun()


def render_delivery_promise_card(data: dict, original_request: dict):
    """Cuadro principal con la información de entrega unificada, incluyendo
    los resultados del recálculo si están disponibles."""
    st.html("""
        <div style="text-align: center; margin: 2rem 0;">
            <h2 style="color: #2563eb; font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">
                🎯 Fecha Promesa de Entrega
            </h2>
        </div>
    """)

    fecha_entrega = data.get('fecha_entrega', '')
    st.html(f"""
        <div style="
            text-align: center; 
            font-size: 2.5rem; 
            font-weight: 800; 
            color: #1e40af; 
            margin: 1rem 0 2rem 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            padding: 1rem;
            border-radius: 12px;
            border: 2px solid #2563eb;
        ">
            {format_datetime(fecha_entrega)}
        </div>
    """)
    # Request original
    fecha_compra = original_request.get('fecha_compra', '')
    codigo_postal = original_request.get('codigo_postal', '')
    temporada = original_request.get('temporada', '')

    # Resultados generales
    dias_entrega = calculate_days_to_delivery(fecha_compra, fecha_entrega)
    tipo_entrega = data.get('tipo_entrega', {})
    ventana_tiempo = tipo_entrega.get('ventana_tiempo', 'N/A')

    # Detalles lógisticos
    tiendas_display = get_stores_display(data)
    rutas_display = get_routes_display(data)
    score = f"{data.get('score', 0):.3f}"
    costo = data.get('costo', 0)

    # Detalles adicionales
    tiempo_proceso = data.get('tiempo_proceso_ms', 0)
    tipo_display = f"{tipo_entrega.get('icono', '')} {tipo_entrega.get('nombre', 'N/A')}"
    cantidad_solicitada = original_request.get('cantidad', 0)
    inventario_total = data.get('inventario_total_disponible', 0)

    split_info = ""
    if data.get('es_split', False):
        split_data = data.get('split_info', {})
        rutas_count = split_data.get('rutas_seleccionadas', 0)
        split_info = f"📦 SPLIT ({rutas_count} rutas)"

    # Caso recalculo
    recalculo_html = ""
    if data.get('es_recalculo', False):
        tienda_rechazada = data.get('tienda_rechazada', 'N/A')
        es_split_recalculo = data.get('es_split', False)
        if es_split_recalculo:
            tienda_rechazada = st.session_state.get('tienda_rechazada', tienda_rechazada)

        dias_diff = data.get('dias_diferencia', 'N/A')
        fecha_promesa_mantenida = data.get('fecha_promesa_mantenida', False)
        status_promesa = "✅ Mantenida" if fecha_promesa_mantenida else "❌ No mantenida"
        # costo_diff = data.get('costo_diferencia', 0)
        costo_original = st.session_state.get('costo_original', 0)

        # Nos aseguramos que los costos se esten obteniendo correctamente
        print("Costo original", costo_original)
        print("Costo nuevo", costo)

        costo_diff = costo_original - costo

        # Nueva lógica para obtener las rutas descartadas directamente de la consulta a BigQuery
        df_bigquery = get_bigquery_results(original_request)

        if not df_bigquery.empty and tienda_rechazada != 'N/A':
            rutas_descartadas_list = get_rejected_routes(df_bigquery, tienda_rechazada)
            rutas_descartadas_formated = get_rejected_routes_display(rutas_descartadas_list)

        # Manejo robusto de rutas descartadas para mostrar
        if rutas_descartadas_formated:
            rutas_text = ', '.join([str(ruta) for ruta in rutas_descartadas_formated])
        else:
            rutas_text = 'Ninguna'

        # Obtener tipo de impacto si está disponible
        tipo_impacto = data.get('tipo_impacto_aplicado', 'N/A')
        impacto_colors = {
            "BAJA": "🟢",
            "MEDIANA": "🟡",
            "ALTA": "🔴"
        }
        tipo_impacto_display = f"{impacto_colors.get(tipo_impacto, '⚪')} {tipo_impacto}"

        recalculo_html = f"""
            <div style="
                border-top: 1px solid #e5e7eb;
                padding-top: 2rem;
                margin-top: 2rem;
            ">
                <h4 style="text-align: center; color: #374151; font-weight: 600; margin-bottom: 1.5rem;">
                    🔄 Resultados del Recálculo
                </h4>
                <div style="display: flex; justify-content: space-around; text-align: center; gap: 1rem; margin-bottom: 1.5rem;">
                    <div style="flex: 1;">
                        <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">
                            📅 Fecha Original
                        </div>
                        <div style="color: #374151; font-size: 1rem; font-weight: 600;">
                            {format_datetime(data.get('fecha_entrega_original', 'N/A'))}
                        </div>
                    </div>
                    <div style="flex: 1;">
                        <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">
                            🎯 Fecha Recálculo
                        </div>
                        <div style="color: #374151; font-size: 1rem; font-weight: 600;">
                            {format_datetime(data.get('fecha_entrega', 'N/A'))}
                        </div>
                    </div>
                
                    <div style="flex: 1;">
                        <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-bottom: 0.5rem;">
                            ⌛ Fecha Promesa
                        </div>
                        <div style="color: #374151; font-size: 1rem; font-weight: 600;">
                        {status_promesa}
                    </div>
                </div>
                    <div style="flex: 1;">
                        <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">
                            📊 Diferencia
                        </div>
                        <div style="color: #374151; font-size: 1rem; font-weight: 600;">
                            {dias_diff} días
                        </div>
                    </div>
                </div>

                <div style="
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 1rem;
                    text-align: center;
                ">
                    <div style="
                        background-color: #f1f5f9;
                        border-radius: 8px;
                        padding: 1rem;
                    ">
                        <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-bottom: 0.5rem;">
                            💰 Diferencia de Costo
                        </div>
                        <div style="color: #374151; font-size: 1rem; font-weight: 600;">
                            {format_currency(costo_diff)}
                        </div>
                    </div>
                    <div style="
                        background-color: #f1f5f9;
                        border-radius: 8px;
                        padding: 1rem;
                    ">
                        <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-bottom: 0.5rem;">
                            ⚖️ Tipo de Impacto
                        </div>
                        <div style="color: #374151; font-size: 1rem; font-weight: 600;">
                            {tipo_impacto_display}
                        </div>
                    </div>
                    <div style="
                        background-color: #f1f5f9;
                        border-radius: 8px;
                        padding: 1rem;
                    ">
                        <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-bottom: 0.5rem;">
                            🏪 Tienda Rechazada
                        </div>
                        <div style="color: #374151; font-size: 1rem; font-weight: 600;">
                            {tienda_rechazada}
                        </div>
                    </div>
                    <div style="
                        background-color: #f1f5f9;
                        border-radius: 8px;
                        padding: 1rem;
                    ">
                        <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-bottom: 0.5rem;">
                            🛣️ Rutas Descartadas
                        </div>
                        <div style="color: #374151; font-size: 1rem; font-weight: 600; word-break: break-all;">
                            {rutas_text}
                        </div>
                    </div>
                </div>
            </div>
        """

    # --- Bloque html completo
    st.html(f"""
        <div style="
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border: 2px solid #e2e8f0;
            border-radius: 16px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        ">
        
            <h4 style="text-align: center; color: #374151; font-weight: 600; margin-bottom: 1.5rem;">
            🔎 INFORMACIÓN DE ENTREGA
            </h4>
            
            <div style="
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1.5rem;
                text-align: center;
                margin-bottom: 2rem;
            ">

                <div>
                    <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                        📅 FECHA DE COMPRA
                    </div>
                    <div style="color: #374151; font-size: 1rem; font-weight: 600;">
                        {format_datetime(fecha_compra)}
                    </div>
                </div>

                <div>
                    <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                        📍 CÓDIGO POSTAL DESTINO
                    </div>
                    <div style="color: #374151; font-size: 1rem; font-weight: 600;">
                        {codigo_postal}
                    </div>
                </div>

                <div>
                    <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                        ⏰ LLEGA EN
                    </div>
                    <div style="color: #059669; font-size: 1.25rem; font-weight: 700;">
                        {dias_entrega}
                    </div>
                </div>

                <div>
                    <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                        🚚 TIPO DE ENTREGA
                    </div>
                    <div style="color: #374151; font-size: 1rem; font-weight: 600;">
                        {tipo_display}
                    </div>
                </div>

                <div>
                    <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                        🕐 VENTANA HORARIA
                    </div>
                    <div style="color: #374151; font-size: 1rem; font-weight: 600;">
                        {ventana_tiempo}
                    </div>
                </div>
                
            </div>
            
            <h4 style="text-align: center; color: #374151; font-weight: 600; margin-bottom: 1.5rem;">
            🛣️ INFORMACIÓN LOGÍSTICA
            </h4>

            <div style="
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1.5rem;
                text-align: center;
                margin-bottom: 2rem;
            ">

                <div>
                    <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                        🏪 TIENDA(S) ASIGNADA(S)
                    </div>
                    <div style="color: #374151; font-size: 1rem; font-weight: 600;">
                        {tiendas_display}
                    </div>
                </div>

                <div>
                    <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                        🗺️ RUTA(S) SELECCIONADA(S)
                    </div>
                    <div style="color: #374151; font-size: 1rem; font-weight: 600; word-break: break-all;">
                        {rutas_display}
                    </div>
                </div>

                <div>
                    <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                        💰 COSTO TOTAL
                    </div>
                    <div style="color: #374151; font-size: 1rem; font-weight: 600;">
                        {format_currency(costo)}
                    </div>
                </div>

                <div>
                    <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                        ⚡ TIEMPO DE PROCESAMIENTO
                    </div>
                    <div style="color: #374151; font-size: 1rem; font-weight: 600;">
                        {tiempo_proceso:.2f} ms
                    </div>
                </div>
                <div>
                    <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                        📊 CANTIDAD SOLICITADA
                    </div>
                    <div style="color: #374151; font-size: 1rem; font-weight: 600;">
                        {cantidad_solicitada}
                    </div>
                </div>
                
                <div>
                    <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                        🏬 INVENTARIO TOTAL
                    </div>
                    <div style="color: #374151; font-size: 1rem; font-weight: 600;">
                        {inventario_total}
                    </div>
                </div>

                <div>
                    <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                        🚚 TEMPORADA
                    </div>
                    <div style="color: #374151; font-size: 1rem; font-weight: 600;">
                        {temporada}
                    </div>
                </div>
                

                {f'<div><div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">📦 TIPO</div><div style="color: #f59e0b; font-size: 1rem; font-weight: 600;">{split_info}</div></div>' if split_info else ''}
            </div>

            {recalculo_html}
        </div>
    """)

def render_error_card(data_error: dict):
    detail_error = data_error.get('detail', {})
    if not detail_error:
        st.error("❌ No se encontraron detalles del error.")
        return

    error_type = detail_error.get('error', 'N/A')
    message = detail_error.get('message', 'N/A')
    cantidad_solicitada = detail_error.get('cantidad_solicitada', 0)
    inventario_disponible = detail_error.get('inventario_total_disponible', 0)
    tiendas_con_inventario = detail_error.get('tiendas_con_inventario', 0)
    sugerencia = detail_error.get('sugerencia', 'N/A')

    # Formateamos el error
    error_type = error_type.replace("_", " ")

    st.html(f"""
    <div style="background-color: #ffebee; border: 1px solid #ef9a9a; border-radius: 8px; padding: 20px; margin-top: 20px;">
        <h3 style="color: #c62828; margin-top: 0;">¡Error! 🚫</h3>
        <p style="font-weight: bold;">Error detectado: {error_type}</p>
        <p>{message}</p>
        <hr style="border-top: 1px dashed #ef9a9a;">
        <p><strong>Cantidad solicitada:</strong> <span style="font-weight: bold; color: #c62828;">{cantidad_solicitada}</span></p>
        <p><strong>Inventario disponible:</strong> <span style="font-weight: bold; color: #4caf50;">{inventario_disponible}</span></p>
        <p><strong>Tiendas con inventario:</strong> {tiendas_con_inventario}</p>
        <hr style="border-top: 1px dashed #ef9a9a;">
        <p style="font-style: italic;"><strong>Sugerencia:</strong> {sugerencia}</p>
    </div>
    """)

def render_delivery_calendar(data: dict, original_request: dict):
    """Calendario de fechas importantes con mejor diseño"""
    st.markdown("#### 📅 Calendario de Entregas")

    events = []

    # Fecha de compra
    fecha_compra_str = original_request.get('fecha_compra', '')
    if fecha_compra_str:
        try:
            fecha_compra_date = datetime.fromisoformat(fecha_compra_str.replace('Z', '+00:00')).date()
            events.append({
                "title": "Compra",
                "start": fecha_compra_date.isoformat(),
                "color": "#3b82f6",
                "borderColor": "#1d4ed8",
                "textColor": "#ffffff"
            })
        except ValueError:
            pass

    # Fecha de entrega
    fecha_entrega_str = data.get('fecha_entrega', '')
    if fecha_entrega_str:
        try:
            fecha_entrega_date = datetime.fromisoformat(fecha_entrega_str.replace('Z', '+00:00')).date()
            events.append({
                "title": "Entrega",
                "start": fecha_entrega_date.isoformat(),
                "color": "#10b981",
                "borderColor": "#059669",
                "textColor": "#ffffff"
            })
        except ValueError:
            pass

    # Fecha de recálculo si existe
    if data.get('es_recalculo', False):
        fecha_original_str = data.get('fecha_entrega_original', '')
        if fecha_original_str:
            try:
                fecha_original_date = datetime.fromisoformat(fecha_original_str.replace('Z', '+00:00')).date()
                events.append({
                    "title": "Entrega Original",
                    "start": fecha_original_date.isoformat(),
                    "color": "#ef4444",
                    "borderColor": "#dc2626",
                    "textColor": "#ffffff"
                })
            except ValueError:
                pass

    # Mostrar leyenda de colores
    if events:
        st.html("""
            <div style="margin-bottom: 1rem; font-size: 0.875rem; display: flex; gap: 1rem; flex-wrap: wrap;">
                <span style="display: flex; align-items: center; gap: 0.25rem;">
                    <div style="width: 12px; height: 12px; background: #3b82f6; border-radius: 50%;"></div>
                    Compra
                </span>
                <span style="display: flex; align-items: center; gap: 0.25rem;">
                    <div style="width: 12px; height: 12px; background: #10b981; border-radius: 50%;"></div>
                    Entrega
                </span>
            </div>
        """)

    calendar_options = {
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth"
        },
        "initialView": "dayGridMonth",
        "height": 450,
        "locale": "es",
        "eventDisplay": "block",
        "dayMaxEvents": 3
    }

    calendar(events=events, options=calendar_options, key="delivery_calendar")

def render_external_factors_table(data: dict):
    """Tabla de factores externos y contexto con mejor diseño"""
    st.markdown("#### 🌍 Factores Externos y Contexto")

    # Crear tabs para organizar la información
    tab1, tab2, tab3 = st.tabs(["🌤️ Climático", "📍 Geográfico", "⚠️ Eventos"])

    with tab1:
        clima = data.get('contexto_climatico', {})
        if clima:
            clima_df = pd.DataFrame([
                {"Factor": "🏔️ Región", "Valor": clima.get('region_nombre', 'N/A')},
                {"Factor": "🗺️ Estado", "Valor": clima.get('estado_principal', 'N/A')},
                {"Factor": "🌡️ Clima Actual", "Valor": clima.get('clima_actual', 'N/A')},
                {"Factor": "❄️ Temp. Mín", "Valor": f"{clima.get('temperatura_min', 'N/A')}°C"},
                {"Factor": "🔥 Temp. Máx", "Valor": f"{clima.get('temperatura_max', 'N/A')}°C"},
                {"Factor": "🌧️ Precipitación", "Valor": f"{clima.get('precipitacion_anual', 'N/A')} mm"},
                {"Factor": "📏 Altitud", "Valor": f"{clima.get('altitud_msnm', 'N/A')} msnm"}
            ])
            st.dataframe(
                clima_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Factor": st.column_config.TextColumn("Factor", width="medium"),
                    "Valor": st.column_config.TextColumn("Valor", width="medium")
                }
            )
        else:
            st.info("No hay información climática disponible")

    with tab2:
        geo = data.get('contexto_geografico', {})
        if geo:
            geo_df = pd.DataFrame([
                {"Factor": "📮 Rango CP", "Valor": geo.get('rango_cp', 'N/A')},
                {"Factor": "🏛️ Estado/Alcaldía", "Valor": geo.get('estado_alcaldia', 'N/A')},
                {"Factor": "🛡️ Zona Seguridad", "Valor": geo.get('zona_seguridad', 'N/A')},
                {"Factor": "🏙️ Tipo Zona", "Valor": geo.get('tipo_zona', 'N/A')},
                {"Factor": "🏪 Cobertura Liverpool", "Valor": "✅ Sí" if geo.get('cobertura_liverpool') else "❌ No"},
                {"Factor": "⏱️ Tiempo Base", "Valor": f"{geo.get('tiempo_entrega_base_horas', 'N/A')} hrs"}
            ])
            st.dataframe(
                geo_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Factor": st.column_config.TextColumn("Factor", width="medium"),
                    "Valor": st.column_config.TextColumn("Valor", width="medium")
                }
            )
        else:
            st.info("No hay información geográfica disponible")

    with tab3:
        factores = data.get('factores_externos', [])
        if factores:
            eventos_data = []
            for factor in factores:
                eventos_data.append({
                    "🎯 Evento": factor.get('evento_detectado', 'N/A'),
                    "📈 Demanda": f"{factor.get('factor_demanda', 'N/A')}x",
                    "🌤️ Clima": factor.get('condicion_clima', 'N/A'),
                    "🚗 Tráfico": factor.get('trafico_nivel', 'N/A'),
                    "⏳ +Tiempo": f"{factor.get('impacto_tiempo_extra_horas', 'N/A')}h",
                    "🔴 Criticidad": factor.get('criticidad_logistica', 'N/A')
                })

            eventos_df = pd.DataFrame(eventos_data)
            st.dataframe(
                eventos_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "🎯 Evento": st.column_config.TextColumn("Evento", width="medium"),
                    "📈 Demanda": st.column_config.TextColumn("Demanda", width="small"),
                    "🌤️ Clima": st.column_config.TextColumn("Clima", width="medium"),
                    "🚗 Tráfico": st.column_config.TextColumn("Tráfico", width="small"),
                    "⏳ +Tiempo": st.column_config.TextColumn("Tiempo", width="small"),
                    "🔴 Criticidad": st.column_config.TextColumn("Criticidad", width="medium")
                }
            )
        else:
            st.info("No se detectaron factores externos especiales")

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
                        <li style='margin-bottom: 0.3rem;'><strong>Tiendas Seleccionadas:</strong> {len(tiendas_seleccionadas)}</li>
                        <li style='margin-bottom: 0.3rem;'><strong>Cantidad Solicitada:</strong> {split_info.get('cantidad_total', 'N/A')}</li>
                        <li style='margin-bottom: 0.3rem;'><strong>Costo Total:</strong> {format_currency(split_info.get('costo_total', 0))}</li>
                        <li style='margin-bottom: 0.3rem;'><strong>Tiempo Total:</strong> {split_info.get('tiempo_total', 'N/A')} días</li>
                    </ul>
                </div>
                """

            detalle_rutas = split_info.get('detalle_rutas', [])
            if detalle_rutas:
                #split_html_content += "<h4 style='color: #4A4A4A; margin-top: 2rem;'>🔄 DETALLES RUTAS SPLIT</h4>"

                table_header = """
                    <table style="width: 100%; border-collapse: collapse; margin: 10px 0; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
                        <thead style="background-color: #E3F2FD;">
                            <tr>
                                <th style="padding: 12px; border: 1px solid #BBDEFB; text-align: center; color: #3F51B5;">Ruta</th>
                                <th style="padding: 12px; border: 1px solid #BBDEFB; text-align: center; color: #3F51B5;">ID Trazo</th>
                                <th style="padding: 12px; border: 1px solid #BBDEFB; text-align: center; color: #3F51B5;">Tienda</th>
                                <th style="padding: 12px; border: 1px solid #BBDEFB; text-align: center; color: #3F51B5;">Inventario</th>
                                <th style="padding: 12px; border: 1px solid #BBDEFB; text-align: center; color: #3F51B5;">Seleccionados</th>
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


            st.markdown("### 🔀 Detalle rutas - Caso split")
            st.html(split_html_content)

# Funciones auxiliares
def calculate_days_to_delivery(fecha_compra_str: str, fecha_entrega_str: str) -> str:
    """Calcular días hasta entrega"""
    if not fecha_compra_str or not fecha_entrega_str:
        return "N/A"

    try:
        fecha_compra = datetime.fromisoformat(fecha_compra_str.replace('Z', '+00:00'))
        fecha_entrega = datetime.fromisoformat(fecha_entrega_str.replace('Z', '+00:00'))
        diferencia = (fecha_entrega.date() - fecha_compra.date()).days

        if diferencia == 0:
            return "HOY"
        elif diferencia == 1:
            return "MAÑANA"
        elif diferencia > 0:
            return f"EN {diferencia} DÍAS"
        else:
            return f"HACE {abs(diferencia)} DÍAS"
    except:
        return "N/A"

def get_rejected_routes(df_bigquery: pd.DataFrame, rejected_store_id: str) -> list:
    """
    Obtiene todas las rutas asociadas a una tienda rechazada del DataFrame de BigQuery.

    Args:
        df_bigquery (pd.DataFrame): El DataFrame completo con los resultados de BigQuery.
        rejected_store_id (str): El ID de la tienda que fue rechazada.

    Returns:
        list: Una lista de IDs de rutas asociadas a la tienda rechazada.
    """

    if 'TDA_CVE' in df_bigquery.columns and 'ID_TRAZO' in df_bigquery.columns:
        # Filtra el DataFrame para obtener solo las filas de la tienda rechazada
        rejected_routes_df = df_bigquery[df_bigquery['TDA_CVE'] == rejected_store_id]

        # Extrae los IDs de las rutas y elimina duplicados
        rejected_routes = rejected_routes_df['ID_TRAZO'].unique().tolist()

        return rejected_routes

    else:
        st.warning("⚠️ El DataFrame no contiene las columnas necesarias ('ID_TIENDA' o 'ID_TRAZO').")
        return []

def get_stores_display(data: dict) -> str:
    """Obtener display de tiendas (manejar splits)"""
    if data.get('es_split', False):
        split_info = data.get('split_info', {})
        detalle_rutas = split_info.get('detalle_rutas', [])
        tiendas = [str(ruta.get('tienda', '')) for ruta in detalle_rutas]
        return ', '.join(tiendas) if tiendas else 'N/A'
    else:
        return str(data.get('tienda', 'N/A'))


def get_routes_display(data: dict) -> str:
    """Obtener display de rutas (manejar splits)"""
    if data.get('es_split', False):
        split_info = data.get('split_info', {})
        return f"{split_info.get('rutas_seleccionadas', 'N/A')} rutas"
    else:
        trazo_id = data.get('id_trazo', 'N/A')
        # Mostrar solo los primeros 8 caracteres del ID para mejor legibilidad
        return trazo_id[:8] + "..." if len(trazo_id) > 8 else trazo_id

def get_rejected_routes_display(routes: list):
    """
    Formatear cada elemento de la lista de rutas rechazadas.
    """
    formated_routes = []

    for route in routes:

        formated_routes.append(route[:8] + "..." if len(route) > 8 else route)

    return formated_routes

