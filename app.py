import core.data_import as dimp
import data.sqlite_handler as data
import core.data_analysis as dan

def main():
    exists, has_rows = data.check_table()

    if not has_rows:
        file_choice = dimp.show_and_select_csv()
        print(file_choice)

        raw_df = dimp.csv_file_to_df(file_choice)

        df_clean = dimp.basic_clean(raw_df)
        data.add_main_data(df_clean)

        df_daily = dimp.basic_to_daily_clean(df_clean)
        data.add_subject_hours(df_daily)
        dan.plot_daily_subj_hours_line(df_daily, add_avg=True)

        # weekly_df = dimp.generate_weekly_hours_dataframe(df_clean)
        # data.add_weekly_hours(weekly_df)
    
    # else:
    #     periods = ['1St Semester', '2Nd Semester']
    #     df_daily = data.get_df_periods(periods, data_series='daily')
    #     dan.plot_daily_subj_hours_line(df_daily, add_avg=True, roll_avg=7)
 
# df_pivot = dan.pivoter(weekly_df)
# dan.plot_daily_subj_hours_line(subhr_df)

# dan.plot_week_hours_barchart(df_pivot)

print("Program start.")
main()