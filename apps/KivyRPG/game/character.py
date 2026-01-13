import math
from kivy.graphics.transformation import Matrix
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
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
    game_controller = None
    game_manager = None

    @classmethod
    def set_managers(cls, actor_manager, level_manager, effect_manager, game_controller, game_manager):
        cls.actor_manager = actor_manager
        cls.level_manager = level_manager
        cls.effect_manager = effect_manager
        cls.game_controller = game_controller
        cls.game_manager = game_manager

    def __init__(self, name, character_data, pos):
        super().__init__(size=character_data.size)
        actor_type = character_data.actor_type       
        self.name = name
        self.action = None
        self.actor_type = actor_type       
        self.actor_id = character_data.actor_id
        self.actor_key = character_data.actor_key
        self.actor_category = get_actor_category(actor_type)
        self.blockable = get_is_blockable_actor_category(self.actor_category) 
        self.data = character_data
        self.property = None
        self.behavior = None
        self.center = Vector(pos)
        self.radius = math.sqrt(sum([x*x for x in self.size])) * 0.5
        self.updated_transform = True
        self.is_player = actor_type is ActorType.PLAYER
        self.update_term = 1.0 / 60.0        
        self.update_time = 0.0
        self.action = Action(character_data.action_data)
        self.property = CharacterProperty(self, character_data.property_data)
        self.behavior = create_behavior(self, actor_type) 
        self.image = Image(size=character_data.size, fit_mode="fill")
        self.image.texture = self.action.get_current_texture()
        self.add_widget(self.image)
        self.transform_component = TransformComponent(self, pos, self.property)
        self.weapon = None
        self.set_weapon(character_data.weapon_data)
 
    def get_is_player(self):
        return self.is_player

    def get_actor_type(self):
        return self.actor_type

    def get_actor_id(self):
        return self.actor_id

    def get_actor_key(self):
        return self.actor_key

    def get_actor_category(self):
        return self.actor_category

    def is_blockable(self):
        return self.blockable

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

    def get_size(self):
        return self.transform_component.get_size()
    
    def get_pos(self):
        return self.transform_component.get_pos()
    
    def set_pos(self, pos):
        if pos != self.get_pos():
            self.updated_transform = True 
            self.transform_component.set_pos(pos)
            self.level_manager.update_actor_on_tile(self)

    def get_prev_pos(self):
        return self.transform_component.get_prev_pos()
    
    def get_bound_min(self):
        return self.transform_component.bound_min 

    def get_bound_max(self):
        return self.transform_component.bound_max

    def get_updated_transform(self):
        return self.updated_transform
        
    def set_weapon(self, weapon_data):
        self.remove_weapon()
        if weapon_data:
            self.weapon = Weapon(self, weapon_data)
            self.add_widget(self.weapon)

    def remove_weapon(self):
        if self.weapon:
            self.remove_widget(self.weapon)
            self.weapon = None

    # Property
    def get_property(self):
        return self.property

    def get_property_data(self):
        return self.property_data

    def get_extra_property(self):
        return self.property.extra_property

    def get_extra_property_data(self):
        return self.property.extra_property.property_data

    def is_criminal(self):
        return self.property.is_criminal()

    def get_criminal(self):
        return self.property.get_criminal()

    def add_criminal(self, criminal):
        self.property.add_criminal(criminal)

    def is_attackable(self):
        return self.property.has_hp_property()

    def is_attackable_target(self, target):
        if not target.is_attackable():
            return False
        elif self.is_player or target.is_criminal():
            return True
        elif self.actor_category is ActorCategory.CHARACTER:
            return target.actor_category is ActorCategory.MONSTER
        elif self.actor_category is ActorCategory.MONSTER:
            return target.actor_category is ActorCategory.CHARACTER or target.actor_category == ActorCategory.BUILDING
        return False

    def is_criminal_target(self, target):
        return target.actor_category is ActorCategory.CHARACTER or target.actor_category is ActorCategory.BUILDING

    def is_alive(self):
        return self.property.is_alive()
    
    def set_dead(self):
        self.property.set_dead()

    def get_damage(self):
        return self.weapon.get_damage()
    
    def set_damage(self, damage, attack_force=None):
        self.property.set_damage(damage)
        if attack_force:
            self.transform_component.set_attack_force(attack_force)

    def add_hp(self, hp):
        self.property.add_hp(hp)

    def set_move_speed(self, move_speed):
        self.property.set_move_speed(move_speed)
        
    def add_item(self, item_data):
        item_actor = self.property.add_item(item_data)
        if self.is_player:
            if True or item_actor.get_actor_type() == ActorType.HP:
                self.game_controller.add_item_to_quick_slot(item_actor)
            self.game_controller.update_inventory_menu()

    def get_item(self, actor_key):
        return self.property.get_item(actor_key)

    def get_items(self):
        return self.property.get_items()

    def get_item_count(self, actor_key):
        return self.property.get_item_count(actor_key)

    def use_item(self, actor_key, count=1, interaction=True):
        used_item = self.property.use_item(actor_key, count, interaction)
        if self.is_player:
            self.game_controller.update_inventory_menu()
        return used_item

    # Transform
    def move_to(self, pos):
        if self.level_manager.is_in_level(self):
            self.transform_component.move_to(pos)
    
    def set_move_direction(self, direction):
        self.transform_component.set_move_direction(direction)
    
    def trace_actor(self, actor):
        self.transform_component.trace_actor(self.level_manager, actor)

    def collide_actor(self, bound_min, bound_max):
        return self.transform_component.collide_actor(bound_min, bound_max)

    # Actions    
    def set_attack(self):
        if self.weapon and not self.action.is_action_state(ActionState.ATTACK):
            self.action.set_action_state(ActionState.ATTACK)
            front = self.get_front()
            attack_bound = self.get_size() * front
            attack_bound_min = self.get_bound_min() + attack_bound
            attack_bound_max = self.get_bound_max() + attack_bound
            targets = self.level_manager.get_collide_actor(attack_bound_min, attack_bound_max, filter=self)
            for target in targets:
                actor_type = target.get_actor_type()
                if self.is_attackable_target(target):
                    damage = self.get_damage()
                    force = (target.get_pos() - self.get_pos()).normalize() * ATTACK_FORCE
                    self.actor_manager.regist_attack_info(self, target, damage, force)
            self.weapon.set_attack(front)

    def update(self, player_pos, dt):
        if not self.is_player:
            self.update_time += dt
            if self.update_time < self.update_term:
                return
            else:
                dt = self.update_time
                self.update_time = 0.0
            distance = player_pos.distance(self.get_pos())
            self.update_term = 1.0 - math.exp((distance - 1000.0) * -0.001) 

        self.behavior.update_behavior(dt)
        self.action.update_action(dt)
        
        if self.weapon:
            self.weapon.update_weapon(dt, self.get_front())

        if self.updated_transform or self.property.has_walk_property():
            self.updated_transform = self.transform_component.update_transform(dt) or self.updated_transform
            if self.updated_transform:
                self.center = self.transform_component.get_pos()
                prev_direction_x = self.get_direction_x()
                curr_front_x = sign(self.transform_component.front.x)
                if 0 != curr_front_x and prev_direction_x != curr_front_x:
                    self.flip_widget()
                self.level_manager.update_actor_on_tile(self)
            self.updated_transform = False

        # get item or building
        if self.is_player:
            collide_actors = self.transform_component.collide_actors
            interaction_target = None 
            for actor in collide_actors:
                self.game_controller.set_target(actor)
                actor.behavior.on_collide_actor(self)
                if actor.get_actor_category() is ActorCategory.BUILDING:
                    interaction_target = actor
            self.game_controller.set_interaction_target(interaction_target)
        self.property.update_property(dt) 

