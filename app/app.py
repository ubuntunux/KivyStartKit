import os
import sys
import traceback

from kivy.app import App
from kivy.core.window import Window
from kivy.config import Config
from kivy.clock import Clock
from kivy.metrics import Metrics
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.vkeyboard import VKeyboard
from kivy.logger import Logger

from app.constants import *
from utility.kivy_helper import *
from utility.singleton import SingletonInstane


class MyApp(App, SingletonInstane):
    def __init__(self):
        super(MyApp, self).__init__()
        
        self.app_name = "KivyStartKit"
        Logger.info(f'Run: {self.app_name}')

        self.is_first_update = False
        self.screen_helper = None
        self.screen = None
        
    def destroy(self):
        pass

    def on_stop(self):
        self.destroy()
        Config.write()

    def build(self):
        # Window.maximize()
        Window.softinput_mode = 'below_target'
        # keyboard_mode: '', 'system', 'dock', 'multi', 'systemanddock', 'systemandmulti'
        Config.set('kivy', 'keyboard_mode', 'system')
        Window.configure_keyboards()

        self.root = Widget()
        self.screen_helper = ScreenHelper(size=Window.size)
        self.root.add_widget(self.screen_helper.screen_manager)
        self.screen = Screen(name=self.app_name)
        self.screen_helper.add_screen(self.screen)
        self.screen_helper.current_screen(self.screen)

        layout = BoxLayout(orientation='vertical', size=(1, 1))
        self.screen.add_widget(layout)
        btn = Button(text=self.app_name)
        layout.add_widget(btn)

        Clock.schedule_interval(self.update, 0)
        return self.root

    def first_update(self):
        pass

    def update(self, dt):
        if self.is_first_update:
            self.first_update()
            self.is_first_update = False

