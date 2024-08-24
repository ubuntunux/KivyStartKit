from distutils.dir_util import copy_tree
import os
import traceback
import uuid

from kivy.logger import Logger
from kivy.metrics import dp as DP
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

from core import platform
from core.base_app import BaseApp
from core.main_app import MainApp
from core.constants import *
from utility.screen_manager import ScreenHelper
from utility.kivy_widgets import *
from utility.kivy_helper import *

src__init__ = """
__author__ = ""
__email__ = ""
__copyright__ = ""
__license__ = ""
__version__ = "1.0.0"

from .main import App
# You must declare '__app__' as a class of application
__app__ = App
"""

src__main__ = """
from kivy.logger import Logger
from kivy.uix.button import Button
from core.base_app import BaseApp

# You must keep this rule.
class App(BaseApp):
    app_name = "Hello, world!"
    orientation = "all" # all, landscape, portrait
    allow_multiple_instance = False
    
    def __init__(self):
        super().__init__()
        
    def on_initialize(self):
        btn = Button(text="Hello, world!", size_hint=(1, 1))
        self.add_widget(btn)
    
    def on_stop(self):
        pass
    
    def on_back(self):
        return False
        
    def on_resize(self, window, width, height):
        pass
        
    def on_update(self, dt):
        pass
"""


# You must keep this rule.
class App(BaseApp):
    app_name = "Add App..."
    orientation = "all" # all, landscape, portrait
    allow_multiple_instance = False
    
    def __init__(self):
        super().__init__()
        self.filechooser = None
        self.input_app_name = None
        self.heights = 0

    def on_initialize(self):
        layout = BoxLayout(orientation="vertical", size_hint=(1, 1))
        create_dynamic_rect(layout, (0,0,0,1))
        self.add_widget(layout)
        
        content_height = DP(40)
        
        platform_api = platform.get_platform_api()
        self.filechooser = FileChooserListView(size_hint=(1, None), path=platform_api.get_home_directory())
        def on_submit(*args, **kwargs):
            title.text = self.filechooser.path
        self.filechooser.bind(on_entries_cleared=on_submit)
        layout.add_widget(self.filechooser)
       
        self.heights += content_height
        title = Label(halign="left", text="", font_size="12dp", size_hint=(1, None), height=content_height)
        layout.add_widget(title)
    
        self.heights += content_height
        self.input_app_name = TextInput(hint_text="Input a application name", size_hint=(1, None), height=content_height)
        def on_enter(instance, value):
            Logger.info(value)
        self.input_app_name.bind(on_text_validate=on_enter)
        layout.add_widget(self.input_app_name)
        
        self.heights += content_height
        btn_layout = BoxLayout(orientation="horizontal", size_hint=(1, None), height=content_height)
        btn_yes = Button(text='Yes', size_hint=(1, 1))
        btn_no = Button(text='No', size_hint=(1, 1))
        btn_yes.bind(on_press=self.on_press_yes)
        btn_no.bind(on_press=self.on_press_no)
        btn_layout.add_widget(btn_no)
        btn_layout.add_widget(btn_yes)
        layout.add_widget(btn_layout)
        
        self.on_resize(Window, Window.width, Window.height)
        
    def on_stop(self):
        pass
        
    def on_press_yes(self, inst):
        app_path = self.filechooser.path
        module_name = self.input_app_name.text.strip()
        if not module_name:
            app_path, module_name = os.path.split(app_path)
        module_path = os.path.join(app_path, module_name)
        
        if not os.path.exists(module_path):
            try:
                os.makedirs(module_path)
                init_filepath = os.path.join(module_path, "__init__.py")
                with open(init_filepath, "w") as f:
                    f.write(src__init__)
                main_filepath = os.path.join(module_path, "main.py")
                with open(main_filepath, "w") as f:
                    f.write(src__main__)
            except:
                Logger.error(traceback.format_exc())
        
        app_info = {
            "path": app_path,
            "module": module_name
        }
        
        filenames = os.listdir(APP_DATA_FOLDER) if os.path.exists(APP_DATA_FOLDER) else []
        num_app = len(filenames)
        index = num_app
        filename = ""
        while True:
            filename = str(num_app) + ".app"
            if filename not in filenames:
                break
            index += 1
        filepath = os.path.join(APP_DATA_FOLDER, filename)
        if not os.path.exists(filepath):
            main_app = MainApp.instance()
            if main_app.register_module_info(app_info):
                main_app.ui_manager.arrange_icons()
                try:
                    with open(filepath, "w") as f:
                        f.write(str(app_info))
                    Logger.info(f"register app: {app_info}")
                except:
                    Logger.error(traceback.format_exc())
        self.stop()
    
    def on_press_no(self, inst):
        self.stop()
    
    def on_back(self):
        self.stop()
        return True
        
    def on_resize(self, window, width, height):
        self.filechooser.height = height - self.heights
        
    def on_update(self, dt):
        pass
