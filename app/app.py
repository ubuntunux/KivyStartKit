import os
import sys
import traceback

import kivy
from kivy import platform
from kivy.app import App
from kivy.base import EventLoop
from kivy.core.window import Window
from kivy.config import Config
from kivy.clock import Clock
from kivy.metrics import Metrics
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.vkeyboard import VKeyboard
from kivy.uix.widget import Widget
from kivy.logger import Logger

from app.constants import *
from toast import toast
from utility.screen_manager import ScreenHelper
from utility.kivy_helper import *
from utility.singleton import SingletonInstane

autoclass = None
android = None
if platform == 'android':
    try:
        import android
        from jnius import autoclass
        AndroidString = autoclass('java.lang.String')
        PythonActivity = autoclass('org.renpy.android.PythonActivity')
        VER = autoclass('android.os.Build$VERSION')
    except:
        print(traceback.format_exc())


class BaseApp(App):
    def __init__(self, app_name):
        Logger.info(f'Run: {app_name}')
        self.main_app = MainApp.instance()
        self.app_name = app_name
        self.initialized = False
        self.__screen = Screen(name=app_name)
        self.__back_event = None

    def initialize(self):
        layout = BoxLayout(orientation='vertical', size=(1, 1))
        btn = Button(text="BaseApp", size_hint=(1,1))
        layout.add_widget(btn)
        self.add_widget(layout)
    
    def stop(self):
        self.main_app.unregist_app(self)
    
    def has_back_event(self):
        return self.__back_event is not None
    
    def run_back_event(self):
        return self.__back_event()
            
    def set_back_event(self, func):
        self.__back_event = func
        
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


class MainApp(App, SingletonInstane):
    def __init__(self, app_name):
        super(MainApp, self).__init__()
        
        Logger.info(f'Run: {app_name}')
        self.app_name = app_name
        self.root_widget = None
        self.screen_helper = None
        self.screen = None
        self.apps = []
        self.registed_apps = []
        self.unregist_apps = []
        
        self.is_popup = False
        self.popup_layout = None
        
    def destroy(self):
        self.clear_apps()

    def on_stop(self, instance=None):
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
        
        # post process
        self.bind(on_start=self.do_on_start)
        return self.root_widget
    
    def do_on_start(self, ev):
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)
        Clock.schedule_interval(self.update, 0)
    
    def hook_keyboard(self, window, key, *largs):
        # key - back
        if key == 27:
            self.back_event()
            return True
                
    def back_event(self):
        current_app = self.get_current_app()
        if current_app is not None and current_app.has_back_event():
            current_app.run_back_event()
        elif self.is_popup and self.popup_layout:
            self.popup_layout.dismiss()
            self.is_popup = False
        elif 1 == len(self.apps):
            # show exit popup
            self.popup("Exit?", "", self.stop, None)
        else:
            self.unregist_app(current_app)

    def popup(self, title, message, lambda_yes, lambda_no):
        if self.is_popup:
            return
        self.is_popup = True
        content = BoxLayout(orientation="vertical", size_hint=(1, 1))
        self.popup_layout = Popup(title=title, content=content, auto_dismiss=False, size_hint=(0.9, 0.2))
        content.add_widget(Label(text=message))
        btn_layout = BoxLayout(orientation="horizontal", size_hint=(1, 1), spacing=kivy.metrics.dp(5))
        btn_yes = Button(text='Yes')
        btn_no = Button(text='No')
        btn_layout.add_widget(btn_no)
        btn_layout.add_widget(btn_yes)

        content.add_widget(btn_layout)
        result = True

        def close_popup(instance, is_yes):
            if is_yes and lambda_yes:
                lambda_yes()
            elif lambda_no:
                lambda_no()
            self.popup_layout.dismiss()
            self.is_popup = False

        btn_yes.bind(on_press=lambda inst: close_popup(inst, True))
        btn_no.bind(on_press=lambda inst: close_popup(inst, False))
        self.popup_layout.open()
        return
        
    def get_current_app(self):
        current_screen_name = self.screen_helper.get_current_screen_name()
        for app in self.apps:
            if current_screen_name == app.get_screen().name:
                return app
        return None
    
    def clear_apps(self):
        for app in self.apps:
            self.unregist_app(app)
    
    def regist_app(self, app):
        if app not in self.registed_apps and app not in self.apps:
            self.registed_apps.append(app)
            
    def unregist_app(self, app):
        if app not in self.unregist_apps and app in self.apps:
            self.unregist_apps.append(app)

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
                toast(app.app_name)
                self.apps.append(app)
        self.registed_apps.clear()
        
        # update apps
        for app in self.apps:
            app.update(dt)
        
        # unregist app
        if 0 < len(self.unregist_apps):
            for app in self.unregist_apps:
                app.on_stop()
                self.apps.remove(app)
            self.unregist_apps.clear()
            # terminate application
            if 0 == len(self.apps):
                self.stop()
        

