import streamlit as st
import pandas as pd
import base64
import os
import plot_function as pf


#Plotar mais de uma variável no gráfico 
#Plotar mais de um gráfico

@st.cache
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


if 'run_num' not in st.session_state:
	st.session_state.run_num = 0
if 'data_save' not in st.session_state:
	st.session_state.data_save = 0
if 'file_save' not in st.session_state:
	st.session_state.file_save = 0
	
	
if st.session_state.run_num == 0:
	st.sidebar.markdown('To use the app, click on button below to ' + 
			    'upload your DDI database.')

	st.session_state.file_save = st.sidebar.file_uploader("# Upload the data", type=['xlsx'])



if st.session_state.file_save is not None:
	if st.session_state.run_num == 0:
		data = data_processing(st.session_state.file_save)
		st.session_state.data_save = data
	
	st.markdown('This is the loaded data')
	
	
	if st.checkbox('Show Loaded Data'):
		st.dataframe(st.session_state.data_save)

	#-----Creating different dataframes for each engine operation-------
	points = sorted(st.session_state.data_save['Condition'].unique())

	#for x in range(1, 1 + len(st.session_state.data_save.groupby('Condition').count().iloc[:, 1])):
	#	globals()['df%s' % x] = st.session_state.data_save.where(st.session_state.data_save['Condition'] == 
	#				   	points[x-1]).dropna(subset=['File Name'])
		
				#-----Drop down list for each variable-------
	form1 = st.form(key='Options')
	
	vars = st.session_state.data_save.columns.astype(str)
	
	var_plot = form1.multiselect(
	'Choose the variable to be ploted', vars)

	option2 = form1.selectbox(
	'Choose engine operation condition', points)

	
	df_plot = st.session_state.data_save.where(st.session_state.data_save['Condition'] == 
					   	option2).dropna(subset=['File Name'])
	
	
	plot_button = form1.form_submit_button('Plot')
	plot_state = button_states()
        	
	st.markdown(type(var_plot))

	if plot_button:
		st.session_state.run_num = 1
		fig = pf.plot(df_plot, var_plot)
		st.plotly_chart(fig)


    
 
