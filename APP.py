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
if 'txt_vars' not in st.session_state:
	st.session_state.txt_vars = 0
	
	
if st.session_state.run_num == 0:
	st.sidebar.markdown('To use the app, click on button below to ' + 
			    'upload your DDI database.')

	st.session_state.file_save = st.sidebar.file_uploader("# Upload the data", type=['xlsx'])
	
	st.session_state.txt_vars = ['BHP SI', 'BMEP SI', 'BMEP SI M', 'BSFC SI', 'c AVGCA50M', 'c ELS_NMEPM', 'c FMEP', 'CO', 
		   'CO2', 'd Speed', 'd Torque SI', 'FA_AIRMASS mgpc', 'FA1000Avg BP F', 'H', 'HC', 'IMEP SI', 
		   'IMEP01COV M', 'IMEP01LNV M', 'IMEP02COV M', 'IMEP02LNV M', 'IMEP03COV M', 'IMEP03LNV M', 'IMEP04COV M', 
		   'IMEP04LNV M', 'IMEP05COV M', 'IMEP05LNV M', 'IMEP06COV M', 'IMEP06LNV M', 'IMEPCOV_Avg', 'IMEPLNV_Avg', 
		   'KNINSQ Knock Limit', 'KNINSQ M', 'KNINSQ RT_max', 'KnockHeavy', 'KnockLight', 'KnockModerate', 'n ACT', 
		   'n ACT_SPK_CYL1', 'n BASE_SPK', 'n DL_ETRQ_SO', 'n ECT', 'n SPK_ADJ', 'n VVT_EXH_CAM_1_CL_POS', 
		   'n VVT_EXH_CAM_2_CL_POS', 'n VVT_EXH_CAM_M_CL_POS', 'n VVT_EXH_CAM_M_CL_POS', 'n VVT_INT_CAM_1_CL_POS', 
		   'n VVT_INT_CAM_2_CL_POS', 'NOX', 'O2', 'p Coolant Out SI', 'p Corr F SI', 'p Crankcase SI', 'p E Left SI', 
		   'p E Right SI', 'p Fuel Rail SI', 'p Man Abs SI', 'p Oil SI', 't Corr F SI', 't E Left SI', 't E Right SI', 
		   't Fuel Rail SI', 't Oil Gallery SI', 'VE_measured', 'VE_Nominal']

	
	



if st.session_state.file_save is not None:
	if st.session_state.run_num == 0:
		data = data_processing(st.session_state.file_save)
		st.session_state.data_save = data
	
	st.markdown('This is the loaded data')
	
	
	if st.checkbox('Show Loaded Data'):
		st.dataframe(st.session_state.data_save)
		
	vars_selection = st.radio('Variables Selection', ('Important Vars', 'All Vars')) 

	#-----Creating different dataframes for each engine operation-------
	points = sorted(st.session_state.data_save['Condition'].unique())

	
	#-----Drop down list for each variable-------
	form1 = st.form(key='Options')
	
	vars = st.session_state.data_save.columns.values.tolist()
	
	if vars_selection == 'Important Vars':
		var_plot = form1.multiselect(
			'Choose the variable to be ploted', st.session_state.txt_vars)
	else:
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
		fig = pf.plot(df_plot, list(var_plot), check_std, n_data, std_input, period)
		st.plotly_chart(fig)
		
		df_plot = df_plot[st.session_state.txt_vars]
		colunas = df_plot.std().index.values
		for i in colunas:
			mediadf = df_plot[i].mean()
			stddf = df_plot[i].std()
			df_plot[i] = df_plot.loc[(df_plot[i] > mediadf+std_input*stddf) | (df_plot[i] < mediadf-std_input*stddf)]

		st.selectbox('outliers', df_plot.tail(5).dropna(axis=1, how='all').columns.values.tolist())
