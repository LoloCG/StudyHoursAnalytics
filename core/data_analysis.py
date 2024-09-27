import pandas as pd
import matplotlib.pyplot as plt

def pivoter(df):
    df_pivot = df.pivot_table(index='Week', columns=['Period', 'Subject'], values='Time Spent (Hrs)', fill_value=0)
    df_pivot = df_pivot.sort_index()
    
    return df_pivot

def plot_daily_subj_hours_line(df, avg_wind=None):
    '''
        Plots a line chart showing the time spent on different subjects over a period of time.

        Processes the input DataFrame by selecting the required columns and 
            grouping them before filling in gaps in the date range with 0 time spent.
    '''
    df = df[['Period', 'Start Date', 'Time Spent (Hrs)']]
    
    df_grouped = df.groupby(['Period', 'Start Date'], as_index=False).sum()

    df_list = []
    for period in df_grouped['Period'].unique():
        df_period = df_grouped[df_grouped['Period'] == period]
        
        period_min = pd.Timestamp(df_period['Start Date'].min())
        period_max = pd.Timestamp(df_period['Start Date'].max())

        full_range = pd.DataFrame({'Start Date': pd.date_range(start=period_min, end=period_max)})


        df_period = df_grouped[df_grouped['Period'] == period].copy()
        df_period['Start Date'] = pd.to_datetime(df_period['Start Date'])
        full_range['Start Date'] = pd.to_datetime(full_range['Start Date'])
        
        df_merged = pd.merge(full_range, df_period, on='Start Date', how='left')

        df_merged['Time Spent (Hrs)'] = df_merged['Time Spent (Hrs)'].fillna(0)
        df_merged['Period'] = df_merged['Period'].ffill()

        df_merged['Day'] = df_merged['Start Date'].apply(lambda x: (pd.Timestamp(x) - period_min).days)
        
        if avg_wind is not None:
            df_merged['Day'] = df_merged['Day'].rolling(window=avg_wind, min_periods=1).mean()

        df_list.append(df_merged)

    df = pd.concat(df_list, ignore_index=True)

    df = df[['Period', 'Day', 'Time Spent (Hrs)']]
    
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

