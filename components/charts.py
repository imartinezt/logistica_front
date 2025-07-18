import streamlit as st
from datetime import datetime
from components.layout import render_header, render_back_button
from services.api_client import APIClient
from utils.helpers import format_currency, format_datetime, get_delivery_status_badge


def render_results_dashboard():
    """Dashboard de resultados simplificado"""
    data = st.session_state.prediction_data
    original_request = st.session_state.get('original_request', {})

    render_back_button()
    render_header("📊 Resultados de Predicción", "Análisis de entrega")


    es_recalculo = data.get('es_recalculo', False)

    if es_recalculo:
        tab1, tab2 = st.tabs(["📊 Resultado Principal", "🔄 Resultado de Recálculo"])

        with tab1:
            st.info("📋 **Resultados principales del análisis**")
            render_main_results(data, original_request)

        with tab2:
            st.success("🔄 **Resultados del recálculo ejecutado**")
            render_recalculo_comparison(data)
            render_main_results(data, original_request)
    else:
        render_main_results(data, original_request)
    render_recalculate_section(data, original_request)


def render_main_results(data: dict, original_request: dict):
    """Renderizar los resultados principales"""
    render_delivery_summary(data, original_request)
    render_context_info(data)
    render_alternatives_table(data)


def render_recalculo_comparison(data: dict):
    """Mostrar comparación del recálculo"""
    st.markdown("### 🔄 Comparación del Recálculo")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "📅 Fecha Original",
            format_datetime(data.get('fecha_entrega_original', 'N/A')),
            help="Fecha de entrega de la predicción original"
        )

    with col2:
        st.metric(
            "🎯 Fecha Nueva",
            format_datetime(data.get('fecha_entrega', 'N/A')),
            help="Nueva fecha de entrega después del recálculo"
        )

    with col3:
        dias_diff = data.get('dias_diferencia', 'N/A')
        delta_color = "normal"
        if isinstance(dias_diff, (int, float)):
            delta_color = "inverse" if dias_diff > 0 else "normal"

        st.metric(
            "📊 Diferencia",
            f"{dias_diff} días" if dias_diff != 'N/A' else 'N/A',
            delta=f"{dias_diff} días" if isinstance(dias_diff, (int, float)) else None,
            delta_color=delta_color
        )
    st.markdown("**📋 Detalles del Recálculo:**")

    col1, col2 = st.columns(2)

    with col1:
        fecha_promesa_mantenida = data.get('fecha_promesa_mantenida', False)
        status_promesa = "✅ Mantenida" if fecha_promesa_mantenida else "❌ No mantenida"
        st.info(f"**Fecha Promesa:** {status_promesa}")

        costo_diff = data.get('costo_diferencia', 0)
        st.info(f"**Diferencia de Costo:** {format_currency(costo_diff)}")

    with col2:
        tienda_rechazada = data.get('tienda_rechazada', 'N/A')
        st.info(f"**Tienda Rechazada:** {tienda_rechazada}")

        rutas_descartadas = data.get('rutas_descartadas', [])
        rutas_text = ', '.join(rutas_descartadas) if rutas_descartadas else 'Ninguna'
        st.info(f"**Rutas Descartadas:** {rutas_text}")

    st.markdown("---")


def render_delivery_summary(data: dict, original_request: dict):
    """Resumen principal de la entrega"""
    st.subheader("🎯 Resumen de Entrega")

    fecha_compra = original_request.get('fecha_compra', '')
    fecha_entrega = data.get('fecha_entrega', '')
    try:
        if fecha_compra and fecha_entrega:
            fecha_compra_dt = datetime.fromisoformat(fecha_compra.replace('Z', '+00:00'))
            fecha_entrega_dt = datetime.fromisoformat(fecha_entrega.replace('Z', '+00:00'))
            dias_diferencia = (fecha_entrega_dt - fecha_compra_dt).days
        else:
            dias_diferencia = data.get('dias', 0)
    except:
        dias_diferencia = data.get('dias', 0)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📅 Fecha Compra", format_datetime(fecha_compra))
        st.metric("🎯 Fecha Entrega", format_datetime(fecha_entrega))

    with col2:
        st.metric("⏰ Días para Entrega", f"{dias_diferencia} días")
        tipo_entrega = data.get('tipo_entrega', {})
        ventana = tipo_entrega.get('ventana_tiempo', 'N/A')
        st.metric("🕐 Ventana Horaria", ventana)

    with col3:
        st.metric("💰 Costo Total", format_currency(data.get('costo', 0)))
        st.metric("🏪 Tienda Asignada", data.get('tienda', 'N/A'))

    with col4:
        metodo = data.get('metodo', 'N/A')
        st.markdown("**🚚 Método de Entrega**")
        st.markdown(get_delivery_status_badge(metodo), unsafe_allow_html=True)
        st.metric("📊 Score", f"{data.get('score', 0):.3f}")

    tipo_entrega = data.get('tipo_entrega', {})
    if tipo_entrega:
        st.info(
            f"**{tipo_entrega.get('icono', '')} {tipo_entrega.get('nombre', 'N/A')}** - {tipo_entrega.get('descripcion', 'N/A')}")

    es_split = data.get('es_split', False)
    if es_split:
        split_info = data.get('split_info', {})
        if split_info:
            st.warning(f"""
            **📦 ENTREGA DIVIDIDA (SPLIT)**
            - **Rutas Seleccionadas:** {split_info.get('rutas_seleccionadas', 'N/A')}
            - **Cantidad Total:** {split_info.get('cantidad_total', 'N/A')}
            - **Costo Total:** {format_currency(split_info.get('costo_total', 0))}
            - **Tiempo Total:** {split_info.get('tiempo_total', 'N/A')} días
            - **Algoritmo:** {split_info.get('algoritmo_optimizacion', 'N/A')}
            """)

            detalle_rutas = split_info.get('detalle_rutas', [])
            if detalle_rutas:
                st.markdown("**🔄 Detalles de Rutas del Split:**")
                split_html = """
                <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
                    <tr style="background-color: #e3f2fd;">
                        <th style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">Ruta</th>
                        <th style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">ID Trazo</th>
                        <th style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">Tienda</th>
                        <th style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">Cantidad</th>
                        <th style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">Días</th>
                        <th style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">Costo</th>
                        <th style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">Score</th>
                    </tr>
                """

                for i, ruta in enumerate(detalle_rutas):
                    split_html += f"""
                    <tr>
                        <td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">Ruta {i + 1}</td>
                        <td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">{ruta.get('id_trazo', 'N/A')}</td>
                        <td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">{ruta.get('tienda', 'N/A')}</td>
                        <td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">{ruta.get('cantidad', 'N/A')}</td>
                        <td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">{ruta.get('dias', 'N/A')}</td>
                        <td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">{format_currency(ruta.get('costo_total_ruta', 0))}</td>
                        <td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">{ruta.get('score', 0):.3f}</td>
                    </tr>
                    """

                split_html += "</table>"
                st.markdown(split_html, unsafe_allow_html=True)


def render_context_info(data: dict):
    """Información contextual"""
    st.subheader("🗺️ Información Contextual")

    geo_context = data.get('contexto_geografico', {})
    clima_context = data.get('contexto_climatico', {})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📍 Información Geográfica**")
        geo_html = """
        <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
            <tr style="background-color: #e3f2fd;">
                <th style="padding: 8px; border: 1px solid #dee2e6; text-align: left;">Campo</th>
                <th style="padding: 8px; border: 1px solid #dee2e6; text-align: left;">Valor</th>
            </tr>
        """

        geo_data = [
            ("Código Postal", geo_context.get('rango_cp', 'N/A')),
            ("Estado/Alcaldía", geo_context.get('estado_alcaldia', 'N/A')),
            ("Zona de Seguridad", geo_context.get('zona_seguridad', 'N/A')),
            ("Tipo de Zona", geo_context.get('tipo_zona', 'N/A')),
            ("Cobertura Liverpool", "✅ Sí" if geo_context.get('cobertura_liverpool', False) else "❌ No"),
            ("Tiempo Base", geo_context.get('tiempo_entrega_base_horas', 'N/A'))
        ]

        for campo, valor in geo_data:
            geo_html += f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #dee2e6;">{campo}</td>
                <td style="padding: 8px; border: 1px solid #dee2e6;">{valor}</td>
            </tr>
            """

        geo_html += "</table>"
        st.markdown(geo_html, unsafe_allow_html=True)

        if geo_context.get('observaciones'):
            st.info(f"**Observaciones:** {geo_context.get('observaciones')}")

    with col2:
        st.markdown("**🌤️ Información Climática**")
        clima_html = """
        <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
            <tr style="background-color: #e3f2fd;">
                <th style="padding: 8px; border: 1px solid #dee2e6; text-align: left;">Campo</th>
                <th style="padding: 8px; border: 1px solid #dee2e6; text-align: left;">Valor</th>
            </tr>
        """

        clima_data = [
            ("Región", clima_context.get('region_nombre', 'N/A')),
            ("Estado Principal", clima_context.get('estado_principal', 'N/A')),
            ("Clima Actual", clima_context.get('clima_actual', 'N/A')),
            ("Temperatura",
             f"{clima_context.get('temperatura_min', 'N/A')}°C - {clima_context.get('temperatura_max', 'N/A')}°C"),
            ("Altitud", f"{clima_context.get('altitud_msnm', 'N/A')} msnm"),
            ("Precipitación", f"{clima_context.get('precipitacion_anual', 'N/A')} mm")
        ]

        for campo, valor in clima_data:
            clima_html += f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #dee2e6;">{campo}</td>
                <td style="padding: 8px; border: 1px solid #dee2e6;">{valor}</td>
            </tr>
            """

        clima_html += "</table>"
        st.markdown(clima_html, unsafe_allow_html=True)

        if clima_context.get('factores_especiales'):
            st.info(f"**Factores Especiales:** {clima_context.get('factores_especiales')}")


def render_alternatives_table(data: dict):
    """Tabla de alternativas"""
    st.subheader("📋 Alternativas Evaluadas")

    alternativas = data.get('alternativas', [])

    if alternativas:
        for i, alt in enumerate(alternativas):
            is_selected = alt.get('selected', False)

            if is_selected:
                st.success(f"""
                **🏆 SELECCIONADA - Rank {alt.get('rank', 'N/A')}**
                - **ID Trazo:** {alt.get('id', 'N/A')}
                - **Tienda:** {alt.get('tienda', 'N/A')}
                - **Método:** {alt.get('metodo', 'N/A')}
                - **Días:** {alt.get('dias', 'N/A')}
                - **Costo:** {format_currency(alt.get('costo', 0))}
                - **Inventario:** {alt.get('inventario', 'N/A')}
                - **Score:** {alt.get('score', 0):.3f}
                """)
            else:
                st.info(f"""
                **Rank {alt.get('rank', 'N/A')}**
                - **ID Trazo:** {alt.get('id', 'N/A')}
                - **Tienda:** {alt.get('tienda', 'N/A')}
                - **Método:** {alt.get('metodo', 'N/A')}
                - **Días:** {alt.get('dias', 'N/A')}
                - **Costo:** {format_currency(alt.get('costo', 0))}
                - **Inventario:** {alt.get('inventario', 'N/A')}
                - **Score:** {alt.get('score', 0):.3f}
                """)

        total_opciones = len(alternativas)
        seleccionadas = sum(1 for alt in alternativas if alt.get('selected', False))

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total Opciones", total_opciones)
        with col2:
            st.metric("✅ Seleccionadas", seleccionadas)
        with col3:
            tiempo_proceso = data.get('tiempo_proceso_ms', 0)
            st.metric("⏱️ Tiempo Proceso", f"{tiempo_proceso:.2f} ms")

        st.markdown("**📋 Información Adicional:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📦 Inventario Total", data.get('inventario_total_disponible', 'N/A'))
        with col2:
            st.metric("🏪 Tiendas con Inventario", data.get('tiendas_con_inventario', 'N/A'))
        with col3:
            st.metric("🔢 Opciones Evaluadas", data.get('opciones_evaluadas', 'N/A'))

        pesos_aplicados = data.get('pesos_aplicados', {})
        if pesos_aplicados:
            st.markdown("**⚖️ Pesos Aplicados en el Algoritmo:**")
            pesos_html = """
            <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
                <tr style="background-color: #e3f2fd;">
                    <th style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">Factor</th>
                    <th style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">Peso (%)</th>
                </tr>
            """

            for factor, peso in pesos_aplicados.items():
                factor_nombre = factor.replace('_', ' ').title()
                peso_porcentaje = f"{peso * 100:.1f}%"
                pesos_html += f"""
                <tr>
                    <td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">{factor_nombre}</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">{peso_porcentaje}</td>
                </tr>
                """

            pesos_html += "</table>"
            st.markdown(pesos_html, unsafe_allow_html=True)
    else:
        st.info("No se encontraron alternativas")


def render_recalculate_section(data: dict, original_request: dict):
    """Sección de recálculo"""
    st.markdown("---")
    st.subheader("🔄 Recálculo de Entrega")

    fecha_entrega_promesa = data.get('fecha_entrega', '')
    tienda_rechazada = data.get('tienda', 0)
    alternativas = data.get('alternativas', [])
    rutas_seleccionadas = [alt.get('id', '') for alt in alternativas if alt.get('selected', False)]
    can_recalculate = bool(
        original_request.get('codigo_postal') and
        original_request.get('sku_id') and
        fecha_entrega_promesa and
        tienda_rechazada
    )

    if not can_recalculate:
        st.warning("⚠️ No se pueden realizar recálculos. Faltan datos del request original.")
        return

    with st.expander("⚙️ Configurar Recálculo", expanded=False):
        st.markdown("**Datos del recálculo (extraídos automáticamente):**")

        col1, col2 = st.columns(2)

        with col1:
            st.info(f"**Fecha Entrega Promesa:** {format_datetime(fecha_entrega_promesa)}")
            st.info(f"**Tienda a Rechazar:** {tienda_rechazada}")

        with col2:
            st.info(f"**Rutas a Rechazar:** {', '.join(rutas_seleccionadas) if rutas_seleccionadas else 'Ninguna'}")

            priorizar_fecha_promesa = st.checkbox(
                "Priorizar Fecha Promesa",
                value=False,
                help="Si está activado, priorizará mantener la fecha promesa original"
            )

    if st.checkbox("📋 Ver datos que se enviarán al API", value=False):
        request_data = {
            "codigo_postal": original_request.get('codigo_postal', ''),
            "sku_id": original_request.get('sku_id', ''),
            "cantidad": original_request.get('cantidad', 1),
            "fecha_compra_original": original_request.get('fecha_compra', ''),
            "fecha_entrega_promesa": fecha_entrega_promesa,
            "tienda_rechazada": tienda_rechazada,
            "temporada": original_request.get('temporada', 'TEMPORADA_BAJA'),
            "rutas_rechazadas": rutas_seleccionadas,
            "priorizar_fecha_promesa": st.session_state.get('priorizar_fecha_promesa', False)
        }
        st.json(request_data)

    if st.button("🔄 Ejecutar Recálculo", type="secondary", use_container_width=True):
        priorizar = st.session_state.get('priorizar_fecha_promesa', False)
        st.session_state.show_results = True

        execute_recalculation(data, original_request, priorizar, rutas_seleccionadas)


def execute_recalculation(data: dict, original_request: dict, priorizar_fecha_promesa: bool, rutas_rechazadas: list):
    """Ejecutar recálculo"""
    try:
        codigo_postal = original_request.get('codigo_postal', '')
        sku_id = original_request.get('sku_id', '')
        cantidad = original_request.get('cantidad', 1)
        fecha_compra_original = original_request.get('fecha_compra', '')
        temporada = original_request.get('temporada', 'TEMPORADA_BAJA')

        fecha_entrega_promesa = data.get('fecha_entrega', '')
        tienda_rechazada = data.get('tienda', 0)

        if not codigo_postal or not sku_id or not fecha_compra_original:
            st.error("❌ Faltan datos del request original para el recálculo")
            return

        if not fecha_entrega_promesa or not tienda_rechazada:
            st.error("❌ Faltan datos de la respuesta original para el recálculo")
            return

        result_placeholder = st.empty()

        with st.status("🔄 Ejecutando recálculo...", expanded=True) as status:
            st.write("🔍 Preparando datos del recálculo...")
            st.write(f"📍 CP: {codigo_postal} | SKU: {sku_id} | Cantidad: {cantidad}")
            st.write(f"🏪 Rechazando tienda: {tienda_rechazada}")
            st.write(f"🚫 Rechazando rutas: {', '.join(rutas_rechazadas) if rutas_rechazadas else 'Ninguna'}")

            api_client = APIClient()
            result, error = api_client.recalculate_delivery(
                codigo_postal=codigo_postal,
                sku_id=sku_id,
                cantidad=cantidad,
                fecha_compra_original=fecha_compra_original,
                fecha_entrega_promesa=fecha_entrega_promesa,
                tienda_rechazada=tienda_rechazada,
                temporada=temporada,
                rutas_rechazadas=rutas_rechazadas,
                priorizar_fecha_promesa=priorizar_fecha_promesa
            )

            if result:
                st.write("✅ Recálculo completado exitosamente")
                status.update(label="✅ Recálculo Completado", state="complete", expanded=False)

                st.session_state.prediction_data = result
                st.session_state.show_results = True

                with result_placeholder.container():
                    st.success("🎉 **Recálculo completado exitosamente!**")

                    if result.get('es_recalculo', False):
                        st.info(f"""
                        **📊 Resumen del Recálculo:**
                        - **Fecha entrega original:** {format_datetime(result.get('fecha_entrega_original', 'N/A'))}
                        - **Fecha entrega nueva:** {format_datetime(result.get('fecha_entrega', 'N/A'))}
                        - **Diferencia en días:** {result.get('dias_diferencia', 'N/A')}
                        - **Fecha promesa mantenida:** {'✅ Sí' if result.get('fecha_promesa_mantenida', False) else '❌ No'}
                        - **Diferencia de costo:** {format_currency(result.get('costo_diferencia', 0))}
                        """)

                    if st.button("🔄 Ver Resultados Completos en Pestañas", type="primary", key="refresh_results"):
                        st.rerun()

                    st.info(
                        "💡 **Tip:** Haz clic en el botón de arriba para ver los resultados completos organizados en pestañas.")

            else:
                st.write("❌ Error en el recálculo")
                status.update(label="❌ Error en Recálculo", state="error", expanded=False)

                with result_placeholder.container():
                    st.error(f"🚫 **Error en el recálculo:** {error}")

                    with st.expander("🔍 Detalles del Error", expanded=False):
                        st.write("**Datos enviados:**")
                        st.json({
                            "codigo_postal": codigo_postal,
                            "sku_id": sku_id,
                            "cantidad": cantidad,
                            "fecha_compra_original": fecha_compra_original,
                            "fecha_entrega_promesa": fecha_entrega_promesa,
                            "tienda_rechazada": tienda_rechazada,
                            "temporada": temporada,
                            "rutas_rechazadas": rutas_rechazadas,
                            "priorizar_fecha_promesa": priorizar_fecha_promesa
                        })
                        st.write(f"**Error recibido:** {error}")

    except Exception as e:
        st.error(f"❌ Error en recálculo: {str(e)}")
        st.write(f"**Detalles del error:** {str(e)}")