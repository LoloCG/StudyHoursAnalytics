import core.data_import as dimp

def main():
    raw_df = dimp.get_csv_file()
    df_clean = dimp.basic_clean(raw_df)

    print(df_clean.head())

main()