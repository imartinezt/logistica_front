import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar
from utils.helpers import format_currency, format_datetime
from services.bigquery_service import get_bigquery_client, execute_bigquery_query, compare_bigquery_with_results


def render_results_page():
    """Página de resultados minimalista y elegante"""
    data = st.session_state.prediction_data
    original_request = st.session_state.get('original_request', {})

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
    """Cuadro principal con la información de entrega unificada"""

    # Título principal
    st.html("""
        <div style="text-align: center; margin: 2rem 0;">
            <h2 style="color: #2563eb; font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">
                🎯 Fecha Promesa de Entrega
            </h2>
        </div>
    """)

    # Fecha de entrega destacada
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

    # Extraer todos los datos necesarios
    fecha_compra = original_request.get('fecha_compra', '')
    codigo_postal = original_request.get('codigo_postal', '')
    dias_entrega = calculate_days_to_delivery(fecha_compra, fecha_entrega)
    tipo_entrega = data.get('tipo_entrega', {})
    ventana_tiempo = tipo_entrega.get('ventana_tiempo', 'N/A')
    tiendas_display = get_stores_display(data)
    rutas_display = get_routes_display(data)
    score = f"{data.get('score', 0):.3f}"
    costo = format_currency(data.get('costo', 0))
    tiempo_proceso = data.get('tiempo_proceso_ms', 0)
    tipo_display = f"{tipo_entrega.get('icono', '')} {tipo_entrega.get('nombre', 'N/A')}"

    # Información adicional para splits
    split_info = ""
    if data.get('es_split', False):
        split_data = data.get('split_info', {})
        rutas_count = split_data.get('rutas_seleccionadas', 0)
        split_info = f"📦 SPLIT ({rutas_count} rutas)"

    # Cuadro unificado estilo "fechas importantes"
    st.html(f"""
        <div style="
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border: 2px solid #e2e8f0;
            border-radius: 16px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        ">
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

            <div style="
                border-top: 1px solid #e5e7eb;
                padding-top: 2rem;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1.5rem;
                text-align: center;
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
                        ⭐ SCORE
                    </div>
                    <div style="color: #374151; font-size: 1rem; font-weight: 600;">
                        {score}
                    </div>
                </div>

                <div>
                    <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                        💰 COSTO TOTAL
                    </div>
                    <div style="color: #374151; font-size: 1rem; font-weight: 600;">
                        {costo}
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

                {f'<div><div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">📦 TIPO</div><div style="color: #f59e0b; font-size: 1rem; font-weight: 600;">{split_info}</div></div>' if split_info else ''}
            </div>
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


def render_bigquery_analysis(data: dict, original_request: dict):
    """Análisis completo: BigQuery vs Algoritmo"""
    st.markdown("---")
    st.markdown("### 🔍 Análisis de Datos: Disponibles vs Seleccionados")

    # Obtener cliente y datos de BigQuery
    bq_client = get_bigquery_client()

    if not bq_client:
        st.warning("⚠️ BigQuery no está configurado. Mostrando solo alternativas del algoritmo.")
        render_algorithm_alternatives_only(data)
        return

    # Ejecutar consulta
    df_bigquery = execute_bigquery_query(bq_client, original_request)

    if df_bigquery.empty:
        st.warning("⚠️ No se encontraron datos en BigQuery para este CP + SKU")
        render_algorithm_alternatives_only(data)
        return

    # Comparar datos de BigQuery con resultados del algoritmo
    df_comparison = compare_bigquery_with_results(df_bigquery, data)

    # Mostrar métricas de resumen
    render_comparison_metrics(df_comparison, data)

    # Mostrar tabla comparativa
    render_comparison_table(df_comparison)


def render_comparison_metrics(df_comparison: pd.DataFrame, data: dict):
    """Métricas de comparación entre datos disponibles y seleccionados con mejor diseño"""

    total_disponibles = len(df_comparison)
    seleccionados = len(df_comparison[df_comparison['SELECCIONADO'] == True])
    evaluados = len(df_comparison[df_comparison['STATUS'].str.contains('Evaluado')])
    descartados = len(df_comparison[df_comparison['STATUS'].str.contains('Descartado')])
    tasa_utilizacion = (seleccionados / total_disponibles * 100) if total_disponibles > 0 else 0

    # Contenedor unificado para métricas
    st.html(f"""
        <div style="
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border: 2px solid #3b82f6;
            border-radius: 12px;
            padding: 2rem;
            margin: 1.5rem 0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        ">
            <h4 style="text-align: center; color: #1e40af; margin-bottom: 1.5rem; font-size: 1.125rem;">
                📊 Resumen de Análisis
            </h4>
            <div style="
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 1.5rem;
                text-align: center;
            ">
                <div>
                    <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                        📊 TOTAL DISPONIBLES
                    </div>
                    <div style="color: #374151; font-size: 1.5rem; font-weight: 700;">
                        {total_disponibles}
                    </div>
                    <div style="color: #6b7280; font-size: 0.75rem; margin-top: 0.25rem;">
                        en BigQuery
                    </div>
                </div>

                <div>
                    <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                        🟢 SELECCIONADOS
                    </div>
                    <div style="color: #059669; font-size: 1.5rem; font-weight: 700;">
                        {seleccionados}
                    </div>
                    <div style="color: #6b7280; font-size: 0.75rem; margin-top: 0.25rem;">
                        por algoritmo
                    </div>
                </div>

                <div>
                    <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                        🟡 EVALUADOS
                    </div>
                    <div style="color: #d97706; font-size: 1.5rem; font-weight: 700;">
                        {evaluados}
                    </div>
                    <div style="color: #6b7280; font-size: 0.75rem; margin-top: 0.25rem;">
                        no seleccionados
                    </div>
                </div>

                <div>
                    <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                        🔴 DESCARTADOS
                    </div>
                    <div style="color: #dc2626; font-size: 1.5rem; font-weight: 700;">
                        {descartados}
                    </div>
                    <div style="color: #6b7280; font-size: 0.75rem; margin-top: 0.25rem;">
                        reglas negocio
                    </div>
                </div>

                <div>
                    <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                        📈 TASA UTILIZACIÓN
                    </div>
                    <div style="color: #7c3aed; font-size: 1.5rem; font-weight: 700;">
                        {tasa_utilizacion:.1f}%
                    </div>
                    <div style="color: #6b7280; font-size: 0.75rem; margin-top: 0.25rem;">
                        eficiencia
                    </div>
                </div>
            </div>
        </div>
    """)


def render_comparison_table(df_comparison: pd.DataFrame):
    """Tabla comparativa con colores según estatus"""
    st.markdown("#### 📋 Tabla Comparativa: Todos los Datos vs Algoritmo")

    # Configurar colores para la tabla
    def style_status_column(val):
        if '🟢' in val:
            return 'background-color: #dcfce7; color: #166534'
        elif '🟡' in val:
            return 'background-color: #fef3c7; color: #92400e'
        elif '🔴' in val:
            return 'background-color: #fee2e2; color: #dc2626'
        else:
            return 'background-color: #f3f4f6; color: #6b7280'

    # Aplicar estilos
    styled_df = df_comparison.style.applymap(
        style_status_column,
        subset=['STATUS']
    ).format({
        'SCORE': lambda x: f"{x:.3f}" if pd.notna(x) else "",
        'COSTO_FIJO': lambda x: f"${x:,.0f}" if pd.notna(x) else "",
        'RANK': lambda x: f"#{int(x)}" if pd.notna(x) else ""
    })

    # Mostrar tabla
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "STATUS": st.column_config.TextColumn(
                "Status",
                help="Estado del registro en el proceso de selección",
                width="medium"
            ),
            "RANK": st.column_config.TextColumn(
                "Rank",
                help="Posición en el ranking del algoritmo",
                width="small"
            ),
            "SCORE": st.column_config.NumberColumn(
                "Score",
                help="Puntuación asignada por el algoritmo",
                format="%.3f"
            ),
            "TIENDA": st.column_config.NumberColumn(
                "Tienda",
                help="ID de la tienda",
                format="%d"
            ),
            "DIAS_ENTREGA": st.column_config.NumberColumn(
                "Días",
                help="Días de entrega estimados",
                format="%d"
            ),
            "COSTO_FIJO": st.column_config.NumberColumn(
                "Costo",
                help="Costo fijo de la ruta",
                format="$%.0f"
            ),
            "INVENTARIO_OH": st.column_config.NumberColumn(
                "Inventario",
                help="Inventario disponible en la tienda",
                format="%d"
            )
        }
    )

    # Leyenda de colores
    st.html("""
        <div style="margin-top: 1rem; padding: 1rem; background: #f9fafb; border-radius: 8px;">
            <h5>📋 Leyenda de Status:</h5>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.5rem; margin-top: 0.5rem;">
                <span>🟢 <strong>Seleccionado:</strong> Elegido por el algoritmo</span>
                <span>🟡 <strong>Evaluado:</strong> Considerado pero no seleccionado</span>
                <span>🔴 <strong>Descartado:</strong> Rechazado por reglas de negocio</span>
                <span>⚪ <strong>No Evaluado:</strong> No llegó al algoritmo</span>
            </div>
        </div>
    """)


def render_algorithm_alternatives_only(data: dict):
    """Mostrar solo las alternativas del algoritmo cuando BigQuery no está disponible"""
    st.markdown("#### 📋 Alternativas Evaluadas por el Algoritmo")

    alternativas = data.get('alternativas', [])
    if not alternativas:
        st.warning("No se encontraron alternativas en los datos del algoritmo")
        return

    # Preparar datos para la tabla
    table_data = []
    for alt in alternativas:
        status = "🟢 Seleccionada" if alt.get('selected', False) else "🟡 Alternativa"

        table_data.append({
            "🏆 Rank": alt.get('rank', 'N/A'),
            "📊 Status": status,
            "🆔 ID Trazo": alt.get('id', 'N/A'),
            "🏪 Tienda": alt.get('tienda', 'N/A'),
            "🚚 Método": alt.get('metodo', 'N/A'),
            "📅 Días": alt.get('dias', 'N/A'),
            "💰 Costo": format_currency(alt.get('costo_fijo', 0)),
            "📦 Inventario": alt.get('inventario', 'N/A'),
            "🏢 Capacidad": alt.get('capacidad', 'N/A'),
            "⭐ Score": f"{alt.get('score', 0):.3f}"
        })

    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)


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