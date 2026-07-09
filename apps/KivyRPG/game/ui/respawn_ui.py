from enum import Enum
from functools import partial
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.metrics import dp
from ..character_data import * 
from ..constant import *

class GameMenuType(Enum):
    RESPAWN_AT_TOWN = 0
    RESPAWN_HERE = 1

class RespawnUI:
    def __init__(self, app, game_controller):
        self.app = app
        self.game_controller = game_controller
        self.menu_height = dp(40)
        self.actor_manager = None
        self.parent_layer = None
        self.menu_layout = None

    def initialize(self, actor_manager, parent_layer):
        self.actor_manager = actor_manager
        self.parent_layer = parent_layer
        self.menu_background = FloatLayout(
            pos_hint={"center_x":0.5, "center_y":0.5},
            size_hint=(1, 1),
        )
        create_dynamic_rect(self.menu_background, (0,0,0,0.3))

        self.menu_layout = BoxLayout(
            orientation='vertical',
            pos_hint={"center_x":0.5, "center_y":0.5},
            size_hint=(None, None),
        )
        self.menu_background.add_widget(self.menu_layout)

        def add_button(title, callback):
            btn = Button(text=title, background_color=(0.5,0.5,0.5), size_hint=(1, 1), opacity=0.8)
            btn.bind(on_press=callback)
            self.menu_layout.add_widget(btn)

        add_button("Respawn at town", self.callback_respawn_at_town)
        add_button("Respawn here", self.callback_respawn_here)

        self.menu_layout.size = (dp(300), dp(50) * len(self.menu_layout.children))

    def is_opened(self):
        return self.menu_background.parent is not None

    def open_respawn_menu(self):
        if not self.is_opened():
            self.parent_layer.add_widget(self.menu_background) 

    def close_respawn_menu(self, widget=None):
        if self.is_opened():
            self.parent_layer.remove_widget(self.menu_background)

    def callback_respawn_at_town(self, widget):
        self.close_respawn_menu()
        self.game_controller.respawn(True)

    def callback_respawn_here(self, widget):
        self.game_controller.game_manager.effect_manager.create_effect(
            effect_name=FX_WARN
        )
        return

        self.close_respawn_menu()
        self.game_controller.respawn(False)

    def on_resize(self, window, width, height):
        pass

    def update(self, dt):
        player = self.actor_manager.get_player()
        if player and not player.is_alive(): 
            self.open_respawn_menu()
