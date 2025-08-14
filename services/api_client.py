import requests
from config.settings import Config


class APIClient:
    """Cliente para interactuar con la API de predicción de entregas"""

    def __init__(self):
        self.base_url = Config.API_BASE_URL
        self.timeout = Config.API_TIMEOUT

    def predict_delivery(self, codigo_postal: str, sku_id: str, cantidad: int, temporada: str, fecha_compra: str):
        """
        Realizar predicción de entrega

        Args:
            codigo_postal (str): Código postal de destino
            sku_id (str): ID del SKU
            cantidad (int): Cantidad de productos
            temporada (str): Temporada comercial
            fecha_compra (str): Fecha de compra en formato ISO

        Returns:
            tuple: (result_data, error_message)
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
                             tienda_rechazada: int, tipo_impacto: str, permitir_split: bool = True):
        """
        Realizar recálculo de entrega cuando una tienda es rechazada

        FORMATO ACTUALIZADO - Nuevo API

        Args:
            codigo_postal (str): Código postal de destino
            sku_id (str): ID del SKU
            cantidad (int): Cantidad de productos
            fecha_compra_original (str): Fecha de compra original
            fecha_entrega_promesa (str): Fecha promesa de entrega original
            tienda_rechazada (int): ID de tienda rechazada
            tipo_impacto (str): Tipo de impacto ("BAJA", "MEDIANA", "ALTA")
            permitir_split (bool): Permitir división en múltiples tiendas

        Returns:
            tuple: (result_data, error_message)
        """
        url = f"{self.base_url}{Config.API_RECALCULATE_ENDPOINT}"
        payload = {
            "codigo_postal": codigo_postal,
            "sku_id": sku_id,
            "cantidad": cantidad,
            "fecha_compra_original": fecha_compra_original,
            "fecha_entrega_promesa": fecha_entrega_promesa,
            "tienda_rechazada": tienda_rechazada,
            "tipo_impacto": tipo_impacto,
            "permitir_split": permitir_split
        }

        try:
            response = requests.post(url, json=payload, timeout=self.timeout)

            if response.status_code == 200:
                return response.json(), None
            else:
                # Intentar obtener más detalles del error
                try:
                    error_detail = response.json()
                    error_msg = error_detail.get('detail', response.text)
                except:
                    error_msg = response.text

                return None, f"Error {response.status_code}: {error_msg}"

        except requests.exceptions.Timeout:
            return None, "⏰ Tiempo de espera agotado. El servidor tardó demasiado en responder."
        except requests.exceptions.ConnectionError:
            return None, "🔌 Error de conexión. Verifique que el servidor esté disponible."
        except requests.exceptions.RequestException as e:
            return None, f"🚫 Error de solicitud: {str(e)}"
        except Exception as e:
            return None, f"❌ Error inesperado: {str(e)}"

    # MÉTODO LEGACY - mantener por compatibilidad si es necesario
    def recalculate_delivery_legacy(self, codigo_postal: str, sku_id: str, cantidad: int,
                                    fecha_compra_original: str, fecha_entrega_promesa: str,
                                    tienda_rechazada: int, temporada: str, rutas_rechazadas: list,
                                    priorizar_fecha_promesa: bool, permitir_split: bool = True):
        """
        Método legacy para recálculo (formato anterior)
        Mantener solo si hay endpoints que aún usan el formato anterior
        """
        url = f"{self.base_url}/api/v1/fee/recalculate-legacy"  # endpoint legacy
        payload = {
            "codigo_postal": codigo_postal,
            "sku_id": sku_id,
            "cantidad": cantidad,
            "fecha_compra_original": fecha_compra_original,
            "fecha_entrega_promesa": fecha_entrega_promesa,
            "tienda_rechazada": tienda_rechazada,
            "temporada": temporada,
            "rutas_rechazadas": rutas_rechazadas,
            "priorizar_fecha_promesa": priorizar_fecha_promesa,
            "permitir_split": permitir_split
        }

        try:
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