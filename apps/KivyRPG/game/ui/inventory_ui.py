
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.metrics import dp
from ..game_resource import GameResourceManager
from ..constant import *

class ItemUI(ButtonBehavior, BoxLayout):
    def __init__(self, item_actor, size, callback):
        padding = [dp(6), dp(6), 0, 0]
        text_height = dp(10)

        super().__init__(size_hint=(None, None), size=size, padding=padding)
        self.bind(on_press=callback)
        self.item_actor = item_actor
        item_data = item_actor.data

        icon_size = size[1] - text_height - padding[1] - padding[3]
        icon_layout = BoxLayout(
            orientation='vertical', 
            size_hint=(None, None),
            width=icon_size,
            height=icon_size + text_height,
            padding=padding
        )
        icon = Image(
            size_hint=(None, None), 
            width=icon_size,
            height=icon_size,
            fit_mode="fill"
        )
        icon.texture = item_data.action_data.get('idle').texture
        item_count_label = Label(
            halign='left',
            valign='middle',
            size_hint=(1, None), 
            height=text_height,
            text=str(item_actor.get_extra_property().get_item_count())
        )
        icon_layout.add_widget(icon)
        icon_layout.add_widget(item_count_label)
        self.add_widget(icon_layout)

        desc_padding = dp(10)
        desc_size = [size[0] - icon_layout.width - desc_padding, icon_size]
        description_layout = BoxLayout(
            orientation='vertical', 
            size_hint=(None, None),
            size=desc_size,
            padding=[desc_padding, 0,0,0]
        )
        description_label = Label(
            halign='left',
            valign='top',
            size_hint=(None, None),
            size=desc_size,
            text_size=desc_size,
            text=item_data.display_name
        )
        description_label.bind(size=description_label.setter('text_size'))
        description_layout.add_widget(description_label)
        self.add_widget(description_layout)
 
        price_layout = BoxLayout(size_hint=(1,1))
        self.add_widget(price_layout)
        self.item_data = item_data

class InventoryUI:
    def __init__(self, app, game_controller):
        self.app = app
        self.game_controller = game_controller
        self.actor_manager = None
        self.parent_layer = None
        self.inventory_menu_layout = None
        self.box_layout = None
        self.items = {}
        self.owner_actor = None
        self.width = dp(200)
        self.button_size = dp(60)

    def initialize(self, actor_manager, parent_layer):
        self.actor_manager = actor_manager
        self.parent_layer = parent_layer 

    def open_inventory_menu(self, inventory_actor):
        self.close_inventory_menu()

        self.owner_actor = inventory_actor
        button_count = 5
        self.inventory_menu_layout = ScrollView(
            do_scroll_y=True,
            pos_hint={'center_y': 0.5},
            size_hint=(None, None),
            size=(self.width, self.button_size * button_count),
        )
        create_dynamic_rect(self.inventory_menu_layout, (0,0,0,0.5)) 

        self.box_layout = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
        )
        self.inventory_menu_layout.add_widget(self.box_layout)
        self.parent_layer.add_widget(self.inventory_menu_layout)
        self.update_inventory_menu()
        self.on_resize(Window, Window.width, Window.height)

    def close_inventory_menu(self):
        if self.inventory_menu_layout and self.inventory_menu_layout.parent:
            self.inventory_menu_layout.parent.remove_widget(self.inventory_menu_layout)
        self.inventory_menu_layout = None
        self.owner_actor = None
        self.items.clear()
    
    def update_inventory_menu(self):
        if self.owner_actor:
            item_map = self.owner_actor.get_items()
            items = list(item_map.items())
            #items.sort()
            for (actor_key, item_actor) in items:
                item = ItemUI(
                    item_actor,
                    (self.width, self.button_size),
                    self.callback_buy_item
                )
                self.box_layout.add_widget(item)
                self.items[actor_key] = item
            self.box_layout.height = len(self.box_layout.children) * self.button_size
        else:
            self.close_inventory_menu()

    def callback_buy_item(self, inst, *args): 
        self.game_controller.callback_buy_item(inst.item_data)

    def on_resize(self, window, width, height):
        if self.inventory_menu_layout:
            self.inventory_menu_layout.x = window.width * 0.5 + dp(20)

    def update(self, dt):
        pass


