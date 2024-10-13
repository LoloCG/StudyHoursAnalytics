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


    # logger.info(f"Plotting daily hours graph")
    # df_weekly = data.get_df_periods(data_series='weekly')
    # dan.plot_week_hours_barchart(df_weekly)

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

    def update_current_course(self):
        logger.info(f"Updating current course data.")
        start_seq = StartSequence()
        df, file_name = start_seq.select_current_year()
        df_edit = start_seq.edit_course_params(df=df, file_name=file_name)
        start_seq.upsert_current_year_table(df=df_edit)

    def get_basic_stats(self):
        import pandas as pd

        df = data.get_df_periods(data_series='daily')

        # config = None
        # with open('config.json', 'r') as file:
        #     config = json.load(file)
        
        # current_course_file = config['Current year']['csv name']
        # current_course = config[current_course_file]['Course Name']
        
        df_sum = df.groupby('Date', as_index=False)['Time Spent (Hrs)'].sum()

        last_day = pd.to_datetime(df_sum['Date'].max()).strftime('%d-%m-%Y')
        last_day_tot_hours = df_sum.loc[df_sum['Date'].idxmax(), 'Time Spent (Hrs)']

        print(f"last day: {last_day}, with {last_day_tot_hours}")
        
    def plot_weekly_hours(self):
        logger.info(f"Plotting daily hours graph")
        df_weekly = data.get_df_periods(data_series='weekly')

        dan.plot_week_hours_barchart(df_weekly)

class StartSequence:
    def start_sequence_check(self):
        exists, has_rows = data.check_table()
        logger.debug(f"database table: exists={exists}, has_rows={has_rows}")

        if not has_rows:
            logger.info(f"Database does not contain any data.")
            past_courses, current_course_dict = dimp.check_json_courses_data()
            
            if past_courses and current_course_dict:
                logger.info(f"JSON config contains past and current course data.")
                self.autoimport_past_from_json(past_courses) 
                logger.info(f"Correctly imported past course data.")     
                self.autoimport_current_from_json(current_course_dict)
                return None
            else:
                logger.warning(f"JSON config does NOT contain current or past course data.")
                pass
                
        if has_rows:
            logger.info(f"Database contains existing data.")
            df, file_name = self.select_current_year()
            df_edit = self.edit_course_params(df=df, file_name=file_name)
            self.upsert_current_year_table(df=df_edit)
            return None

    def autoimport_past_from_json(self,past_courses):
        for course_file in past_courses:
            raw_df = dimp.csv_file_to_df(course_file)
            df_edit = self.edit_course_params(df=raw_df, file_name=course_file)
            self.add_df_to_tables(df=df_edit)

    def autoimport_current_from_json(self,current_course_dict):
        folder_path, file_name = dimp.select_current_year_file()
        raw_df = dimp.csv_file_to_df(chosen_file=file_name, folder_path=folder_path)
        df_edit = self.edit_course_params(df=raw_df, file_name=file_name)
        self.upsert_current_year_table(df=df_edit)

    def manual_import_past_courses(self):
        file_paths = dimp.get_files_from_input_path()
        return file_paths

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
        return df, file_name

    def upsert_current_year_table(self, df):
        logger.debug(f"Upserting current year df to db table.")
        tm = data.TableManager()
        with tm:
            unique_cols = ['Start Date', 'Start Time', 'End Time']
            tm.select_table(table_opt='main')
            tm.upsert_to_table(
                df=df, 
                unique_cols=unique_cols)
            
        df_daily = dimp.basic_to_daily_clean(df)
        with tm:
            unique_cols = ['Course', 'Period', 'Subject', 'Day']
            tm.select_table(table_opt='day')
            tm.upsert_to_table(df=df_daily, unique_cols=unique_cols)
        
        weekly_df = dimp.generate_weekly_hours_dataframe(df)
        with tm:
            unique_cols = ['Period', 'Week', 'Subject']
            tm.select_table(table_opt='week')
            tm.upsert_to_table(df=weekly_df, unique_cols=unique_cols)

        logger.info("Finalized current course import/update")
        
        return True

logger_instance = LoggerSingleton()
logger_instance.set_logger_config(level='DEBUG')
logger_instance.set_third_party_loggers_level(level='ERROR')
logger = logger_instance.get_logger()
logger.info("Starting main sequence...")
main()


# df_pivot = dan.pivoter(weekly_df)
# dan.plot_week_hours_barchart(df_pivot)
