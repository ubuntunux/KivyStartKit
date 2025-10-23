from kivy.graphics.transformation import Matrix
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.scatter import Scatter
from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivy.metrics import dp
from utility.kivy_helper import *
from .transform_component import TransformComponent
from .action import *
from .behavior import *
from .character_data import *
from .character_property import *
from .weapon import *
from .constant import *


class Character(Scatter):
    actor_manager = None
    level_manager = None
    effect_manager = None
    
    @classmethod
    def set_managers(cls, actor_manager, level_manager, effect_manager):
        cls.actor_manager = actor_manager
        cls.level_manager = level_manager
        cls.effect_manager = effect_manager
    
    def __init__(self, character_data, pos, size):
        super().__init__(size=size)
        actor_type = character_data.actor_type
        action = Action(character_data.action_data)
        character_property = CharacterProperty(self, character_data.property_data)
        behavior = Behavior.create_behavior(self, actor_type) 
       
        self.action = action
        self.image = Image(size=size, fit_mode="fill")
        self.image.texture = action.get_current_texture()
        self.add_widget(self.image)
        
        self.property = character_property
        self.behavior = behavior
        self.transform_component = TransformComponent(self, pos, self.property)
        self.center = Vector(pos)
        self.radius = math.sqrt(sum([x*x for x in size])) * 0.5
        self.updated_transform = True
        self.is_player = actor_type is ActorType.PLAYER
        
        self.weapon = None
        if character_data.weapon_data:
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
    
    def get_attack_pos(self):
        attack_dist = 100.0
        return Vector(self.get_pos() + self.get_front() * attack_dist)
    
    def get_front(self):
        return self.transform_component.get_front()

    def get_direction_x(self):
        return sign(self.transform[0])
    
    def get_radius(self):
        return self.radius
    
    def get_pos(self):
        return self.transform_component.get_pos()
    
    def get_prev_pos(self):
        return self.transform_component.get_prev_pos()
    
    def get_updated_transform(self):
        return self.updated_transform
        
    # Property
    def get_property(self):
        return self.property

    def is_alive(self):
        return 0 < self.property.get_hp()
    
    def get_damage(self):
        return self.weapon.get_damage()
    
    def set_damage(self, damage, attack_force=None):
        self.property.set_damage(damage)
        if attack_force:
            self.transform_component.set_attack_force(attack_force)

    def set_move_speed(self, move_speed):
        self.property.set_move_speed(move_speed)
        
    # Transform
    def move_to(self, pos):
        if self.level_manager.is_in_level(self):
            self.transform_component.move_to(pos)
    
    def set_move_direction(self, direction):
        self.transform_component.set_move_direction(direction)
    
    def trace_actor(self, actor):
        self.transform_component.trace_actor(self.level_manager, actor)

    # Actions    
    def set_attack(self):
        if self.weapon and not self.action.is_action_state(ActionState.ATTACK):
            self.action.set_action_state(ActionState.ATTACK)
            self.weapon.set_attack(self.get_front())
            target = self.level_manager.get_collide_point(self.get_attack_pos(), 100.0, [self])
            if target and target is not self:
                damage = self.get_damage()
                force = (target.get_pos() - self.get_pos()).normalize() * 1000.0
                self.actor_manager.regist_attack_info(self, target, damage, force)
    
    def update(self, dt):
        self.behavior.update_behavior(dt)
        self.action.update_action(dt)
        
        if self.weapon:
            self.weapon.update_weapon(dt, self.get_front())

        if self.property.has_walk_property():
            self.updated_transform = self.transform_component.update_transform(dt)
            if self.updated_transform:
                self.center = self.transform_component.get_pos()
                prev_direction_x = self.get_direction_x()
                curr_front_x = sign(self.transform_component.front.x)
                if 0 != curr_front_x and prev_direction_x != curr_front_x:
                    self.flip_widget()
        self.property.update_property(dt) 
