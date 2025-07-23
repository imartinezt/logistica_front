import os

from dotenv import load_dotenv

load_dotenv()

class Config:

    # API endpoints
    API_BASE_URL = "https://dev-fee-back-img-209565165407.us-central1.run.app"
    API_PREDICT_ENDPOINT = "/api/v1/fee/predict"
    API_RECALCULATE_ENDPOINT = "/api/v1/fee/recalculate"

    # API general configuration
    API_TIMEOUT = 30
    APP_TITLE = "Logistics Intelligence Platform"
    APP_ICON = "📊"

    # Default parameters
    LAYOUT = "wide"
    DEFAULT_CP = "02125"
    DEFAULT_SKU = "1147407030"
    DEFAULT_QUANTITY = 1
    DEFAULT_TEMPORADA = "TEMPORADA_ALTA"
    MIN_CP_LENGTH = 5
    MIN_SKU_LENGTH = 3
    MAX_QUANTITY = 100
    CHART_HEIGHT = "400px"
    TEMPORADAS = ["TEMPORADA_ALTA", "TEMPORADA_BAJA"]

    # =================================== Configuración para PROD ============================
    SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT").replace("\r", "")
    PROJECT_ID = os.getenv("PROJECT_ID").replace("\r", "")
    DATASET_ID = os.getenv("DATASET_ID").replace("\r", "")
    TABLE_ID = os.getenv("TABLE_ID").replace("\r", "")