import pandas as pd
import matplotlib.pyplot as plt

def pivoter(df):
    df_pivot = df.pivot_table(index='Week', columns=['Period', 'Subject'], values='Time Spent (Hrs)', fill_value=0)
    df_pivot = df_pivot.sort_index()
    
    return df_pivot

def plot_daily_subj_hours_line(df, add_avg=False, roll_avg=None):
    import matplotlib.patheffects as path_effects # prev PathEffects
    from matplotlib.ticker import MaxNLocator
    import matplotlib.cm as cm
    '''
        Plots a line chart showing the time spent on different subjects over a period of time.
    '''
    df = df[['Period', 'Day', 'Time Spent (Hrs)']]
    
    if add_avg:
        df_avg = df.groupby('Day', as_index=False)['Time Spent (Hrs)'].mean()
        df_avg['Period'] = 'Average'
        df = pd.concat([df, df_avg[['Period', 'Day', 'Time Spent (Hrs)']]], axis=0, ignore_index=True)
    
    if roll_avg is not None:
        df_avg_list = []
        for period in df['Period'].unique():        
            df_period = df[df['Period'] == period].sort_values('Day')

            df_period['Rolled Time Spent (Hrs)'] = df_period['Time Spent (Hrs)'].rolling(window=roll_avg, min_periods=1).mean()

            df_avg_list.append(df_period)

        df = pd.concat(df_avg_list, ignore_index=True)

    plt.style.use('bmh')
    
    fig, ax = plt.subplots(figsize=(9, 5))
    
    cmap = cm.get_cmap('prism', len(df['Period'].unique()))  # Dark2 Set1  inferno
    # color_cycle = cycler(color=['#4F81BD', '#C0504D', '#9BBB59', '#8064A2'])  

    fig.set_facecolor('#444444') 

    line_params = {
        'alpha':        0.65, 
        'ls':           ':', 
        'linewidth':    1,
        'zorder':       1
    }  
    avg_line_params = {
        'alpha':        0.75, 
        'ls':           '-', 
        'linewidth':    2,
        'color':        '0.85',
        'zorder':       3,
    }
    path_efx_avg = [path_effects.SimpleLineShadow(offset=(0.5, -1), shadow_color='white'), path_effects.Normal()]
    
    if roll_avg is not None:
        plot_data = 'Rolled Time Spent (Hrs)'
    else: plot_data = 'Time Spent (Hrs)'

    n = 0
    for period in df['Period'].unique():
        period_data = df[df['Period'] == period]
        
        if period == 'Average': 
            ax.plot(period_data['Day'], period_data[plot_data], 
                label=f'{period}', **avg_line_params,
                path_effects=path_efx_avg)
            continue
        ax.plot(period_data['Day'], period_data[plot_data], label=f'{period}', color=cmap(n), **line_params)
        n += 1

    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=10)) 
    ax.tick_params(colors='0.8')

    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')

    # ax.set_autoscale_on(True)
    ax.set_facecolor('#444444')
    
    plt.xticks(rotation=45)
    # #747474
    ax.legend(loc='upper left', labelcolor='0.8', frameon=False) # , framealpha=0.2
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