from kivy.graphics.transformation import Matrix
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.scatter import Scatter
from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivy.metrics import dp
from utility.kivy_helper import *
from .constant import *


class CharacterProperties:
    def __init__(self, owner, property_data):
        self.owner = owner
        self.hp = 100.0
        self.mp = 100.0
        self.sp = 100.0
        self.move_speed = 1.0
        self.property_data = property_data

        self.ui_layout = BoxLayout(
            size_hint=(None, None),
            size=(dp(50), dp(6)),
            padding=dp(1)
        )
        create_dynamic_rect(self.ui_layout, (0,0,0,1))
        owner.add_widget(self.ui_layout)

        self.ui_width = dp(48)
        self.ui_hp = Widget(
            pos_hint={'x': 0}, 
            size_hint=(None, 1),
            width=self.ui_width
        )
        create_dynamic_rect(self.ui_hp, (1,0,0,1))
        self.ui_layout.add_widget(self.ui_hp)

    def reset_properties(self):
        self.sp = self.property_data.max_sp
        self.hp = self.property_data.max_hp
        self.mp = self.property_data.max_mp
    
    def get_max_sp(self):
        return self.property_data.max_sp
        
    def get_max_hp(self):
        return self.property_data.max_hp

    def get_max_mp(self):
        return self.property_data.max_mp

    def get_hp(self):
        return self.hp
    
    def get_mp(self):
        return self.mp
    
    def get_sp(self):
        return self.sp

    def get_walk_speed(self):
        return self.property_data.walk_speed * self.move_speed
    
    def set_damage(self, damage):
        self.hp -= damage
        
    def set_move_speed(self, move_speed):
        self.move_speed = move_speed

    def update_property(self, dt):
        self.ui_hp.width = self.ui_width * (self.get_hp() / self.get_max_hp())


