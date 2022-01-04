import streamlit as st
import pandas as pd
import base64
import os

st.title("DDI Analysis")

st.sidebar.markdown('To use the app, click on button below to ' + 
                    'upload your DDI database.')

file = st.sidebar.file_uploader("# Upload the data", type=['xlsx'])
