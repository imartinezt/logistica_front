import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuración centralizada de la aplicación"""

    # === API Configuration ===
    API_BASE_URL = "https://dev-fee-back-img-209565165407.us-central1.run.app"
    API_PREDICT_ENDPOINT = "/api/v1/fee/predict"
    API_RECALCULATE_ENDPOINT = "/api/v1/fee/recalculate"
    API_TIMEOUT = 30

    # === App Configuration ===
    APP_TITLE = "Fecha de Entrega Estimada"
    APP_ICON = "📦"
    LAYOUT = "wide"

    # === Form Defaults ===
    DEFAULT_CP = "52715"
    DEFAULT_SKU = "1139002876"
    DEFAULT_QUANTITY = 1
    DEFAULT_TEMPORADA = "TEMPORADA_ALTA"

    # === Validation Rules ===
    MIN_CP_LENGTH = 5
    MIN_SKU_LENGTH = 3
    MAX_QUANTITY = 100

    # === Business Constants ===
    TEMPORADAS = ["TEMPORADA_ALTA", "TEMPORADA_BAJA"]

    # === BigQuery Configuration ===
    SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT", "").replace("\r", "")
    PROJECT_ID = os.getenv("PROJECT_ID", "").replace("\r", "")
    DATASET_ID = os.getenv("DATASET_ID", "").replace("\r", "")
    TABLE_ID = os.getenv("TABLE_ID", "").replace("\r", "")