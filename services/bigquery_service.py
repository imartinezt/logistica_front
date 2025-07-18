class BigQueryDirectService:
    """🔍 Servicio para consultas directas a BigQuery usando Application Default Credentials"""

    def __init__(self, project_id: str, dataset_id: str, table_id: str):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id

        try:
            self.client = bigquery.Client(project=project_id)
            logger.info(f"🔍 BigQuery Direct Service inicializado para {project_id}.{dataset_id}.{table_id}")
            logger.info("✅ Usando Application Default Credentials (gcloud auth)")
        except Exception as e:
            logger.error(f"❌ Error inicializando BigQuery client: {e}")
            logger.error("💡 Ejecuta: gcloud auth application-default login")
            raise

    async def query_direct_fee_options(self, sku_cve: int, cp: int) -> List[Dict[str, Any]]:
        """
        🎯 Query directa a BigQuery - exactamente igual que la competencia

        Args:
            sku_cve: SKU del producto
            cp: Código postal

        Returns:
            Lista de registros de BigQuery
        """

        logger.info(f"🔍 Ejecutando query directa BigQuery para SKU={sku_cve}, CP={cp}")
        query = f"""
            SELECT 
                ID_TRAZO,
                SKU_CVE,
                CP,
                TIPO,
                MET_ENTREGA,
                TDA_CVE,
                INVENTARIO_OH,
                ASIGNACIONES_TDA,
                CAPACIDAD_TDA,
                REAL_CAP_STORE,
                CAPACIDAD_ME,
                DESC_FRECUENCIA,
                TIEMPO,
                TIEMPO_2,
                TIEMPO_3,
                COSTO,
                ZONA_ROJA,
                TRAFICO,
                DESASTRE_NATURAL,
                EXCL_PROD,
                TUBERIA
            FROM `{self.project_id}.{self.dataset_id}.{self.table_id}`
            WHERE 1=1
                AND SKU_CVE = {sku_cve}
                AND CP = {cp}
                AND NOT (MET_ENTREGA = 'FLOTA LIVERPOOL' AND ZONA_ROJA = 1)
                AND NOT (MET_ENTREGA = 'MENSAJERIA EXTERNA' AND EXCL_PROD != 0)
                AND INVENTARIO_OH > 0
            ORDER BY TIEMPO_3 ASC, COSTO ASC
        """

        try:
            loop = asyncio.get_event_loop()
            query_job = await loop.run_in_executor(None, self.client.query, query)
            results = await loop.run_in_executor(None, lambda: list(query_job.result()))
            records = []
            for row in results:
                record = dict(row)
                records.append(record)

            logger.info(f"✅ BigQuery devolvió {len(records)} registros")
            return records

        except Exception as e:
            logger.error(f"❌ Error en query BigQuery: {e}")
            raise