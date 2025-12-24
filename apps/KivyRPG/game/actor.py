import copy
from enum import Enum
from kivy.logger import Logger
from kivy.vector import Vector
from utility.singleton import SingletonInstance
from utility.kivy_helper import *
from .effect import GameEffectManager
from .game_resource import GameResourceManager
from .behavior import *
from .character import *
from .action import *
from .character_data import *
from .character_property import *
from .weapon import *
from .reward import get_rewards
from .constant import *


class AttackInfo():
    def __init__(self, actor, target, damage, force):
        self.actor = actor
        self.target = target
        self.damage = damage
        self.force = force
    
class ActorManager(SingletonInstance):
    def __init__(self, app):
        self.app = app
        self.level_manager = None
        self.actors = []
        self.actor_type_map = {}
        self.dead_characters = []
        self.attack_infos = []
        self.player = None
             
    def initialize(self, game_controller, level_manager):
        self.game_controller = game_controller
        self.level_manager = level_manager

    def close(self):
        pass
        
    def get_player(self):
        return self.player
        
    def get_actors(self):
        return self.actors

    def get_actors_by_type(self, actor_type):
        return self.actor_type_map.get(actor_type, [])
        
    def clear_actors(self):
        for actor in self.actors:
            self.level_manager.pop_actor(actor)
        self.player = None
        self.actors.clear()
        self.actor_type_map.clear()

    def remove_actors_by_type(self, actor_type):
        actors = copy.copy(self.get_actors_by_type(actor_type))
        for actor in actors:
            self.remove_actor(actor)

    def remove_actor(self, actor):
        self.level_manager.pop_actor(actor)
        if actor in self.actors:
            self.actors.remove(actor)
        actors_by_type = self.get_actors_by_type(actor.actor_type)
        if actor in actors_by_type:
            actors_by_type.remove(actor)

    def create_item(self, item_data):
        return Character(character_data=item_data, pos=Vector(0,0), name=item_data.name)

    def spawn_actor(self, actor_data_name, pos=None, name=''):
        if pos is None:
            pos = self.level_manager.get_random_pos()
        if not name:
            name = actor_data_name
        character_data = GameResourceManager.instance().get_character_data(actor_data_name)  
        character = Character(character_data=character_data, pos=pos, name=name)
        self.actors.append(character)
        if character.actor_type not in self.actor_type_map:
            self.actor_type_map[character.actor_type] = []
        self.actor_type_map[character.actor_type].append(character)

        layer_index = 1 if character.property.has_walk_property() else 2
        if character.is_player:
            self.player = character
            layer_index = 0
        self.level_manager.add_actor(character, layer_index)
        return character

    def spawn_around_actor_type(self, actor_data_name, target_actor_type, radius_min, radius_max):
        target_actors = self.get_actors_by_type(target_actor_type)
        if target_actors:
            return self.spawn_around_actor(target_actors[0])
        return None

    def spawn_around_actor(self, actor_data_name, target_actor, radius_min, radius_max, check_collide=True):
        actor = self.spawn_actor(actor_data_name)
        self.placement_around_actor(actor, target_actor, radius_min, radius_max, check_collide=True)
        return actor

    def placement_around_actor(self, actor, target_actor, radius_min, radius_max, check_collide=True):
        NUM_TRY = 10
        for i in range(NUM_TRY):
            x = random.random() * 2.0 - 1.0
            y = random.random() * 2.0 - 1.0
            t = random.random()
            offset = radius_min * (1.0 - t) + radius_max * t

            if check_collide:
                size = (target_actor.get_size() + actor.get_size()) * 0.5 + Vector(offset, offset) 
            else:
                size = Vector(offset, offset)  

            if abs(x) < abs(y):
                x = target_actor.center[0] + size[0] * x
                y = target_actor.center[1] + size[1] * (1 if 0 < y else -1)  
            else:
                x = target_actor.center[0] + size[0] * (1 if 0 < x else -1)
                y = target_actor.center[1] + size[1] * y  
            pos = Vector(x,y)
            actor.set_pos(pos) 
            if not check_collide or not self.level_manager.get_actors_on_tiles_with_actor(actor):
                break

    def callback_touch(self, inst, touch):
        touch_pos = Vector(touch.pos)
        actors = self.level_manager.get_collide_point(touch_pos)
        if self.player and self.player.is_alive():
            if actors:
                self.get_player().trace_actor(actors[0])
            else:
                self.get_player().move_to(touch_pos)
                
    def callback_move(self, direction):
        if self.player:
            self.player.set_move_direction(direction)
        
    def callback_attack(self, inst):
        if self.player:
            self.player.set_attack()   
        
    def regist_attack_info(self, actor, target, damage, force):
        self.attack_infos.append(AttackInfo(actor, target, damage, force))
    
    def update(self, dt):
        effect_manager = GameEffectManager.instance()

        # dead
        for actor in self.dead_characters:
            self.remove_actor(actor)
        self.dead_characters = []

        # update
        player_pos = self.player.get_pos() if self.player else Vector(0.0, 0.0)
        for actor in self.actors:
            if actor.is_alive():
                actor.update(player_pos, dt)
            else:
               self.dead_characters.append(actor)
        
        # attack infos
        for attack_info in self.attack_infos:
            if attack_info.target and \
               attack_info.target.is_alive():
                if attack_info.actor.is_player:
                    if not get_is_enemy_actor_category(attack_info.target.get_actor_category(), attack_info.actor.get_actor_category()):
                        attack_info.actor.set_criminal(True)
                attack_info.target.set_damage(attack_info.damage, attack_info.force)
                effect_manager.create_effect(
                    effect_name=FX_HIT,
                    attach_to=attack_info.target
                )
                if not attack_info.target.is_player:
                    self.game_controller.set_target(attack_info.target)
                # spawn reward
                if not attack_info.target.is_alive():
                    if attack_info.actor.is_player:
                        for (reward_index, item_actor) in enumerate(get_rewards(self, self.player, attack_info.target)):
                            radius_min = 0
                            radius_max = 0
                            collide_check = False
                            if reward_index != 0:
                                radius_min = 50
                                radius_max = 100
                                collide_check = True
                            self.placement_around_actor(item_actor, attack_info.target, radius_min, radius_max, collide_check) 
                    self.dead_characters.append(attack_info.target)
        self.attack_infos = []
        
            
