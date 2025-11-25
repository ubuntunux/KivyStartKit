from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.metrics import dp
from utility.kivy_widgets import *
from ..game_resource import GameResourceManager
from ..constant import *

class GameInfoUI:
    def __init__(self):
        self.actor_manager = None
        self.level_manager = None
        self.layout = None

    def initialize(self, actor_manager, level_manager, parent_layer):
        self.actor_manager = actor_manager
        self.level_manager = level_manager
        self.layout = BoxLayout(
            orientation='vertical',
            x=dp(10),
            size_hint=(None, None),
            width=dp(200),
            padding=dp(10)
        )
        self.layout.bind(minimum_height=self.layout.setter('height'))
        create_dynamic_rect(self.layout, (0,0,0,0.3))

        ui_height = dp(20)
        self.gold_ui = AutoLabel(
            text='GOLD: 0',
            size_hint=(None, None),
            height=ui_height,
            font_size=dp(16), 
            bold=True
        )
        self.layout.add_widget(self.gold_ui)
        
        self.time_of_day_ui = AutoLabel(
            text='14:00 PM',
            size_hint=(None, None),
            height=ui_height,
            font_size=dp(16), 
            bold=True
        )
        self.layout.add_widget(self.time_of_day_ui)
        parent_layer.add_widget(self.layout)
        self.on_resize(Window, Window.width, Window.height)
    
    def on_resize(self, window, width, height):
        self.layout.y = height - (self.layout.height + dp(100))

    def update(self, dt):
        player = self.actor_manager.get_player()
        gold = player.get_gold()
        self.gold_ui.text = f'GOLD: {gold}'


