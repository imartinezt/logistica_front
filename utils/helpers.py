from datetime import datetime
import pandas as pd
import streamlit as st
from jinja2 import Template


def init_session_state():
    """Inicializar el estado de la sesión"""
    if 'prediction_data' not in st.session_state:
        st.session_state.prediction_data = None
    elif 'prediction_data_recalculate' not in st.session_state:
        st.session_state.prediction_data_recalculate = None
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False
    if 'show_results_recalculate' not in st.session_state:
        st.session_state.show_results_recalculate = False
    if 'hora_compra' not in st.session_state:
        st.session_state.hora_compra = datetime.now().time()
    if 'fecha_compra' not in st.session_state:
        st.session_state.fecha_compra = datetime.now().date()
    if 'tienda_rechazada' not in st.session_state:
        st.session_state.tienda_rechazada = None

def format_currency(amount: float) -> str:
    """Formatear cantidad como moneda mexicana"""
    return f"${amount:,.2f}"

def format_percentage(value: float) -> str:
    """Formatear como porcentaje"""
    return f"{value * 100:.1f}%"

def format_datetime(datetime_str: str) -> str:
    """Formatear datetime string"""
    try:
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        return dt.strftime('%d/%m/%Y')
    except:
        return "N/A"

def format_datetime_with_time(datetime_str: str) -> str:
    """Formatear datetime string con hora"""
    try:
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        return dt.strftime('%d/%m/%Y a las %H:%M')
    except:
        return "N/A"

## Modificación
def get_delivery_status_badge(delivery_type: str) -> str:
    """
    Obtener badge de tipo de entrega
    """
    delivery_type_upper = delivery_type.upper()
    badge_info = {
        "color": "#64748b", # Default gray
        "icon": "📋",
        "label": delivery_type
    }

    if "FLOTA LIVERPOOL" in delivery_type_upper:
        badge_info = {
            "color": "#FFC0CB",
            "icon": "🏠",
            "label": "FLOTA LIVERPOOL"
        }
    elif "MENSAJERIA EXTERNA" in delivery_type_upper:
        badge_info = {
            "color": "#ADD8E6",
            "icon": "🚚",
            "label": "MENSAJERIA EXTERNA"
        }
    elif "EDT" in delivery_type_upper or "PROGRAMADA" in delivery_type_upper:
        badge_info = {
            "color": "#90EE90",
            "icon": "🗓️",
            "label": delivery_type
        }

    return f'''
    <span style="
        background: {badge_info["color"]};
        color: black; /* Changed to black for better contrast on light backgrounds */
        padding: 0.375rem 0.875rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        font-family: Inter, system-ui, sans-serif;
        letter-spacing: 0.025em;
    ">
        {badge_info["icon"]} {badge_info["label"]}
    </span>
    '''

def render_prediction_results(data: dict):
    """
    Renderizar los resultados completos de la predicción de entrega,
    adaptándose si hay un split en la entrega.
    """
    st.subheader("📊 Resultados de la Predicción de Entrega")

    # Sección principal de métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**🛣️ Información de ruta**")
        st.metric("📦 ID Trazo", data.get('id_trazo', 'N/A'))
        st.metric("📍 Tienda", data.get('tienda', 'N/A'))
        st.metric("🚚 Método", data.get('metodo', 'N/A'))
    with col2:
        st.markdown("**🗓️Fechas importantes**")
        st.metric("⏳ Días Estimados", data.get('dias', 'N/A'))
        st.metric("🗓️ Fecha Entrega", format_datetime(data.get('fecha_entrega', '')))
    with col3:
        st.markdown("**💲Desglose de costos**")
        st.metric("🛒 Cantidad Total", data.get('cantidad_total', 'N/A'))
        st.metric("💰 Costo Unitario", format_currency(data.get('costo_unitario', 0)))
        st.metric("💲 Costo Total", format_currency(data.get('costo', 0)))
    with col4:
        st.markdown("**⚙️ Detalles técnicos**")
        st.metric("⏱️ Tiempo de procesamiento", f"{data.get('tiempo_proceso_ms', 0):.2f} ms")
        st.metric("✨ Score", format_percentage(data.get('score', 0)))

    st.markdown("---")
    st.subheader("🗺️ Contexto Geográfico")
    geo_context = data.get('contexto_geografico', {})
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🌍 Rango CP", geo_context.get('rango_cp', 'N/A'))
        st.metric("🏘️ Estado/Alcaldía", geo_context.get('estado_alcaldia', 'N/A'))
        st.metric("🏬 Cobertura Liverpool", "✅ Sí" if geo_context.get('cobertura_liverpool', False) else "❌ No")
    with col2:
        st.metric("🚨 Zona Seguridad", geo_context.get('zona_seguridad', 'N/A'))
        st.metric("🏙️ Tipo de Zona", geo_context.get('tipo_zona', 'N/A'))
    with col3:
        st.metric("⏳ Tiempo Entrega Base (horas)", geo_context.get('tiempo_entrega_base_horas', 'N/A'))
        st.metric("📝 Observaciones", geo_context.get('observaciones', 'N/A'))

    st.markdown("---")
    st.subheader("☁️ Contexto Climático")
    clim_context = data.get('contexto_climatico', {})
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📍 Región", clim_context.get('region_nombre', 'N/A'))
        st.metric("🗺️ Estado Principal", clim_context.get('estado_principal', 'N/A'))
    with col2:
        st.metric("☀️ Clima Actual", clim_context.get('clima_actual', 'N/A'))
        st.metric("🌡️ Temperatura (Min/Max)",
                  f"{clim_context.get('temperatura_min', 'N/A')}°C / {clim_context.get('temperatura_max', 'N/A')}°C")
    with col3:
        st.metric("⛰️ Altitud (msnm)", clim_context.get('altitud_msnm', 'N/A'))
        st.metric("💧 Precipitación Anual", f"{clim_context.get('precipitacion_anual', 'N/A')} mm")
        st.metric("⚡ Factores Especiales", clim_context.get('factores_especiales', 'N/A'))

# Métodos auxiliares
def highlight_selected_row(row):
    """
    Define el estilo para resaltar las filas donde 'selected' es True.
    """
    if row['selected']:
        return ['background-color: #d4edda'] * len(row)
    return [''] * len(row)


def generate_comparison_table(df_bigquery, api_data: dict, original_request: dict, recalculate: bool = False):
    """Generates and styles the comparison DataFrame for display."""
    st.subheader("🎨Tabla Comparativa de Rutas")

    if api_data and not df_bigquery.empty:
        ganadores = []  # selected: true
        alternativas = []  # selected: false

        for alt in api_data.get('alternativas', []):
            if alt.get('selected', False):
                ganadores.append(alt.get('id', ''))
            else:
                alternativas.append(alt.get('id', ''))

        # Formateo para frontend
        ganadores_display = ", ".join(ganadores)
        alternativas_display = ", ".join(alternativas)

        st.write(f"🏆 Rutas ganadoras: {ganadores_display}")
        st.write(f"🥈 Alternativas encontradas: {alternativas_display}")

        def clasificar_ruta(row):
            id_trazo = str(row['ID_TRAZO'])
            if id_trazo in ganadores:
                return 'GANADOR'
            elif id_trazo in alternativas:
                return 'ALTERNATIVA'
            else:
                return 'OTROS'

        df_bigquery['CLASIFICACION_ML'] = df_bigquery.apply(clasificar_ruta, axis=1)

        # --- Identify excluded store ---
        excluded_store_cve = api_data.get('tienda_rechazada', None)
        es_split = api_data.get('es_split', False)
        es_recalculo = api_data.get('es_recalculo', False)

        # Inicializa la columna ES_EXCLUIDA a False para todas las filas
        # Esto es crucial para que las rutas no excluidas no se queden sin valor
        # y para que las condiciones posteriores puedan establecerla a True.
        df_bigquery['ES_EXCLUIDA'] = False

        # Caso complejo recalculo (split)
        if es_split and es_recalculo:
            # Asegúrate de que 'tienda_rechazada' en session_state sea una lista
            excluded_stores = st.session_state.get('tienda_rechazada', [])
            if excluded_stores and 'TDA_CVE' in df_bigquery.columns:
                # Convertir todos los elementos de excluded_stores a string antes de unirlos
                excluded_stores_str = [str(s) for s in excluded_stores]
                st.warning(
                    f"🚨 **Se detectaron tiendas excluidas:** Se resaltarán en rojo las rutas de las siguientes tiendas **{', '.join(excluded_stores_str)}**.")
                # Usa .isin() para marcar todas las filas donde TDA_CVE esté en la lista de tiendas excluidas
                df_bigquery['ES_EXCLUIDA'] = df_bigquery['TDA_CVE'].isin(excluded_stores)
            # Si excluded_stores está vacío o TDA_CVE no existe, ES_EXCLUIDA permanece False

        elif es_recalculo and not es_split:
            if excluded_store_cve and 'TDA_CVE' in df_bigquery.columns:
                st.warning(
                    f"🚨 **Tienda Excluida detectada:** Se resaltarán en rojo las rutas de la tienda **{excluded_store_cve}**.")
                # Caso simple de recalculo (una sola tienda excluida)
                df_bigquery['ES_EXCLUIDA'] = df_bigquery['TDA_CVE'] == excluded_store_cve
            # Si excluded_store_cve es None o TDA_CVE no existe, ES_EXCLUIDA permanece False

        # El bloque 'elif not es_recalculo:' ya no es necesario
        # porque ES_EXCLUIDA se inicializa a False al principio.

        conteos = df_bigquery['CLASIFICACION_ML'].value_counts()
        st.write("📊 **Distribución de las rutas:**")
        for tipo, cantidad in conteos.items():
            emoji = "🏆" if tipo == "GANADOR" else "🥈" if tipo == "ALTERNATIVA" else "📋"
            st.write(f"{emoji} {tipo}: {cantidad} rutas")

        columnas_display = ['ID_TRAZO', 'SKU_CVE', 'CP', 'TDA_CVE', 'INVENTARIO_OH', 'MET_ENTREGA', 'REAL_CAP_STORE',
                            'CAPACIDAD_ME', 'TIEMPO_3', 'COSTO', 'ZONA_ROJA', 'TRAFICO', 'DESASTRE_NATURAL',
                            'EXCL_PROD', 'TUBERIA', 'CLASIFICACION_ML']
        columnas_disponibles = [col for col in columnas_display if col in df_bigquery.columns]

        df_display = df_bigquery[columnas_disponibles + ['ES_EXCLUIDA']].copy()
        rename_map = {
            'ID_TRAZO': 'Trazo',
            'SKU_CVE': 'SKU_CVE',
            'CP': 'CP',
            'TDA_CVE': 'Tienda',
            'INVENTARIO_OH': 'Inventario',
            'MET_ENTREGA': 'Met_Entrega',
            'REAL_CAP_STORE': 'Cap_TDA',
            'CAPACIDAD_ME': 'Cap_ME',
            'TIEMPO_3': 'Tiempo',
            'COSTO': 'Costo',
            'ZONA_ROJA': 'Zona',
            'TRAFICO': 'Trafico',
            'DESASTRE_NATURAL': 'Desastre',
            'EXCL_PROD': 'EXCL_PROD',
            'TUBERIA': 'Tuberia',
            'CLASIFICACION_ML': 'Decisión',
            'ES_EXCLUIDA': 'Es_Excluida'
        }

        for old, new in rename_map.items():
            if old in df_display.columns:
                df_display = df_display.rename(columns={old: new})

        orden_clasificacion = {'GANADOR': 1, 'ALTERNATIVA': 2, 'OTROS': 3}
        df_display['_orden'] = df_display['Decisión'].map(orden_clasificacion)
        df_display = df_display.sort_values(['_orden', 'Tiempo', 'Costo']).drop('_orden', axis=1)

        df_display_for_html = df_display.drop('Es_Excluida', axis=1, errors='ignore')

        def build_html_table(df_to_render, original_df_with_flags):
            html = """
            <style>
                table {
                    border-collapse: collapse;
                    width: 100%;
                    font-family: Arial, sans-serif;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.08); /* A bit more pronounced shadow */
                    border-radius: 8px; /* Rounded corners for the table */
                    overflow: hidden; /* Ensures border-radius applies to content */
                }
                th, td {
                    border: 1px solid #e0e0e0; /* Lighter borders */
                    padding: 10px; /* Slightly more padding */
                    text-align: center;
                    vertical-align: middle;
                }
                th {
                    background-color: #f0f2f6; /* Lighter header background */
                    color: #333333; /* Darker text for headers */
                    font-weight: bold;
                    text-transform: uppercase;
                    font-size: 0.9em;
                }
                /* Removed: tr:nth-child(even) { background-color: #f9f9f9; } */
                tr:hover { /* Hover effect */
                    background-color: #f1f1f1;
                }
                .GANADOR {
                    background-color: #E6F7EA; /* Very Light Green */
                    font-weight: bold;
                    border-left: 4px solid #4CAF50; /* Green highlight on left */
                }
                .ALTERNATIVA {
                    background-color: #FFFDE7; /* Very Light Yellow */
                    border-left: 4px solid #FFC107; /* Amber highlight on left */
                }
                .OTROS {
                    background-color: #F8F8F8; /* Even lighter gray */
                }
                .EXCLUIDA {
                    background-color: #FFEBEE !important; /* Very Light Red */
                    color: #D32F2F !important; /* Dark Red text */
                    font-weight: bold;
                    border-left: 4px solid #F44336 !important; /* Red highlight on left */
                }
                caption {
                    caption-side: bottom;
                    font-size: 0.8em;
                    margin-top: 10px;
                    color: #777;
                }
            </style>
            <table>
                <thead>
                    <tr>
                        {% for col in df_to_render.columns %}
                        <th>{{ col }}</th>
                        {% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for index, row in df_to_render.iterrows() %}
                    {% set original_row = original_df_with_flags.loc[index] %} {# Get the full row from the original DataFrame #}
                    <tr class="{{ original_row['Decisión'] }} {% if original_row['Es_Excluida'] %}EXCLUIDA{% endif %}">
                        {% for cell in row %}
                        <td>{{ cell }}</td>
                        {% endfor %}
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            """
            template = Template(html)
            return template.render(df_to_render=df_to_render, original_df_with_flags=original_df_with_flags)

        # Call build_html_table with the df_display DataFrame that includes 'ES_EXCLUIDA'
        st.html(build_html_table(df_display_for_html, df_display))

    else:
        st.warning("❌ Ocurrio un error y no fue posible generar la tabla comparativa:")
        if not api_data:
            st.write("   • No se encontró una solicitud a la API.")
        if df_bigquery.empty:
            st.write("   • No se encontraron datos en BigQuery.")