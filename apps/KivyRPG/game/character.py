from kivy.graphics.transformation import Matrix
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.scatter import Scatter
from kivy.uix.widget import Widget
from kivy.vector import Vector
from utility.kivy_helper import *
from .transform_component import TransformComponent
from .character_data import *
from .weapon import Weapon
from .constant import *


class Action():
    def __init__(self, action_data):
        self.action_data = action_data
        self.action_state = ActionState.IDLE
        self.action_time = 0.0
        self.action_time_map = {
            ActionState.IDLE: 0,
            ActionState.ATTACK: 0.1
        }
   
    def is_action_state(self, action_state):
        return self.action_state == action_state
     
    def get_action_state(self):
        return self.action_state
    
    def set_action_state(self, action_state):
        self.action_state = action_state
        self.action_time = self.action_time_map.get(action_state, 1.0)
        
    def get_current_texture(self):
        action_data = self.action_data.get("idle")
        if action_data:
             return action_data.texture
        return None
        
    def update_action(self, dt):
        if ActionState.IDLE != self.action_state:
            if self.action_time < 0:
                self.set_action_state(ActionState.IDLE)
            self.action_time -= dt
        
class CharacterProperties():
    def __init__(self, property_data):
        self.hp = 100.0
        self.mp = 100.0
        self.property_data = property_data
    
    def reset_properties(self):
        self.hp = self.property_data.max_hp
        self.mp = self.property_data.max_mp
    
    def get_hp(self):
        return self.hp
    
    def get_mp(self):
        return self.mp
    
    def get_walk_speed(self):
        return self.property_data.walk_speed
    
    def set_damage(self, damage):
        self.hp -= damage


class Character(Scatter):
    actor_manager = None
    level_manager = None
    effect_manager = None
    
    @classmethod
    def set_managers(cls, actor_manager, level_manager, effect_manager):
        cls.actor_manager = actor_manager
        cls.level_manager = level_manager
        cls.effect_manager = effect_manager
    
    def __init__(self, character_data, tile_pos, size, is_player):
        super().__init__(size=size)
        self.action = Action(character_data.action_data)
        self.image = Image(size=size, fit_mode="fill")
        self.image.texture = self.action.get_current_texture()
        self.add_widget(self.image)
        
        self.properties = CharacterProperties(character_data.property_data)
        self.behavior = character_data.behavior_class(self)
        self.transform_component = TransformComponent(self, tile_pos, self.properties)
        self.center = self.transform_component.get_pos()
        self.updated_pos = True
        self.updated_tile_pos = True
        self.spawn_tile_pos = Vector(tile_pos)
        self.is_player = is_player
        
        self.weapon = Weapon(self, character_data.weapon_data)
        self.add_widget(self.weapon)
    
    def on_touch_down(inst, touch):
        # do nothing
        return False
        
    def flip_widget(self):
        self.apply_transform(
            Matrix().scale(-1.0, 1.0, 1.0),
            post_multiply=True,
            anchor=self.to_local(*self.center)
        )
                 
    def get_spawn_tile_pos(self):
        return self.spawn_tile_pos
    
    def set_spawn_tile_pos(self, spawn_tile_pos):
        self.spawn_tile_pos = Vector(spawn_tile_pos)
        
    def get_front_tile_pos(self):
        return get_next_tile_pos(self.get_tile_pos(), self.get_front())
    
    def get_front(self):
        return self.transform_component.get_front()

    def get_direction_x(self):
        return sign(self.transform[0])
    
    def get_pos(self):
        return self.transform_component.get_pos()
    
    def get_tile_pos(self):
        return self.transform_component.get_tile_pos()
    
    def get_prev_pos(self):
        return self.transform_component.get_prev_pos()
    
    def get_prev_tile_pos(self):
        return self.transform_component.get_prev_tile_pos()
    
    def get_coverage_tile_pos(self):
        return self.transform_component.get_coverage_tile_pos()
             
    def get_updated_pos(self):
        return self.updated_pos
        
    def get_updated_tile_pos(self):
        return self.updated_tile_pos
    
    # Properties
    def is_alive(self):
        return 0 < self.properties.get_hp()
    
    def get_damage(self):
        return self.weapon.get_damage()
    
    def set_damage(self, damage):
        self.properties.set_damage(damage)
        
    # Transform
    def move_to(self, tile_pos):
        if self.level_manager.is_in_level(tile_pos):
            self.transform_component.trace_actor(self.level_manager, None)
            self.transform_component.move_to(self.level_manager, tile_pos)
    
    def trace_actor(self, actor):
        self.transform_component.trace_actor(self.level_manager, actor)

    # Actions    
    def set_attack(self):
        if not self.action.is_action_state(ActionState.ATTACK):
            self.action.set_action_state(ActionState.ATTACK)
            self.weapon.set_attack(self.get_front())
            target = self.level_manager.get_actor(self.get_front_tile_pos())
            if target and target is not self:
                damage = self.get_damage()
                self.actor_manager.regist_attack_info(self, target, damage)
    
    def update(self, dt):
        self.behavior.update_behavior(self.actor_manager, self.level_manager, dt)
        self.action.update_action(dt)
        self.weapon.update_weapon(dt, self.get_front())
        self.updated_pos = self.transform_component.update_transform(self.level_manager, dt)
        self.updated_tile_pos = self.get_prev_tile_pos() != self.get_tile_pos()
        if self.updated_pos:
            self.center = self.transform_component.get_pos()
            prev_direction_x = self.get_direction_x()
            curr_front_x = sign(self.transform_component.front.x)
            if 0 != curr_front_x and prev_direction_x != curr_front_x:
                self.flip_widget()
            