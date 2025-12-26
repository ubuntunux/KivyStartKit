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
from .inn_property import *
from .item_property import *

class CharacterProperty(BaseProperty):
    extra_property_map = {
        DungeonPropertyData: DungeonProperty,
        InnPropertyData: InnProperty,
        ItemPropertyData: ItemProperty,
    }

    def __init__(self, actor, property_data):
        super().__init__(actor, property_data)
        self.hp = 0.0
        self.mp = 0.0
        self.sp = 0.0
        self.move_speed = 1.0
        self.extra_property = None
        self.property_data = property_data
        self.ui_width = dp(48)
        self.ui_layout = None
        self.ui_hp = None
        self.alive = True 
        self.criminal = 0 
        self.criminal_time = 0.0
        self.items = {}

        extra_property_data = property_data.extra_property_data
        extra_propert_class = self.extra_property_map.get(type(extra_property_data))
        if extra_propert_class:
            self.extra_property = extra_propert_class(actor, extra_property_data)

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
        self.criminal = 0
        self.criminal_time = 0.0

    def is_alive(self):
        return self.alive

    def is_criminal(self):
        return 0 < self.criminal

    def get_criminal(self):
        return self.criminal

    def add_criminal(self, criminal):
        self.criminal = min(MAX_CRIMINAL, self.criminal + criminal)
        self.criminal_time += self.criminal * CRIMINAL_TIME_RATIO 

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
    
    def add_item(self, item_data):
        item_actor = self.items.get(item_data.actor_key)
        if item_actor:
            count = item_data.get_extra_property_data().get_item_count()
            item_actor.get_extra_property().add_item_count(count)
        else:
            item_actor = self.actor.actor_manager.create_item(item_data) 
            self.items[item_data.actor_key] = item_actor 
        return item_actor

    def get_item(self, actor_key):
        return self.items.get(actor_key)

    def get_item_count(self, actor_key):
        item_actor = self.items.get(actor_key)
        if item_actor:
            return item_actor.get_extra_property().get_item_count()
        return 0

    def use_item(self, actor_key, count=1, interaction=True):
        item_actor = self.get_item(actor_key)
        item_count = item_actor.get_extra_property().get_item_count() if item_actor else 0
        if count <= item_count:
            item_actor.get_extra_property().add_item_count(-count)
            if interaction:
                item_actor.behavior.on_interaction(self.actor)
            if 0 == item_actor.get_extra_property().get_item_count():
                self.items.pop(actor_key)
            return True
        return False

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
        if 0 < self.criminal_time and 0 < self.criminal and self.criminal < MAX_CRIMINAL:
            self.criminal_time -= dt
            if self.criminal_time < CRIMINAL_TIMES[self.criminal - 1]:
                self.criminal -= 1
                if self.criminal <= 0:
                    self.criminal = 0
                    self.criminal_time = 0.0
        if self.extra_property:
            self.extra_property.update_property(dt)
        if self.actor.get_is_player() and self.has_hp_property():
            self.ui_hp.width = self.ui_width * (self.get_hp() / self.get_max_hp())


