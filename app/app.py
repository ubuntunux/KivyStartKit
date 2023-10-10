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


class BaseApp(App):
    def __init__(self, app_name):
        Logger.info(f'Run: {app_name}')
        self.my_app = MyApp.instance()
        self.app_name = app_name
        self.initialized = False
        self.__screen = Screen(name=app_name)

    def initialize(self):
        layout = BoxLayout(orientation='vertical', size=(1, 1))
        btn = Button(text="BaseApp", size_hint=(1,1))
        layout.add_widget(btn)
        self.add_widget(layout)
    
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
        self.registed_apps = []
        
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
        self.screen_helper.add_screen(self.screen, True)
        
        # app list view
        self.app_btn_size = [Window.size[0] * 0.3, Window.size[1] * 0.05]
        self.app_layout = BoxLayout(orientation='horizontal', size_hint=(None, None), size=(0, self.app_btn_size[1]))
        self.app_scroll_view = ScrollView(
            pos_hint=(None, None), 
            pos=(0, Window.size[1] - self.app_btn_size[1]), 
            size_hint=(None, None), 
            width=Window.size[0], 
            height=self.app_btn_size[1]
        )
        self.app_scroll_view.add_widget(self.app_layout)
        self.root_widget.add_widget(self.app_scroll_view)  
        
        Clock.schedule_interval(self.update, 0)
        return self.root_widget
    
    def regist_app(self, app):
        if app not in self.registed_apps and app not in self.apps:
            self.registed_apps.append(app)

    def update(self, dt):
        # initialize new apps
        is_empty_apps = 0 == len(self.apps)
        for (i, app) in enumerate(self.registed_apps):
            if False == app.initialized:
                app.initialize()
                app.initialized = True
                # add app screen
                display_screen = not is_empty_apps or i == 0
                self.screen_helper.add_screen(app.get_screen(), display_screen)
                # add to app list
                app_btn = Button(text=app.app_name, size_hint=(None, None), size=self.app_btn_size)
                app_btn.app_screen = app.get_screen()
                def active_screen(inst):
                    self.screen_helper.current_screen(inst.app_screen)
                app_btn.bind(on_press=active_screen)
                self.app_layout.add_widget(app_btn)
                self.app_layout.width = self.app_btn_size[0] * len(self.app_layout.children)
                if not is_empty_apps and Window.size[0] < self.app_layout.width:
                    self.app_scroll_view.scroll_x = 1.0
                self.apps.append(app)
        self.registed_apps.clear()
        
        # update apps
        for app in self.apps:
            app.update(dt)
        

