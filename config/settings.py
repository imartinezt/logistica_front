class Config:

    # API endpoints
    API_BASE_URL = "http://0.0.0.0:8000"
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

    # ------------------------------------------------------------------
    # Google Cloud / BigQuery Configuration
    # ------------------------------------------------------------------
    PROJECT_ID: str = "liv-dev-dig-chatbot"
    DATASET_ID: str = "Fecha_Estimada_Entrega"
    TABLE_ID: str = "TB_FEE_RESULTADO_FINAL__JUL14_OPTIMIZED"
    TABLE_ID_ORIGINAL: str = "TB_FEE_RESULTADO_FINAL__JUL14_OPTIMIZED"