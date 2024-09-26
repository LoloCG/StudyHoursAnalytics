import pandas as pd
import matplotlib.pyplot as plt

def pivoter(df):
    df_pivot = df.pivot_table(index='Week', columns=['Period', 'Subject'], values='Time Spent (Hrs)', fill_value=0)
    df_pivot = df_pivot.sort_index()
    
    return df_pivot

def plot_daily_subj_hours_line(df):
    df = df[['Start Date', 'Time Spent (Hrs)']]

    df = df.groupby('Start Date').sum()

    from matplotlib.ticker import MaxNLocator
    fig, ax = plt.subplots(layout='constrained')

    ax.plot(df.index, df['Time Spent (Hrs)']) # After groupby('Start Date'), 'Start Date' will set as the index.
    ax.xaxis.set_major_locator(MaxNLocator(nbins='auto'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.show()

def plot_week_hours_barchart(df_pivoted):
    from matplotlib.ticker import MaxNLocator
    fig, axes = plt.subplots(layout='constrained')

    for column in df_pivoted.columns:
        axes.plot(df_pivoted.index, df_pivoted[column], label=column)
    
    locator = MaxNLocator(nbins=8) # manual set of ticks
    axes.xaxis.set_major_locator(locator)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.show()

