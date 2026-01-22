from enum import Enum
from functools import partial
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.metrics import dp
from ..character_data import * 
from ..constant import *

class InteractionType(Enum):
    TRADE = 0
    ENTER = 1
 
class InteractionUI:
    def __init__(self):
        self.remove_candidate_interactions = {}
        self.ui_interactions = {}
        self.menu_height = dp(40)
        self.callback_interaction = None

    def initialize(self, callback_interaction):
        self.callback_interaction = callback_interaction
        self.ui_interactions = {}
        self.remove_candidate_interactions = {}

    def create_button(self, layout, title, interaction_type):
        btn = Button(
            text=title,
            pos_hint={'center_x': 0.5, 'center_y':0.5},
            size_hint=(1, 1),
            background_color=(0,0,0,0.5)
        )
        btn.bind(on_press=partial(self.callback_interaction, interaction_type))
        layout.add_widget(btn)
        return btn
    
    def on_resize(self, window, width, height):
        pass

    def set_interaction_target(self, target):
        if target in self.remove_candidate_interactions:
            self.ui_interactions[target] = self.remove_candidate_interactions.pop(target)
        elif target not in self.ui_interactions:
            ui_interaction = BoxLayout(
                orientation='vertical',
                pos_hint={'center_x': 0.5, 'center_y':0.5},
                size_hint = (None, None),
                size = (dp(120), self.menu_height),
            )

            if target.actor_type in [ActorType.INN, ActorType.CASTLE]:
                self.create_button(ui_interaction, 'TRADE', InteractionType.TRADE)
            if target.actor_type is ActorType.DUNGEON:
                self.create_button(ui_interaction, 'ENTER', InteractionType.ENTER)
            ui_interaction.center = target.get_pos()
            ui_interaction.height = self.menu_height * len(ui_interaction.children)
            target.parent.add_widget(ui_interaction)
            self.ui_interactions[target] = ui_interaction

    def update(self, player, dt):
        for (target, ui_interaction) in self.remove_candidate_interactions.items():
            ui_interaction.parent.remove_widget(ui_interaction)

        self.remove_candidate_interactions = self.ui_interactions
        self.ui_interactions = {}
