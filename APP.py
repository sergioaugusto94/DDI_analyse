import streamlit as st
import pandas as pd
import base64
import os
import plot_function as pf

# Criar uma variável de estado que evita com que a função data_processing seja re executada
# Exportar a variável data processada 

#@st.cache
def data_processing(file):
	#--------Loading dataset-------
	data = pd.read_excel(file, sheet_name='Channel Info')

	#--------Variables-Units-Precision-------
	units = data.iloc[0,:]
	precision = data.iloc[1,:]
	variables = data.columns

      	#--------Removing Empty Rows and Defining Conditions that were ran-------
	data.dropna(inplace = True, subset = [data.columns[1]])
	data['Condition'] = data[['CL_dSpeed', 'CL_BMEP SI', 'CL_Throttle', 
                                'n VVT_ICL1_DIAL_CL_VAL', 
                                'n DL_SPK_ADV', 
                                'n VVL_STATE_ACT']].astype(str).agg('_'.join, axis=1)

      	#-----Defining the date that the test were ran--------------
	data['Date'] = (data['TimeStamp'].str.slice(start=20) + 
                      data['TimeStamp'].str.slice(start=3, stop=10) + 
                      data['TimeStamp'].str.slice(start=10, stop=19))

	data['Date'] = pd.to_datetime(data['Date'], format='%Y %b %d %H:%M:%S')
	
	return data


@st.cache(allow_output_mutation=True)
def button_states():
	return {"pressed": False}


st.title("DDI Analysis")

st.sidebar.markdown('To use the app, click on button below to ' + 
                    'upload your DDI database.')

file = st.sidebar.file_uploader("# Upload the data", type=['xlsx'])

if 'run_num' not in st.session_state:
	st.session_state.run_num = 0

if file is not None:
	#if st.session_state.run_num == 0:
	data = data_processing(file)

	#-----Creating different dataframes for each engine operation-------
	points = data['Condition'].unique()

	for x in range(1, 1 + len(data.groupby('Condition').count().iloc[:, 1])):
		globals()['df%s' % x] = data.where(data['Condition'] == 
						points[x-1]).dropna(subset=['File Name'])
		
	st.markdown('This is the loaded data')
	st.dataframe(data)
		
	#-----Drop down list for each variable-------
	form1 = st.form(key='Options')
	
	option = form1.selectbox(
	'How would you like to be contacted?',
	('BSFC SI', 'BMEP SI', 'n VVL_STATE_ACT'))
	#------------

	option2 = form1.selectbox(
	'How would you like to be contacted?',
		('df1', 'df2', 'df3', 'df4', 'df5'))

	dic = {'df1': df1, 'df2': df2, 'df3': df3, 'df4': df4, 'df5': df5}

	df_plot = dic[option2]
	var = option
	
	plot_button = form1.form_submit_button('Plot')
	plot_state = button_states()
        
	
	#if plot_button:
		#plot_state.update({'pressed': True})

	#if plot_state['pressed']:
	if plot_button:
		st.session_state.run_num = 1
		fig = pf.plot(df_plot, var)
		st.plotly_chart(fig)


    
