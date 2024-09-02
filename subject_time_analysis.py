import os,sys
import pandas as pd
import matplotlib.pyplot as plt

from modules import DataPlotter, DataCleaner, DataFrameTransformer, ExcelDataExtract

def show_weekly_hours_per_subject(dataframe):
    
    def clean_dataframe_data(dataframe):
        transformed_df = DataCleaner(dataframe)
        ColToFilter = 'Period'
        FilterValues = ['1St Semester', '2Nd Semester']
        transformed_df.filter_df_column_by_val(ColToFilter,FilterValues)
                
        df = transformed_df.dataframe[['Time Spent (Hrs)', 'Period','Subject', 'date', 'year', 'month', 'day']]
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df['Week'] = df['date'].dt.to_period('W-SUN')

        df = df.groupby(['Period', 'Subject', 'Week'])['Time Spent (Hrs)'].sum().reset_index()

        df_pivot = df.pivot_table(index='Week', columns=['Period', 'Subject'], values='Time Spent (Hrs)', fill_value=0)
        
        df_pivot = df_pivot.sort_index()

        return df_pivot

    clean_dataframe = clean_dataframe_data(dataframe)

    print(f"Plotting data:\n{clean_dataframe}")
    df_plot = DataPlotter(clean_dataframe)
    df_plot.plot_stacked_bar_chart()
    
    return

def show_total_hours_per_subject_per_perdiod(dataframe):
    def clean_dataframe_data(dataframe):
        ColToFilter = 'Period'
        FilterValues = ['1St Semester', '2Nd Semester']
        df_cleaned = DataCleaner(dataframe)
        df_cleaned.filter_df_column_by_val(ColToFilter,FilterValues)

        colsToGroup = ['Time Spent (Hrs)', 'Period', 'Subject']
        transformed_df = DataFrameTransformer(df_cleaned.dataframe)
        transformed_df.multiIndex_group(colsToGroup)

        return transformed_df.dataframe

    clean_dataframe = clean_dataframe_data(dataframe)

    print(f"Plotting data:\n{clean_dataframe}")
    df_plot = DataPlotter(clean_dataframe)
    df_plot.identify_column_hierarchy()
    df_plot.plot_hierarchical_categorical_bar_chart()




