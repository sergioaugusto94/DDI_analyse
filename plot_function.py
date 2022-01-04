import plotly.express as px
import plotly.graph_objects as go


def plot(df_plot, var):
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
    mean = [df_plot[var].mean()]*df_plot.shape[0]
    std_max = [df_plot[var].mean() + 
               df_plot[var].std()]*df_plot.shape[0]
    std_min = [df_plot[var].mean() - 
               df_plot[var].std()]*df_plot.shape[0]

    # Outliers Data Frame
    outliers = df_plot[(df_plot[var] < df_plot[var].mean() - df_plot[var].std()) | 
                       (df_plot[var] > df_plot[var].std() + 
                        df_plot[var].mean())].dropna(subset=['File Name'])

    #--------PLOT----------
    # Recorded Data
    fig = px.scatter(df_plot, 'Date', var, title=title_df, width=1100, height=600)
    # Outliers Anotation
    if outliers.shape[0] != 0:
      for i in range(outliers.shape[0]):
        fig.add_annotation(x=outliers['Date'].iloc[i], y=outliers[var].iloc[i],
                  text=(str(round(outliers[var].iloc[i],2))+ ' ( ' + 
                        str(round((outliers[var].iloc[i]-df_plot[var].mean())/
                                  df_plot[var].mean()*100,2)) + '%)'), 
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
                      str(round(df_plot[var].std()/df_plot[var].mean()*100,2)) + 
                      '%)'), showarrow=False, xanchor="left", yshift=8)
    # Std Min Line
    fig.add_trace(go.Scatter(x=df_plot['Date'], y=std_min, mode='lines', 
                             line=dict(dash='dot', color='orange'), name='Std min'))
    fig.add_annotation(x=df_plot['Date'].min(), y=std_min[0],
                text=(str(round(std_min[0],2))+ ' (- ' + 
                      str(round(df_plot[var].std()/df_plot[var].mean()*100,2)) + 
                      '%)'), showarrow=False, xanchor="left", yshift=8)
    return fig
