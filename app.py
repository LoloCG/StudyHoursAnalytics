import core.data_import as dimp
import data.sqlite_handler as data
import core.data_analysis as dan
import CLI_native_tools as clin
import json
import interface.kivy_main as kivy_main

def main():
    kivy_main.MainWindows().run()
    
class StartSequence:
    def __init__(self):
        exists, has_rows = data.check_table()
        # logger.debug(f"exists={exists}, has_rows={has_rows}")

        if not has_rows: # No db, it needs to import files
            # logger.info(f"Database does not contain any data")
            # check existence of config for auto loading.
            past_courses, current_course_dict = dimp.check_json_courses_data()

            if past_courses is None:
                file_paths = dimp.get_files_from_input_path() # The UI should ask to select from these, and execute further logic with them

            else:
                for course_file in past_courses:
                    raw_df = dimp.csv_file_to_df(file)
                    self.process_df(df=raw_df)

            if current_course_dict:
                raw_df = dimp.csv_file_to_df(
                    chosen_file=current_course_dict['csv name'], 
                    folder_path=current_course_dict['folder path'])
                self.process_df(df=raw_df)
            else:
                # This will later contain the logic of selection of current year files and their cleaning... todo in future code...
                pass
                # folder_path, file_name = dimp.select_current_year_file()

    def process_selected_past_courses(self, selected_files):
        for file in selected_files:
            raw_df = dimp.csv_file_to_df(file)
            self.process_df(df=raw_df)
        return self

    def process_df(self, df):
        df_clean = dimp.basic_cleaning(df)
        df_edit = dimp.edit_course_params(df=df_clean, file=file) # this should be something that also requires the interface to interact.
        data.add_main_data(df_edit)
        
        df_daily = dimp.basic_to_daily_clean(df_edit)
        data.add_subject_hours(df_daily)

        weekly_df = dimp.generate_weekly_hours_dataframe(df_clean)
        data.add_weekly_hours(weekly_df)
        return True

    def edit_course_params(self, df, file_name):
        df_edit = dimp.edit_course_params(df=df_clean, file=file_name)
        return df_edit
    
    def upsert_current_year_table(self, df, file_name):
        df_clean = dimp.basic_cleaning(df)
        
        df_edit = self.edit_course_params()

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

def plot_daily_hours(): # will be future option in the main menu
    # logger.info(f"Plotting daily hours graph")
    df_daily = data.get_df_periods(data_series='daily')
    
    config = None
    with open('config.json', 'r') as file:
        config = json.load(file)
    
    current_course_file = config['Current year']['csv name']
    current_course = config[current_course_file]['Course Name']
    # logger.debug(f"Current course selected={str(current_course)}")
    dan.plot_daily_subj_hours_line(df_daily, current_course=current_course, add_avg=True, roll_avg=7)
    return


# logger.info("Starting main sequence...")
main()

# weekly_df = dimp.generate_weekly_hours_dataframe(df_clean)
# data.add_weekly_hours(weekly_df)
# df_pivot = dan.pivoter(weekly_df)
# dan.plot_week_hours_barchart(df_pivot)


def main_menu_loop(): # NOT USED ANYMORE
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
