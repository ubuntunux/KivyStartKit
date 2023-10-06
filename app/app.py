import os
import sys
import traceback

from kivy.app import App
from kivy.core.window import Window
from kivy.config import Config
from kivy.clock import Clock
from kivy.metrics import Metrics
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.vkeyboard import VKeyboard
from kivy.logger import Logger

from app.constants import *
from utility.screen_manager import ScreenHelper
from utility.kivy_helper import *
from utility.singleton import SingletonInstane


class BaseApp(App, SingletonInstane):
    def __init__(self, app_name):
        Logger.info(f'Run: {app_name}')
        self.my_app = MyApp.instance()
        self.app_name = app_name
        self.initialized = False
        self.__screen = Screen(name=app_name)

    def initialize(self):
        pass
    
    def destroy(self):
        pass
        
    def get_screen(self):
        return self.__screen
    
    def get_children(self):
        return self.__screen.children
    
    def clear_widget(self):
        self.__screen.clear_widget()
        
    def add_widget(self, widget):
        self.__screen.add_widget(widget)

    def remove_widget(self, widget):
        self.__screen.remove_widget(widget)

    def update(self, dt):
        pass


class MyApp(App, SingletonInstane):
    def __init__(self, app_name):
        super(MyApp, self).__init__()
        
        Logger.info(f'Run: {app_name}')
        self.app_name = app_name
        self.root_widget = None
        self.screen_helper = None
        self.screen = None
        self.apps = []
        
    def destroy(self):
        pass

    def on_stop(self):
        self.destroy()
        Config.write()

    def build(self):
        # Window.maximize()
        Window.softinput_mode = 'below_target'
        # keyboard_mode: '', 'system', 'dock', 'multi', 'systemanddock', 'systemandmulti'
        Config.set('kivy', 'keyboard_mode', 'system')
        Window.configure_keyboards()
        self.root_widget = Widget()
        self.screen_helper = ScreenHelper(size=Window.size)
        self.root_widget.add_widget(self.screen_helper.screen_manager)
        self.screen = Screen(name=self.app_name)
        self.screen_helper.add_screen(self.screen)
        self.screen_helper.current_screen(self.screen)

        btn = Button(text=self.app_name)
        btn.bind(on_press=lambda inst:self.screen_helper.cycle_screen())
        layout = BoxLayout(orientation='vertical', size=(1, 1))
        layout.add_widget(btn)
        self.screen.add_widget(layout)
        
        Clock.schedule_interval(self.update, 0)
        return self.root_widget
    
    def regist_app(self, app):
        if app not in self.apps:
            self.apps.append(app)

    def update(self, dt):
        for app in self.apps:
            if False == app.initialized:
                app.initialize()
                app.initialized = True
                self.screen_helper.add_screen(app.get_screen())
                #self.screen_helper.current_screen(app.get_screen())
            app.update(dt)
        

