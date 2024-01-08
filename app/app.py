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
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from utility.toast import toast
from utility.kivy_helper import *
from utility.screen_manager import ScreenHelper
from utility.singleton import SingletonInstance


bright_blue = [1.5, 1.5, 2.0, 2]
dark_gray = [0.4, 0.4, 0.4, 2]
        
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
        log_info(traceback.format_exc())


class BaseApp(App):
    app_name = ""
    
    def __init__(self, orientation="all"):
        Logger.info(f'Run: {self.get_name()}')
        self.main_app = MainApp.instance()
        self.orientation = orientation
        self.__screen = Screen(name=self.get_app_id())
        self.__back_event = None
        self.size = MainApp.instance().size
        self.width = self.size[0]
        self.height = self.size[1]
        self.initialized = False
        
    def __initialize(self):
        self.initialize()
        self.initialized = True
        
    def __on_stop(self):
        self.on_stop()
        self.clear_instance()
    
    def initialize(self):
        raise Exception("must implement!")
        
    def on_stop(self):
        raise Exception("must implement!")
    
    def update(self, dt):
        raise Exception("must implement!")

    @classmethod
    def get_name(cls):
        if cls.app_name:
            return cls.app_name
        return cls.__name__
    
    def get_app_id(self):
        return str(id(self))
    
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
        
        self.registed_classes = []
        self.current_app = None
        self.active_apps = {}
        self.active_app_buttons = {}
        self.app_scroll_view = None
        self.app_layout = None
        self.app_button_size = (300, 100)
        self.is_popup = False
        self.popup_layout = None
        
        self.app_press_time = {}
        
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
        
    def get_app_id(self):
        return str(id(self))
        
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
        self.menu_btn = Button(text="menu", size_hint=(None, 1.0), width=self.app_button_size[0], background_color=dark_gray)
        self.menu_layout.add_widget(self.menu_btn)
        
        self.app_layout = BoxLayout(orientation='horizontal', size_hint=(None, 1.0))
        self.app_scroll_view = ScrollView(size_hint=(1, 1))
        self.app_scroll_view.add_widget(self.app_layout)
        self.menu_layout.add_widget(self.app_scroll_view)
        
        self.screen = Screen(name=self.get_app_id())
        # background icons
        self.registed_app_layout = FloatLayout(size_hint=(1,1))
        for (i, cls) in enumerate(self.registed_classes):
            padding=10
            size=200+padding*2
            btn = Button(
                text=cls.get_name(),
                pos=(i * (size + padding * 2) + padding, self.height - (size + padding)),
                size_hint=(None, None),
                size=(size, size),
                background_color=dark_gray,
                #background_normal="data/icons/icon.png"
            )
            def create_app(cls, inst):
                self.create_app(cls)
            btn.bind(on_press=partial(create_app, cls))
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
                self.set_current_active_app(None)
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
        
    def register_app(self, cls):
        if cls not in self.registed_classes:
            self.registed_classes.append(cls)
    
    def unregister_app(self, cls):
        if cls in self.registed_classes:
            self.registed_classes.remove(cls)

    def create_app(self, cls):
        app = cls.instance()
        if not app.initialized:
            app._BaseApp__initialize()
            app_btn = Button(text=app.get_name(), size_hint=(None, 1.0), width=self.app_button_size[0], background_color=dark_gray)        
            def deactive_app(app, dt):
                self.deactive_app(app)
            def on_press(app, inst):
                event = Clock.schedule_once(partial(deactive_app, app), 1)
                self.app_press_time[app] = event
            def on_release(app, inst):
                event = self.app_press_time.pop(app)
                Clock.unschedule(event)
                self.set_current_active_app(app)
            app_btn.bind(
                on_press=partial(on_press, app),
                on_release=partial(on_release, app)
            )
            self.app_layout.add_widget(app_btn)        
            self.app_layout.width = app_btn.width * len(self.app_layout.children)
            if Window.size[0] < self.app_layout.width:
                self.app_scroll_view.scroll_x = 1.0        
            self.active_app_buttons[app.get_app_id()] = app_btn
            self.active_apps[app.get_app_id()] = app
            self.screen_helper.add_screen(app.get_screen(), False)
        self.set_current_active_app(app)
                
    def destroy_apps(self):
        keys = list(self.active_apps.keys())
        for key in keys:
            app = self.active_apps[key]
            self.deactive_app(app)
            
        while self.registed_classes:
            app = self.registed_classes[-1]
            self.unregister_app(app)  
                
    def set_current_active_app(self, app):
        if app is self.current_app:
            return
            
        if app is None:
            self.screen_helper.current_screen(self.screen)
            self.set_orientation(self.orientation)
            self.show_app_list(True)
        else:
            self.screen_helper.current_screen(app.get_screen())
            self.set_orientation(app.get_orientation())
            toast(app.get_name())
            self.show_app_list(False)
        self.current_app = app
            
    def deactive_app(self, app):
        btn = self.active_app_buttons.pop(app.get_app_id())
        btn.parent.remove_widget(btn)
        self.screen_helper.remove_screen(app.get_screen())
        self.screen_helper.current_screen(self.screen)
        if app is self.current_app:
            self.current_app = None 
        self.active_apps.pop(app.get_app_id())
        app._BaseApp__on_stop()
                
    def update(self, dt):
        dt = max(1/1000, min(dt, 1/10))
        
        for app in self.active_apps.values():
            app.update(dt)
