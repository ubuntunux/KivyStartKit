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

class BaseProperty:
    def __init__(self, owner):
        self.owner = owner

    def reset_property(self):
        pass

    def update_property(self, dt):
        pass

class SpawnerProperty(BaseProperty):
    def __init__(self, owner, property_data):
        super().__init__(owner)
        self.property_data = property_data

    def get_spawn_data(self):
        return self.property_data.spawn_data

    def get_spawn_term(self):
        return self.property_data.spawn_term

    def get_limit_spawn_count(self):
        return self.property_data.limit_spawn_count

    def get_spawn_data(self):
        return self.property_data.spawn_data


class CharacterProperty(BaseProperty):
    def __init__(self, owner, property_data):
        super().__init__(owner)
        self.hp = 0.0
        self.mp = 0.0
        self.sp = 0.0
        self.move_speed = 1.0
        self.spawner_property = None
        self.property_data = property_data
        self.ui_width = dp(48)
        self.ui_layout = None
        self.ui_hp = None

        if property_data.spawner_property_data:
            self.spawner_property = SpawnerProperty(owner, property_data.spawner_property_data)

        self.reset_property()
        self.build_ui()

    def build_ui(self):
        if not self.has_sp_property() and not self.has_hp_property() and not self.has_mp_property():
            return

        self.ui_layout = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            size=(self.ui_width + 2, dp(6)),
            padding=dp(1)
        )
        create_dynamic_rect(self.ui_layout, (0,0,0,1))
        self.owner.add_widget(self.ui_layout)

        if self.has_hp_property():
            self.ui_hp = Widget(
                pos_hint={'x': 0}, 
                size_hint=(None, 1),
                width=self.ui_width
            )
            create_dynamic_rect(self.ui_hp, (1,0,0,1))
            self.ui_layout.add_widget(self.ui_hp)

    def reset_property(self):
        if self.spawner_property:
            self.spawner_property.reset_property()
        self.sp = self.property_data.max_sp
        self.hp = self.property_data.max_hp
        self.mp = self.property_data.max_mp
    
    def has_sp_property(self):
        return 0 <self.property_data.max_sp

    def has_hp_property(self):
        return 0 <self.property_data.max_hp

    def has_mp_property(self):
        return 0 <self.property_data.max_mp

    def has_walk_property(self):
        return 0 <self.property_data.walk_speed
    
    def get_max_sp(self):
        return self.property_data.max_sp
        
    def get_max_hp(self):
        return self.property_data.max_hp

    def get_max_mp(self):
        return self.property_data.max_mp
   
    def get_mp(self):
        return self.mp
    
    def get_sp(self):
        return self.sp

    def get_walk_speed(self):
        return self.property_data.walk_speed * self.move_speed

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
        if self.spawner_property:
            self.spawner_property.update_property(dt)
        if self.has_hp_property():
            self.ui_hp.width = self.ui_width * (self.get_hp() / self.get_max_hp())


