from SQLite_ORM.basics import *
from SQLite_ORM.pandas_addon import *
import pandas as pd
import sys,os

db_name = 'studyanalytics.db'
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

main_table_name = 'main_data'
daily_hours_table_name = 'daily_hours'
weekly_hours_table_name = 'weekly_hours'

def check_table(table_name=main_table_name):
    db = DBManager(db_name=db_name, db_path=db_path)
    with db.connector:
        exists, has_rows = db.table_manager.check_table(main_table_name)
    return exists, has_rows

def add_main_data(df):
    tm = TableManager()
    with tm:
        tm.create_and_append_to_table(df, table_name=main_table_name)

def add_subject_hours(df):
    tm = TableManager()
    with tm:
        tm.create_and_append_to_table(df, table_name=daily_hours_table_name)

def add_weekly_hours(df):
    tm = TableManager()
    with tm:
        tm.create_and_append_to_table(df, table_name=weekly_hours_table_name)

def get_daily_hours_periods(periods):
    '''
        Requires a list of Periods as string, located in the column Period of the dataframe.
    '''
    db = DBManager(db_name=db_name, db_path=db_path)
    connector = db.connector
    
    conditions = {'Period': periods}

    df = retrieve_as_df(
        connector_obj=connector, 
        table_name=daily_hours_table_name, 
        conditions=conditions)

    return df

class TableManager:
    def __init__(self):
        self.db = DBManager(db_name=db_name, db_path=db_path)

    def __enter__(self):
        self.db.connector.connect()
        self.connector_obj = self.db.get_connector()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.connector.close()
        self.connector_obj = None

    def create_and_append_to_table(self, df, table_name):
        insert_data_from_df(
            dataframe=df,
            connector_obj=self.connector_obj, 
            table_name=table_name)
