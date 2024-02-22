import copy
from glob import glob
import inspect
import importlib
import os
import traceback
from collections import OrderedDict
from functools import partial
import sys
import types

import kivy
from kivy.app import App
from kivy.base import EventLoop
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.metrics import dp as DP
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scatter import Scatter
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from utility.toast import toast
from utility.kivy_helper import *
from utility.kivy_widgets import *
from utility.screen_manager import ScreenHelper
from utility.singleton import SingletonInstance

from . import platform
from .constants import *
from .base_app import BaseApp
from .ui import UIManager


class MainApp(App, SingletonInstance):
    app_name = "Kivy Start Kit"
    app_directory = "apps"
    orientation = "all"
    platform_api = platform.get_platform_api()
       
    def __init__(self):
        super(MainApp, self).__init__()
        Logger.info(f'Run: {self.app_name}')
        self.registed_modules = []
        self.current_app = None
        self.active_apps = {}
        self.module_apps = {}
        self.root_widget = None
        self.screen_helper = None
        self.ui_manager = UIManager()
        self.exit_popup = KivyPopup()
        self.key_press_time = {}
        
        self.bind(on_start=self.do_on_start)
    
    def build(self):
        #Window.maximize()
        Window.softinput_mode = 'below_target'
        # keyboard_mode: '', 'system', 'dock', 'multi', 'systemanddock', 'systemandmulti'
        Config.set('kivy', 'keyboard_mode', 'system')
        Window.configure_keyboards()
        Window.bind(on_resize=self.on_resize)
        Window.bind(on_key_up=self.on_key_up)
        Window.bind(on_keyboard=self.on_key_down)
        
        self.root_widget = RelativeLayout(size_hint=(1,1))
        background = Image(source="data/images/ubuntu-wallpaper-mobile.jpg", size_hint=(1,1), fit_mode="fill")
        self.root_widget.add_widget(background)
        self.screen_helper = ScreenHelper(size_hint=(1,1))
        self.root_widget.add_widget(self.screen_helper.screen_manager)
        
        self.ui_manager.initialize(display_name="UI Manager")
        self.ui_manager.build(self.root_widget, self.screen_helper)
        
        # exit popup
        content_widget = Label(text="Do you really want to quit?")
        def on_press_yes(inst):
            self.stop()
            self.exit_popup.dismiss()
        btn_yes = Button(text='Yes')
        btn_no = Button(text='No')
        btn_yes.bind(on_press=on_press_yes)
        btn_no.bind(on_press=lambda inst: self.exit_popup.dismiss())
        self.exit_popup.initialize_popup(
            title="Exit", 
            content_widget=content_widget, 
            buttons=[btn_no, btn_yes]
        )    
        return self.root_widget
        
    def destroy(self):
        self.destroy_apps()
        Config.set('graphics', 'width', Window.width)
        Config.set('graphics', 'height', Window.height)
        Config.write()
        Logger.info(f"destroy {self.app_name}")

    def on_stop(self, instance=None):
        self.destroy()
         
    def get_app_directory(self):
        self.platform_api.get_app_directory()
        
    def set_orientation(self, orientation="all"):
        self.platform_api.set_orientation(orientation)

    def do_on_start(self, ev):
        self.register_modules()
        self.ui_manager.show_app_list(False)
        Clock.schedule_interval(self.update, 0)
    
    def on_resize(self, window, width, height):
        for app in self.active_apps.values():
            app.on_resize(window, width, height)
        self.ui_manager.on_resize(window, width, height)
    
    def on_key_down(self, window, key, scancode, codepoint, modifier):
        if key in self.key_press_time:
            return True
            
        key_event = None
        
        # key - back
        if key == 27:
            def deactive_current_app(triggered_time):
                app = self.get_current_app()
                if app:
                    self.deactive_app(app)
                else:
                    self.back_event()
            key_event = Clock.schedule_once(deactive_current_app, 1)
        else:
            return False
         
        if key_event:   
            self.key_press_time[key] = key_event   
        return True
        
    def on_key_up(self, window, key, scancode):
        key_event = self.key_press_time.get(key, None)
        is_valid_event = key_event and key_event.is_triggered != 0
        # key - back
        if key == 27:
            if is_valid_event:
                self.back_event()
        else:
            return False
               
        if key in self.key_press_time:
            self.key_press_time.pop(key)
            
        if key_event:
            Clock.unschedule(key_event)
        return True

    def back_event(self):
        current_app = self.get_current_app()
        if current_app is not None:
            if not current_app.on_back():
                self.set_current_active_app(None)
        elif self.exit_popup.is_opened():
            self.exit_popup.dismiss()
        else:
            self.exit_popup.open()
            
    def get_current_app(self):
        return self.current_app
        
    def register_modules(self):
        for filename in glob(f"{APP_DATA_FOLDER}/*.app"):
            app_info = {}
            try:
                with open(filename, "r") as f:
                    app_info = eval(f.read())
            except:
                Logger.error(traceback.format_exc())
            self.register_module_info(app_info)
        self.ui_manager.arrange_icons()
        
    def register_module_info(self, app_info):
        module_dirname = app_info.get("path", "")
        module_name = app_info.get("module", "")
        module_path = os.path.join(module_dirname, module_name)
        result = False
        if os.path.exists(module_path):
            if module_dirname not in sys.path:
                sys.path.append(module_dirname)
            try:
                exec(f"import {module_name}")
                result = eval(f"self.register_module({module_name})")
            except:
                Logger.error(traceback.format_exc())
        return result
        
    def register_module(self, module):
        if module in self.registed_modules or type(module) is not types.ModuleType:
            return False
            
        app_class = getattr(module, "__app__", None)
        if not inspect.isclass(app_class) or not issubclass(app_class, BaseApp):
            return False
        
        Logger.info(f"register_module: {module}")
                                   
        def create_app(module, inst):
            self.create_app(module)
        
        def delete_app(module, inst):
            self.unregister_module(module)
            self.ui_manager.arrange_icons()
            
        self.ui_manager.create_app_icon(
            module_path=module.__file__,
            icon_name=app_class.get_app_name(),
            icon_file=LOGO_FILE,
            on_press=partial(create_app, module),
            on_long_press=partial(delete_app, module)
        )
        self.registed_modules.append(module)
        return True
    
    def unregister_module(self, module):
        Logger.info(f"unregister_module: {module}")   
        if module in self.registed_modules:
            apps = copy.copy(self.module_apps.get(module, []))
            for app in apps:
                self.deactive_app(app)
            self.ui_manager.remove_app_icon(module.__file__)
            self.registed_modules.remove(module)
    
    def create_app(self, module):
        try:
            app = module.__app__.instance()
        except:
            error = traceback.format_exc()
            Logger.info(error)
            # todo - popup message
            toast(error)
            return
        
        if app is None or not isinstance(app, BaseApp):
            return
        
        app_id = app.get_app_id()  
        if app_id not in self.active_apps:
            display_name = app.get_app_name()
            Logger.info(f"create_app: {app.get_app_name()}")
         
            try:
                app.initialize(display_name=display_name)
            except:
                error = traceback.format_exc()
                Logger.info(error)
                # todo - popup message
                toast(error)
                return
                
            self.ui_manager.create_active_app_button(
                app,
                display_name,
                self.set_current_active_app
            )
            self.active_apps[app_id] = app
            if module in self.module_apps:
                self.module_apps[module].append(app)
            else:
                self.module_apps[module] = [app]
            self.screen_helper.add_screen(app.get_screen(), False)
        self.set_current_active_app(app)
                
    def destroy_apps(self):
        keys = list(self.active_apps.keys())
        for key in keys:
            app = self.active_apps[key]
            self.deactive_app(app)
            
        while self.registed_modules:
            module = self.registed_modules[-1]
            self.unregister_module(module)  
                
    def set_current_active_app(self, app):
        if app is self.current_app:
            return
        
        Logger.info(f"set_current_active_app: {app}")
           
        if app is None:
            self.ui_manager.show_app_list(True)
            self.screen_helper.current_screen(self.ui_manager.get_screen())
            self.set_orientation(self.ui_manager.get_orientation())
        else:
            self.ui_manager.show_app_list(False)
            self.screen_helper.current_screen(app.get_screen())
            self.set_orientation(app.get_orientation())
            toast(app.get_app_name())
        self.current_app = app

    def deactive_app(self, app):
        Logger.info(f"deactive_app: {app.get_app_name()}")
        self.ui_manager.deactive_app_button(app)
        self.screen_helper.current_screen(self.ui_manager.get_screen())
        self.screen_helper.remove_screen(app.get_screen())
        if app is self.current_app:
            self.current_app = None 
        self.active_apps.pop(app.get_app_id())
        for (module, apps) in self.module_apps.items():
            if app in apps:
                apps.remove(app)
                break
        app.stop()
   
    def update(self, dt):
        dt = max(1/1000, min(dt, 1/10))
        deactive_apps = []
        for app in self.active_apps.values():
            app.on_update(dt)
            if app.is_stopped():
                deactive_apps.append(app)
        
        for app in deactive_apps:
            self.deactive_app(app)
