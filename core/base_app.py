from kivy.logger import Logger
from kivy.uix.screenmanager import Screen
from utility.singleton import SingletonInstance


class BaseApp(SingletonInstance):
    app_name = "App"
    app_icon_file = ""
    orientation = "all"
    allow_multiple_instance = False 
    
    def __init__(self):
        super().__init__()
        self.__display_name = self.app_name
        self.__app_id = str(id(self))
        self.__screen = None
        self.__back_event = None
        self.__initialized = False
        self.__stop = False
        
    def initialize(self, display_name):
        if not self.__initialized:
            Logger.info(f"initialize {display_name}")
            self.__display_name = display_name
            self.__screen = Screen(name=self.get_app_id())
            self.on_initialize()
            self.__initialized = True
            
    def is_stopped(self):
        return self.__stop
        
    def stop(self):
        if not self.__stop:
            Logger.info(f"on_stop {self.get_display_name()}")
            self.on_stop()
            self.clear_instance()
            self.__stop = True
    
    def on_initialize(self):
        raise Exception("must implement!")
 
    def on_stop(self):
        raise Exception("must implement!")
    
    def on_back(self):
        raise Exception("must implement!")
    
    def on_resize(self, window, width, height):
        raise Exception("must implement!")

    def on_update(self, dt):
        raise Exception("must implement!")

    @ classmethod
    def get_app_name(cls):
        return cls.app_name
    
    @ classmethod
    def get_app_icon_file(cls):
        return cls.app_icon_file
   
    @ classmethod
    def get_orientation(cls):
        return cls.orientation
    
    def get_app_id(self):
        return self.__app_id
    
    def get_display_name(self):
        return self.__display_name

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
