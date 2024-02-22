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
from .base_app import BaseApp


bright_blue = [1.5, 1.5, 2.0, 2]
dark_gray = [0.4, 0.4, 0.4, 2]


class UIManager(BaseApp):
    app_name = "UI Manager"
    orientation = "portrait"
    
    def __init__(self):
        super().__init__()
        self.active_app_buttons = {}
        self.app_scroll_view = None
        self.app_layout = None
        self.app_button_size = (DP(120), DP(30))
        self.menu_layout = None
        self.menu_layout_box = None
        self.background_layout = None
        self.icon_size = (DP(60), DP(60))
        self.icon_font_height = DP(15)
        self.icon_padding = DP(10)
        self.icons = []
        self.module_icon_map = {}
        self.app_press_time = {}
        self.app_icon_press_time = {}
        
    def on_initialize(self):
        pass
        
    def on_stop(self):
        pass
        
    def on_back(self):
        return False
        
    def on_resize(self, window, width, height):
        self.arrange_icons()
        
    def on_update(self, dt):
        pass
    
    def build(self, root_widget, screen_helper):
        # app list view
        self.menu_layout = BoxLayout(
            orientation='horizontal', 
            size_hint=(1.0, None), 
            height=self.app_button_size[1]
        )
        with self.menu_layout.canvas:
            Color(0,0,0,0.1)
            self.menu_layout_box = Rectangle(size=(max(Window.height, Window.height), self.menu_layout.height))
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
        self.get_screen().add_widget(self.background_scroll_view)
        screen_helper.add_screen(self.get_screen(), True)
        root_widget.add_widget(self.menu_layout)
    
    def create_app_icon(self, module_path, icon_name, icon_file, on_press, on_long_press):  
        icon_layout = BoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            size=add(self.icon_size, (0, self.icon_font_height))
        )
        icon_btn = Image(
            size_hint=(None, None),
            size=self.icon_size,
            source=icon_file,
            fit_mode="fill"
        )
        def on_touch_down(on_long_press, inst, touch):
            if inst.collide_point(*touch.pos):
                Logger.info(f"down: {inst}")
                event = Clock.schedule_once(on_long_press, 1)
                self.app_icon_press_time[inst] = event
                return True
            return False
            
        def on_touch_up(on_press, inst, touch):
            if inst.collide_point(*touch.pos):
                if inst in self.app_icon_press_time:
                    event = self.app_icon_press_time.pop(inst)
                    #Logger.info(f"up: event.is_triggered {event.is_triggered}")
                    if event.is_triggered != 0:
                        Clock.unschedule(event)
                        on_press(inst)
                        return True
            return False
            
        icon_btn.bind(
            on_touch_down=partial(on_touch_down, on_long_press),
            on_touch_up=partial(on_touch_up, on_press)
        )
        icon_label = Label(
            text=icon_name,
            halign="center",
            size_hint=(None,None),
            size=(self.icon_size[0], self.icon_font_height)
        )
        icon_layout.add_widget(icon_btn)
        icon_layout.add_widget(icon_label)
        self.module_icon_map[module_path] = icon_layout
        self.icons.append(icon_layout)
        
    def remove_app_icon(self, module_path):
        icon_layout = self.module_icon_map.get(module_path, None)
        Logger.info(f"remove_app_icon: {icon_layout}")
        if icon_layout in self.icons:
            self.icons.remove(icon_layout)
    
    def create_active_app_button(
        self,
        app,
        display_name,
        callback_set_current_active_app
    ):
        app_btn = Button(
            text=display_name,
            size_hint=(None, 1.0),
            width=self.app_button_size[0],
            background_color=dark_gray
        )        
        def deactive_app(app, dt):
            app.stop()
        def on_press(app, inst):
            event = Clock.schedule_once(partial(deactive_app, app), 1)
            self.app_press_time[app] = event
        def on_release(app, inst):
            if app in self.app_press_time:
                event = self.app_press_time.pop(app)
                Clock.unschedule(event)
                callback_set_current_active_app(app)
        app_btn.bind(
            on_press=partial(on_press, app),
            on_release=partial(on_release, app)
        )
        self.app_layout.add_widget(app_btn)        
        self.app_layout.width = app_btn.width * len(self.app_layout.children)
        if Window.size[0] < self.app_layout.width:
            self.app_scroll_view.scroll_x = 1.0        
        app_id = app.get_app_id()
        self.active_app_buttons[app_id] = app_btn
        
    def deactive_app_button(self, app):
        btn = self.active_app_buttons.pop(app.get_app_id())
        btn.parent.remove_widget(btn)
        if app in self.app_press_time:
            self.app_press_time.pop(app)
        self.show_app_list(show = 0 < len(self.active_app_buttons))
      
    def show_app_list(self, show):
        y = 0 if show else -self.menu_layout.height
        self.menu_layout.pos = (self.menu_layout.pos[0], y)
        self.menu_layout_box.pos = self.menu_layout.pos
    
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
            
    