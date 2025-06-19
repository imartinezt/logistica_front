from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

import pandas as pd
import streamlit as st
import os

from typing import Dict
import plotly.express as px

def load_csv_data(base_path: str) -> Dict[str, pd.DataFrame]:
    """
    Busca todos los archivos .csv en el directorio base_path y los carga en un diccionario de DataFrames.

    Args:
        base_path (str): La ruta del directorio donde se buscarán los archivos .csv.

    Returns:
        Dict[str, pd.DataFrame]: Un diccionario donde las claves son los nombres de los archivos (sin extensión)
                                      y los valores son los DataFrames correspondientes.
    """

    dataframes = {}
    if not os.path.isdir(base_path):
        st.error(f"La ruta '{base_path}' no es un directorio válido.")
        return dataframes

    for filename in os.listdir(base_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(base_path, filename)
            df_name = os.path.splitext(filename)[0]  # Obtiene el nombre del archivo sin la extensión
            try:
                df = pd.read_csv(file_path)
                dataframes[df_name] = df
            except Exception as e:
                st.error(f"No se pudo cargar el archivo '{filename}': {e}")

    return dataframes


def select_dataframe(dataframe_dict: Dict[str, pd.DataFrame]):
    """
    Selecciona el dataframe a desplegar de una lista de dataframes y permite calcular métricas.

    Args:
        dataframe_dict Dict[str]: Diccionario que contiene la lista de dataframes a usar
    """

    if not dataframe_dict:
        st.warning("No se encontró ningún conjunto de datos para visualizar.")
        return pd.DataFrame()

    dataframes_names = dataframe_dict.keys()
    selected_name = st.selectbox("Seleccionar un conjunto de datos", dataframes_names)

    selected_df = dataframe_dict.get(selected_name)

    if selected_df is not None:

        return selected_df, selected_name

    # if selected_df is not None:
    #
    #     # Usamos pestañas para organizar la visualización y las métricas
    #     current_df, tab_insights = st.tabs([f"Visualizar información", "Análisis Estadístico"])
    #
    #     with current_df:
    #         st.subheader(f"🛒 DataFrame seleccionado: {selected_name}")
    #
    #     with tab_insights:
    #         render_dataframe_insights(selected_df, selected_name)
    #
    #     return selected_df

    else:
        st.warning("El DataFrame seleccionado no se encontró. Esto no debería ocurrir.")
        return pd.DataFrame()


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega la opción de filtrar la información del dataframe

    Args:
        df (pd.DataFrame): Dataframe original

    Returns:
        pd.DataFrame: Dataframe después de los filtros aplicados
    """

    # Transformar las columnas que contienen fechas en un formato standard (datetime)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col], format="%Y-%m-%d")
                df[col] = df[col].dt.date() # Conversión para que solo se considere la fecha (sin hora)
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Selecciona la columna para filtrar", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))

            # Variables catégoricas
            # if isinstance(df[column], pd.CategoricalDtype) or df[column].nunique() < 10:
            if isinstance(df[column], pd.CategoricalDtype): # TODO Verificar que las variables categoricas sean correctamente  parseadas
                user_cat_input = right.multiselect(
                    f"Valores para {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )

                df = df[df[column].isin(user_cat_input)]

            # Valores númericos
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Valores para {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]


            # Fechas
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Valores para {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date.normalize(), end_date.normalize())]
            else:
                # Búsqueda por texto
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input, case=False)] # TODO: Case sensitive

    return df


def get_dataframe_insights(df: pd.DataFrame, df_name: str) -> pd.DataFrame:
    """
    Agrega una capa de información sobre el DataFrame para calcular y mostrar métricas.

    Args:
        df (pd.DataFrame): El DataFrame sobre el cual calcular las métricas
        df_name (str): El nombre del DataFrame para referencia en el UI.
    """
    st.subheader(f"📈 Análisis de métricas para: {df_name}")

    if df.empty:
        st.info("El DataFrame está vacío. No se pueden calcular métricas.")
        return

    # Selección de columnas para analizar
    all_columns = df.columns.tolist()
    selected_columns = st.multiselect(
        "Selecciona las columnas para analizar",
        all_columns,
        default=all_columns[:min(1, len(all_columns))]
    )

    if not selected_columns:
        st.info("Por favor, selecciona al menos una columna para calcular métricas.")
        return

    # Definir métricas disponibles
    numeric_metrics_options = [
        "Media (Promedio)", "Mediana", "Moda", "Mínimo", "Máximo", "Conteo (No Nulos)", "Número de Valores Únicos",
    ]
    categorical_metrics_options = [
        "Moda", "Conteo (No Nulos)", "Número de Valores Únicos",
    ]

    # Selección de métricas
    st.markdown("---")
    st.write("**Métricas a calcular:**")
    col1, col2 = st.columns(2)
    with col1:
        selected_numeric_metrics = st.multiselect(
            "Métricas para columnas numéricas",
            numeric_metrics_options,
            default=["Conteo (No Nulos)", "Número de Valores Únicos"]
        )
    with col2:
        selected_categorical_metrics = st.multiselect(
            "Métricas para columnas categóricas/texto",
            categorical_metrics_options,
            default=["Conteo (No Nulos)", "Número de Valores Únicos"]
        )

    st.markdown("---")
    metrics_results = {}

    for col in selected_columns:

        metrics_results[col] = {}
        column_data = df[col]
        metrics_results[col]["Conteo (No Nulos)"] = column_data.count()

        if is_numeric_dtype(column_data):

            # 1. Calcular de MEDIA
            if "Media (Promedio)" in selected_numeric_metrics:
                mean_val = column_data.mean()
                metrics_results[col]["Media (Promedio)"] = f"{mean_val:.2f}"

            # 2. Calcular MEDIANA
            if "Mediana" in selected_numeric_metrics:
                median_val = column_data.median()
                metrics_results[col]["Mediana"] = f"{median_val:.2f}"

            # 3. Calcular MODA
            if "Moda" in selected_numeric_metrics:
                mode_val = column_data.mode()
                if not mode_val.empty:
                    # Función para formatear cada moda a 2 decimales
                    formatter = lambda x: f"{x:.2f}"
                    metrics_results[col]["Moda"] = ', '.join(mode_val.map(formatter))
                else:
                    metrics_results[col]["Moda"] = "N/A"

            if "Mínimo" in selected_numeric_metrics:
                min_val = column_data.min()
                metrics_results[col]["Mínimo"] = f"{min_val:.2f}"

            if "Máximo" in selected_numeric_metrics:
                max_val = column_data.max()
                metrics_results[col]["Máximo"] = f"{max_val:.2f}"

        elif is_object_dtype(column_data) or isinstance(column_data.dtype, pd.CategoricalDtype):
            if "Moda" in selected_categorical_metrics:
                mode_val = column_data.mode()
                metrics_results[col]["Moda"] = ', '.join(map(str, mode_val)) if not mode_val.empty else "N/A"
            if "Número de Valores Únicos" in selected_categorical_metrics:
                metrics_results[col]["Número de Valores Únicos"] = column_data.nunique()

        elif is_datetime64_any_dtype(column_data):
            if "Mínimo" in selected_numeric_metrics:
                metrics_results[col]["Fecha Más Temprana"] = column_data.min()
            if "Máximo" in selected_numeric_metrics:
                metrics_results[col]["Fecha Más Tardia"] = column_data.max()

    # Convertir los resultados a un DataFrame para una mejor visualización
    if not metrics_results:
        st.info("No se calcularon métricas con las selecciones actuales.")
        return

    metrics_df = pd.DataFrame.from_dict(metrics_results, orient='index')
    metrics_df.index.name = "Columna"

    # Reorganizar columnas
    general_cols = ["Conteo (No Nulos)"]
    other_cols = [col for col in metrics_df.columns if col not in general_cols]
    final_cols_order = general_cols + sorted(other_cols)
    metrics_df = metrics_df.reindex(columns=final_cols_order).T  # Transponer

    return metrics_df