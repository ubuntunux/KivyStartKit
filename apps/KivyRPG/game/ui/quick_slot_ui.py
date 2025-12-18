from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.metrics import dp
from ..game_resource import GameResourceManager
from ..constant import *

class ItemUI(ButtonBehavior, BoxLayout):
    def __init__(self, width, height, callback):
        icon_size = width - dp(4)
        super().__init__(
            orientation='vertical',
            size_hint=(None, None),
            size=(width, height)
        )
        self.bind(on_press=callback)
        
        self.icon = Image(
            size_hint=(None, None), 
            width=icon_size,
            height=icon_size,
            fit_mode="fill"
        )
        self.label = Label(
            halign='left',
            valign='middle',
            size_hint=(1, 1), 
        )
        self.add_widget(self.icon)
        self.add_widget(self.label)
        
        self.actor = None
        self.update_item()

    def is_empty(self):
        return self.actor is None

    def add_item(self, item_actor):
        self.actor = item_actor
        self.update_item()

    def update_item(self): 
        count = self.actor.get_extra_property().get_item_count() if self.actor else 0
        if 0 < count:
            self.icon.texture = self.actor.data.action_data.get('idle').texture
            self.icon.opacity = 1
            self.icon.disabled = False
            self.label.text = f'{count}'
        else:
            self.remove_item() 

    def remove_item(self):
        self.actor = None
        self.icon.opacity = 0
        self.icon.disabled = True
        self.label.text = ''

class QuickSlotUI:
    def __init__(self, app, game_controller):
        self.app = app
        self.game_controller = game_controller
        self.actor_manager = None
        self.layer = None
        self.items = []

    def initialize(self, actor_manager, parent_layer):
        self.actor_manager = actor_manager
        quick_slot_count = 10
        button_width = dp(40)
        button_height = button_width + dp(20)
        self.layout = BoxLayout(
            orientation="horizontal",
            pos_hint={'center_x': 0.5},
            y=dp(10),
            size_hint=(None, None),
            size=(button_width * quick_slot_count, button_height)
        )
        create_dynamic_rect(self.layout, (0,0,0,0.5))

        for i in range(quick_slot_count):
            item = ItemUI(
                button_width,
                button_height,
                self.callback_use_item
            )
            self.layout.add_widget(item)
            self.items.append(item)
 
        parent_layer.add_widget(self.layout)
    
    def update_quick_slot(self, player):
        for (i, item) in enumerate(self.items):
            if not player or not item.actor or not player.get_item(item.actor.get_actor_key()):
                item.remove_item()
            item.update_item()

    def add_item(self, item_actor):
        for (i, item) in enumerate(self.items):
            if item.actor is None or item.actor is item_actor:
                item.add_item(item_actor)
                break

    def callback_use_item(self, item):
        if item.actor and 0 < item.actor.get_extra_property().get_item_count():
            self.game_controller.use_item(item.actor.get_actor_key())
        item.update_item()

    def on_resize(self, window, width, height):
        pass

    def update(self, dt):
        pass


