from kivy.logger import Logger
from kivy.uix.button import Button
from core.base_app import BaseApp

# You must keep this rule.
class App(BaseApp):
    app_name = "Add App..."
    orientation = "all" # all, landscape, portrait
    __instance = None
    __initialized = False
    
    def __new__(cls, *args, **kargs):
        if cls.__instance is None: 
            cls.__instance = super().__new__(cls)
        return cls.__instance
        
    @classmethod
    def __clear_instance__(cls):
        cls.__instance = None
        cls.__initialized = False
    
    def __init__(self):
        if App.__initialized:
            return  
        super().__init__()
        
        App.__initialized = True
        
    def initialize(self):
        pass
        
    def on_stop(self):
        self.__clear_instance__()
        
    def on_resize(self, window, width, height):
        pass
        
    def update(self, dt):
        pass
