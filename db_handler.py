main_verbose = True

import sys, os
import pandas as pd

sys.path.append(r'C:\Users\Lolo\Desktop\Programming\GITRepo\PythonLearn-Resources\Databases\SQLite')
from MODULE_SQLite_functions import DatabaseHandler
sys.path.append(r'C:\Users\Lolo\Desktop\Programming\GITRepo\PythonLearn-Resources\Data analysis\Pandas\Excel')
from MODULE_pandas_excel_functions import ExcelDataExtract
sys.path.append(r'C:\Users\Lolo\Desktop\Programming\GITRepo\PythonLearn-Resources\Data analysis\Pandas')
from MODULE_pandas_basic import DataCleaner

main_db_name = 'StudyAnalysis.db'
db_folder_dir = os.path.dirname(os.path.abspath(__file__))
main_db = DatabaseHandler(db_name=main_db_name, db_dir=db_folder_dir)
main_table_name = 'full_data'

def main():

    target_file_folder_dir = os.path.dirname(os.path.abspath(__file__)) 
    chosen_file = '3º FarmNutr TDL_Log.csv'

    if main_db.check_db_existance() is False:
        print("Database does not exist, setting it up:")
        
        excelCSV_raw = ExcelDataExtract(file_folder_dir=target_file_folder_dir)
        excelCSV_raw.load_csv_to_dataframe(chosen_file)

        create_main_db(excelCSV_raw.dataframe)

    else:
        print("Database already exists. Update function not yet implemented...")
        return
        
def create_main_db(dataframe):
    df_full = DataCleaner(dataframe)
    col_2_split = 'Path'
    split_columns = ['Period', 'Subject', 'Path3']
    df_full.split_column_into_multiple(columnName=col_2_split, separator='\\', newColList=split_columns)
    df_full.normalize_column_strings(columnName='Subject')
    df_full.normalize_column_strings(columnName='Period')
    df_full.convert_dataframe_dates(dateColumn='Start Date')
    df_full.convert_comma_to_dot(columnName='Time Spent (Hrs)')
    
    df = df_full.dataframe
    columns = df.columns
    data_types = df.dtypes
    table_dict = dict(zip(columns, data_types))
    
    SQL_table_dict = main_db.convert_dict_valType_to_sqlType(table_dict)
    main_db.create_db_table(table_items=SQL_table_dict, table_name=main_table_name,verbose=main_verbose)
    main_db.insert_data_from_df(dataframe=df)
    main_db.close_connection()

    print("Database created successfully...")

def retrieve_main_table():
    print("Obtaining dataframe from main database table...")

    df = main_db.retrieve_all_data_as_df(tableName=main_table_name)

    return df