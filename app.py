import core.data_import as dimp
import data.sqlite_handler as data
import core.data_analysis as dan
import CLI_native_tools as clin

def main():
    exists, has_rows = data.check_table()

    if not has_rows:
        print("Database does not contain any data.\nSelect file to import.")
        import_csv_to_database()
    
    while True:
        choice = main_menu_loop()
        if choice is None: break

# df_pivot = dan.pivoter(weekly_df)
# dan.plot_week_hours_barchart(df_pivot)

def main_menu_loop():
    option_str_list = [
        'Display daily study Hours',
        'Import .CSV file',
        "Import current year's .CSV file",
        # 'Display Weekly Study Hours'
    ]
    choice = clin.ask_loop_show_and_select_options(option_str_list=option_str_list, exit_msg='Exit program.')
    if choice is None: return None
    options_funcs = [
        lambda: plot_daily_hours(),
        lambda: import_csv_to_database(),
        lambda: import_current_year_csv()
        ]
    clin.call_function_from_choice(user_choice=choice, options_funcs=options_funcs)

def plot_daily_hours():
    df_daily = data.get_df_periods(data_series='daily')
    dan.plot_daily_subj_hours_line(df_daily, add_avg=True, roll_avg=7)
    return

def import_csv_to_database():
    file_choice = dimp.show_and_select_csv()
    print(file_choice)

    raw_df = dimp.csv_file_to_df(file_choice)

    df_clean = dimp.basic_cleaning(raw_df)
    df_edit = dimp.edit_course_params(df=df_clean, file=file_choice)
    
    data.add_main_data(df_edit)

    df_daily = dimp.basic_to_daily_clean(df_edit)
    data.add_subject_hours(df_daily)

    weekly_df = dimp.generate_weekly_hours_dataframe(df_clean)
    data.add_weekly_hours(weekly_df)
    return True

def import_current_year_csv():
    folder_path, file_name = dimp.select_current_year_file()
    print(f"Current year file:\n{folder_path}/{file_name}")
    
    raw_df = dimp.csv_file_to_df(chosen_file=file_name, folder_path=folder_path)

    df_clean = dimp.basic_cleaning(raw_df)
    df_edit = dimp.edit_course_params(df=df_clean)
    
    data.add_main_data(df_edit)

    df_daily = dimp.basic_to_daily_clean(df_edit)
    data.add_subject_hours(df_daily)

    weekly_df = dimp.generate_weekly_hours_dataframe(df_clean)
    data.add_weekly_hours(weekly_df)
    return True

print("Program start.")
main()