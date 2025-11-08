import os
import sys
import traceback

from kivy.config import Config
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from core.base_app import BaseApp
from utility.kivy_helper import *
from utility.singleton import SingletonInstance
from utility.kivy_widgets import DebugLabel

from .game.level import LevelManager
from .game.actor import ActorManager
from .game.effect import GameEffectManager
from .game.game_controller import GameController
from .game.game_resource import GameResourceManager
from .game.game_manager import GameManager

class KivyRPGApp(BaseApp):
    app_name = "Kivy RPG"
    orientation = "all" # all, landscape, portrait
    allow_multiple_instance = False

    def __init__(self):
        super().__init__()
        game_path = os.path.split(__file__)[0]
        self.resource_manager = GameResourceManager.instance(game_path)
        self.level_manager = LevelManager.instance(self)
        self.actor_manager = ActorManager.instance(self)
        self.effect_manager = GameEffectManager.instance(self)
        self.game_controller = GameController.instance(self)
        self.game_manager = GameManager.instance(self)
        self.debug_label = None
        
    def build(self):
        self.debug_label = DebugLabel(
            pos=(0, Window.height),
            text="debug", 
            halign='left',
            font_size="12sp",
            size_hint=(None, None),
            width=Window.width,
            display_count=40,
            display_time=20
        )
        self.add_widget(self.debug_label)
        
    def debug_print(self, text):
        if str != type(text):
            text = str(text)
        self.debug_label.debug_print(text)
        
    def on_initialize(self):
        self.resource_manager.initialize()
        self.level_manager.initialize(self, self.actor_manager, self.effect_manager)
        self.actor_manager.initialize(self.game_controller, self.level_manager)
        self.effect_manager.initialize(self.level_manager, self.level_manager.get_effect_layout())
        self.game_controller.initialize(self, self.game_manager, self.level_manager, self.actor_manager)
        self.game_manager.initialize()
        self.build()

        self.game_manager.game_start()

    def on_stop(self):
        self.game_manager.close()
        self.game_controller.close()
        self.effect_manager.close()
        self.actor_manager.close()
        self.level_manager.close()
        self.resource_manager.close()

    def on_back(self):
        pass
        
    def on_resize(self, window, width, height):
        self.game_controller.on_resize(window, width, height)
        
    def on_update(self, dt):
        self.debug_label.update(dt)
        self.debug_label.pos = (0, Window.height - self.debug_label.height)
        self.game_manager.update(dt)
        self.game_controller.update(dt)
        self.effect_manager.update(dt)
        self.actor_manager.update(dt)
        self.level_manager.update(dt)
        
