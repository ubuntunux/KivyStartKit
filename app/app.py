import traceback
from functools import partial

import kivy
from kivy import platform
from kivy.app import App
from kivy.base import EventLoop
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from utility.toast import toast
from utility.kivy_helper import *
from utility.screen_manager import ScreenHelper
from utility.singleton import SingletonInstance

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
        raise Exception("must implement!")
    
    def on_stop(self):
        raise Exception("must implement!")
    
    def update(self, dt):
        raise Exception("must implement!")

    def stop(self):
        self.main_app.unregister_app(self)

    def get_name(self):
        return self.app_name
        
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


class MainApp(App, SingletonInstance):
    def __init__(self, app_name):
        super(MainApp, self).__init__()
        Logger.info(f'Run: {app_name}')
        self.app_name = app_name
        self.root_widget = None
        self.screen_helper = None
        self.screen = None
        self.apps = {}
        self.registed_apps = []
        self.unregister_apps = []
        self.app_history = []
        self.current_app = None
        
        self.active_app_buttons = {}
        self.app_scroll_view = None
        self.app_layout = None
        self.app_button_width = 100.0
        self.is_popup = False
        self.popup_layout = None
        
    def get_name(self):
        return self.app_name
        
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
        self.root_widget = BoxLayout(orientation='vertical', size=Window.size)
        
        # app list view
        self.app_button_width = 300
        self.app_layout = BoxLayout(orientation='horizontal', size_hint=(None, 1.0))
        self.app_scroll_view = ScrollView(size_hint=(1, 1))
        self.app_scroll_view.add_widget(self.app_layout)
        menu_size_hint_y = get_size_hint_y(Window.size, 100.0)
        self.menu_layout = BoxLayout(orientation='horizontal', size_hint=(1.0, menu_size_hint_y))
        self.menu_btn = Button(text="menu", size_hint=(None, 1.0), width=self.app_button_width)
        self.menu_layout.add_widget(self.menu_btn)
        self.menu_layout.add_widget(self.app_scroll_view)
        
        # screen manager
        self.screen = Screen(name=self.get_name())
        self.screen_helper = ScreenHelper(size_hint=(1, (1.0 - menu_size_hint_y)))
        self.screen_helper.add_screen(self.screen, True)
        self.root_widget.add_widget(self.screen_helper.screen_manager)
        self.root_widget.add_widget(self.menu_layout)

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
            self.unregister_app(current_app)

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
     
    def show_app_list(self, show):
        self.app_layout.disabled = not show
        self.app_layout.opacity = 1 if show else 0
    
    def get_current_app(self):
        return self.app_history[-1] if 0 < len(self.app_history) else None
        
    def clear_apps(self):
        for app in self.apps.values():
            self.unregister_app(app)

    def register_app(self, app):
        if app not in self.registed_apps and app.get_name() not in self.apps:
            self.registed_apps.append(app)

    def unregister_app(self, app):
        if app not in self.unregister_apps and app.get_name() in self.apps:
            self.unregister_apps.append(app)

    def initialize_registed_apps(self, num_apps):
        if 0 < len(self.registed_apps):
            was_empty_apps = 0 == num_apps
            for (i, app) in enumerate(self.registed_apps):
                if not app.initialized:
                    app.initialize()
                    app.initialized = True
                    # add to active app list
                    app_btn = Button(text=app.get_name(), size_hint=(None, 1.0), width=self.app_button_width)                
                    def active_app(app, inst):
                        self.active_app(app, True)
                    app_btn.bind(on_press=partial(active_app, app))
                    self.app_layout.add_widget(app_btn)                
                    self.app_layout.width = app_btn.width * len(self.app_layout.children)
                    if not was_empty_apps and Window.size[0] < self.app_layout.width:
                        self.app_scroll_view.scroll_x = 1.0                
                    self.active_app_buttons[app.get_name()] = app_btn
                    self.apps[app.get_name()] = app
                    self.active_app(app, False)
            # active app
            if was_empty_apps:
                self.active_app(self.registed_apps[0], True)             
            self.registed_apps.clear()
            
    def destroy_unregisted_apps(self):
        if 0 < len(self.unregister_apps):
            for app in self.unregister_apps:
                self.deactive_app(app)     
                btn = self.active_app_buttons.pop(app.get_name())
                btn.parent.remove_widget(btn)
                self.apps.pop(app.get_name())
            self.unregister_apps.clear()
            # terminate application
            if 0 == len(self.apps):
                self.stop()

    def active_app(self, app, display_app=True):
        num_apps = self.app_history.count(app)
        if 0 == num_apps or app != self.current_app:
            if 0 == num_apps:
                self.screen_helper.add_screen(app.get_screen(), False)
            if display_app:
                self.current_app = app
                self.screen_helper.current_screen(app.get_screen())
                toast(app.get_name())
            self.app_history.append(app)
            
    def deactive_app(self, app):
        num_apps = self.app_history.count(app)
        if 0 < num_apps:
            self.current_app = None 
            self.screen_helper.remove_screen(app.get_screen())
            app.on_stop()
            for i in range(num_apps):
                self.app_history.remove(app)
            if 0 < len(self.app_history):
                self.active_app(self.app_history[-1])

    def update(self, dt):
        prev_num_apps = len(self.apps)
        self.initialize_registed_apps(prev_num_apps)
        
        # update apps
        for app in self.apps.values():
            app.update(dt)

        self.destroy_unregisted_apps()