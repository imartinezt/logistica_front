import requests

from config.settings import Config


class APIClient:
    def __init__(self):
        self.base_url = Config.API_BASE_URL
        self.timeout = Config.API_TIMEOUT

    def predict_delivery(self, codigo_postal: str, sku_id: str, cantidad: int, temporada: str, fecha_compra: str):
        """Realizar predicción de entrega"""
        url = f"{self.base_url}/api/v1/fee/predict"
        payload = {
            "codigo_postal": codigo_postal,
            "sku_id": sku_id,
            "cantidad": cantidad,
            "temporada": temporada,
            "fecha_compra": fecha_compra
        }

        try:
            response = requests.post(url, json=payload, timeout=self.timeout)

            if response.status_code == 200:
                return response.json(), None
            else:
                error_msg = f"Error {response.status_code}: {response.text}"
                return None, error_msg

        except requests.exceptions.Timeout:
            return None, "⏰ Tiempo de espera agotado"
        except requests.exceptions.ConnectionError:
            return None, "🔌 Error de conexión"
        except requests.exceptions.RequestException as e:
            return None, f"🚫 Error de solicitud: {str(e)}"
        except Exception as e:
            return None, f"❌ Error inesperado: {str(e)}"

    def recalculate_delivery(self, codigo_postal: str, sku_id: str, cantidad: int,
                             fecha_compra_original: str, fecha_entrega_promesa: str,
                             tienda_rechazada: int, temporada: str, rutas_rechazadas: list,
                             priorizar_fecha_promesa: bool):
        """Recalcular entrega"""
        url = f"{self.base_url}/api/v1/fee/recalculate"
        payload = {
            "codigo_postal": codigo_postal,
            "sku_id": sku_id,
            "cantidad": cantidad,
            "fecha_compra_original": fecha_compra_original,
            "fecha_entrega_promesa": fecha_entrega_promesa,
            "tienda_rechazada": tienda_rechazada,
            "temporada": temporada,
            "rutas_rechazadas": rutas_rechazadas,
            "priorizar_fecha_promesa": priorizar_fecha_promesa
        }

        try:
            response = requests.post(url, json=payload, timeout=self.timeout)

            if response.status_code == 200:
                return response.json(), None
            else:
                error_msg = f"Error {response.status_code}: {response.text}"
                return None, error_msg

        except requests.exceptions.Timeout:
            return None, "⏰ Tiempo de espera agotado"
        except requests.exceptions.ConnectionError:
            return None, "🔌 Error de conexión"
        except requests.exceptions.RequestException as e:
            return None, f"🚫 Error de solicitud: {str(e)}"
        except Exception as e:
            return None, f"❌ Error inesperado: {str(e)}"