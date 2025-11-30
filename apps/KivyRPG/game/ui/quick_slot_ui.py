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
    def __init__(self, parent, size, callback):
        self.actor = None
        self.button = Button(
            size_hint=(None, None), 
            size=(size, size),
            text=''
        )
        self.button.owner = self
        self.button.bind(on_press=callback)
        parent.add_widget(self.button)

    def add_item(self, item_actor):
        self.actor = item_actor
        self.update_item()

    def update_item(self): 
        count = self.actor.get_instance_count() if self.actor else 0
        if 0 < count:
            self.button.text = f'{self.actor.data.display_name}:{count}'
        else:
            self.remove_item() 

    def remove_item(self):
        self.item_data = None
        self.button.text = ''

class QuickSlotUI:
    def __init__(self, app, game_controller):
        self.app = app
        self.game_controller = game_controller
        self.actor_manager = None
        self.layer = None
        self.items = []

    def initialize(self, actor_manager, parent_layer):
        self.actor_manager = actor_manager
        quick_slot_count = 5
        button_size = dp(50)
        self.layout = BoxLayout(
            orientation="horizontal",
            pos_hint={'center_x': 0.5},
            y=0,
            size_hint=(None, None),
            size=(button_size * quick_slot_count, button_size)
        )

        for i in range(quick_slot_count):
            item = ItemUI(
                self.layout,
                button_size,
                self.callback_use_item
            )
            self.items.append(item)
 
        parent_layer.add_widget(self.layout)

    def add_item(self, item_actor):
        for item in self.items:
            if item.actor is None or item.actor is item_actor:
                item.add_item(item_actor)
                break

    def callback_use_item(self, button):
        item = button.owner
        if item.actor and 0 < item.actor.get_instance_count():
            self.game_controller.use_item(item.actor)
            item.update_item()
            if item.actor.get_instance_count() <= 0:
                item.remove_item()

    def on_resize(self, window, width, height):
        pass

    def update(self, dt):
        pass


