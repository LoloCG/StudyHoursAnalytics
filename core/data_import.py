import Excel_Tools.import_export_utils as imex 
import Data_Cleaning.data_cleaning_utils as dclean
import pandas as pd
from pathlib import Path
import CLI_native_tools as clin
input_folder_path = Path(r'C:\Users\Lolo\Desktop\Programming\GITRepo\StudyHoursAnalytics\data_example') 

def show_and_select_csv():
    files = []
    for item in input_folder_path.iterdir():
        files.append(item.name)
    choice = clin.show_and_select_options(str_list=files)
    
    return files[choice-1]

def csv_file_to_df(chosen_file):
    input_csv = imex.ExcelImporter() 
    input_csv.add_extraction_folder(input_folder_path) 
    input_csv.add_file(chosen_file) 
    df = input_csv.csv_to_dataframe()
    
    return df

def basic_cleaning(df_raw):
    def delete_negative_times(df):
        import numpy as np
        print("Removing negative times, lower than 30s, and other...")
        negval_condition = (df['Time Spent (Hrs)'] < 0) & (df['Type'] == 'Adjusted')
        pos_rows = df[~negval_condition]
        neg_rows = df[negval_condition]

        date_threshold = pd.Timedelta(days=2) # threshold
        time_threshold = 0.5

        for _, neg_row in neg_rows.iterrows():
            close_condition = (
                (abs(pos_rows['Time Spent (Hrs)'] + neg_row['Time Spent (Hrs)']) < time_threshold) & 
                (abs(pos_rows['End Date'] - neg_row['End Date']) < date_threshold)
            )
            pos_rows = pos_rows[~close_condition]

        pos_rows = pos_rows[~(pos_rows['Time Spent (Hrs)'] <= 0.008)]

        return pos_rows
   
    print("Basic Cleaning...")

    df_raw.drop('User ID', axis=1, inplace=True)
    df_raw.drop('Task ID', axis=1, inplace=True)
    df_raw.drop('Comment', axis=1, inplace=True)
    
    cleaner = dclean.DFCleaner(df_raw)

    new_columns = ['Period', 'Subject', 'pathinfo']
    cleaner.split_column(column='Path', separator='\\', new_columns=new_columns, expand=True, drop_old=True)
    cleaner.normalize_column_strings(column='Period')
    cleaner.normalize_column_strings(column='Subject')

    cleaner.convert_df_dates(date_column='Start Date', single_col=True)
    cleaner.convert_df_dates(date_column='End Date', single_col=True)
    cleaner.convert_df_times(time_column='Start Time', single_col=True)
    cleaner.convert_df_times(time_column='End Time', single_col=True)

    cleaner.replace_comma_to_dot(column='Time Spent (Hrs)')

    df_clean = cleaner.dataframe

    df_clean2 = delete_negative_times(df_clean)

    ini_neg = len(df_clean[df_clean['Time Spent (Hrs)'] < 0])
    post_neg = len(df_clean2[df_clean2['Time Spent (Hrs)'] < 0])
    print(f"Deleted {post_neg-ini_neg} negative values, converted removed {len(df_clean2)-len(df_clean)} total rows")

    return df_clean2

def edit_course_params(file, df):
    print(f"Select course name for {file}.")
    course_name = input("Course name: ")
    df['Course'] = course_name
    

    
    while True:
        periods = df['Period'].unique()
        print(f"Edit periods in the course?:")
        choice = clin.ask_loop_show_and_select_options(periods, exit_msg='Continue.')
        if choice == None: 
            print("Continuing...")
            return df
        
        keep_period = input(f"Do you want to keep the period '{periods[choice-1]}'? (Y/N): ").lower()

        if keep_period == "n":
            df = df[df['Period'] != periods[choice-1]]
            print(f"Period '{periods[choice-1]}' removed from dataset.")
            continue
        
        name_change_ask = input(f"Do you want to re-name the period '{periods[choice-1]}'? (Y/N): ").lower()
        if name_change_ask == "y":
            new_period_name = input(f"New name: ")
            df.loc[df['Period'] == periods[choice-1], 'Period'] = new_period_name
            print(f"Period '{periods[choice-1]}' has been renamed to '{new_period_name}'.")
            period_name = new_period_name
            
        else: 
            period_name = periods[choice-1]
    
        earliest_date = df.loc[df['Period'] == period_name, 'Start Date'].min().strftime('%a, %d %b %Y') #.strftime('%d-%m-%Y')
        print(f"Start date of {period_name} = {earliest_date}")
        
        adjust_date = input(f"Do you want to adjust the start date? (Y/N): ").lower()
        
        if adjust_date == "y":
            new_start_date_str = input("Enter the new start date (DD-MM-YY): ")
            new_start_date = pd.to_datetime(new_start_date_str, dayfirst=True).date()

            new_row = {
                'Period':           period_name, 
                'Start Date':       (new_start_date), # the format that is required is 2023-07-18
                'Start Time':       '00:00',
                'Time Spent (Hrs)': 0,
                'End Date':	        new_start_date,
                'End Time':         '00:00',
            } 
            print(f"New row = {new_row}")
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            print(f"Start date for period '{period_name}' updated to {new_start_date.strftime('%a, %d %b %Y')}.")
        df['Course'] = df['Course'].ffill()

def basic_to_daily_clean(df_clean):
    ''' '''
    def fill_missing_days(df, period):
        '''
            Used along the iteration. It selects the period values from the dataframe, 
                obtains the range of days from start to finish, merges it with the period df, 
                and fills the missing values (time spent = 0, periods with those that belong to it).
        '''
        df_period = df[df['Period'] == period]

        period_min = pd.Timestamp(df_period['Start Date'].min())
        period_max = pd.Timestamp(df_period['Start Date'].max())
        
        full_range = pd.DataFrame({'Start Date': pd.date_range(start=period_min, end=period_max)})

        df_period = df[df['Period'] == period].copy()
        df_period['Start Date'] = pd.to_datetime(df_period['Start Date'])
        full_range['Start Date'] = pd.to_datetime(full_range['Start Date'])
        
        df_merged = pd.merge(full_range, df_period, on='Start Date', how='left')

        df_merged['Time Spent (Hrs)'] = df_merged['Time Spent (Hrs)'].fillna(0)
        df_merged['Period'] = df_merged['Period'].ffill()

        df_merged['Day'] = df_merged['Start Date'].apply(lambda x: (pd.Timestamp(x) - period_min).days)
        
        return df_merged

    wanted_cols = ['Course', 'Period', 'Subject', 'Time Spent (Hrs)', 'Start Date']
    df = df_clean[wanted_cols]

    df.loc[:, 'Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce').dt.date

    df = df.groupby(['Course','Period','Subject', 'Start Date'], as_index=False,dropna=False).sum()

    df_list = []
    for period in df['Period'].unique():
        df_filled = fill_missing_days(df=df, period=period)
        df_list.append(df_filled)

    # Concatenates the list of df made by the iteration
    df = pd.concat(df_list, ignore_index=True)
    
    # changes the date into the chosen format
    df['Date'] = df['Start Date'].dt.strftime('%d/%m/%Y')
    df = df.drop(columns=['Start Date'])
    return df

def generate_weekly_hours_dataframe(df_clean):
    ''' '''
    wanted_cols = ['Period', 'Subject', 'Time Spent (Hrs)', 'Start Date', 'End Date', 'Start Time', 'End Time']
    df = df_clean[wanted_cols]

    filter_values = ['1St Semester', '2Nd Semester']
    filter_col = 'Period'
    df = df[df[filter_col].isin(filter_values)]

    df['Start Date'] = pd.to_datetime(df['Start Date'])

    df['Week'] = df['Start Date'].dt.to_period('W-SUN').astype(str)

    df = df.groupby(['Period', 'Subject', 'Week'])['Time Spent (Hrs)'].sum().reset_index()
    # df = df.groupby('Week')['Time Spent (Hrs)'].sum().reset_index()
    
    weekly_df = df

    return weekly_df

