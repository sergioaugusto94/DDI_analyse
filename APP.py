pip install openpyxl

import streamlit as st
import pandas as pd
import base64
import os

st.title("DDI Analysis")

st.sidebar.markdown('To use the app, click on button below to ' + 
                    'upload your DDI database.')

file = st.sidebar.file_uploader("# Upload the data", type=['xlsx'])

@st.cache(allow_output_mutation=True)
def button_states():
    return {"pressed": False}

if file is not None:
    data = pd.read_excel(file)
    st.dataframe(data)
    st.markdown('This is the loaded data')
    run_button = st.button('Plot')
    run_state = button_states()

    
