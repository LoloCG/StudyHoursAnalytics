import pandas as pd
import matplotlib.pyplot as plt
from PyLogger.basic_logger import LoggerSingleton

logger = LoggerSingleton().get_logger()

def pivoter(df):
    df_pivot = df.pivot_table(index='Week', columns=['Period', 'Subject'], values='Time Spent (Hrs)', fill_value=0)
    df_pivot = df_pivot.sort_index()
    
    return df_pivot

def plot_daily_subj_hours_line(df, current_course=None, add_avg=False, roll_avg=None):
    import matplotlib.patheffects as path_effects # prev PathEffects
    from matplotlib.ticker import MaxNLocator
    import matplotlib.cm as cm
    '''
        Plots a line chart showing the time spent on different subjects over a period of time.
    '''
    df = df.sort_values(by='Date')
    logger.info(f"last day in plot: {pd.to_datetime(df['Date'].max()).strftime('%d-%m-%Y')} in {df.loc[df['Date'].idxmax(), 'Course']}")

    df = df[['Course','Period', 'Day', 'Time Spent (Hrs)']]
    
    if add_avg:
        df_avg = df.groupby('Day', as_index=False)['Time Spent (Hrs)'].mean()
        df_avg['Course'] = 'Average'
        df_avg['Period'] = 'Average'
        df = pd.concat([df, df_avg[['Course', 'Period', 'Day', 'Time Spent (Hrs)']]], axis=0, ignore_index=True)
    
    period_list = [] 
    for course in df['Course'].unique():
        course_data = df[(df['Course'] == course)]
        for period in course_data['Period'].unique():
            unique_period = str(course + ';' + period)
            period_list.append(unique_period)

    if roll_avg is not None:
        df_avg_list = []
        for unique_period in period_list:
            course, period = unique_period.split(';')
            period_data = df[(df['Course'] == course) & (df['Period'] == period)].sort_values('Day')
            period_data['Rolled Time Spent (Hrs)'] = period_data['Time Spent (Hrs)'].rolling(window=roll_avg, min_periods=1).mean()
            df_avg_list.append(period_data)
                
        df = pd.concat(df_avg_list, ignore_index=True)

    plt.style.use('bmh')

    fig, ax = plt.subplots(figsize=(11, 6))

    cmap = cm.get_cmap('Set1', len(period_list)) # Dark2, Set1, inferno, prism
    # color_cycle = cycler(color=['#4F81BD', '#C0504D', '#9BBB59', '#8064A2'])  

    fig.set_facecolor('#444444') 
    current_line_params = {
        'alpha':        0.8, 
        'ls':           '-', 
        'linewidth':    1.7,
        'color':        '0.9',
        'zorder':       1,
    }
    line_params = {
        'alpha':        0.7, 
        'ls':           ':', 
        'linewidth':    1.5,
        'zorder':       1
    }  
    avg_line_params = {
        'alpha':        0.8, 
        'ls':           '-', 
        'linewidth':    2.25,
        'color':        '0.7',
        'zorder':       2,
    }
    path_efx_avg = [path_effects.SimpleLineShadow(offset=(0.5, -1), shadow_color='white'), path_effects.Normal()]
    
    if roll_avg is not None:
        plot_data = 'Rolled Time Spent (Hrs)'
    else: plot_data = 'Time Spent (Hrs)'

    n = 0
    for unique_period in period_list:
        course, period = unique_period.split(';')
        period_data = df[(df['Course'] == course) & (df['Period'] == period)].sort_values('Day')

        if period == 'Average': 
            ax.plot(period_data['Day'], period_data[plot_data], 
                label=f'{period}', **avg_line_params,
                path_effects=path_efx_avg)
            continue
        
        if course == current_course: # this will have to be modified for more than 1 semester... this is a quick fix...
            ax.plot(period_data['Day'], period_data[plot_data], 
                label=f'{course} - {period}',
                **current_line_params,
                path_effects=path_efx_avg)
            continue

        ax.plot(period_data['Day'], period_data[plot_data], label=f'{course} - {period}', color=cmap(n), **line_params)
        n += 1

    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=10)) 
    ax.tick_params(colors='0.8')
    ax.set_xlabel('Day', color='0.8')  # Label for the X axis (Day)
    ax.set_ylabel('Time Spent (Hours)', color='0.8')  

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