from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput

# from kivy.uix import Button, BoxLayout, Label, GridLayout, Popup, Screen
# from kivy.uix.actionbar import ActionBar, ActionView, ActionButton, ActionPrevious
# from kivy.core.window import Window
# from kivy.uix.screenmanager import ScreenManager

# Window.clearcolor = (0.1, 0.1, 0.1, 1)

class FileSelectionScreen(GridLayout):
    def __init__(self):




class MainWindows(App):
    def __init__(self)
        
    def build(self):
        start_seq = StartSequence()  # Create orchestrator instance
        return FileSelectionScreen(orchestrator=start_seq)  
        
# class MainMenuLayout(GridLayout):
#     def __init__(self, **kwargs):
#         super(MainMenuLayout, self).__init__(**kwargs)

#         self.cols = 1
#         self.button_1 = Button(text="Button 1")
#         self.button_2 = Button(text="Button 2")
#         self.button_3 = Button(text="Button 3")

#         self.add_widget(self.button_1)
#         self.add_widget(self.button_2)    
#         self.add_widget(self.button_3)

# class MainWindows(App):
#     def build(self):
#         main_layout = GridLayout(orientation='tb-lr', rows=2)

#         top_label = Label(text ="Study Hours Analytics") # , is_shortened=True ,text_size=(None, 100)
#         main_layout.add_widget(top_label)

#         second_grid_layout = MainMenuLayout()
#         main_layout.add_widget(second_grid_layout)
        
#         return main_layout


