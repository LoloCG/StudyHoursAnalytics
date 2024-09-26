import core.data_import as dimp
import data.sqlite_handler as data

def main():
    exists, has_rows = data.check_table()

    if not has_rows:
        raw_df = dimp.get_csv_file()

        df_clean = dimp.basic_clean(raw_df)
        data.add_main_data(df_clean)

        subhr_df = dimp.generate_subject_hours_dataframe(df_clean)
        data.add_subject_hours(subhr_df)

        weekly_df = dimp.generate_weekly_hours_dataframe(df_clean)
        data.add_weekly_hours(weekly_df)
    
        df_pivot = dimp.pivoter(weekly_df)
        print(df_pivot)

main()