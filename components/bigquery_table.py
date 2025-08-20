from services.bigquery_service import get_bigquery_client, execute_bigquery_query, compare_bigquery_with_results
import streamlit as st
import pandas as pd

@st.cache_data(show_spinner=False)
def get_bigquery_results(original_request: dict):
    """
    Ejecuta una consulta en bigquery y la almacena en cache
    """
    bq_client = get_bigquery_client()
    if not bq_client:
        st.warning("⚠️ BigQuery no está configurado.")
        return None

    return execute_bigquery_query(bq_client, original_request)


def render_bigquery_analysis(data: dict, original_request: dict):
    """Análisis simplificado: BigQuery con datos pintados según algoritmo"""
    st.markdown("---")
    st.markdown("### 📊 Análisis de Datos: Algoritmo ML")

    df_bigquery = get_bigquery_results(original_request)

    if df_bigquery.empty:
        st.warning("⚠️ No se encontraron datos en BigQuery para este CP + SKU")
        return

    # Comparar datos de BigQuery con resultados del algoritmo
    df_with_status = compare_bigquery_with_results(df_bigquery, data)

    # Mostrar resumen rápido
    total_registros = len(df_with_status)
    ganadores = len(df_with_status[df_with_status['STATUS_ML'] == 'GANADOR'])
    alternativas = len(df_with_status[df_with_status['STATUS_ML'] == 'ALTERNATIVA'])
    descartadas = len(df_with_status[df_with_status['STATUS_ML'] == 'DESCARTADA'])
    sin_match = len(df_with_status[df_with_status['STATUS_ML'] == 'SIN_MATCH'])

    # Verificar si es recálculo para mostrar métricas apropiadas
    es_recalculo = data.get('es_recalculo', False)

    if es_recalculo:
        # Mostrar 5 columnas cuando hay recálculo
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("📊 Total Registros", total_registros)
        with col2:
            st.metric("🟢 Ganadores", ganadores)
        with col3:
            st.metric("🟡 Alternativas", alternativas)
        with col4:
            st.metric("🔴 Descartadas", descartadas)
        with col5:
            st.metric("⚪ Sin Match", sin_match)
    else:
        # Mostrar 4 columnas cuando no hay recálculo
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Registros", total_registros)
        with col2:
            st.metric("🟢 Ganadores", ganadores)
        with col3:
            st.metric("🟡 Alternativas", alternativas)
        with col4:
            st.metric("⚪ Sin Match", sin_match)

    # Tabla principal con colores
    render_bigquery_table_with_colors(df_with_status, es_recalculo)


def render_bigquery_table_with_colors(df_with_status: pd.DataFrame, es_recalculo: bool = False):
    """Renderizar tabla de BigQuery con colores según status ML usando columnas reales"""

    # Verificar que tengamos datos
    if df_with_status.empty:
        st.warning("No hay datos para mostrar")
        return

    # Función para aplicar colores - usar la columna STATUS_ML que debe existir
    def style_row_by_status(row):
        if 'STATUS_ML' not in row:
            return [''] * len(row)  # Sin estilo si no hay STATUS_ML

        status = row['STATUS_ML']
        if status == 'GANADOR':
            return ['background-color: #dcfce7; color: #166534; font-weight: bold'] * len(row)  # Verde
        elif status == 'ALTERNATIVA':
            return ['background-color: #fef3c7; color: #92400e'] * len(row)  # Amarillo
        elif status == 'DESCARTADA':
            return ['background-color: #fecaca; color: #dc2626; font-weight: bold'] * len(row)  # Rojo
        else:
            return ['background-color: #f9fafb; color: #374151'] * len(row)  # Gris claro

    # Preparar DataFrame para mostrar
    df_display = df_with_status.copy()

    # Verificar que STATUS_ML existe
    if 'STATUS_ML' not in df_display.columns:
        st.error("Error: No se pudo procesar el estado ML")
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        return

    # Agregar columna visual de status
    status_display = []
    for status in df_display['STATUS_ML']:
        if status == 'GANADOR':
            status_display.append('🟢 GANADOR')
        elif status == 'ALTERNATIVA':
            status_display.append('🟡 ALTERNATIVA')
        elif status == 'DESCARTADA':
            status_display.append('🔴 DESCARTADA')
        else:
            status_display.append('⚪ SIN MATCH')

    df_display['STATUS'] = status_display

    # Preparar columnas para mostrar (STATUS primero, luego las originales, pero NO STATUS_ML)
    cols_to_show = ['STATUS'] + [col for col in df_display.columns if col not in ['STATUS', 'STATUS_ML']]

    # Aplicar estilos al DataFrame completo (que aún tiene STATUS_ML)
    styled_df = df_display.style.apply(style_row_by_status, axis=1)

    # Configurar columnas dinámicamente según lo que existe
    column_config = {
        "STATUS": st.column_config.TextColumn(
            "Status ML",
            help="Resultado del algoritmo ML",
            width="medium"
        )
    }

    # Agregar configuraciones para columnas comunes si existen
    for col in df_display.columns:
        if col in ['STATUS', 'STATUS_ML']:
            continue

        col_upper = str(col).upper()

        if 'COSTO' in col_upper:
            column_config[col] = st.column_config.NumberColumn(
                col,
                help="Costo de la ruta",
                format="$%.0f"
            )
        elif 'TIEMPO' in col_upper or 'DIAS' in col_upper:
            column_config[col] = st.column_config.NumberColumn(
                col,
                help="Tiempo de entrega",
                format="%d"
            )
        elif 'INVENTARIO' in col_upper:
            column_config[col] = st.column_config.NumberColumn(
                col,
                help="Inventario disponible",
                format="%d"
            )
        elif 'TIENDA' in col_upper or 'TDA' in col_upper:
            column_config[col] = st.column_config.NumberColumn(
                col,
                help="ID de la tienda",
                format="%d"
            )
        elif 'TRAZO' in col_upper:
            column_config[col] = st.column_config.TextColumn(
                col,
                help="ID del trazo",
                width="medium"
            )

    # Mostrar tabla - usar subset de columnas para ocultar STATUS_ML
    try:
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            column_config=column_config,
            column_order=cols_to_show  # Especificar orden de columnas excluyendo STATUS_ML
        )
    except Exception as e:
        st.error(f"Error mostrando tabla estilizada: {str(e)}")
        # Fallback: mostrar tabla sin estilos
        df_simple = df_display[cols_to_show]
        st.dataframe(df_simple, use_container_width=True, hide_index=True)

    # Leyenda - incluir descartadas solo si es recálculo
    leyenda_descartadas = """
        <span style="display: flex; align-items: center; gap: 0.5rem;">
            <div style="width: 16px; height: 16px; background: #fecaca; border: 1px solid #dc2626; border-radius: 3px;"></div>
            <strong>🔴 DESCARTADA:</strong> Ruta descartada en recálculo
        </span>
    """ if es_recalculo else ""

    st.html(f"""
        <div style="margin-top: 1rem; padding: 1rem; background: #f9fafb; border-radius: 8px; border: 1px solid #e5e7eb;">
            <div style="display: flex; gap: 2rem; align-items: center; justify-content: center; flex-wrap: wrap;">
                <span style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="width: 16px; height: 16px; background: #dcfce7; border: 1px solid #16a34a; border-radius: 3px;"></div>
                    <strong>🟢 GANADOR:</strong> Seleccionado por el algoritmo
                </span>
                <span style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="width: 16px; height: 16px; background: #fef3c7; border: 1px solid #d97706; border-radius: 3px;"></div>
                    <strong>🟡 ALTERNATIVA:</strong> Evaluado pero no seleccionado
                </span>
                {leyenda_descartadas}
                <span style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="width: 16px; height: 16px; background: #f9fafb; border: 1px solid #6b7280; border-radius: 3px;"></div>
                    <strong>⚪ SIN MATCH:</strong> No evaluado por el algoritmo
                </span>
            </div>
        </div>
    """)