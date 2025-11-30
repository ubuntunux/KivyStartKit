from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.metrics import dp
from ..game_resource import GameResourceManager
from ..constant import *

class ItemUI:
    def __init__(self, item_data, parent_layer, size, callback):
        self.item_data = item_data
        button = Button(
            size_hint=(None, None), 
            size=(size, size),
            text=item_data.display_name
        )
        button.owner = self
        button.bind(on_press=callback)
        parent_layer.add_widget(button)
 
class TradeUI:
    def __init__(self, app, game_controller):
        self.app = app
        self.game_controller = game_controller
        self.actor_manager = None
        self.parent_layer = None
        self.trade_menu_layout = None
        self.items = [] 

    def initialize(self, actor_manager, parent_layer):
        self.actor_manager = actor_manager
        self.parent_layer = parent_layer

    def open_trade_menu(self, trade_actor):
        self.close_trade_menu()

        button_count = 5
        button_size = dp(50)
        self.trade_menu_layout = BoxLayout(
            orientation="vertical",
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(None, None),
            size=(button_size * button_count, button_size)
        )
        
        hp_item_data = GameResourceManager.instance().get_character_data('items/hp_100')  
        for i in range(button_count):
            item = ItemUI(
                hp_item_data,
                self.trade_menu_layout,
                button_size,
                self.callback_buy_item
            )
            self.items.append(item)

        self.parent_layer.add_widget(self.trade_menu_layout)

    def close_trade_menu(self):
        if self.trade_menu_layout and self.trade_menu_layout.parent:
            self.trade_menu_layout.parent.remove_widget(self.trade_menu_layout)
        self.trade_menu_layout = None
        self.items.clear()
    
    def callback_buy_item(self, inst, *args): 
        self.game_controller.callback_buy_item(inst.owner.item_data)

    def on_resize(self, window, width, height):
        pass

    def update(self, dt):
        pass


