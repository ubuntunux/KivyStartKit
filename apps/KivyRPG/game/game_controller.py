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
from .ui.interaction_ui import InteractionUI, InteractionType
from .ui.inventory_ui import InventoryUI
from .ui.trade_ui import TradeUI
from .ui.player_controller import PlayerController
from .ui.game_menu import GameMenu
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
        self.interaction_ui = InteractionUI()
        self.inventory_ui = InventoryUI(app, self)
        self.trade_ui = TradeUI(app, self)
        self.trade_actor = None
        self.game_menu = GameMenu(app, self)

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
        self.interaction_ui.initialize(self.callback_interaction)
        self.inventory_ui.initialize(actor_manager, self.controller_layer)
        self.trade_ui.initialize(actor_manager, self.controller_layer)
        self.trade_actor = None
        self.game_menu.initialize(actor_manager, self.controller_layer)

        menu_layout = BoxLayout(
            orientation='vertical',
            pos_hint={"right":1, "top":1},
            size_hint=(None, None),
            size=(dp(150), dp(150)),
            opacity=0.5
        )
        # reset level
        btn = Button(text="Reset", size_hint=(1, 1))
        btn.bind(on_press=game_manager.callback_reset)
        menu_layout.add_widget(btn)

        # change time
        btn = Button(text="Night Time", size_hint=(1, 1))
        btn.bind(on_press=level_manager.callback_night_time)
        menu_layout.add_widget(btn)

        # game menu
        btn = Button(text="Menu", size_hint=(1, 1))
        btn.bind(on_press=self.callback_open_game_menu)
        menu_layout.add_widget(btn)

        self.controller_layer.add_widget(menu_layout)
         
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

    # game menu
    def callback_open_game_menu(self, widget):
        self.game_menu.open_game_menu()

    def is_game_menu_opened(self):
        return self.game_menu.is_opened()

    # inventory
    def open_inventory_menu(self, actor):
        self.inventory_ui.open_inventory_menu(actor)

    def update_inventory_menu(self):
        self.inventory_ui.update_inventory_menu()

    def close_inventory_menu(self):
        self.inventory_ui.close_inventory_menu()

    # trade menu
    def open_trade_menu(self, trade_actor):
        player = self.actor_manager.get_player()
        self.trade_ui.open_trade_menu(trade_actor)
        self.open_inventory_menu(player)

    def close_trade_menu(self):
        self.trade_ui.close_trade_menu()
        self.close_inventory_menu()

    def is_trade_mode(self):
        return self.trade_actor is not None

    def set_trade_actor(self, trade_actor):
        if trade_actor and self.trade_actor is not trade_actor:
            self.open_trade_menu(trade_actor)
        elif trade_actor is None:
            self.close_trade_menu()
        self.trade_actor = trade_actor

    def callback_interaction(self, interaction_type, inst_widget):
        player = self.actor_manager.get_player()
        if not player or player.is_criminal():
            # criminal warn
            self.game_manager.effect_manager.create_effect(
                effect_name=FX_WARN,
                attach_to=player
            )
        else:
            # interaction
            if interaction_type == InteractionType.TRADE:
                self.set_trade_actor(player)

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
                    sell_price = max(1, int(price/4))
                    player.add_item(item_data, sell_price)
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

    def set_interaction_target(self, target):
        self.interaction_ui.set_interaction_target(target)

    def pressed_direction(self, direction):
        self.actor_manager.callback_move(direction)

    def callback_touch_down_move(self, inst):
        if self.is_game_menu_opened():
            return

        self.set_trade_actor(None)

    def callback_attack(self, inst):
        if self.is_game_menu_opened():
            return

        if self.is_trade_mode():
            self.set_trade_actor(None)
        else:
            self.actor_manager.callback_attack(inst)

    def update(self, dt):
        player = self.actor_manager.get_player()
        self.player_controller.update(dt)
        self.player_property_ui.update(dt)
        self.interaction_ui.update(player, dt)
        self.quick_slot.update(dt)
        self.target_property_ui.update(dt)
        self.game_info_ui.update(dt)
        self.inventory_ui.update(dt) 
        self.trade_ui.update(dt) 
        self.game_menu.update(dt) 
