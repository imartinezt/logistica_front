class Config:
    # API Configuration
    API_BASE_URL = "http://0.0.0.0:8000"
    API_PREDICT_ENDPOINT = "/api/v1/fee/predict"
    API_TIMEOUT = 30

    # App Configuration
    APP_TITLE = "Logistics Intelligence Platform"
    APP_ICON = "📊"
    LAYOUT = "wide"

    # Defaults
    DEFAULT_CP = ""
    DEFAULT_SKU = ""
    DEFAULT_QUANTITY = 1

    # Executive Color Palette
    PRIMARY_COLOR = "#1e40af"  # Corporate Blue
    SECONDARY_COLOR = "#0f172a"  # Deep Navy
    ACCENT_COLOR = "#3b82f6"  # Bright Blue
    SUCCESS_COLOR = "#10b981"  # Professional Green
    WARNING_COLOR = "#f59e0b"  # Executive Amber
    ERROR_COLOR = "#ef4444"  # Corporate Red
    INFO_COLOR = "#0ea5e9"  # Sky Blue

    # Text Colors
    TEXT_PRIMARY = "#1e293b"  # Charcoal
    TEXT_SECONDARY = "#64748b"  # Medium Gray
    TEXT_LIGHT = "#94a3b8"  # Light Gray

    # Background Colors
    BG_PRIMARY = "#ffffff"  # Pure White
    BG_SECONDARY = "#f8fafc"  # Very Light Gray
    BG_CARD = "#ffffff"  # Card White

    # Border Colors
    BORDER_COLOR = "#e2e8f0"  # Subtle Border
    BORDER_ACCENT = "#cbd5e1"  # Accent Border

    # Component Settings
    CHART_HEIGHT = "500px"
    METRICS_CHART_HEIGHT = "400px"
    MIN_CP_LENGTH = 5
    MIN_SKU_LENGTH = 3
    MAX_QUANTITY = 100

    # Graph Node Colors - Executive Palette
    GRAPH_COLORS = {
        "destination": "#1e40af",  # Primary Blue for destination
        "product": "#0ea5e9",  # Sky Blue for products
        "store_with_stock": "#10b981",  # Green for available inventory
        "store_no_stock": "#94a3b8",  # Light Gray for no stock
        "cedis": "#6366f1",  # Indigo for distribution centers
        "fleet_internal": "#3b82f6",  # Blue for internal fleet
        "fleet_external": "#8b5cf6",  # Purple for external fleet
        "factors": "#f59e0b",  # Amber for external factors
        "alternatives": "#64748b"  # Medium Gray for alternatives
    }

    # Chart Settings
    CHART_CONFIG = {
        "font_family": "Inter, system-ui, sans-serif",
        "title_size": 18,
        "label_size": 12,
        "legend_size": 11,
        "animation_duration": 800,
        "shadow_color": "rgba(0, 0, 0, 0.1)"
    }