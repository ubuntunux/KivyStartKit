from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.metrics import dp
from ..game_resource import GameResourceManager
from ..constant import *

class ItemUI(ButtonBehavior, BoxLayout):
    def __init__(self, item_data, size, callback):
        super().__init__(size_hint=(None, None), size=size)
        self.bind(on_press=callback)
        
        text_height = dp(10)
        icon_size = size[1] - text_height
        layout = BoxLayout(
            orientation='vertical', 
            size_hint=(None, None),
            width=size[1],
            height=size[1]
        )
        icon = Image(
            size_hint=(None, None), 
            width=icon_size,
            height=icon_size,
            fit_mode="fill"
        )
        icon.texture = item_data.action_data.get('idle').texture
        label = Label(
            halign='left',
            valign='middle',
            size_hint=(None, None), 
            width=size[1],
            height=text_height,
            text=item_data.display_name
        )
        layout.add_widget(icon)
        layout.add_widget(label)
        self.add_widget(layout)
 
        price_layout = BoxLayout(size_hint=(1,1))
        self.add_widget(price_layout)
        self.item_data = item_data

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
        width = button_size * 5.0
        self.trade_menu_layout = BoxLayout(
            orientation="vertical",
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(None, None),
            size=(width, button_size * button_count)
        )
        create_dynamic_rect(self.trade_menu_layout, (0,0,0,0.5)) 
        item_data_list = [ITEM_HP_A, ITEM_HP_B, ITEM_HP_A, ITEM_HP_A, ITEM_HP_A] 
        for i in range(button_count):
            item_data = GameResourceManager.instance().get_character_data(item_data_list[i])  
            item = ItemUI(
                item_data,
                (width, button_size),
                self.callback_buy_item
            )
            self.trade_menu_layout.add_widget(item)
            self.items.append(item)

        self.parent_layer.add_widget(self.trade_menu_layout)

    def close_trade_menu(self):
        if self.trade_menu_layout and self.trade_menu_layout.parent:
            self.trade_menu_layout.parent.remove_widget(self.trade_menu_layout)
        self.trade_menu_layout = None
        self.items.clear()
    
    def callback_buy_item(self, inst, *args): 
        self.game_controller.callback_buy_item(inst.item_data)

    def on_resize(self, window, width, height):
        pass

    def update(self, dt):
        pass


