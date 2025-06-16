import streamlit as st
import sys
from pathlib import Path

current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from components.layout import setup_page_config, load_custom_css
from components.forms import render_prediction_form
from components.charts import render_results_dashboard
from utils.helpers import init_session_state

"""
@Autor: Iván Martínez Trejo
contacto: imartinezt@liverpool.com.mx
Front end - FEE
"""
def main():
    setup_page_config()
    load_custom_css()
    init_session_state()

    if st.session_state.show_results and st.session_state.prediction_data:
        render_results_dashboard()
    else:
        render_prediction_form()


if __name__ == "__main__":
    main()