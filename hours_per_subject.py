import os,sys
import pandas as pd

sys.path.append(r'C:\Users\Lolo\Desktop\Programming\GITRepo\PythonLearn-Resources\Data analysis\Matplotlib')    
from MODULE_matplot_pandas import DataPlotter
sys.path.append(r'C:\Users\Lolo\Desktop\Programming\GITRepo\PythonLearn-Resources\Data analysis\Pandas')    
from MODULE_pandas_basic import DataCleaner, DataFrameTransformer
sys.path.append(r'C:\Users\Lolo\Desktop\Programming\GITRepo\PythonLearn-Resources\Data analysis\Pandas\Excel')
from MODULE_pandas_excel_functions import ExcelDataExtract

def main(dataframe):
    clean_dataframe = clean_dataframe_for_plotting(dataframe)

    print(f"Plotting data:\n{clean_dataframe}")
    df_plot = DataPlotter(clean_dataframe)
    df_plot.identify_column_hierarchy()
    df_plot.plot_hierarchical_categorical_bar_chart()

def clean_dataframe_for_plotting(dataframe):
    ColToFilter = 'Period'
    FilterValues = ['1St Semester', '2Nd Semester']
    df_cleaned = DataCleaner(dataframe)
    df_cleaned.filter_df_column_by_val(ColToFilter,FilterValues)

    colsToGroup = ['Time Spent (Hrs)', 'Period', 'Subject']
    transformed_df = DataFrameTransformer(df_cleaned.dataframe)
    transformed_df.multiIndex_group(colsToGroup)

    return transformed_df.dataframe

def main2(dataframe):
    clean_dataframe = clean_dataframe_for_main2(dataframe)
    
    #print(f"DEBUG: Plotting data:\n{clean_dataframe}")
    df_plot = DataPlotter(clean_dataframe)
    df_plot.identify_column_hierarchy()
    df_plot.plot_hierarchical_categorical_bar_chart()
    return

def clean_dataframe_for_main2(dataframe):
    """
    MVP:
        -Group 'Time Spent (Hrs)' by week and per subject:
            -Requires to create a column (maybe?) of the week as string of start to end date.
    """
    transformed_df = DataCleaner(dataframe)
    ColToFilter = 'Period'
    FilterValues = ['1St Semester', '2Nd Semester']
    transformed_df.filter_df_column_by_val(ColToFilter,FilterValues)
    
    print(f"DEBUG: df after transforming:\n{transformed_df.dataframe}")
    
    df = transformed_df.dataframe[['Time Spent (Hrs)', 'Period','Subject', 'date', 'year', 'month', 'day']]
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['Week'] = df['date'].dt.to_period('W-SUN')

    df = df.groupby(['Period', 'Subject', 'Week'])['Time Spent (Hrs)'].sum().reset_index()

    print(f"DEBUG: df after grouping:\n{df}\n")
    
    return df