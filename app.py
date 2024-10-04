import core.data_import as dimp
import data.sqlite_handler as data
import core.data_analysis as dan
import CLI_native_tools as clin
import json
from core.logger import setup_logger, set_logger_config, set_third_party_loggers_level

def main():
    exists, has_rows = data.check_table()
    logger.debug(f"exists={exists}, has_rows={has_rows}")

    main_menu_opts = None
    if not has_rows:
        logger.info(f"Database does not contain any data")
        start_course_import()
        main_menu_opts

    while True:
        choice = main_menu_loop()
        if choice is None: break

# df_pivot = dan.pivoter(weekly_df)
# dan.plot_week_hours_barchart(df_pivot)

def main_menu_loop():
    option_str_list = [
        'Display daily study Hours',
        # 'Import .CSV file',
        "Import/update current year's .CSV file",
        # 'Display Weekly Study Hours'
    ]
    choice = clin.ask_loop_show_and_select_options(option_str_list=option_str_list, exit_msg='Exit program.')
    if choice is None: return None

    options_funcs = [
        lambda: plot_daily_hours(),
        # lambda: import_csv_to_database(), # Change to another abstraction function that includes the files...
        lambda: import_current_year_csv()
        ]
    clin.call_function_from_choice(user_choice=choice, options_funcs=options_funcs)
    return True

def plot_daily_hours():
    logger.info(f"Plotting daily hours graph")
    df_daily = data.get_df_periods(data_series='daily')
    
    config = None
    with open('config.json', 'r') as file:
        config = json.load(file)
    
    current_course_file = config['Current year']['csv name']
    current_course = config[current_course_file]['Course Name']
    logger.debug(f"Current course selected={str(current_course)}")
    dan.plot_daily_subj_hours_line(df_daily, current_course=current_course, add_avg=True, roll_avg=7)
    return

def start_course_import():
    file_choice = None
    past_courses, current_course_dict = dimp.check_json_courses_data()
    print(f"dict: {current_course_dict}")
    
    main_menu_opts = None
    if past_courses is None:
        file_choice = dimp.show_and_select_csv()
        import_csv_to_database(file_choice)
    else:
        for course_file in past_courses:
            import_csv_to_database(course_file)
        if current_course_dict:
            import_current_year_csv(
                folder_path=current_course_dict['folder path'], 
                file_name=current_course_dict['csv name'])

def import_csv_to_database(file_choice=None):
    if file_choice == None :
        file_choice = dimp.show_and_select_csv()

    raw_df = dimp.csv_file_to_df(file_choice)

    logger.info(f"Performing cleaning of {file_choice}")
    df_clean = dimp.basic_cleaning(raw_df)
    df_edit = dimp.edit_course_params(df=df_clean, file=file_choice)
    
    data.add_main_data(df_edit)

    df_daily = dimp.basic_to_daily_clean(df_edit)
    data.add_subject_hours(df_daily)

    weekly_df = dimp.generate_weekly_hours_dataframe(df_clean)
    data.add_weekly_hours(weekly_df)
    return True

def import_current_year_csv(folder_path=None, file_name=None):
    if folder_path == None and file_name == None:
        folder_path, file_name = dimp.select_current_year_file()
    
    raw_df = dimp.csv_file_to_df(chosen_file=file_name, folder_path=folder_path)

    logger.info(f"Performing cleaning of {file_name}")
    df_clean = dimp.basic_cleaning(raw_df)
    df_edit = dimp.edit_course_params(df=df_clean, file=file_name)
    
    tm = data.TableManager()
    with tm:
        unique_cols = ['Start Date', 'Start Time', 'End Time']
        tm.select_table(table_opt='main')
        tm.upsert_to_table(
            df=df_edit, 
            unique_cols=unique_cols)
        
    df_daily = dimp.basic_to_daily_clean(df_edit)
    with tm:
        unique_cols = ['Course', 'Period', 'Subject', 'Day']
        tm.select_table(table_opt='day')
        tm.upsert_to_table(df=df_daily, unique_cols=unique_cols)
    
    return True
    # weekly_df = dimp.generate_weekly_hours_dataframe(df_clean)
    # data.add_weekly_hours(weekly_df)

logger = setup_logger()
set_logger_config(level='INFO')
logger.info("Starting main sequence...")
set_third_party_loggers_level()
main()