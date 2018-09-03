
# coding: utf-8

# ### Functons for plotting graphs for Pet Store Sales Report

# In[1]:

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime
from dateutil.relativedelta import relativedelta

#%matplotlib inline


# In[2]:

# Define colors 
# "Tableau 20" colors in RGB 
tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),    
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),    
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),    
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),    
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]    
  
# Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.    
for i in range(len(tableau20)):    
    r, g, b = tableau20[i]    
    tableau20[i] = (r / 255., g / 255., b / 255.)    


# In[3]:

# Align right and left Y axies to the same height (secondary y-axis)
def align_yaxis(ax1, ax2):
    'Align zeros of the two axes, zooming them out by same ratio'
    axes = (ax1, ax2)
    extrema = [ax.get_ylim() for ax in axes]
    tops = [extr[1] / (extr[1] - extr[0]) for extr in extrema]
    # Ensure that plots (intervals) are ordered bottom to top:
    if tops[0] > tops[1]:
        axes, extrema, tops = [list(reversed(l)) for l in (axes, extrema, tops)]

    # How much would the plot overflow if we kept current zoom levels?
    tot_span = tops[1] + 1 - tops[0]

    b_new_t = extrema[0][0] + tot_span * (extrema[0][1] - extrema[0][0])
    t_new_b = extrema[1][1] - tot_span * (extrema[1][1] - extrema[1][0])
    axes[0].set_ylim(extrema[0][0], b_new_t)
    axes[1].set_ylim(t_new_b, extrema[1][1])# Functions used for charts


# Insert 0 if there is no entry for the month
def getChartData(df, item, last_FY_start_mo, last_FY_start, report_date):

    df1 = df[(df['対象商材']==item) & (df['Year-Month']>=last_FY_start_mo)]
    
    # create df with months of chart range
    idx = pd.date_range(last_FY_start, report_date, freq='M').to_period('m')
    d={'Year-Month':list(idx), 'key':1}
    df_month=pd.DataFrame(d)

    # create df with company that has a record in this FY and last FY
    co = df1['Display Co Name'].unique().tolist()
    d = {'Display Co Name': co, 'key':1}
    df_co = pd.DataFrame(d)
    
    df_month_co = pd.merge(df_month, df_co, how='inner', on='key')
    
    df2=pd.merge(df_month_co, df1, how ='left', on = ['Year-Month', 'Display Co Name'])
    df2.fillna(value =0, inplace=True)
    df2['対象商材']=item
    df2['3rd Party or Inter']=3
 
    return df2


def get_thisFY_pivot_df(df, current_FY_start_mo, report_date_mo): 
    
    df = df[(df['Year-Month']>= current_FY_start_mo) & 
            (df['Year-Month']<= report_date_mo)].pivot(index='Year-Month', 
                                                       columns='Display Co Name')['Actual Sales (Ex) in 1000']
    
    return df



def get_chart_df(df, start_mo, end_mo):
    
    df_FY = df[(df['Year-Month']>= start_mo) & (df['Year-Month']<= end_mo)].copy()
    df_FY_agg = df_FY.groupby(by='Year-Month').sum().reset_index()[['Year-Month', 'Actual Sales (Ex) in 1000']]

    # Add cumulative column
    df_FY_agg['Cumulative'] = df_FY_agg['Actual Sales (Ex) in 1000'].cumsum()

    return df_FY_agg


# In[4]:

# Function to plot chart
def plotChart(df_thisFY_pivot, df_thisFY, df_lastFY, item, report_date, outputPath):
    
    
    # Colors
    colors = tableau20
    
    width = 0.3
    shift = width/2

    fig = plt.figure(figsize=(12, 6))
    ax = plt.subplot(111)

    #　This year's bar graph
    df_thisFY_pivot.plot(kind='bar', stacked=True, width=width, ax=ax, position = 0, 
                         color = colors if df_thisFY_pivot.shape[1]>1 else colors[0], linewidth = 0.5)
 
    # Last year's bar graph
    df_lastFY['Actual Sales (Ex) in 1000'].plot(kind='bar', width=width, ax=ax, color='darkgray', label='Last Year', 
                                                position=1, linewidth = 0, grid=True)
    #ax2 = df_lastFY['Actual Sales (Ex) in 1000'].plot(kind='bar', width=width, ax=ax, color='darkgray', label='Last Year', position=1, linewidth = 0, grid=True)

    # Last year's line graph
    ax2=df_lastFY['Cumulative'].plot(kind='line', color=tableau20[6], secondary_y=True, linewidth=2, style='.--' ,
                                             grid=True, label='Cumulative Last Year')

    # This year's line graph
    ax2=df_thisFY['Cumulative'].plot(kind='line', color=tableau20[6], secondary_y=True, linewidth=2, style='.-' ,
                                             grid=True, label='Cumulative This Year')


    # fig.suptitle('Super title')
    plt.title('FY2018 {0} Sales Result (3rd Party Sales)'.format(item), fontsize=14)

    ax.set_xlabel(' ', fontsize = 10) #Month
    ax.set_ylabel('Unit in 1,000 Yen', fontsize = 12)
    ax2.set_ylabel('Cumulative', fontsize = 12)

    plt.xlim([-1,12])
    plt.xticks(range(12), ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'], rotation=360)

    # Legend
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.08), shadow=False, ncol=5, frameon=False) # under
    ax2.legend(loc='center', bbox_to_anchor=(0.5, -0.08), shadow=False, ncol=5, frameon=False) # under

    
    # Value label 

    # This year line graph
    for i, label in enumerate(list(df_thisFY.index)):
        height = df_thisFY.ix[label]['Cumulative']
        offset = 0
        ax2.annotate('¥{0:,.{1}f}'.format(height, 0), (i, height), clip_on=True, color='navy', fontsize=11,
                     weight = 'bold', va='bottom', horizontalalignment = 'right') 

    # Last year line graph
    for i, label in enumerate(list(df_lastFY.index)):
        height = df_lastFY.ix[label]['Cumulative'] 
        offset = 1 if height >= 20 else -1
        ax2.annotate('¥{0:,.{1}f}'.format(height, 0), (i, height-offset), clip_on=True, color=tableau20[6], fontsize=11,
                    va='top' if height >= 20 else 'bottom', 
                    horizontalalignment = 'left')

    
    align_yaxis(ax, ax2)
    
    
     # Output to png
    d=str(report_date.date()).replace('-', '')
    output_chart = outputPath + '{0}_{1}.png'.format(item, d)
    plt.savefig(output_chart, dpi=150, bbox_inches='tight')

    plt.close(fig)


# In[ ]:



