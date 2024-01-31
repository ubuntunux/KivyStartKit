from glob import glob
import inspect
import importlib
import os
import traceback
from collections import OrderedDict
from functools import partial
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
        self.root_widget = None
        self.screen_helper = None
        self.ui_manager = UIManager()
        self.popup = KivyPopup()
        
        self.bind(on_start=self.do_on_start)
    
    def build(self):
        #Window.maximize()
        Window.softinput_mode = 'below_target'
        # keyboard_mode: '', 'system', 'dock', 'multi', 'systemanddock', 'systemandmulti'
        Config.set('kivy', 'keyboard_mode', 'system')
        Window.configure_keyboards()
        Window.bind(on_resize=self.on_resize)
        
        self.root_widget = RelativeLayout(size_hint=(1,1))
        background = Image(source="data/images/ubuntu-wallpaper-mobile.jpg", size_hint=(1,1), fit_mode="fill")
        self.root_widget.add_widget(background)
        self.screen_helper = ScreenHelper(size_hint=(1,1))
        self.root_widget.add_widget(self.screen_helper.screen_manager)
        
        self.ui_manager._BaseApp__initialize(display_name="UI Manager")
        self.ui_manager.build(self.root_widget, self.screen_helper)
        
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
        self.register_apps()
        self.ui_manager.show_app_list(False)
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)
        Clock.schedule_interval(self.update, 0)
    
    def on_resize(self, window, width, height):
        for app in self.active_apps.values():
            app.on_resize(window, width, height)
        self.ui_manager.on_resize(window, width, height)
        
    def hook_keyboard(self, window, key, *largs):
        # key - back
        if key == 27:
            self.back_event()
            return True

    def back_event(self):
        current_app = self.get_current_app()
        if current_app is not None:
            if current_app.has_back_event():
                current_app.run_back_event()
            else:
                self.set_current_active_app(None)
        elif self.popup.is_opened():
            self.popup.dismiss()
        else:
            self.popup.open(
                title="Exit", 
                body_widget=Label(text="Do you really want to quit?"), 
                callback_yes=self.stop
            )
            
    def get_current_app(self):
        return self.current_app
        
    def register_apps(self):
        from apps import example
        self.register_app(example)
        
        from apps import jarvis
        self.register_app(jarvis)
        
        import sys
        sys.path.append("..")
        import KivyRPG
        self.register_app(KivyRPG)
        
        from apps import addapp
        self.register_app(addapp)
        
        self.ui_manager.arrange_icons()
        
    def register_app(self, module):
        if module in self.registed_modules or type(module) is not types.ModuleType:
            return
            
        app_class = getattr(module, "__app__", None)
        if not inspect.isclass(app_class) or not issubclass(app_class, BaseApp):
            return
                                      
        def create_app(module, inst):
            self.create_app(module)       
        
        self.ui_manager.create_app_icon(
            icon_name=app_class.get_app_name(),
            icon_file=LOGO_FILE,
            on_press=partial(create_app, module),  
        )
        self.registed_modules.append(module)
    
    def unregister_app(self, module):
        if module in self.registed_modules:
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
            try:
                app._BaseApp__initialize(display_name=display_name)
            except:
                error = traceback.format_exc()
                Logger.info(error)
                # todo - popup message
                toast(error)
                return
                
            self.ui_manager.create_active_app_button(
                app,
                display_name,
                self.deactive_app,
                self.set_current_active_app
            )
            self.active_apps[app_id] = app
            self.screen_helper.add_screen(app.get_screen(), False)
        self.set_current_active_app(app)
                
    def destroy_apps(self):
        keys = list(self.active_apps.keys())
        for key in keys:
            app = self.active_apps[key]
            self.deactive_app(app)
            
        while self.registed_modules:
            app = self.registed_modules[-1]
            self.unregister_app(app)  
                
    def set_current_active_app(self, app):
        if app is self.current_app:
            return
            
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
        self.ui_manager.deactive_app_button(app)
        self.screen_helper.current_screen(self.ui_manager.get_screen())
        self.screen_helper.remove_screen(app.get_screen())
        if app is self.current_app:
            self.current_app = None 
        self.active_apps.pop(app.get_app_id())
        app._BaseApp__on_stop()
                
    def update(self, dt):
        dt = max(1/1000, min(dt, 1/10))
        
        for app in self.active_apps.values():
            app.update(dt)
