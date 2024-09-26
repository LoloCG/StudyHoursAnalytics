import sys, os
import Excel_Tools.import_export_utils as imex 
import Data_Cleaning.data_cleaning_utils as dclean
import pandas as pd

def get_csv_file():
    chosen_file = '3º FarmNutr TDL_Log.csv'
    target_folder = r'C:\Users\Lolo\Desktop\Programming\GITRepo\StudyHoursAnalytics\data_example'

    input_csv = imex.ExcelImporter()
    input_csv.add_extraction_folder(target_folder)
    input_csv.add_file(chosen_file)
    df = input_csv.csv_to_dataframe()
    return df

def basic_clean(df_raw):
    df_raw.drop('User ID', axis=1, inplace=True)
    df_raw.drop('Task ID', axis=1, inplace=True)
    df_raw.drop('Comment', axis=1, inplace=True)
    
    cleaner = dclean.DFCleaner(df_raw)

    new_columns = ['Period', 'Subject', 'pathinfo']
    cleaner.split_column(column='Path', separator='\\', new_columns=new_columns, expand=True, drop_old=True)
    cleaner.normalize_column_strings(column='Period')
    cleaner.normalize_column_strings(column='Subject')

    cleaner.convert_df_dates(date_column='Start Date', single_col=True)
    cleaner.convert_df_dates(date_column='End Date', single_col=True)
    cleaner.convert_df_times(time_column='Start Time', single_col=True)
    cleaner.convert_df_times(time_column='End Time', single_col=True)

    cleaner.replace_comma_to_dot(column='Time Spent (Hrs)')
    
    return cleaner.dataframe

def generate_subject_hours_dataframe(df_clean):
    ''' '''
    wanted_cols = ['Period', 'Subject', 'Time Spent (Hrs)', 'Start Date', 'Start Time']
    df = df_clean[wanted_cols]

    filter_values = ['1St Semester', '2Nd Semester']
    filter_col = 'Period'
    
    # df['Week'] = df['Start Date'].dt.to_period('W-SUN')

    subhr_df = df[df[filter_col].isin(filter_values)]
    
    return subhr_df

def generate_weekly_hours_dataframe(df_clean):
    ''' '''
    wanted_cols = ['Period', 'Subject', 'Time Spent (Hrs)', 'Start Date', 'End Date', 'Start Time', 'End Time']
    df = df_clean[wanted_cols]

    filter_values = ['1St Semester', '2Nd Semester']
    filter_col = 'Period'
    df = df[df[filter_col].isin(filter_values)]

    df['Start Date'] = pd.to_datetime(df['Start Date'])

    df['Week'] = df['Start Date'].dt.to_period('W-SUN').astype(str)

    df = df.groupby(['Period', 'Subject', 'Week'])['Time Spent (Hrs)'].sum().reset_index()
    # df = df.groupby('Week')['Time Spent (Hrs)'].sum().reset_index()
    
    weekly_df = df

    return weekly_df

def pivoter(df): # This is not used yet
    df_pivot = df.pivot_table(index='Week', columns=['Period', 'Subject'], values='Time Spent (Hrs)', fill_value=0)
    df_pivot = df_pivot.sort_index()
    
    return df_pivot