from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.metrics import dp
from ..game_resource import GameResourceManager
from ..constant import *

class PlayerPropertyUI:
    def __init__(self, app, game_controller):
        self.app = app
        self.game_controller = game_controller
        self.actor_manager = None

    def initialize(self, actor_manager, parent_layer):
        self.actor_manager = actor_manager
        layout = BoxLayout(
            orientation="horizontal",
            pos_hint={'center_x': 0.5},
            y=0,
            size_hint=(None, None),
            size=(dp(50), dp(50))
        )
        
        parent_layer.add_widget(layout)
    
    def on_resize(self, window, width, height):
        pass

    def update(self, dt):
        player = self.actor_manager.get_player()



