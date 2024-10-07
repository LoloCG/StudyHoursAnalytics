import core.data_import as dimp
import data.sqlite_handler as data
import core.data_analysis as dan
import CLI_native_tools as clin
import json
from interface.kivy_main import MainWindows
from PyLogger.basic_logger import LoggerSingleton

def main():
    start_seq = StartSequence()
    MainWindows(start_seq, AppMenuInterface).run()

class AppMenuInterface:
    def plot_daily_hours(self): # will be future option in the main menu
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

class StartSequence:
    def start_db_check(self):
        exists, has_rows = data.check_table()
        logger.debug(f"exists={exists}, has_rows={has_rows}")

        if not has_rows: # No db, it needs to import files
            logger.info(f"Database does not contain any data")
            past_courses, current_course_dict = dimp.check_json_courses_data() # check existence of config for auto loading.

            if past_courses is None:
                self.file_paths = dimp.get_files_from_input_path() # and execute further logic with them
            
            else:
                for course_file in past_courses:
                    raw_df = dimp.csv_file_to_df(course_file)
                    df_edit = self.edit_course_params(df=raw_df, file_name=course_file)
                    self.add_df_to_tables(df=df_edit)
                    
            if current_course_dict:
                raw_df = dimp.csv_file_to_df(
                    chosen_file=current_course_dict['csv name'], # 4º FarmaNutr TDL_Log
                    folder_path=current_course_dict['folder path']) #G:\Mi unidad\24-25-4ºFarmaNutr
                
                # df_edit = self.edit_course_params(df=raw_df,file_name=current_course_dict['csv name'])
                self.upsert_current_year_table(df=raw_df, file_name=current_course_dict['csv name'])
            else:
                # This will later contain the logic of selection of current year files and their cleaning... todo in future code...
                pass
                # folder_path, file_name = dimp.select_current_year_file()

    def import_selected_courses(self, selected_files):
        dict_df = {}
        for file in selected_files:
            raw_df = dimp.csv_file_to_df(file)
            logger.debug(f"Processing dataframe for {file}")
            dict_df[file] = raw_df 
            # self.edit_course_params(df=raw_df,file=file)
        return dict_df

    def add_df_to_tables(self, df):
        data.add_main_data(df)
        
        df_daily = dimp.basic_to_daily_clean(df)
        data.add_subject_hours(df_daily)

        weekly_df = dimp.generate_weekly_hours_dataframe(df)
        data.add_weekly_hours(weekly_df)
        return True

    def edit_course_params(self, df, file_name):
        df_clean = dimp.basic_cleaning(df)
        df_edit = dimp.edit_course_params(df=df_clean, file=file_name)
        return df_edit
    
    def select_current_year(self):
        folder_path, file_name = dimp.select_current_year_file()
        df = dimp.csv_file_to_df(chosen_file=file_name, folder_path=folder_path)
        self.upsert_current_year_table(df=df, file_name=file_name)

    def upsert_current_year_table(self, df, file_name):
        df_edit = self.edit_course_params(df=df, file_name=file_name)

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
        
        logger.info("Finalized current course import/update")

        return True

logger_instance = LoggerSingleton(main_log_level='DEBUG', disable_third_party=True)
logger_instance.set_third_party_loggers_level(level='ERROR')
logger = logger_instance.get_logger()
logger.info("Starting main sequence...")
main()

# weekly_df = dimp.generate_weekly_hours_dataframe(df_clean)
# data.add_weekly_hours(weekly_df)
# df_pivot = dan.pivoter(weekly_df)
# dan.plot_week_hours_barchart(df_pivot)
