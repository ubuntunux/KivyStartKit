import os
import traceback
from collections import OrderedDict
from functools import partial

import kivy
from kivy.app import App
from kivy.logger import Logger
from kivy.uix.screenmanager import Screen

from .main_app import MainApp


class BaseApp(App):
    app_name = ""
    
    def __init__(self, orientation="all"):
        Logger.info(f'Run: {self.get_name()}')
        self.main_app = MainApp.instance()
        self.orientation = orientation
        self.__screen = Screen(name=self.get_app_id())
        self.__back_event = None
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
    
    def on_resize(self, window, width, height):
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
