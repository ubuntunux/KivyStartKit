from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scatter import Scatter
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.utils import platform 
from utility.singleton import SingletonInstance
from .game_resource import GameResourceManager
from .ui.game_info_ui import GameInfoUI
from .ui.target_property_ui import TargetPropertyUI
from .ui.player_property_ui import PlayerPropertyUI
from .ui.quick_slot_ui import QuickSlotUI
from .ui.trade_ui import TradeUI
from .ui.player_controller import PlayerController
from .constant import *
       
class GameController(SingletonInstance):
    def __init__(self, app):
        self.app = app
        self.actor_manager = None
        self.level_manager = None
        self.game_manager = None
        self.player_controller = PlayerController(app, self)
        self.quick_slot = QuickSlotUI(app, self)
        self.player_property_ui = PlayerPropertyUI(app, self) 
        self.target_property_ui = TargetPropertyUI()
        self.game_info_ui = GameInfoUI()
        self.trade_ui = TradeUI(app, self)
        
    def initialize(self, parent_widget, game_manager, level_manager, actor_manager):
        self.level_manager = level_manager
        self.actor_manager = actor_manager
        self.game_manager = game_manager

        self.trade_layer = FloatLayout(size_hint=(1,1))        
        self.controller_layer = FloatLayout(size_hint=(1,1))        
        self.player_controller.initialize(self.controller_layer)
        self.quick_slot.initialize(actor_manager, self.controller_layer)
        self.player_property_ui.initialize(actor_manager, self.controller_layer)
        self.target_property_ui.initialize(self.controller_layer)
        self.game_info_ui.initialize(actor_manager, level_manager, self.controller_layer)
        self.trade_ui.initialize(actor_manager, self.controller_layer)

        # reset level
        btn = Button(text="Reset", pos_hint={"right":1, "top":1}, size_hint=(None, 0.05), width=300, opacity=0.5)
        btn.bind(on_press=game_manager.callback_reset)
        self.controller_layer.add_widget(btn)

        # change time
        btn = Button(text="Night Time", pos_hint={"right":1, "top":0.95}, size_hint=(None, 0.05), width=300, opacity=0.5)
        btn.bind(on_press=level_manager.callback_night_time)
        self.controller_layer.add_widget(btn)
        
        parent_widget.add_widget(self.controller_layer)
        parent_widget.add_widget(self.trade_layer)

    def close(self):
        self.player_controller.close()

    def on_resize(self, window, width, height):
        self.player_controller.on_resize(window, width, height)
        self.quick_slot.on_resize(window, width, height)
        self.player_property_ui.on_resize(window, width, height)
        self.target_property_ui.on_resize(window, width, height)
        self.game_info_ui.on_resize(window, width, height)
        self.trade_ui.on_resize(window, width, height)

    def open_trade_menu(self, trade_actor):
        self.trade_ui.open_trade_menu(trade_actor)

    def close_trade_menu(self):
        self.trade_ui.close_trade_menu()

    def callback_buy_item(self, item_data):
        player = self.actor_manager.get_player()
        if player:
            player.buy_item(item_data)

    def add_item(self, item_actor):
        self.quick_slot.add_item(item_actor)

    def use_item(self, item_actor):
        player = self.actor_manager.get_player()
        if player:
            player.use_item(item_actor)

    def set_target(self, target):
        self.target_property_ui.set_target(target)

    def pressed_direction(self, direction):
        self.actor_manager.callback_move(direction)
    
    def update(self, dt):
        self.player_controller.update(dt)
        self.player_property_ui.update(dt)
        self.quick_slot.update(dt)
        self.target_property_ui.update(dt)
        self.game_info_ui.update(dt)
        self.trade_ui.update(dt) 
