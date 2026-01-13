from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scatter import Scatter
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
from .ui.inventory_ui import InventoryUI
from .ui.trade_ui import TradeUI
from .ui.player_controller import PlayerController
from .character_data import *
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
        self.inventory_ui = InventoryUI(app, self)
        self.trade_ui = TradeUI(app, self)
        
    def initialize(self, parent_widget, game_manager, level_manager, actor_manager):
        self.level_manager = level_manager
        self.actor_manager = actor_manager
        self.game_manager = game_manager

        self.controller_layer = FloatLayout(size_hint=(1,1))        
        self.player_controller.initialize(self.controller_layer)
        self.quick_slot.initialize(actor_manager, self.controller_layer)
        self.player_property_ui.initialize(actor_manager, self.controller_layer)
        self.target_property_ui.initialize(self.controller_layer)
        self.game_info_ui.initialize(actor_manager, level_manager, self.controller_layer)
        self.inventory_ui.initialize(actor_manager, self.controller_layer)
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

    def close(self):
        self.player_controller.close()

    def on_resize(self, window, width, height):
        self.player_controller.on_resize(window, width, height)
        self.quick_slot.on_resize(window, width, height)
        self.player_property_ui.on_resize(window, width, height)
        self.target_property_ui.on_resize(window, width, height)
        self.game_info_ui.on_resize(window, width, height)
        self.inventory_ui.on_resize(window, width, height)
        self.trade_ui.on_resize(window, width, height)

    def open_inventory_menu(self, actor):
        self.inventory_ui.open_inventory_menu(actor)

    def update_inventory_menu(self):
        self.inventory_ui.update_inventory_menu()

    def close_inventory_menu(self):
        self.inventory_ui.close_inventory_menu()

    def open_trade_menu(self, trade_actor):
        player = self.actor_manager.get_player()
        self.trade_ui.open_trade_menu(trade_actor)
        self.open_inventory_menu(player)

    def close_trade_menu(self):
        self.trade_ui.close_trade_menu()
        self.close_inventory_menu()

    def callback_buy_item(self, buy_item_data):
        player = self.actor_manager.get_player()
        if player:
            item_price = buy_item_data.get_extra_property_data().price
            result = True
            for (actor_data_name, price) in item_price.items():
                item_data = GameResourceManager.instance().get_character_data(actor_data_name)
                if player.get_item_count(item_data.actor_key) < price:
                    result = False
                    break

            if result:
                self.game_manager.effect_manager.create_effect(
                    effect_name=FX_PICK_ITEM,
                    attach_to=player
                )

                for (item_data_name, price) in item_price.items():
                    item_data = GameResourceManager.instance().get_character_data(item_data_name)
                    player.use_item(item_data.actor_key, price, interaction=False)
                player.add_item(buy_item_data)
                return True
        return False

    def callback_sell_item(self, sell_item_data):
        player = self.actor_manager.get_player()
        if player and sell_item_data.actor_type != ActorType.GOLD:
            if player.use_item(sell_item_data.actor_key, 1, interaction=False):
                self.game_manager.effect_manager.create_effect(
                    effect_name=FX_PICK_ITEM,
                    attach_to=player
                )
                item_price = sell_item_data.get_extra_property_data().price
                for (item_data_name, price) in item_price.items():
                    item_data = GameResourceManager.instance().get_character_data(item_data_name)
                    player.add_item(item_data, price)
                return True
        return False

    # quick slot
    def update_quick_slot(self):
        player = self.actor_manager.get_player()
        self.quick_slot.update_quick_slot(player)

    def add_item_to_quick_slot(self, item_actor):
        self.quick_slot.add_item(item_actor)
        self.update_quick_slot()

    def use_item(self, actor_key):
        player = self.actor_manager.get_player()
        if player:
            player.use_item(actor_key, 1, interaction=True)
        self.update_quick_slot()

    def set_target(self, target):
        self.target_property_ui.set_target(target)

    def get_interaction_target(self):
        return self.target_property_ui.get_interaction_target()

    def set_interaction_target(self, target):
        self.target_property_ui.set_interaction_target(target)

    def pressed_direction(self, direction):
        self.actor_manager.callback_move(direction)

    def callback_touch_down_move(self, inst):
        self.game_manager.set_trade_actor(None)

    def callback_attack(self, inst):
        if self.game_manager.is_trade_mode():
            self.game_manager.set_trade_actor(None)
        else:
            self.actor_manager.callback_attack(inst)

    def update(self, dt):
        self.player_controller.update(dt)
        self.player_property_ui.update(dt)
        self.quick_slot.update(dt)
        self.target_property_ui.update(dt)
        self.game_info_ui.update(dt)
        self.inventory_ui.update(dt) 
        self.trade_ui.update(dt) 
