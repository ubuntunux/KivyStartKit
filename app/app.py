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
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
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
def run_on_ui_thread(func):
    return func

if platform == 'android':
    try:
        import android
        from android.runnable import run_on_ui_thread
        from jnius import autoclass
        AndroidString = autoclass('java.lang.String')
        AndroidActivityInfo = autoclass('android.content.pm.ActivityInfo')
        AndroidPythonActivity = autoclass('org.kivy.android.PythonActivity')
    except:
        print(traceback.format_exc())


class BaseApp(App):
    def __init__(self, app_name, orientation="all"):
        Logger.info(f'Run: {app_name}')
        self.main_app = MainApp.instance()
        self.app_name = app_name
        self.orientation = orientation
        self.initialized = False
        self.__screen = Screen(name=app_name)
        self.__back_event = None
        self.size = MainApp.instance().size
        self.width = self.size[0]
        self.height = self.size[1]

    def initialize(self):
        raise Exception("must implement!")
    
    def on_stop(self):
        raise Exception("must implement!")
    
    def update(self, dt):
        raise Exception("must implement!")

    def get_name(self):
        return self.app_name
    
    def get_orientation(self):
        return self.orientation
        
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
        self.orientation = "all"
        self.app_name = app_name
        self.root_widget = None
        self.screen_helper = None
        self.screen = None
        self.size = (Window.size[0], Window.size[1])
        self.width = self.size[0]
        self.height = self.size[1]
        
        self.registed_apps = []
        self.current_app = None
        self.active_apps = {}
        self.active_app_buttons = {}
        self.app_scroll_view = None
        self.app_layout = None
        self.app_button_size = (300, 100)
        self.is_popup = False
        self.popup_layout = None
        
    @run_on_ui_thread      
    def set_orientation(self, orientation="all"):
        if platform == 'android':
            activity = AndroidPythonActivity.mActivity
            request_orientation = AndroidActivityInfo.SCREEN_ORIENTATION_SENSOR
            if "landscape" == orientation:
                request_orientation = AndroidActivityInfo.SCREEN_ORIENTATION_LANDSCAPE
            elif "portrait" == orientation:
                request_orientation = AndroidActivityInfo.SCREEN_ORIENTATION_PORTRAIT
            activity.setRequestedOrientation(request_orientation)
        else:
            pass
    
    def get_name(self):
        return self.app_name
        
    def destroy(self):
        self.destroy_apps()

    def on_stop(self, instance=None):
        self.destroy()
        Config.write()

    def build(self):
        Window.maximize()
        Window.softinput_mode = 'below_target'
        # keyboard_mode: '', 'system', 'dock', 'multi', 'systemanddock', 'systemandmulti'
        Config.set('kivy', 'keyboard_mode', 'system')
        Window.configure_keyboards()
        
        # app list view
        self.menu_layout = BoxLayout(orientation='horizontal', size_hint=(1.0, None), height=self.app_button_size[1])
        self.menu_btn = Button(text="menu", size_hint=(None, 1.0), width=self.app_button_size[0])
        self.menu_layout.add_widget(self.menu_btn)
        
        self.app_layout = BoxLayout(orientation='horizontal', size_hint=(None, 1.0))
        self.app_scroll_view = ScrollView(size_hint=(1, 1))
        self.app_scroll_view.add_widget(self.app_layout)
        self.menu_layout.add_widget(self.app_scroll_view)
        
        self.screen = Screen(name=self.get_name())
        # background icons
        self.registed_app_layout = GridLayout(cols=6)
        for app in self.registed_apps:
            btn = Button(text=app.get_name())
            def active_app(app, inst):
                self.active_app(app)
            btn.bind(on_press=partial(active_app, app))
            self.registed_app_layout.add_widget(btn)
        self.screen.add_widget(self.registed_app_layout)
        
        # screen manager
        self.screen_helper = ScreenHelper(size_hint=(1,1))
        self.screen_helper.add_screen(self.screen, True)
        
        self.root_widget = FloatLayout(size_hint=(1,1))
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
        if current_app is not None:
            if current_app.has_back_event():
                current_app.run_back_event()
            else:
                self.active_app(None)
        elif self.is_popup and self.popup_layout:
            self.popup_layout.dismiss()
            self.is_popup = False
        else:
            self.popup("Exit?", "", self.stop, None)
        
    def popup(self, title, message, lambda_yes, lambda_no):
        if self.is_popup:
            return
        self.is_popup = True
        content = BoxLayout(orientation="vertical", size_hint=(1, 1))
        size_hint = (0.9, 0.2) if get_is_vertical_window() else (0.3, 0.3)
        self.popup_layout = Popup(title=title, content=content, auto_dismiss=False, size_hint=size_hint)
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
        y = 0 if show else -self.menu_layout.height
        self.menu_layout.pos = (self.menu_layout.pos[0], y)
        
    def get_current_app(self):
        return self.current_app
        
    def register_app(self, app):
        #############
        log_info(f"!!!!!!!!!!!\n\nregister_app: MUST CHAGE TO RECIEVE CLASS INSTEAD APP INSTANCE {app.get_name()}\n\n!!!!!!!!!!")
        ###№#########
        if app not in self.registed_apps:
            self.registed_apps.append(app)
    
    def unregister_app(self, app):
        if app in self.registed_apps:
            self.registed_apps.remove(app)

    def initialize_app(self, app):
        if not app.initialized:
            app.initialize()
            app.initialized = True
            app_btn = Button(text=app.get_name(), size_hint=(None, 1.0), width=self.app_button_size[0])        
            def deactive_app(app, inst):
                self.deactive_app(app)
            app_btn.bind(on_press=partial(deactive_app, app))
            self.app_layout.add_widget(app_btn)        
            self.app_layout.width = app_btn.width * len(self.app_layout.children)
            if Window.size[0] < self.app_layout.width:
                self.app_scroll_view.scroll_x = 1.0        
            self.active_app_buttons[app.get_name()] = app_btn
            self.active_apps[app.get_name()] = app
                
    def destroy_apps(self):
        keys = list(self.active_apps.keys())
        for key in keys:
            app = self.active_apps[key]
            self.deactive_app(app)
            
        while self.registed_apps:
            app = self.registed_apps[-1]
            self.unregister_app(app)  
                
    def active_app(self, app):
        if app is self.current_app:
            return
            
        if app is None:
            self.screen_helper.current_screen(self.screen)
            self.set_orientation(self.orientation)
            self.show_app_list(True)
        else:
            if not app.initialized:
                self.initialize_app(app)
                self.screen_helper.add_screen(app.get_screen(), False)
            self.screen_helper.current_screen(app.get_screen())
            self.set_orientation(app.get_orientation())
            toast(app.get_name())
            self.show_app_list(False)
        self.current_app = app
            
    def deactive_app(self, app):
        btn = self.active_app_buttons.pop(app.get_name())
        btn.parent.remove_widget(btn)
        self.screen_helper.remove_screen(app.get_screen())
        self.screen_helper.current_screen(self.screen)
        if app is self.current_app:
            self.current_app = None 
        self.active_apps.pop(app.get_name())
        app.on_stop()
                
    def update(self, dt):
        dt = max(1/1000, min(dt, 1/10))
        
        for app in self.active_apps.values():
            app.update(dt)
