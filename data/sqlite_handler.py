from SQLite_ORM.basics import *
from SQLite_ORM.pandas_addon import insert_data_from_df

import sys,os

db_name = 'studyanalytics.db'
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

main_table_name = 'main_table'

def check_table(table_name=main_table_name):
    db = DBManager(db_name=db_name, db_path=db_path)
    with db.connector:
        exists, has_rows = db.table_manager.check_table(main_table_name)
    return exists, has_rows

def create_and_append_df(df):
    db = DBManager(db_name=db_name, db_path=db_path)

    db.connector.connect()
    connector_obj = db.get_connector()
    insert_data_from_df(dataframe=df, connector_obj=connector_obj, table_name=main_table_name)
    db.connector.close()
    