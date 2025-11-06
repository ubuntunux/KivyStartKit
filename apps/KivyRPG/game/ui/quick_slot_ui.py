from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.metrics import dp
from ..game_resource import GameResourceManager
from ..constant import *

class QuickSlotUI:
    def __init__(self, app, game_controller):
        self.app = app
        self.game_controller = game_controller
        self.actor_manager = None

    def initialize(self, actor_manager, parent_layer):
        self.actor_manager = actor_manager
        button_count = 5
        button_size = dp(50)
        layout = BoxLayout(
            orientation="horizontal",
            pos_hint={'center_x': 0.5},
            y=0,
            size_hint=(None, None),
            size=(button_size * button_count, button_size)
        )
        
        for i in range(button_count):
            button = Button(
                size_hint=(None, None), 
                size=(button_size, button_size)
            )
            layout.add_widget(button)

        parent_layer.add_widget(layout)

    def on_resize(self, window, width, height):
        pass

    def update(self, dt):
        player = self.actor_manager.get_player()



