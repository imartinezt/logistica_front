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
        SELECT * FROM `{Config.PROJECT_ID}.{Config.DATASET_ID}.{Config.TABLE_ID}`
        WHERE 1=1
            AND SKU_CVE = {sku_cve}
            AND CP = {cp}
            AND NOT (MET_ENTREGA = 'FLOTA LIVERPOOL' AND ZONA_ROJA = 1)
            AND NOT (MET_ENTREGA = 'MENSAJERIA EXTERNA' AND EXCL_PROD != 0)
            AND INVENTARIO_OH > 0
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
    Comparar datos de BigQuery con resultados del algoritmo y pintar según match exacto

    Args:
        df_bigquery: DataFrame de BigQuery con todas las opciones (columnas reales)
        prediction_data: Datos de predicción del algoritmo

    Returns:
        DataFrame: Datos con columna de STATUS para pintar
    """
    if df_bigquery.empty:
        return df_bigquery

    # Crear copia para no modificar original
    df_result = df_bigquery.copy()
    df_result['STATUS_ML'] = 'SIN_MATCH'

    # Obtener alternativas del API
    alternativas = prediction_data.get('alternativas', [])

    # Buscar qué columnas existen para hacer el match
    id_trazo_col = None
    tienda_col = None

    # Buscar columna de ID_TRAZO (puede tener diferentes nombres)
    for col in df_result.columns:
        if 'ID_TRAZO' in str(col).upper() or 'TRAZO' in str(col).upper():
            id_trazo_col = col
            break

    # Buscar columna de TIENDA
    for col in df_result.columns:
        if 'TIENDA' in str(col).upper() or 'TDA' in str(col).upper():
            tienda_col = col
            break

    # Debug: mostrar qué columnas encontramos
    print(f"DEBUG - Columna ID_TRAZO encontrada: {id_trazo_col}")
    print(f"DEBUG - Columna TIENDA encontrada: {tienda_col}")
    print(f"DEBUG - Alternativas del API: {len(alternativas)}")

    # Clasificar cada registro según el API - MATCH EXACTO PRIORITARIO
    for idx, row in df_result.iterrows():
        match_found = False

        # PASO 1: Intentar match EXACTO por ID_TRAZO (prioritario)
        if id_trazo_col and id_trazo_col in row:
            id_trazo_bq = str(row[id_trazo_col]).strip()

            for alt in alternativas:
                api_id = str(alt.get('id', '')).strip()

                if id_trazo_bq == api_id and api_id != '':  # Match exacto y no vacío
                    if alt.get('selected', False):
                        df_result.at[idx, 'STATUS_ML'] = 'GANADOR'
                        print(f"DEBUG - GANADOR por ID_TRAZO: {id_trazo_bq}")
                    else:
                        df_result.at[idx, 'STATUS_ML'] = 'ALTERNATIVA'
                        print(f"DEBUG - ALTERNATIVA por ID_TRAZO: {id_trazo_bq}")
                    match_found = True
                    break

        # PASO 2: Solo si NO hubo match por ID_TRAZO, intentar por TIENDA
        if not match_found and tienda_col and tienda_col in row:
            tienda_bq = row[tienda_col]

            for alt in alternativas:
                api_tienda = alt.get('tienda', 0)

                if tienda_bq == api_tienda and api_tienda != 0:  # Match por tienda
                    # PERO solo si el ID_TRAZO de BigQuery NO aparece en ninguna alternativa
                    # (para evitar duplicados cuando ya hay match exacto)
                    id_trazo_bq = str(row.get(id_trazo_col, '')).strip() if id_trazo_col else ''
                    id_ya_matcheado = any(
                        str(a.get('id', '')).strip() == id_trazo_bq
                        for a in alternativas
                        if id_trazo_bq != ''
                    )

                    if not id_ya_matcheado:  # Solo marcar si el ID no está en alternativas
                        if alt.get('selected', False):
                            df_result.at[idx, 'STATUS_ML'] = 'GANADOR'
                            print(f"DEBUG - GANADOR por TIENDA: {tienda_bq}")
                        else:
                            df_result.at[idx, 'STATUS_ML'] = 'ALTERNATIVA'
                            print(f"DEBUG - ALTERNATIVA por TIENDA: {tienda_bq}")
                        break

    # Contar resultados para debug
    ganadores = len(df_result[df_result['STATUS_ML'] == 'GANADOR'])
    alternativas_count = len(df_result[df_result['STATUS_ML'] == 'ALTERNATIVA'])
    sin_match = len(df_result[df_result['STATUS_ML'] == 'SIN_MATCH'])

    print(
        f"DEBUG - Resultados finales: {ganadores} ganadores, {alternativas_count} alternativas, {sin_match} sin match")

    # Ordenar: ganadores primero, luego alternativas, luego otros
    orden_status = {'GANADOR': 1, 'ALTERNATIVA': 2, 'SIN_MATCH': 3}
    df_result['_orden'] = df_result['STATUS_ML'].map(orden_status)
    df_result = df_result.sort_values('_orden', na_position='last')
    df_result = df_result.drop('_orden', axis=1)

    return df_result