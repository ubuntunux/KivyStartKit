from enum import Enum
from functools import partial
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.metrics import dp
from ..constant import *

class InteractionType(Enum):
    TRADE = 0
    SLEEP = 1
    ENTER = 2
 
class InteractionUI:
    def __init__(self):
        self.btn_trade = None
        self.btn_sleep = None
        self.btn_enter = None
        self.btn_close = None
        self.ui_interaction = None
        self.interaction_target = None

    def initialize(self, parent_layer, callback_interaction):
        def create_button(title, interaction_type):
            btn = Button(
                text=title,
                pos_hint={'center_x': 0.5, 'center_y':0.5},
                size_hint=(1, 1),
                background_color=(0,0,0,0.5)
            )
            btn.bind(on_press=partial(callback_interaction, interaction_type))
            return btn
        
        buttons = [
            create_button('TRADE', InteractionType.TRADE), 
            create_button('SLEEP', InteractionType.SLEEP), 
            create_button('ENTER', InteractionType.ENTER), 
        ]

        self.ui_interaction = BoxLayout(
            orientation='vertical',
            pos_hint={'center_x': 0.5, 'center_y':0.5},
            size = (dp(120), dp(40) * len(buttons)),
        )
        for btn in buttons:
            self.ui_interaction.add_widget(btn)

    def on_resize(self, window, width, height):
        pass

    def get_interaction_target(self):
        return self.interaction_target

    def set_interaction_target(self, target, callback):
        if self.interaction_target != target:
            if self.ui_interaction.parent:
                self.ui_interaction.parent.remove_widget(self.ui_interaction)
            if target:
                target.parent.add_widget(self.ui_interaction)
                self.ui_interaction.center = target.get_pos()
                self.ui_interaction.bind(on_press=callback)
            self.interaction_target = target

    def update(self, dt):
        pass
