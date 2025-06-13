# config/settings.py
class Config:
    # API Configuration
    API_BASE_URL = "http://0.0.0.0:8000"
    API_PREDICT_ENDPOINT = "/api/v1/fee/predict"
    API_TIMEOUT = 30

    # App Configuration
    APP_TITLE = "Predictor de Entregas"
    APP_ICON = "📦"
    LAYOUT = "wide"

    # Default Values
    DEFAULT_CP = "05050"
    DEFAULT_SKU = "LIV-004"
    DEFAULT_QUANTITY = 3

    # Paleta de colores contrastante y armoniosa
    PRIMARY_COLOR = "#2D5016"  # Verde Bosque Oscuro
    SECONDARY_COLOR = "#8B4513"  # Marrón Chocolate
    SUCCESS_COLOR = "#1B4332"  # Verde Oscuro
    WARNING_COLOR = "#6D4C41"  # Marrón Medio
    DANGER_COLOR = "#4A148C"  # Púrpura Profundo
    ACCENT_COLOR = "#BF360C"  # Rojo Ladrillo
    TEXT_COLOR = "#2D5016"  # Verde Bosque para texto

    # Chart Configuration
    CHART_HEIGHT = "500px"
    METRICS_CHART_HEIGHT = "400px"