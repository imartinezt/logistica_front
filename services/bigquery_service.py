from config.settings import Config
import streamlit as st
import pandas as pd
from google.cloud import bigquery

@st.cache_resource
def get_bigquery_client():
    """Initializes and returns a BigQuery client."""
    try:
        client = bigquery.Client(project=Config.PROJECT_ID)
        return client
    except Exception as e:
        return None

def execute_bigquery_query(client, original_request):
    """Executes the BigQuery query and returns a DataFrame."""

    sku_cve = original_request.get('sku_id', '')
    cp = original_request.get('codigo_postal', '')
    query = f"""
        SELECT * FROM `liv-dev-dig-chatbot.Fecha_Estimada_Entrega.TB_FEE_RESULTADO_FINAL__JUL14`
        WHERE 1=1
        AND SKU_CVE = {sku_cve}
        AND CP = {cp}
        AND NOT (MET_ENTREGA = 'FLOTA LIVERPOOL' AND ZONA_ROJA = 1)
        AND NOT (MET_ENTREGA = 'MENSAJERIA EXTERNA' AND EXCL_PROD != 0)
        AND INVENTARIO_OH > 0
    """

    if client:
        try:
            query_job = client.query(query)
            df_bigquery = query_job.to_dataframe()
            if len(df_bigquery) == 0:
                st.warning("⚠️ No records found in BigQuery for the given criteria.")
            return df_bigquery
        except Exception as e:
            st.error(f"❌ Error executing query: {str(e)}")
            return pd.DataFrame()
    else:
        return pd.DataFrame()