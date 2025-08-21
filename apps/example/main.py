from kivy.logger import Logger
from kivy.uix.button import Button
from core.base_app import BaseApp

# You must keep this rule.
class App(BaseApp):
    app_name = "Hello, world!"
    orientation = "all" # all, landscape, portrait
    allow_multiple_instance = False
    
    def __init__(self):
        super().__init__()
        
    def on_initialize(self):
        btn = Button(text="Hello, world!", size_hint=(1, 1))
        self.add_widget(btn)
    
    def on_stop(self):
        pass
    
    def on_back(self):
        return False
        
    def on_resize(self, window, width, height):
        pass
        
    def on_update(self, dt):
        pass
 
