import sys, os
import Excel_Tools.import_export_utils as imex 
import Data_Cleaning.data_cleaning_utils as dclean

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

    cleaner.convert_df_dates(date_column='Start Date', single_col=True, keep_original=True)
    cleaner.convert_df_dates(date_column='End Date', single_col=True, keep_original=True)
    cleaner.convert_df_times(time_column='Start Time', single_col=True)
    cleaner.convert_df_times(time_column='End Time', single_col=True)

    cleaner.replace_comma_to_dot(column='Time Spent (Hrs)')
    
    return cleaner.dataframe

get_csv_file()