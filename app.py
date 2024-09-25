import core.data_import as dimp
import data.sqlite_handler as data

def main():
    raw_df = dimp.get_csv_file()
    df_clean = dimp.basic_clean(raw_df)

    data.create_and_append_df(df_clean)

main()