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
    Comparar datos de BigQuery con resultados del algoritmo y pintar según match EXACTO
    CORREGIDO: Marca como descartadas las rutas de la tienda rechazada

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

    # Verificar si es un recálculo y obtener datos relevantes
    es_recalculo = prediction_data.get('es_recalculo', False)
    tienda_rechazada = prediction_data.get('tienda_rechazada', None)
    rutas_descartadas_api = prediction_data.get('rutas_descartadas', [])

    print(f"DEBUG - Es recálculo: {es_recalculo}")
    print(f"DEBUG - Tienda rechazada: {tienda_rechazada}")
    print(f"DEBUG - Rutas descartadas del API: {rutas_descartadas_api}")

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

    print(f"DEBUG - Columna ID_TRAZO encontrada: {id_trazo_col}")
    print(f"DEBUG - Columna TIENDA encontrada: {tienda_col}")
    print(f"DEBUG - Alternativas del API: {len(alternativas)}")

    # Crear un set de IDs ya procesados para evitar duplicados
    processed_ids = set()

    # PASO 1: Marcar rutas descartadas en recálculos
    if es_recalculo and tienda_col:
        print(f"DEBUG - Procesando descarte de rutas...")

        # Opción A: Si el API devuelve rutas descartadas específicas, usarlas
        if rutas_descartadas_api and isinstance(rutas_descartadas_api, list) and id_trazo_col:
            rutas_descartadas_clean = [ruta for ruta in rutas_descartadas_api if ruta and str(ruta).strip()]
            if rutas_descartadas_clean:
                print(f"DEBUG - Usando rutas descartadas del API: {rutas_descartadas_clean}")
                for idx, row in df_result.iterrows():
                    id_trazo_bq = str(row[id_trazo_col]).strip()
                    if id_trazo_bq in rutas_descartadas_clean:
                        df_result.at[idx, 'STATUS_ML'] = 'DESCARTADA'
                        processed_ids.add(id_trazo_bq)
                        print(f"DEBUG - DESCARTADA por API: {id_trazo_bq}")

        # Opción B: Si hay tienda rechazada, marcar todas sus rutas como descartadas
        elif tienda_rechazada is not None:
            print(f"DEBUG - Marcando rutas de tienda rechazada {tienda_rechazada} como descartadas")
            rutas_descartadas_count = 0

            for idx, row in df_result.iterrows():
                tienda_bq = row[tienda_col]

                # Convertir a int para comparación robusta
                try:
                    tienda_bq_int = int(tienda_bq)
                    tienda_rechazada_int = int(tienda_rechazada)

                    if tienda_bq_int == tienda_rechazada_int:
                        df_result.at[idx, 'STATUS_ML'] = 'DESCARTADA'
                        rutas_descartadas_count += 1

                        # Agregar ID a processed_ids si existe
                        if id_trazo_col and id_trazo_col in row:
                            id_trazo_bq = str(row[id_trazo_col]).strip()
                            processed_ids.add(id_trazo_bq)
                            print(f"DEBUG - DESCARTADA por tienda {tienda_rechazada}: {id_trazo_bq}")
                        else:
                            print(f"DEBUG - DESCARTADA por tienda {tienda_rechazada}: fila {idx}")

                except (ValueError, TypeError) as e:
                    print(
                        f"DEBUG - Error comparando tiendas: {e}, tienda_bq={tienda_bq}, tienda_rechazada={tienda_rechazada}")
                    continue

            print(f"DEBUG - Total rutas descartadas por tienda rechazada: {rutas_descartadas_count}")

    # PASO 2: Clasificar cada registro según el API - SOLO POR ID_TRAZO EXACTO
    for idx, row in df_result.iterrows():
        # Solo procesar si no fue ya marcado como descartado
        if df_result.at[idx, 'STATUS_ML'] == 'DESCARTADA':
            continue

        # Solo intentar match por ID_TRAZO si existe la columna
        if id_trazo_col and id_trazo_col in row:
            id_trazo_bq = str(row[id_trazo_col]).strip()

            # Buscar match exacto por ID_TRAZO en las alternativas del API
            for alt in alternativas:
                api_id = str(alt.get('id', '')).strip()

                if id_trazo_bq == api_id and api_id not in processed_ids:
                    if alt.get('selected', False):
                        df_result.at[idx, 'STATUS_ML'] = 'GANADOR'
                        print(f"DEBUG - GANADOR por ID_TRAZO: {api_id}")
                    else:
                        df_result.at[idx, 'STATUS_ML'] = 'ALTERNATIVA'
                        print(f"DEBUG - ALTERNATIVA por ID_TRAZO: {api_id}")

                    processed_ids.add(api_id)
                    break

    # Contar resultados
    ganadores = len(df_result[df_result['STATUS_ML'] == 'GANADOR'])
    alternativas_count = len(df_result[df_result['STATUS_ML'] == 'ALTERNATIVA'])
    descartadas = len(df_result[df_result['STATUS_ML'] == 'DESCARTADA'])
    sin_match = len(df_result[df_result['STATUS_ML'] == 'SIN_MATCH'])

    print(
        f"DEBUG - Resultados finales: {ganadores} ganadores, {alternativas_count} alternativas, {descartadas} descartadas, {sin_match} sin match")

    # Ordenar: ganadores primero, luego alternativas, luego descartadas, luego otros
    orden_status = {'GANADOR': 1, 'ALTERNATIVA': 2, 'DESCARTADA': 3, 'SIN_MATCH': 4}
    df_result['_orden'] = df_result['STATUS_ML'].map(orden_status)
    df_result = df_result.sort_values('_orden', na_position='last')
    df_result = df_result.drop('_orden', axis=1)

    return df_result