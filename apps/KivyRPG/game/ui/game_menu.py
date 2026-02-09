from enum import Enum
from functools import partial
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.metrics import dp
from ..character_data import * 
from ..constant import *

class GameMenuType(Enum):
    NEW = 0
    LOAD = 1
    SAVE = 2
    INVENTORY = 3
    CLOSE = 4

class GameMenu:
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
        self.menu_layout = BoxLayout(
            orientation='vertical',
            pos_hint={"center_x":0.5, "center_y":0.5},
            size_hint=(None, None),
        )

        def add_button(title, callback):
            btn = Button(text=title, size_hint=(1, 1))
            btn.bind(on_press=callback)
            self.menu_layout.add_widget(btn)

        add_button("New", self.callback_new)
        add_button("Load", self.callback_load)
        add_button("Save", self.callback_save)
        add_button("Close", self.close_game_menu)

        self.menu_layout.size = (dp(300), dp(50) * len(self.menu_layout.children))

    def is_opened(self):
        return self.menu_layout.parent is not None

    def open_game_menu(self):
        if not self.is_opened():
            self.parent_layer.add_widget(self.menu_layout) 

    def close_game_menu(self, widget=None):
        if self.is_opened():
            self.parent_layer.remove_widget(self.menu_layout)

    def callback_new(self, widget):
        self.close_game_menu()
        self.game_controller.new_game()

    def callback_load(self, widget):
        self.close_game_menu()
        self.game_controller.load_game()

    def callback_save(self, widget):
        self.close_game_menu()
        self.game_controller.save_game()

    def on_resize(self, window, width, height):
        pass

    def update(self, dt):
        pass
