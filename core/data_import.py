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
    def delete_negative_times(df):
        import numpy as np
        negval_condition = (df['Time Spent (Hrs)'] < 0) & (df['Type'] == 'Adjusted')
        pos_rows = df[~negval_condition]
        neg_rows = df[negval_condition]

        date_threshold = pd.Timedelta(days=2) # threshold
        time_threshold = 0.25

        for _, neg_row in neg_rows.iterrows():
            close_condition = (
                (abs(pos_rows['Time Spent (Hrs)'] + neg_row['Time Spent (Hrs)']) < time_threshold) & # 6 + (-5.8) = 0.2
                (abs(pos_rows['End Date'] - neg_row['End Date']) < date_threshold)
            )
            pos_rows = pos_rows[~close_condition]

        pos_rows = df[~(df['Time Spent (Hrs)'] <= 0.008)]

        return pos_rows
   
    print("cleaning...")

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

    df_clean = cleaner.dataframe

    df_clean2 = delete_negative_times(df_clean)

    ini_neg = len(df_clean[df_clean['Time Spent (Hrs)'] < 0])
    post_neg = len(df_clean2[df_clean2['Time Spent (Hrs)'] < 0])
    print(f"Deleted {post_neg-ini_neg} negative values, converted removed {len(df_clean2)-len(df_clean)} total rows")

    return df_clean2

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

