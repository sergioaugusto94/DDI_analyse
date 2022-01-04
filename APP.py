import streamlit as st
import pandas as pd
import base64
import os

st.title("DDI Analysis")

st.sidebar.markdown('To use the app, click on button below to ' + 
                    'upload your DDI database.')

file = st.sidebar.file_uploader("# Upload the data", type=['xlsx'])


#-----Display the dataset-------
@st.cache(allow_output_mutation=True)
def button_states():
    return {"pressed": False}

if file is not None:
    #--------Loading dataset-------
    data = pd.read_excel(file, sheet_name='Channel Info')
    #---------------

    #--------Variables-Units-Precision-------
    units = data.iloc[0,:]
    precision = data.iloc[1,:]
    variables = data.columns
    #---------------------------

    #--------Removing Empty Rows and Defining Conditions that were ran-------
    data.dropna(inplace = True, subset = [data.columns[1]])
    data['Condition'] = data[['CL_dSpeed', 'CL_BMEP SI', 'CL_Throttle', 
                              'n VVT_ICL1_DIAL_CL_VAL', 
                              'n DL_SPK_ADV', 
                              'n VVL_STATE_ACT']].astype(str).agg('_'.join, axis=1)
    #---------------------------

    #-----Defining the date that the test were ran--------------
    data['Date'] = (data['TimeStamp'].str.slice(start=20) + 
                    data['TimeStamp'].str.slice(start=3, stop=10) + 
                    data['TimeStamp'].str.slice(start=10, stop=19))

    data['Date'] = pd.to_datetime(data['Date'], format='%Y %b %d %H:%M:%S')
    #---------------------------
    
    st.dataframe(data)
    st.markdown('This is the loaded data')
    plot_button = st.button('Plot')
    plot_state = button_states()
    

    #-----Creating different dataframes for each engine operation-------
    points = data['Condition'].unique()

    for x in range(1, 1 + len(data.groupby('Condition').count().iloc[:, 1])):
        globals()['df%s' % x] = data.where(data['Condition'] == 
                                           points[x-1]).dropna(subset=['File Name'])
    #---------------------------


    
