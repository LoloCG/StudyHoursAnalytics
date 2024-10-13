import os
os.environ['KIVY_LOG_MODE'] = 'PYTHON'
from kivy.core.window import Window
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from PyLogger.basic_logger import LoggerSingleton

logger = LoggerSingleton().get_logger()


class FileSelectionScreen(BoxLayout): # not completed yet
    def __init__(self, start_seq):
        super(FileSelectionScreen, self).__init__()
        self.orientation = 'vertical'

        Window.size = (450, 300)
        Window.clearcolor = (0.1, 0.1, 0.1, 1)

        self.start_seq = start_seq

        label = Label(
            text="Please select files to import.",
            size_hint=(1, None),
            height=60,
            padding=(20, 50))
        self.add_widget(label)

        self.selected_files = []

        scroll_view = ScrollView(size_hint=(1, 1))

        scroll_layout = GridLayout(
            cols=2,
            size_hint_y=None, # This allows the layout to grow vertically
            spacing=30,
            padding=(20, 20)
            )
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))

        file_paths = self.start_seq.manual_import_past_courses # Ensure the height grows with content

        self.checkbox_mapping = {}

        for file in file_paths:            
            file_name = str(file.name)
            label = Label(
                size_hint_x=0.7,
                text=file_name,
                height=40)

            checkbox = CheckBox(
                size_hint=(0.3, None),
                size=(30, 30))
            self.checkbox_mapping[checkbox] = file_name

            scroll_layout.add_widget(label)
            scroll_layout.add_widget(checkbox)

        scroll_view.add_widget(scroll_layout)
        self.add_widget(scroll_view)

        import_button = Button(
            text="Import files",
            padding=(20, 40),
            size_hint=(1, None),
            height=50)
        
        import_button.bind(on_press=self.import_selected)
        self.add_widget(import_button)

    def import_selected(self, instance):
        selected_files = [file_name for checkbox, file_name in self.checkbox_mapping.items() if checkbox.active]
        logger.debug(f"Selected files for import: {selected_files}")
        dict_df = self.start_seq.import_selected_courses(selected_files=selected_files)

        self.clear_widgets()

        for df_file, df in dict_df.items():
            # self.course_params_edit(dict_df)

            df_clean = self.start_seq.edit_course_params(df=df, file_name=df_file)
            self.start_seq.add_df_to_tables(df=df_clean)

        logger.info(f"Files added to db tables.")
        
        self.start_seq.select_current_year()
        return

    def course_params_edit(self, dict_df):
        self.cols = 2
        self.rows = 3

        course_name_input = TextInput(
            text='Enter course Name',
            size_hint=(1, None),
            height=40  # Set a fixed height for single-line input
        )
        self.add_widget(course_name_input)

        course_date = TextInput(
            text='Enter course date',
            size_hint=(1, None),
            height=40  # Set a fixed height for single-line input
        )
        self.add_widget(course_name_input)

class MainMenuLayout(BoxLayout):
    def __init__(self, AppMenuInterface):
        super(MainMenuLayout, self).__init__()
        self.menu_interface = AppMenuInterface()
        
        Window.size = (300, 250)
        Window.clearcolor = (0.1, 0.1, 0.1, 1)

        self.orientation='vertical'
        self.spacing=10
        self.padding=10
        
        top_label = Label(
            text ="Study Hours Analytics",
            padding=(40, 40),
            size_hint=(1, None),
            height=100)
            
        self.add_widget(top_label)

        buttons_layout = self.generate_options_buttons()
        self.add_widget(buttons_layout)

    def generate_menu_stats(self, instance):
        self.menu_interface.get_basic_stats()
        pass

    def generate_options_buttons(self):
        buttons_layout = GridLayout(
            cols=1, size_hint_y=None
        )
        buttons_layout.bind(minimum_height=buttons_layout.setter('height'))  # Ensure it adjusts its height to fit children

        options_dict = {
            'Display daily hours': self.plot_daily_hours_action,  # 'Update Course Data'
            'Display weekly hours': self.plot_weekly_hours_action, 
            'Update Course Data': self.update_course_data,
            'Get basic data': self.generate_menu_stats,
            }

        for option, funct in options_dict.items():
            option_btn = Button(
                text=option,
                padding=(20, 40),
                size_hint=(1, None),
                height=50
                )

            option_btn.bind(on_press=funct)

            buttons_layout.add_widget(option_btn)

        return buttons_layout

    def update_course_data(self, instance):
        self.menu_interface.update_current_course()
        return

    def plot_daily_hours_action(self, instance):
        self.menu_interface.plot_daily_hours()
        return

    def plot_weekly_hours_action(self, instance):
        self.menu_interface.plot_weekly_hours()
        return

class MainWindows(App):
    def __init__(self, start_seq, AppMenuInterface):
        super(MainWindows, self).__init__()
        self.start_seq = start_seq
        self.AppMenuInterface = AppMenuInterface

    def build(self):
        result = self.start_seq.start_sequence_check()
        if not result:
            logger.debug("Running MainMenuLayout")
            return MainMenuLayout(self.AppMenuInterface)

        else:
            logger.debug("Running FileSelectionScreen")
            return FileSelectionScreen(self.start_seq)  
