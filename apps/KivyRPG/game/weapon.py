import copy
from kivy.graphics.transformation import Matrix
from kivy.uix.image import Image
from kivy.uix.scatter import Scatter
from kivy.vector import Vector
from utility.kivy_helper import *
from .effect import GameEffectManager


class Weapon(Scatter):
    def __init__(self, actor, weapon_data):
        super().__init__(pos=weapon_data.pos, size=weapon_data.size)
        self.weapon_data = weapon_data
        self.image = Image(size=weapon_data.size, fit_mode="fill")
        self.image.texture = weapon_data.texture
        self.add_widget(self.image)
        
        self.origin = Vector(self.pos)
        self.attack_anim_time = 0.0
        self.attack_dir = Vector(0,0)
        self.actor = actor
    
    def on_touch_down(inst, touch):
        # do nothing
        return False
        
    def get_damage(self):
        return self.weapon_data.damage
    
    def set_attack_dir(self, attack_dir, force_update=False):
        if not force_update and attack_dir[0] == self.attack_dir[0] and attack_dir[1] == self.attack_dir[1]:
            return
        self.attack_dir = Vector(attack_dir)
        self.update_weapon_transform(attack_dir)
    
    def is_attacking(self):
        return 0 < self.attack_anim_time
    
    def set_attack(self, attack_dir):
        self.attack_anim_time = 0.1
        self.set_attack_dir(attack_dir, force_update=True)
        self.create_attack_effect(attack_dir)
        
    def create_attack_effect(self, attack_dir):
        if self.weapon_data.attack_effect:
            pos = Vector(self.center)
            rotation=self.rotation
            size=(100, 100)
            is_actor_flip_x = self.actor.get_direction_x() < 0
            is_dir_vertical = abs(attack_dir.x) < abs(attack_dir.y)
            offset = 50.0
            
            # adjust offset
            if is_dir_vertical:
                pos.y = pos.y - offset * sign(attack_dir.y)    
            else:
                pos.x -= offset
             
             # adjust flip   
            if is_actor_flip_x:
                pos.x = -pos.x
                if is_dir_vertical:
                    rotation += 180
                 
            GameEffectManager.instance().create_effect(
                self.weapon_data.attack_effect,
                center=pos,
                size=size,
                rotation=rotation,
                flip_x=is_actor_flip_x,
                attach_to=self
            )
            
    def update_weapon_transform(self, attack_dir): 
        offset = 50.0 if self.is_attacking() else 0
        if abs(attack_dir.x) < abs(attack_dir.y):
            sign_y = sign(attack_dir.y)
            offset_x = 0 
            if sign_y < 0:
                offset_x = self.origin.x * 0.5
            self.pos = Vector(self.origin.y + offset_x, (self.origin.x + offset) * sign_y)
            self.rotation = 90 * sign_y
        else:
            self.pos = Vector(self.origin.x + offset, self.origin.y)
            self.rotation = 0
        
    def update_weapon(self, dt, player_front):
        self.set_attack_dir(player_front)
        
        if 0 < self.attack_anim_time:
            self.attack_anim_time -= dt
            if self.attack_anim_time <= 0:
                self.set_attack_dir(self.attack_dir, force_update=True)
            
   