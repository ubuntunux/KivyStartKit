from kivy.logger import Logger
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout

from core.base_app import BaseApp
from utility.screen_manager import ScreenHelper

# You must keep this rule.
class App(BaseApp):
    app_name = "Add App..."
    orientation = "all" # all, landscape, portrait
    allow_multiple_instance = False
    
    def __init__(self):
        super().__init__()

    def initialize(self):
        layout = BoxLayout(orientation="vertical", size_hint=(1,1))
        self.add_widget(layout)
        
        screen_helper = ScreenHelper(size_hint=(1,1))
        layout.add_widget(screen_helper.screen_manager)
        
        screen = Screen(name="ok")
        screen_helper.add_screen(screen, True)
        btn = Button(text="Hello, world!", size_hint=(1, 1))
        screen.add_widget(btn)
        
        screen = Screen(name="ok2")
        screen_helper.add_screen(screen, False)
        btn = Button(text="World!", size_hint=(1, 1))
        screen.add_widget(btn)
        
        screen_helper = ScreenHelper(size_hint=(1,1))
        layout.add_widget(screen_helper.screen_manager)
        
        screen = Screen(name="ok2")
        screen_helper.add_screen(screen, True)
        btn = Button(text="Bye, world!", size_hint=(1, 1))
        screen.add_widget(btn)
    
        
    def on_stop(self):
        pass
        
    def on_resize(self, window, width, height):
        pass
        
    def update(self, dt):
        pass
