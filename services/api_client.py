import requests
import streamlit as st
from config.settings import Config
from google.cloud import bigquery


class APIClient:
    def __init__(self):
        self.base_url = Config.API_BASE_URL
        self.timeout = Config.API_TIMEOUT

    def predict_delivery(self, codigo_postal: str, sku_id: str, cantidad: int, temporada: str, fecha_compra: str):
        """
        Realizar predicción de entrega
        """
        url = f"{self.base_url}{Config.API_PREDICT_ENDPOINT}"
        payload = {
            "codigo_postal": codigo_postal,
            "sku_id": sku_id,
            "cantidad": cantidad,
            "temporada": temporada,
            "fecha_compra": fecha_compra
        }

        try:
            with st.spinner("🔮 Procesando predicción..."):
                response = requests.post(url, json=payload, timeout=self.timeout)

                if response.status_code == 200:
                    return response.json(), None
                else:
                    error_msg = f"Error {response.status_code}: {response.text}"
                    return None, error_msg

        except requests.exceptions.Timeout:
            return None, "⏰ Tiempo de espera agotado. El servidor tardó demasiado en responder."
        except requests.exceptions.ConnectionError:
            return None, "🔌 Error de conexión. Verifique que el servidor esté disponible."
        except requests.exceptions.RequestException as e:
            return None, f"🚫 Error de solicitud: {str(e)}"
        except Exception as e:
            return None, f"❌ Error inesperado: {str(e)}"


    def recalculate_delivery(self, codigo_postal: str, sku_id: str, cantidad: int,
                             fecha_compra_original: str, fecha_entrega_promesa: str,
                             tienda_rechazada: int, temporada: str, rutas_rechazadas: list,
                             priorizar_fecha_promesa: bool):
        """
        Realizar el recálculo de entrega cuando una tienda es rechazada
        """
        url = f"{self.base_url}{Config.API_RECALCULATE_ENDPOINT}"
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
            with st.spinner("🔮 Realizando el recalculo para la Fecha promesa de entrega..."):
                response = requests.post(url, json=payload, timeout=self.timeout)

                if response.status_code == 200:
                    return response.json(), None
                else:
                    error_msg = f"Error {response.status_code}: {response.text}"
                    return None, error_msg

        except requests.exceptions.Timeout:
            return None, "⏰ Tiempo de espera agotado. El servidor tardó demasiado en responder."
        except requests.exceptions.ConnectionError:
            return None, "🔌 Error de conexión. Verifique que el servidor esté disponible."
        except requests.exceptions.RequestException as e:
            return None, f"🚫 Error de solicitud: {str(e)}"
        except Exception as e:
            return None, f"❌ Error inesperado: {str(e)}"