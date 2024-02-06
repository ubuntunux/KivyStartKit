from kivy.logger import Logger
from kivy.metrics import dp as DP
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

from core.base_app import BaseApp
from utility.screen_manager import ScreenHelper
from utility.kivy_widgets import *


# You must keep this rule.
class App(BaseApp):
    app_name = "Add App..."
    orientation = "all" # all, landscape, portrait
    allow_multiple_instance = False
    
    def __init__(self):
        super().__init__()
        self.popup = KivyPopup()
        self.filechooser = None

    def on_initialize(self):
        self.filechooser = Label(text="Do you really want to quit?")
        self.filechooser = FileChooserListView(height=DP(500))

        btn_yes = Button(text='Yes')
        btn_no = Button(text='No')
        btn_yes.bind(on_press=self.on_press_yes)
        btn_no.bind(on_press=self.on_press_no)
        
        self.popup.initialize_popup(
            title="Choose a dirctory that include the app.", 
            content_widget=self.filechooser, 
            buttons=[btn_no, btn_yes]
        )
        self.popup.open()
        
    def on_stop(self):
        pass
        
    def on_press_yes(self, inst):
        Logger.info(self.filechooser.path)
        self.stop()
        self.popup.dismiss()
    
    def on_press_no(self, inst):
        self.popup.dismiss()
    
    def on_back(self):
        return False
        
    def on_resize(self, window, width, height):
        pass
        
    def on_update(self, dt):
        pass
