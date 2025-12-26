from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.metrics import dp
from ..game_resource import GameResourceManager
from ..constant import *

class TargetPropertyUI:
    def __init__(self):
        self.ui_width = dp(200)
        self.ui_height = dp(30)
        self.ui_hp = None
        self.ui_text = None
        self.ui_layout = None
        self.ui_text_layout = None
        self.ui_ineraction = None
        self.interaction_target = None
        self.target = None
        self.target_time = 0.0

    def initialize(self, parent_layer):
        self.ui_interaction = Button(
            text='Interaction',
            pos_hint={'center_x': 0.5, 'center_y':0.5},
            size_hint=(None, None),
            size=(dp(120), dp(40))
        )
        self.ui_layout = BoxLayout(
            orientation='vertical',
            pos_hint={'center_x': 0.5},
            size_hint=(None, None),
            padding=dp(4)
        )
        create_dynamic_rect(self.ui_layout, (0,0,0,1))
        parent_layer.add_widget(self.ui_layout)

        self.ui_hp = Widget(pos_hint={'x': 0}, size_hint=(1, 1))
        create_dynamic_rect(self.ui_hp, (1,0,0,1))
        self.ui_layout.add_widget(self.ui_hp)

        self.ui_text_layout = BoxLayout(
            orientation='vertical',
            y=self.ui_layout.y,
            pos_hint={'center_x': 0.5},
            size_hint=(None, None),
            size=self.ui_layout.size,
            padding=dp(4)
        )
        self.ui_text = Label(
            text='TARGET',
            font_size=dp(16)
        )
        self.ui_text_layout.add_widget(self.ui_text)
        parent_layer.add_widget(self.ui_text_layout)
        self.on_resize(Window, Window.width, Window.height)
        self.set_target(None)

    def on_resize(self, window, width, height):
        self.ui_width = window.width * 0.5
        self.ui_height = dp(20)
        self.ui_layout.y = window.height - (self.ui_height + dp(10)) 
        self.ui_layout.size = (self.ui_width, self.ui_height)
        self.ui_text_layout.y = self.ui_layout.y
        self.ui_text_layout.size = self.ui_layout.size

    def set_target(self, target):
        self.target_time = 3.0
        self.target = target
        if target:
            self.ui_layout.opacity = 0.7 
            self.ui_text.text = str(target.actor_type).split('.', 1)[1]
        else:
            self.ui_layout.opacity = 0
            self.ui_text.text = ''

    def get_interaction_target(self):
        return self.interaction_target

    def set_interaction_target(self, target):
        if self.interaction_target != target:
            if self.ui_interaction.parent:
                self.ui_interaction.parent.remove_widget(self.ui_interaction)
            if target:
                target.add_widget(self.ui_interaction)
            self.interaction_target = target

    def update(self, dt):
        if self.target:
            if 0.0 < self.target_time:
                if self.target.property.has_hp_property():
                    t = self.target.property.get_hp() / self.target.property.get_max_hp()
                    if 0 < t:
                        self.ui_hp.size_hint_x = t 
                        self.ui_hp.opacity = 1
                    else:
                        self.ui_hp.opacity = 0
                else:
                    self.ui_hp.opacity = 0
                self.target_time -= dt
                if self.target_time <= 0.0:
                    self.set_target(None)
