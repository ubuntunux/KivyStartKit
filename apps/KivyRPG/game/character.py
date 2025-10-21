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
from .character_data import *
from .weapon import Weapon
from .constant import *


class Action:
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


class Character(Scatter):
    actor_manager = None
    level_manager = None
    effect_manager = None
    
    @classmethod
    def set_managers(cls, actor_manager, level_manager, effect_manager):
        cls.actor_manager = actor_manager
        cls.level_manager = level_manager
        cls.effect_manager = effect_manager
    
    def __init__(self, character_data, pos, size, is_player):
        super().__init__(size=size)
        self.action = Action(character_data.action_data)
        self.image = Image(size=size, fit_mode="fill")
        self.image.texture = self.action.get_current_texture()
        self.add_widget(self.image)
        
        self.properties = CharacterProperties(self, character_data.property_data)
        self.behavior = character_data.behavior_class(self)
        self.transform_component = TransformComponent(self, pos, self.properties)
        self.center = self.transform_component.get_pos()
        self.radius = math.sqrt(sum([x*x for x in size])) * 0.5
        self.updated_transform = True
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
        
    # Properties
    def get_properties(self):
        return self.properties

    def is_alive(self):
        return 0 < self.properties.get_hp()
    
    def get_damage(self):
        return self.weapon.get_damage()
    
    def set_damage(self, damage, attack_force=None):
        self.properties.set_damage(damage)
        if attack_force:
            self.transform_component.set_attack_force(attack_force)

    def set_move_speed(self, move_speed):
        self.properties.set_move_speed(move_speed)
        
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
        if not self.action.is_action_state(ActionState.ATTACK):
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
        self.weapon.update_weapon(dt, self.get_front())
        self.updated_transform = self.transform_component.update_transform(dt)
        if self.updated_transform:
            self.center = self.transform_component.get_pos()
            prev_direction_x = self.get_direction_x()
            curr_front_x = sign(self.transform_component.front.x)
            if 0 != curr_front_x and prev_direction_x != curr_front_x:
                self.flip_widget()
        self.properties.update_property(dt) 
