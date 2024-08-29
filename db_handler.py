'''
About this file:
    It will contain as a module, all the important classes and functions related to the database generation, querying, etc.

MVP:
    - Function to detect if database exists
    - Function to check if there new data is found from the source (e.g.: a CSV file) compared to the database
    - Function to update database with the new data from the source.

'''
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

def main(target_file_folder_dir, chosen_file):
    if main_db.check_db_existance() is False:
        print("Database does not exist, setting it up:")
        
        excelCSV_raw = ExcelDataExtract(file_folder_dir=target_file_folder_dir)
        excelCSV_raw.load_csv_to_dataframe(chosen_file)

        create_main_db()

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
    main_db.create_db_table(tableItems=SQL_table_dict, mainTable_name=main_table_name)
    main_db.insert_data_from_df(dataframe=df)
    main_db.close_connection()

    print("Database created successfully...")

def retrieve_main_table():
    print("Obtaining dataframe from main database table...")

    df = main_db.retrieve_data_as_df(tableName=main_table_name)

    return df