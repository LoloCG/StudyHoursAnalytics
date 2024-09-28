import pandas as pd
import matplotlib.pyplot as plt

def pivoter(df):
    df_pivot = df.pivot_table(index='Week', columns=['Period', 'Subject'], values='Time Spent (Hrs)', fill_value=0)
    df_pivot = df_pivot.sort_index()
    
    return df_pivot

def plot_daily_subj_hours_line(df, add_avg=False):
    import matplotlib.patheffects as PathEffects
    '''
        Plots a line chart showing the time spent on different subjects over a period of time.
    '''
    df = df[['Period', 'Day', 'Time Spent (Hrs)']]
    
    if add_avg:
        df_avg = df.groupby('Day', as_index=False)['Time Spent (Hrs)'].mean()
        df_avg['Period'] = 'Average'
        df = pd.concat([df, df_avg[['Period', 'Day', 'Time Spent (Hrs)']]],axis=0, ignore_index=True)

    
    plt.style.use('bmh')
    from matplotlib.ticker import MaxNLocator
    fig, ax = plt.subplots(figsize=(9, 5))
    
    
    for period in df['Period'].unique():
        period_data = df[df['Period'] == period]
        ax.plot(period_data['Day'], period_data['Time Spent (Hrs)'], label=f'{period}', alpha=0.75, ls='--', linewidth=1)
        
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=10)) 
    plt.xticks(rotation=45)
    
    ax.legend()
    plt.tight_layout()
    plt.show()

def plot_week_hours_barchart(df_pivoted):
    from matplotlib.ticker import MaxNLocator
    fig, axes = plt.subplots()

    for column in df_pivoted.columns:
        axes.plot(df_pivoted.index, df_pivoted[column], label=column)
    
    locator = MaxNLocator(nbins=8) # manual set of ticks
    axes.xaxis.set_major_locator(locator)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.show()

