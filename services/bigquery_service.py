import streamlit as st
import pandas as pd
from google.cloud import bigquery
from config.settings import Config


@st.cache_resource
def get_bigquery_client():
    """Inicializar cliente de BigQuery con cache"""
    try:
        if hasattr(Config, 'SERVICE_ACCOUNT_FILE') and Config.SERVICE_ACCOUNT_FILE:
            client = bigquery.Client.from_service_account_json(Config.SERVICE_ACCOUNT_FILE)
            return client
        else:
            st.warning("⚠️ Configuración de BigQuery no encontrada")
            return None
    except Exception as e:
        st.error(f"❌ Error inicializando cliente BigQuery: {str(e)}")
        return None


def execute_bigquery_query(client, original_request):
    """
    Ejecutar consulta BigQuery para obtener todas las opciones disponibles

    Args:
        client: Cliente de BigQuery
        original_request: Request original con CP y SKU

    Returns:
        DataFrame: Datos de BigQuery
    """
    if not client:
        return pd.DataFrame()

    sku_cve = original_request.get('sku_id', '')
    cp = original_request.get('codigo_postal', '')

    if not sku_cve or not cp:
        st.warning("⚠️ SKU o CP faltante para consulta BigQuery")
        return pd.DataFrame()

    query = f"""
        SELECT 
            TIENDA,
            SKU_CVE,
            CP,
            MET_ENTREGA,
            INVENTARIO_OH,
            DIAS_ENTREGA,
            COSTO_FIJO,
            CAPACIDAD_STORE,
            CAPACIDAD_ME,
            ZONA_ROJA,
            EXCL_PROD,
            ACTIVO
        FROM `{Config.PROJECT_ID}.{Config.DATASET_ID}.{Config.TABLE_ID}`
        WHERE 1=1
            AND CAST(SKU_CVE AS STRING) = '{sku_cve}'
            AND CAST(CP AS STRING) = '{cp}'
            AND INVENTARIO_OH > 0
            AND ACTIVO = 1
        ORDER BY DIAS_ENTREGA ASC, COSTO_FIJO ASC
    """

    try:
        with st.spinner("🔍 Consultando datos de BigQuery..."):
            query_job = client.query(query)
            df_bigquery = query_job.to_dataframe()

        if len(df_bigquery) == 0:
            st.info("ℹ️ No se encontraron registros en BigQuery para los criterios dados")

        return df_bigquery

    except Exception as e:
        st.error(f"❌ Error ejecutando consulta BigQuery: {str(e)}")
        return pd.DataFrame()


def compare_bigquery_with_results(df_bigquery: pd.DataFrame, prediction_data: dict) -> pd.DataFrame:
    """
    Comparar datos de BigQuery con resultados del algoritmo

    Args:
        df_bigquery: DataFrame de BigQuery con todas las opciones
        prediction_data: Datos de predicción del algoritmo

    Returns:
        DataFrame: Datos enriquecidos con status de selección
    """
    if df_bigquery.empty:
        return df_bigquery

    # Crear copia para no modificar original
    df_enriched = df_bigquery.copy()
    df_enriched['STATUS'] = '🔘 Disponible'
    df_enriched['SELECCIONADO'] = False
    df_enriched['RANK'] = None
    df_enriched['SCORE'] = None

    # Obtener tiendas seleccionadas del algoritmo
    selected_stores = set()

    # Manejar splits
    if prediction_data.get('es_split', False):
        split_info = prediction_data.get('split_info', {})
        detalle_rutas = split_info.get('detalle_rutas', [])
        for ruta in detalle_rutas:
            selected_stores.add(ruta.get('tienda'))
    else:
        tienda = prediction_data.get('tienda')
        if tienda:
            selected_stores.add(tienda)

    # Obtener información de alternativas
    alternativas = prediction_data.get('alternativas', [])
    tienda_to_info = {}

    for alt in alternativas:
        tienda = alt.get('tienda')
        if tienda:
            tienda_to_info[tienda] = {
                'rank': alt.get('rank'),
                'score': alt.get('score', 0),
                'selected': alt.get('selected', False)
            }

    # Marcar registros según su status
    for idx, row in df_enriched.iterrows():
        tienda = row['TIENDA']

        if tienda in tienda_to_info:
            info = tienda_to_info[tienda]
            df_enriched.at[idx, 'RANK'] = info['rank']
            df_enriched.at[idx, 'SCORE'] = info['score']

            if info['selected']:
                df_enriched.at[idx, 'STATUS'] = '🟢 Seleccionado'
                df_enriched.at[idx, 'SELECCIONADO'] = True
            else:
                df_enriched.at[idx, 'STATUS'] = '🟡 Evaluado'
        else:
            # Verificar si fue descartado por reglas de negocio
            met_entrega = row['MET_ENTREGA']
            zona_roja = row.get('ZONA_ROJA', 0)
            excl_prod = row.get('EXCL_PROD', 0)

            if (met_entrega == 'FLOTA LIVERPOOL' and zona_roja == 1) or \
                    (met_entrega == 'MENSAJERIA EXTERNA' and excl_prod != 0):
                df_enriched.at[idx, 'STATUS'] = '🔴 Descartado (Reglas)'
            else:
                df_enriched.at[idx, 'STATUS'] = '⚪ No Evaluado'

    # Reordenar columnas
    column_order = [
        'STATUS', 'RANK', 'TIENDA', 'MET_ENTREGA', 'DIAS_ENTREGA',
        'COSTO_FIJO', 'INVENTARIO_OH', 'CAPACIDAD_STORE', 'CAPACIDAD_ME',
        'SCORE', 'ZONA_ROJA', 'EXCL_PROD', 'SKU_CVE', 'CP'
    ]

    # Solo incluir columnas que existen
    available_columns = [col for col in column_order if col in df_enriched.columns]
    df_enriched = df_enriched[available_columns]

    # Ordenar: seleccionados primero, luego por rank, luego por días
    df_enriched = df_enriched.sort_values([
        'SELECCIONADO',
        'RANK',
        'DIAS_ENTREGA',
        'COSTO_FIJO'
    ], ascending=[False, True, True, True], na_position='last')

    return df_enriched