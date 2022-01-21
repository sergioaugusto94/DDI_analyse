import streamlit as st
import pandas as pd
import base64
import os
import plot_function as pf

#Plotar mais de um gráfico

@st.cache
def data_processing(file):
	#--------Loading dataset-------
	data = pd.read_excel(file, sheet_name='Channel Info')
	data = data.drop(data[data.columns].std()[data[data.columns].std()<0.001].index, axis=1)

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
	data['Engine'] = data['File Name'].str[0:11]
	data['Eng_dummy'] = pd.get_dummies(data['Engine'])[data['Engine'].iloc[0]]

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
	
	txt_file = open("var_txt.txt", "r")

	var_txt = []
	for line in txt_file:
		stripped_line = line.strip()
		#line_list = stripped_line.split()
		#var_txt.append(line_list)
	var_txt.append(stripped_line)


txt_file.close()



if st.session_state.file_save is not None:
	if st.session_state.run_num == 0:
		data = data_processing(st.session_state.file_save)
		st.session_state.data_save = data
	
	st.markdown('This is the loaded data')
	
	
	if st.checkbox('Show Loaded Data'):
		st.dataframe(st.session_state.data_save)

	#-----Creating different dataframes for each engine operation-------
	points = sorted(st.session_state.data_save['Condition'].unique())

	
	#-----Drop down list for each variable-------
	form1 = st.form(key='Options')
	
	vars = st.session_state.data_save.columns.values.tolist()
	
	var_plot = form1.multiselect(
	'Choose the variable to be ploted', vars)

	option2 = form1.selectbox(
	'Choose engine operation condition', points)
	
	check_std = form1.checkbox('Print Outliers Description')

	n_data = form1.number_input('Points to Analyse', value=500, step=1)
	
	std_input = form1.number_input('Std multiplier', value=1.5, step=0.1)
	
	period = form1.number_input('Moving Average Period', value=5, step=1)
	
	df_plot = st.session_state.data_save.where(st.session_state.data_save['Condition'] == 
					   	option2).dropna(subset=['File Name'])
	

	plot_button = form1.form_submit_button('Plot')
	plot_state = button_states()
	

	if plot_button:
		st.session_state.run_num = 1
		#fig = pf.plot(df_plot, list(var_plot), check_std)
		fig = pf.plot(df_plot, list(var_plot), check_std, n_data, std_input, period)
		st.plotly_chart(fig)
