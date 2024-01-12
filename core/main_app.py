from glob import glob
import os
import traceback
from collections import OrderedDict
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
from kivy.uix.scatter import Scatter
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from utility.toast import toast
from utility.kivy_helper import *
from utility.kivy_widgets import *
from utility.screen_manager import ScreenHelper
from utility.singleton import SingletonInstance

from .constants import *
from . import platform

bright_blue = [1.5, 1.5, 2.0, 2]
dark_gray = [0.4, 0.4, 0.4, 2]


class MainApp(App, SingletonInstance):
    def __init__(self, app_name):
        super(MainApp, self).__init__()
        Logger.info(f'Run: {app_name}')
        self.platform_api = platform.get_platform_api()
        self.orientation = "all"
        self.app_name = app_name
        self.app_directory = "app"
        self.root_widget = None
        self.screen_helper = None
        self.screen = None
        
        self.registed_classes = []
        self.current_app = None
        self.active_apps = {}
        self.active_app_buttons = {}
        self.app_scroll_view = None
        self.app_layout = None
        self.app_button_size = (300, 100)
        
        self.background_layout = None
        self.icon_size=(200, 200)
        self.icon_font_height=50
        self.icon_padding=20
        self.icons = [] #OrderedDict()
        
        self.is_popup = False
        self.popup_layout = None
        
        self.app_press_time = {}
      
    def set_orientation(self, orientation="all"):
        self.platform_api.set_orientation(orientation)
    
    def get_name(self):
        return self.app_name
        
    def get_app_id(self):
        return str(id(self))
        
    def destroy(self):
        self.destroy_apps()
        Config.set('graphics', 'width', Window.width)
        Config.set('graphics', 'height', Window.height)
        Config.write()
        Logger.info("Bye")

    def on_stop(self, instance=None):
        self.destroy()
        
    def get_app_directory(self):
        if platform == 'android':
            from android.storage import primary_external_storage_path
            SD_CARD = primary_external_storage_path()
        
    def register_apps(self):
        from apps.javis.main import JavisApp
        self.register_app(JavisApp)
        
        from apps.KivyRPG.main import KivyRPGApp
        self.register_app(KivyRPGApp)
        
        self.arrange_icons()
        
    def register_app(self, cls):
        if cls not in self.registed_classes:
            def create_app(cls, inst):
                self.create_app(cls)
            on_press = partial(create_app, cls)
            self.create_app_icon(
                cls.get_name(),
                on_press,
                background_normal="data/icons/logo_image.png"
            )
            #background_color=dark_gray
            self.registed_classes.append(cls)
    
    def unregister_app(self, cls):
        if cls in self.registed_classes:
            self.registed_classes.remove(cls)

    def build(self):
        Window.softinput_mode = 'below_target'
        # keyboard_mode: '', 'system', 'dock', 'multi', 'systemanddock', 'systemandmulti'
        Config.set('kivy', 'keyboard_mode', 'system')
        Window.configure_keyboards()
        
        # app list view
        self.menu_layout = BoxLayout(orientation='horizontal', size_hint=(1.0, None), height=self.app_button_size[1])
        #self.menu_btn = Button(text="menu", size_hint=(None, 1.0), width=self.app_button_size[0], background_color=dark_gray)
        #self.menu_layout.add_widget(self.menu_btn)
        
        self.app_layout = BoxLayout(orientation='horizontal', size_hint=(None, 1.0))
        self.app_scroll_view = ScrollView(size_hint=(1, 1))
        self.app_scroll_view.add_widget(self.app_layout)
        self.menu_layout.add_widget(self.app_scroll_view)
        
        self.screen = Screen(name=self.get_app_id())
        self.background_layout = GridLayout(
            cols=1,
            padding=self.icon_padding,
            spacing=self.icon_padding,
            size_hint=(1,None)
        )
        self.background_scroll_view = ScrollView(size_hint=(1, 1))
        self.background_scroll_view.add_widget(self.background_layout)
        self.screen.add_widget(self.background_scroll_view)
        
        # screen manager
        self.screen_helper = ScreenHelper(size_hint=(1,1))
        self.screen_helper.add_screen(self.screen, True) 
        self.root_widget = FloatLayout(size_hint=(1,1))
        background = Image(source="data/images/ubuntu-wallpaper-mobile.jpg", size_hint=(1,1), fit_mode="fill")
        self.root_widget.add_widget(background)
        self.root_widget.add_widget(self.screen_helper.screen_manager)
        self.root_widget.add_widget(self.menu_layout)

        Window.bind(on_resize=self.on_resize)
        
        # post process
        self.bind(on_start=self.do_on_start)
        return self.root_widget
        
    def clear_icons(self):
        while self.background_layout.children:
            horizontal_layout = self.background_layout.children[-1]
            while horizontal_layout.children:
                icon = horizontal_layout.children[-1]
                horizontal_layout.remove_widget(icon)
            self.background_layout.remove_widget(horizontal_layout)
    
    def arrange_icons(self):
        self.clear_icons()
        for icon in self.icons:
            horizontal_layout = self.get_background_horizontal_layout() 
            horizontal_layout.add_widget(icon)
        
    def get_background_horizontal_layout(self):
        icon_width = self.icon_size[0] + self.icon_padding * 2
        num_x = max(1, int((Window.width - self.icon_padding * 2) / icon_width))    
        spacing = max(0, (Window.width - icon_width * num_x) / (num_x - 1)) + self.icon_padding
        horizontal_layouts = self.background_layout.children   
        if horizontal_layouts:
            horizontal_layout = horizontal_layouts[0]
            if len(horizontal_layout.children) < num_x:
                return horizontal_layout
        
        layout_height = self.icon_size[1] + self.icon_font_height + self.icon_padding
        horizontal_layout = BoxLayout(
            orientation="horizontal",
            padding=self.icon_padding,
            spacing=spacing,
            size_hint=(1,None),
            height=layout_height,
            pos_hint={"top":1}
        )
        self.background_layout.add_widget(horizontal_layout)
        padding = self.background_layout.padding
        spacing = self.background_layout.spacing
        num = len(self.background_layout.children)
        height = layout_height * num + spacing[1] * (num-1) + padding[1] + self.menu_layout.height
        self.background_layout.height = height
        return horizontal_layout
            
    def create_app_icon(self, icon_name, on_press, **kargs):  
        icon_layout = BoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            size=add(self.icon_size, (0, self.icon_font_height))
        )
        icon_btn = Button(
            size_hint=(None, None),
            size=self.icon_size,
            **kargs
        )
        
        icon_btn.bind(on_press=on_press)
        icon_label = Label(
            text=icon_name,
            halign="center",
            size_hint=(None,None),
            size=(self.icon_size[0], self.icon_font_height)
        )
        
        icon_layout.add_widget(icon_btn)
        icon_layout.add_widget(icon_label)
        self.icons.append(icon_layout)
        
    def do_on_start(self, ev):
        self.register_apps()
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)
        Clock.schedule_interval(self.update, 0)
    
    def on_resize(self, window, width, height):
        for app in self.active_apps.values():
            app.on_resize(window, width, height)
        self.arrange_icons()
        
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
                if app in self.app_press_time:
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
        if app in self.app_press_time:
            self.app_press_time.pop(app)
        app._BaseApp__on_stop()
                
    def update(self, dt):
        dt = max(1/1000, min(dt, 1/10))
        
        for app in self.active_apps.values():
            app.update(dt)
