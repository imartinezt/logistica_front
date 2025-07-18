class Config:
    API_BASE_URL = "http://0.0.0.0:8000"
    API_PREDICT_ENDPOINT = "/api/v1/fee/predict"
    API_RECALCULATE_ENDPOINT = "/api/v1/fee/recalculate"
    API_TIMEOUT = 30
    APP_TITLE = "Logistics Intelligence Platform"
    APP_ICON = "📊"
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