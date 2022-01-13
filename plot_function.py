import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def plot(df_plot, lista, check_std):

	var = lista
	
    # Defining the plot title
	thr_title = 'WOT, '
	vvl_state = 'HL, '

	if df_plot['CL_Throttle'].iloc[0].astype(int) < 100:
		thr_title = df_plot['CL_Throttle'].iloc[0].astype(int).astype(str)+' % Thr, '

	if str(df_plot['n VVL_STATE_ACT'].iloc[0]) == '1.0':
		vvl_state = 'LL, '

	title_df = (df_plot['CL_dSpeed'].iloc[0].astype(int).astype(str)+' rpm, '+
		    df_plot['CL_BMEP SI'].iloc[0].astype(int).astype(str)+' kPa, '+
		    thr_title + vvl_state + 
		    str(df_plot['n DL_SPK_ADV'].iloc[0])+' Spark deg')

    # Defining mean and std
	mean = [df_plot[var].unstack().mean()]*df_plot.shape[0]
	std_max = [df_plot[var].unstack().mean() + 
		   df_plot[var].unstack().std()]*df_plot.shape[0]
	std_min = [df_plot[var].unstack().mean() - 
		   df_plot[var].unstack().std()]*df_plot.shape[0]


    # Outliers Data Frame

	outliers = df_plot[var][(df_plot[var] < df_plot[var].unstack().mean() - df_plot[var].unstack().std()) | 
				(df_plot[var] > df_plot[var].unstack().std() + 
				 df_plot[var].unstack().mean())].dropna(how='all')
	outliers = pd.merge(df_plot['Date'], outliers, left_index=True, right_index=True)
	
	#--------PLOT----------
	# Recorded Data
	fig = px.scatter(width=1100, height=600, title=title_df)

	symbols = ['circle', 'square', 'diamond', 'x', 'cross', 'triangle', 'hexagon']
	colors = ['red', 'blue','green','yellow', 'coral', 'snow', 'k', 'magenta', 'cyan', 'lime']
	for i in range(len(var)):
		for j in range(df_plot['Eng_dummy'].unique().shape[0]):
			df_plot2 = df_plot.where(df_plot['Eng_dummy']==j).dropna(subset=['File Name'])
			fig.add_trace(go.Scatter(x = df_plot2['Date'], y=df_plot2[var[i]], mode='markers', name=var[i]+'_'+df_plot2['Engine'].iloc[0], marker=dict(symbol=symbols[j], color=colors[i])))

	melted_out = outliers.melt(id_vars=['Date']).dropna(subset=['value'])

	# Outliers Anotation
	if check_std:
		if melted_out.shape[0] != 0:
			for j in range(melted_out.shape[0]):
				fig.add_annotation(x=melted_out['Date'].iloc[j], y=melted_out['value'].iloc[j],
						   text=(str(round(melted_out['value'].iloc[j],2))+ ' ( ' + 
							 str(round((melted_out['value'].iloc[j]-mean[0])/
								   mean[0]*100,2)) + '%)'), 
						   showarrow=False, xanchor="left", xshift=8)
	# Mean Line
	fig.add_trace(go.Scatter(x=df_plot['Date'], y=mean, mode='lines', 
				 line=dict(dash='dot', color='black'), name='Mean'))
	fig.add_annotation(x=df_plot['Date'].min(), y=mean[0],
			   text=round(mean[0], 2), showarrow=False, xanchor="left", yshift=8)
    # Std Max Line
	fig.add_trace(go.Scatter(x=df_plot['Date'], y=std_max, mode='lines', 
				 line=dict(dash='dot', color='red'), name='Std max'))
	fig.add_annotation(x=df_plot['Date'].min(), y=std_max[0],
			   text=(str(round(std_max[0],2))+ ' (+ ' + 
				 str(round((std_max[0]-mean[0])/mean[0]*100,2)) + 
				 '%)'), showarrow=False, xanchor="left", yshift=8)
    # Std Min Line
	fig.add_trace(go.Scatter(x=df_plot['Date'], y=std_min, mode='lines', 
				 line=dict(dash='dot', color='orange'), name='Std min'))
	fig.add_annotation(x=df_plot['Date'].min(), y=std_min[0],
			   text=(str(round(std_min[0],2))+ ' (- ' + 
				 str(round((std_min[0]-mean[0])/mean[0]*100,2)) + 
				 '%)'), showarrow=False, xanchor="left", yshift=8)


	return fig
