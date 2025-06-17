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
                # st.success(f"CSV '{filename}' cargado como '{df_name}'.")
            except Exception as e:
                st.error(f"No se pudo cargar el archivo '{filename}': {e}")

    return dataframes

def select_dataframe(dataframe_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Selecciona el dataframe a desplegar de una lista de dataframes

    Args:
        dataframe_dict Dict[str]: Diccionario que contiene la lista de dataframes a usar
    """

    if not dataframe_dict:

        st.warning("No se encontró ningun conjunto de datos para visualizar")

        return pd.DataFrame()

    # Obtenemos los dataframes disponibles
    dataframes_names = dataframe_dict.keys()

    # Seleccionamos un dataframe
    selected_name = st.selectbox("Seleccionar una lista de datos", dataframes_names)

    selected_df = dataframe_dict.get(selected_name)

    if selected_df is not None:
        st.subheader(f"💾 Datos del DataFrame: {selected_name}")

        filtered_df = filter_dataframe(selected_df)

        st.subheader(f"🛒 DataFrame Filtrado: {selected_name}")
        return filtered_df
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

    modify = st.checkbox("Añadir filtros")

    if not modify:
        return df

    df = df.copy()

    # Transformar las columnas que contienen fechas en un formato standard (datetime)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
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
            if isinstance(df[column], pd.CategoricalDtype) or df[column].nunique() < 10:
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
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df