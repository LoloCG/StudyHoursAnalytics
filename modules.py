import matplotlib.pyplot as plt
import pandas as pd
import os
import sqlite3

# ========================= MODULE_matplot_pandas/DataPlotter =========================
# =================================== 2024.02.09.1 =========================
class DataPlotter: 
    def __init__(self, dataframe: pd.DataFrame):
        self.dataframe = dataframe

        print()

    def manual_set_chart_titles(self,xy_labels,chart_title):
        self.x_label = xy_labels[0]
        self.y_label = xy_labels[1]

        self.chart_title = chart_title
    
    def identify_column_hierarchy(self,verbose=False):
        self.categorical_columns = None
        self.numerical_columns = None
        self.highest_hierarchy_column = None

        df = self.dataframe
        cat_cols = []
        Num_col = None
        num_uniq_val = 0
        first_hier_col = None

        for colname in df:
            coltype = str(df[colname].dtype)
            if coltype == 'object': 
                cat_cols.append(colname)

                if df[colname].value_counts().mean() > num_uniq_val:
                    
                    num_uniq_val = df[colname].value_counts().mean()
                    first_hier_col = colname

            elif coltype in ['float64','int64']:
                Num_col = colname

        if verbose: print(f"Categorical columm with highest hierarchy: {first_hier_col}")

        self.highest_hierarchy_column = first_hier_col        
        self.categorical_columns = cat_cols
        self.numerical_columns = Num_col

    def plot_stacked_bar_chart(self):
        df = self.dataframe

        figsize = (10,6)
        legend_title = 'Subject'
        colormap='tab20'
        
        ax = df.plot(kind='bar', width=0.75, stacked=True, figsize=figsize, colormap=colormap)
        
        # Get the legend handles and labels
        # handles, labels = ax.get_legend_handles_labels()

        subjects = df.columns.get_level_values('Subject').unique()
        subjects = df.columns.get_level_values('Subject').unique()
        subjects_list = list(subjects)
        # subjects = df['Subject'].unique()
        print(f"\tDEBUG: subjects from df:\n{subjects_list}\n")

        # Set the legend with the filtered handles and labels
        # ax.legend(subjects, subjects, title='Subject', loc='best')
        
        plt.title(self.chart_title,fontsize=16)
        plt.xlabel(self.x_label,fontsize=14)
        plt.ylabel(self.y_label,fontsize=14)

        # plt.legend(title=legend_title, loc='best')
        
        ticks = range(0, len(df.index), 4)
        ax.set_xticks(ticks)
        ax.set_xticklabels([df.index[i] for i in ticks], rotation=45,ha='right')
        # plt.style.use('seaborn-v0_8-pastel')

        plt.tight_layout()

        plt.show()

    def plot_hierarchical_categorical_bar_chart(self):
        """
        Plots a bar chart using a DataFrame with two categorical columns and one numerical column,
        where one categorical column represents a higher hierarchy.

        Parameters:
        df (pd.DataFrame): DataFrame containing the data to plot. It should contain two categorical columns 
                        (one representing a higher hierarchy) and one numerical column.
        """
        # This is to be replaced later by a list parameter in the function...
        catCol1 = self.highest_hierarchy_column 
        catCol2 = list(set(self.categorical_columns) - {catCol1})[0]
        numCol = self.numerical_columns

        df = self.dataframe

        periods = df[catCol1].unique()

        print(f"Plotting bar chart of {numCol} per {catCol2}, separated by {catCol1}...")

        x_values_dict = {period: [] for period in periods}    # Initialize lists to store x values for each period

        fig, ax = plt.subplots(figsize=(10, 6))

        n = 1
        for period in periods:
            filt_df = df[df[catCol1] == period]  

            for subject in filt_df[catCol2]:
                # DEBUG: print(f"{n} - period: {period}, Subject: {subject}") 
                x_values_dict[period].append(n)
                n += 1

            x_values = x_values_dict[period]
            y_values = df.loc[df[catCol1] == period, numCol]
            ax.bar(x_values, y_values, width=0.8, label=period, align='center')

        # Customizing the x-ticks to match the subjects
        all_subjects = list(df[catCol2])
        ax.set_xticks(range(1, n))
        ax.set_xticklabels(all_subjects, rotation=45)

        ax.legend(title=catCol1)
        ax.set_xlabel(catCol2)
        ax.set_ylabel(numCol)
        chartTitle = numCol + " per " + catCol2
        plt.legend(title=chartTitle)
        plt.xticks(rotation=45)
        plt.tight_layout() 
        plt.show()

# ========================= MODULE_SQLite_functions/DatabaseHandler =========================
# =================================== 2024/02/09 =========================

class DatabaseHandler:
    def __init__(self, db_dir, db_name=None):
        """Initialize with the database name and directory.

        Args:
            db_name (str): The name of the database file.
            db_dir (str): The directory where the database file is stored.
        """
        if db_dir is None:
            raise ValueError("Database directory must be provided upon creation")

        self.db_name = db_name
    
        if self.db_name is None:
            self.db_name = 'Database.db'
            print(f"No database name was given. Using '{self.db_name}' as the name")
        elif not isinstance(db_name, str):
            raise ValueError(f"\ndb_name should be a string.\ndb_name type is {isinstance(self.db_name,str)}\n")    
        elif not self.db_name.endswith('.db'):
            self.db_name = self.db_name + ".db"

        self.db_path = os.path.join(db_dir, self.db_name)
        self.connector = None
        self.cursor = None
        self.database_name = None
        self.main_table_name = None
        self.db_table_names = []

    def create_db_table(self, table_items, table_name=None, verbose=False):
        '''
        table_items (dict), key = str, item = SQLdatatype
        mainTable_name (str)

        '''
        if not self.check_db_existance():
            print(f"Setting database {self.db_name} with direction {self.db_path}")

        self.connector = sqlite3.connect(self.db_path)
        self.cursor = self.connector.cursor()

        if table_name is None and self.main_table_name is None:
            self.main_table_name = 'main_table'
            table_name = self.main_table_name
        elif self.main_table_name is None:
            self.main_table_name = table_name
            print(f"Setting the main table name as {table_name}")

        print(f"Creating {self.db_name} database table with name '{table_name}'...")

        if verbose:
            print("Items in table:")
            for item, types in table_items.items():
                print(f"\t{item}")

        columns = ", ".join([f'"{col}" {dtype}' for col, dtype in table_items.items()])
        
        create_table_query = f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {columns}
        )
        '''
        self.cursor.execute(create_table_query)
        self.connector.commit()

    def convert_dict_valType_to_sqlType(self, dtype_dict,verbose=False):
        import numpy as np
        import pandas as pd

        if verbose: print("Converting values from dtype to SQL type values...")
        
        sql_dict = {}
        for key, item in dtype_dict.items():

            sql_type = None
            # Use pandas and numpy functions to determine the dtype category
            if pd.api.types.is_integer_dtype(item) or isinstance(item, int):
                sql_type = 'INTEGER'
            elif pd.api.types.is_float_dtype(item) or isinstance(item, str):
                sql_type = 'REAL'
            elif pd.api.types.is_string_dtype(item) or item == 'O':  # 'O' for object types
                sql_type = 'TEXT'
            elif pd.api.types.is_datetime64_any_dtype(item):
                sql_type = 'TEXT'  # alternatively, use DATETIME format if required...
            elif item == list:
                print(f"!!! - List datatype in dictionary ({key}). Will be stored as concatenated string.")
                sql_type = 'TEXT'
            else:
                raise ValueError(f"Unrecognized dtype ({type(item)}) key: {key}")
                pass
            #print(f"DEBUG: Key ({key}) set as {sql_type}")
            
            sql_dict[key] = sql_type
        
        return sql_dict

    def check_db_existance(self): 
        """Check if the SQLite database file already exists.

        Returns:
            bool: True if the database exists, False otherwise.
        """
        if os.path.exists(self.db_path):
            #print(f"db path is: {self.db_path}")
            return True 
        else:
            print(f"Database does not exist.")
            return False

    def table_has_items(self, table_name=None):
        if not table_name:
            table_name = self.main_table_name
        
        self.check_db_connection(connect=True)
        self.cursor.execute(f"SELECT COUNT(1) FROM {table_name};")
        return self.cursor.fetchone()[0] > 0

    def insert_data_from_df(self, dataframe,table_name=None, verbose=False):
        import pandas as pd
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError(f"The variable passed to insert data to database is not dataframe type. It is '{type(dataframe)}'")
        
        if not table_name:
            table_name = self.main_table_name

        try:
            dataframe.to_sql(table_name, self.connector, if_exists='append', index=False)
            self.connector.commit()
            if verbose: print(f"Data inserted successfully into {table_name}")
            
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            self.connector.rollback()

    def close_connection(self):
        print(f"Closing connection to database.")
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.connector:
            self.connector.close()
            self.connector = None

    def check_db_connection(self, connect=False):
        if self.connector is None or self.cursor is None:
            if connect == True:
                # print(f"DEBUG: Connector or cursor is None, creating connection to db")
                self.connector = sqlite3.connect(self.db_path)
                self.cursor = self.connector.cursor()

    def retrieve_rows_as_dicts(self, search_parameters_dict, table_name=None):
        '''
            Retrieves data from the specified database table based on the parameters provided 
                in the search_parameters_dict. Each row of the result is returned as a dictionary 
                with column names as keys and corresponding row values as values.
            
            Parameters:
                search_parameters_dict: A dictionary where the key is the column name and 
                    the value is the value to search for in that column.
                table_name: (Optional) The name of the table to query. If not provided, 
                    defaults to the main_table_name.

            Returns: 
                A list of dictionaries, where each dictionary represents a row from 
                    the database. Returns None if an error occurs.
        '''

        if table_name is None:
            table_name = self.main_table_name

        try:
            print(f"Retrieving data from {table_name}...")
            
            sql_query = f"SELECT * FROM {table_name} WHERE "

            value_list = []
            n = 0
            for column, value in search_parameters_dict.items():
                value_list.append(value)
                sql_query += str(column) + ' = ?'
                n += 1
                if n < len(search_parameters_dict):
                    sql_query += ' AND '
            
            self.cursor.execute(sql_query, value_list)
            rows = self.cursor.fetchall()

            # Get column names from the cursor description 
            column_names = [description[0] for description in self.cursor.description]

            # Convert each row to a dictionary
            result_dicts = [dict(zip(column_names, row)) for row in rows]
            
            return result_dicts

        except sqlite3.Error as e:
            # Print the error message
            print(f"An error occurred: {e}")
            return None

    def get_last_table_value_of_columns(self, column_names, columns_to_order, table_name=None):
        if table_name is None:
            table_name = self.main_table_name
        
        query = f"""
            SELECT {column_names}
            FROM {table_name}
            ORDER BY {columns_to_order} DESC
            LIMIT 1;
            """
        
        if self.cursor is None:
            self.connector = sqlite3.connect(self.db_path)
            self.cursor = self.connector.cursor()

        self.cursor.execute(query)
        result = self.cursor.fetchone()
            
        # If only one column is selected, return the value directly
        if len(column_names.split(',')) == 1:
            return result[0] if result else None
        else:
            return result if result else None

    def retrieve_all_data_as_df(self, tableName=None):
        if tableName is None and self.main_table_name is None:
            raise BaseException(f"Database table name and main table name are None.")
        elif tableName is None:
            print(f"DEBUG: table name is None when retrieving data...\ntable name used is {self.main_table_name}")
            tableName = self.main_table_name

        if self.connector is None or self.cursor is None:
            print(f"DEBUG: connector or cursor is None, creating connection to db")
            self.connector = sqlite3.connect(self.db_path)
            self.cursor = self.connector.cursor()
        else:
            print(f"DEBUG: Using existing connection and cursor")

        self.cursor.execute(f'SELECT * FROM {tableName}')

        # Fetch all rows
        rows = self.cursor.fetchall()
        
        # Get column names from the cursor
        column_names = [description[0] for description in self.cursor.description]
        
        import pandas as pd
        df = pd.DataFrame(rows, columns=column_names)
        
        return df

    def check_table_existance(self, table_name, verbose=False):
        
        '''
        if self.connector == None: 
            print(f"While checking for connector in table existance, it shows None")
            
        '''
        self.cursor.execute(f"PRAGMA table_info({table_name});")

        # Fetch the results
        result = self.cursor.fetchall()

        # Check if the table exists
        if result:
            if verbose: print(f"Table '{table_name}' exists.")
            return True
        else:
            if verbose: print(f"Table '{table_name}' does not exist.")
            return False

    def insert_data_from_dict(self, data_dict, table_name,verbose=False):
        
        if not table_name:
            table_name = self.main_table_name

        # Construct the SQL query components
        keys = ", ".join(data_dict.keys())
        question_marks = ", ".join(["?" for _ in data_dict])
        values = tuple(data_dict.values())

        insert_query = f"INSERT INTO {table_name} ({keys}) VALUES ({question_marks})"
        
        # Execute the query with error handling
        try:
            self.cursor.execute(insert_query, values)
            self.connector.commit()
            if verbose: 
                print(f"Data inserted successfully into {table_name}")
                print(f"\tinserted: {len(values)} values")
            
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            self.connector.rollback()

# ========================= MODULE_pandas_basic/DataCleaner =========================
# =================================== 2024/02/09 =========================
class DataCleaner:
    def __init__(self, dataframe: pd.DataFrame):
        self.dataframe = dataframe

    def check_columnName_present(self,columnName):
        try:
            if columnName is None: raise ValueError("Column name cannot be None.")
            
            if columnName not in self.dataframe.columns: raise KeyError(f"Column '{columnName}' does not exist in the DataFrame.")
        
        except (ValueError, KeyError) as e:
            caller = inspect.stack()[1].function
            print(f"Error in function '{caller}': {e}")
            raise
        
        except Exception as e:
            # Catch all other unexpected exceptions
            caller = inspect.stack()[1].function
            print(f"An unexpected error occurred in function '{caller}': {e}")
            raise

    def convert_dataframe_dates(self, dateColumn, removeDateCol=True):
        self.check_columnName_present(dateColumn)
        print("Converting dataframe dates into datatime type...")
        
        df = self.dataframe
        if pd.api.types.is_datetime64_any_dtype(df[dateColumn]):
            print(f"Column {dateColumn} is already datetime type...")
            return
        
        df['date'] = pd.to_datetime(df[dateColumn])
        # Extract year, month, and day 
        df['year'] = df['date'].dt.year 
        df['month'] = df['date'].dt.month 
        df['day'] = df['date'].dt.day

        if removeDateCol:
            df.drop(dateColumn, axis=1,inplace=True)

        self.dataframe = df

    def normalize_column_strings(self, columnName, normHead=True, normItems=True):
        self.check_columnName_present(columnName)
        df = self.dataframe
        
        if normItems: df[columnName] = df[columnName].str.strip().str.lower().str.title()

        if normHead: df.columns = df.columns.str.strip().str.lower().str.title()

        self.dataframe = df

    def convert_comma_to_dot(self, columnName, replaceWhat=None, replaceWith=None):
        self.check_columnName_present(columnName)
        df = self.dataframe

        if replaceWhat is None and replaceWith is None: #TODO: make this more dynamic... somehow...
            replaceWhat = ','
            replaceWith = '.'
        elif replaceWhat == ',':
            replaceWith = '.' 

        print(f"Replacing '{replaceWhat}' with '{replaceWith}' in column {columnName}")

        # Perform the replacement operation
        df[columnName] = df[columnName].str.replace(replaceWhat, replaceWith).astype(float)

        self.dataframe = df

    def split_column_into_multiple(self, columnName, separator, newColList, expand=True):
        self.check_columnName_present(columnName)
        df = self.dataframe
        print(f"Splitting column '{columnName}' into '{list(newColList)}'...")
        
        separatorNum = len(newColList)-1

        df[newColList] = df[columnName].str.split(separator, n=separatorNum, expand=expand)
        self.dataframe = df

    def show_missing_files(self, returning=False, verbose=False):
        df = self.dataframe

        col_with_empty = {}
        if df.isnull().any().any():
            df_with_empty = df.columns[df.isnull().any()]

            print(f"Columns that have empty values: ") if verbose else None
            for column in df_with_empty:
                empty_sum = df[column].isnull().sum()
                print(f"\t'{column}', with {empty_sum}") if verbose else None
                col_with_empty[column] = int(empty_sum)
                
                if empty_sum == len(df):
                    print(f"column '{column}' is completely empty ") if verbose else None
                    #empty_col.append(column)
        else:           
            print("No missing values in the dataset.")
            
        if returning:
            return col_with_empty

    def filter_df_column_by_val(self, ColToFilter, FilterValues):
        self.check_columnName_present(ColToFilter)
        print(f"Filtering dataframe for values {list(FilterValues)} located in column '{ColToFilter}'...")

        df = self.dataframe
        df = df[df[ColToFilter].isin(FilterValues)]
        self.dataframe = df

# ========================= MODULE_pandas_basic/DataFrameTransformer =========================
# =================================== 2024/02/09 =========================
class DataFrameTransformer:
    def __init__(self, dataframe: pd.DataFrame):
        self.dataframe = dataframe

    def multiIndex_group(self, colsToGroup):
        '''
        From a dataframe of 3 columns, groups the numerical values by 
            two categorical value columns of a dataframe, returning an index-reset dataframe
        
        Parameters:
            df (dataframe), that is pre-processed. It can include other columns that 
                are not going to be grouped, as the function will only select those that will.
            
            colsToGroup (list), must include 3 column names as string which must be in the following order:
                numerical data, greater categorical data, lower categorical data.
        '''
        print(f"Grouping {colsToGroup[0]} by {colsToGroup[1]} and {colsToGroup[2]}...")

        df = self.dataframe
        df = df[colsToGroup]
        df = df.groupby([colsToGroup[1],colsToGroup[2]]).sum().reset_index()

        self.dataframe = df

# ========================= MODULE_pandas_excel_functions/ExcelDataExtract =========================
# =================================== 2024/02/09 =========================
class ExcelDataExtract:
    def __init__(self, file_folder_dir = None, chosen_file = None):
        self.main_dir = os.path.dirname(os.path.abspath(__file__))
        self.file_folder_dir = file_folder_dir
        self.chosen_file = None
        self.file_type = None

        self.excels_in_folders = []

        self.selected_sheets = None

        self.dataframe = None
        self.dataframe_type = None

    def load_excel_to_dataframe_dict(self, selected_sheets=None, importNaN=True):
        df_dict = {}
        full_file_path = os.path.join(self.file_folder_dir, self.chosen_file)

        sheets_to_load = selected_sheets if selected_sheets else self.selected_sheets

        for sheet in self.selected_sheets:
            print(f"loading {sheet} into dataframe dictionary")

            df = pd.read_excel(full_file_path, sheet_name=sheet)
            
            if importNaN: # First drops columns that have NaN or empty string as headers, then columns where all values are NaN
                df = df.loc[:, df.columns.notnull()]
                df = df.loc[:, df.columns != '']
                df = df.dropna(axis=1, how='all')
                
            df_dict[sheet] = df

        self.dataframe = df_dict
        self.dataframe_type = type(self.dataframe) # Ensures that the dataframe type is <class 'dict'>
        
        #DEBUG: print(f"debug. df type: {self.dataframe_type}\n")

    def load_csv_to_dataframe(self, chosen_file, encoding=None, delimiter=None, skiprows=None):
        self.chosen_file = chosen_file

        targetfile_path = os.path.join(self.file_folder_dir, self.chosen_file)
        print(f"Extracting file {chosen_file} from path {targetfile_path}")
        
        df_raw = pd.read_csv(targetfile_path, encoding='utf-16', delimiter='\t', skiprows=1) # TODO: make dynamic selector of encoding, delimiter, skiprows...
        
        #DEBUG: print(f"Extracted df:\n{df_raw.head()}") 
        #DEBUG: print(f"returning type: {type(df_raw)}")

        self.dataframe = df_raw

    def get_folder_excel_files(self, file_folder_dir=None, file_type = None):
        '''
        Searches the folder given for any excel extension file, printing any that exist and returning a list of the file names.
        
        Parameters:
        file_folder_dir (str): The directory to search for Excel files.

        Returns:
        folder_excels (list): a list of strings of the excel files that are located in the folder direction.
        '''
        self.file_folder_dir = file_folder_dir

        if not os.path.exists(file_folder_dir):
            print(f"Directory {file_folder_dir} does not exist.\n")
            return []
        if not os.path.isdir(file_folder_dir):
            print(f"{file_folder_dir} is not a directory.\n")
            return []
        
        folder_files = os.listdir(file_folder_dir)
        self.excels_in_folders = [file for file in folder_files if file.endswith(('.csv', '.xlsx', '.xls', '.xlsm'))]

        print("Files in the folder:")
        for index, file in enumerate(self.excels_in_folders):
            print(f"{index + 1}: {file}")

    def select_excelFile_fromFolder(self, excels_in_folders=None):
        while True:
            try:
                choice = int(input(f"Enter the number of the file you want to open (1-{len(self.excels_in_folders)}): "))
                if 1 <= choice <= len(self.excels_in_folders):
                    file = self.excels_in_folders[choice - 1]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(self.excels_in_folders)}.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")

        print(f"chosen file: {file}")
        
        self.chosen_file = file
    
    def select_excelSheets_fromFile(self, full_file_path=None):
        '''
        '''
        full_file_path = os.path.join(self.file_folder_dir, self.chosen_file)

        # Determines the engine based on file extension
        if full_file_path.endswith('.xlsx') or full_file_path.endswith('.xlsm'):
            excel_file = pd.ExcelFile(full_file_path, engine='openpyxl')
        elif full_file_path.endswith('.xls'):
            excel_file = pd.ExcelFile(full_file_path, engine='xlrd')
        else:
            raise ValueError("Unsupported file format. \nPlease provide a .xlsm, .xlsx, or .xls file.")
            return

        sheet_names = excel_file.sheet_names
        
        for index, sheet in enumerate(sheet_names):
            print(f"{index + 1}: {sheet}")
        
        user_input = input("Select sheets to load (comma-separated numbers, or enter blank for all): ")

        if user_input.strip() == "":
            self.selected_sheets = sheet_names
        else:
            selected_indices = [int(i) - 1 for i in user_input.split(',')]
            self.selected_sheets = [sheet_names[i] for i in selected_indices]
        
        print(f"selected sheets: {str(self.selected_sheets)}")
        print()

    def detect_csv_delimiter(self): # TODO: finish this function
        delimiters = [',', ';', '\\', '\t'] 
        
    def detect_csv_encoding(): # TODO: finish this function
        encodings = ['utf-8', 'utf-8-sig', 'utf-16', 'latin1', 'iso-8859-1', 'cp1252']

    def detect_csv_header_row():
        print("TODO...")
