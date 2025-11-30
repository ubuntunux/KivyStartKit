from kivy.graphics.transformation import Matrix
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.scatter import Scatter
from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivy.metrics import dp
from utility.kivy_helper import *
from ..character_data import *
from ..constant import *
from .base_property import BaseProperty
from .dungeon_property import *
from .gold_property import *
from .inn_property import *
from .hp_property import *

class CharacterProperty(BaseProperty):
    extra_property_map = {
        DungeonPropertyData: DungeonProperty,
        GoldPropertyData: GoldProperty,
        HpPropertyData: HpProperty,
    }

    def __init__(self, actor, property_data):
        super().__init__(actor, property_data)
        self.hp = 0.0
        self.mp = 0.0
        self.sp = 0.0
        self.gold = 0
        self.move_speed = 1.0
        self.extra_property = None
        self.property_data = property_data
        self.ui_width = dp(48)
        self.ui_layout = None
        self.ui_hp = None
        self.alive = True 
        self.items = {}

        extra_property_data = property_data.extra_property_data
        extra_prropert_class = self.extra_property_map.get(type(extra_property_data))
        if extra_prropert_class:
            self.extra_property = extra_prropert_class(actor, extra_property_data)

        self.reset_property()
        if actor.get_is_player():
            self.build_ui()

    def build_ui(self):
        if not self.has_sp_property() and not self.has_hp_property() and not self.has_mp_property():
            return

        self.ui_layout = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            size=(self.ui_width + dp(2), dp(6)),
            padding=dp(1)
        )
        create_dynamic_rect(self.ui_layout, (0,0,0,1))
        self.actor.add_widget(self.ui_layout)

        if self.has_hp_property():
            self.ui_hp = Widget(
                pos_hint={'x': 0}, 
                size_hint=(None, 1),
                width=self.ui_width
            )
            create_dynamic_rect(self.ui_hp, (1,0,0,1))
            self.ui_layout.add_widget(self.ui_hp)

    def reset_property(self):
        if self.extra_property:
            self.extra_property.reset_property()
        self.sp = self.property_data.max_sp
        self.hp = self.property_data.max_hp
        self.mp = self.property_data.max_mp
        self.alive = True 
    
    def is_alive(self):
        return self.alive

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
    
    def get_gold(self):
        return self.gold

    def add_gold(self, gold):
        self.gold = max(0, self.gold + gold)
        return self.gold

    def add_item(self, item_actor):
        item = self.items.get(item_actor.data)
        if item:
            count = item.get_instance_count()
            item.set_instance_count(count + 1)
        else:
            self.items[item_actor.data] = item_actor 
            item = item_actor
        return item

    def get_item(self, item_data):
        return self.items.get(item_data)

    def use_item(self, item_data):
        item = self.items.get(item_data)
        item_count = item.get_instance_count() if item else 0
        if 0 < item_count:
            if 1 == item_count:
                self.items.pop(item_data)
            else:
                self.items[item_data].set_instance_count(item_count - 1)

    def add_hp(self, hp):
        if self.is_alive() and self.has_hp_property():
            self.hp = min(self.get_max_hp(), self.hp + hp)

    def set_damage(self, damage):
        if self.is_alive() and self.has_hp_property():
            self.hp -= damage
            if self.hp <= 0:
                self.set_dead()

    def set_dead(self):
        self.alive = False

    def set_move_speed(self, move_speed):
        self.move_speed = move_speed

    def update_property(self, dt):
        if self.extra_property:
            self.extra_property.update_property(dt)
        if self.actor.get_is_player() and self.has_hp_property():
            self.ui_hp.width = self.ui_width * (self.get_hp() / self.get_max_hp())


