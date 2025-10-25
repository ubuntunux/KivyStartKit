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
        self.dead_characters = []
        self.attack_infos = []
        self.player = None
        self.test = True
             
    def initialize(self, game_controller, level_manager):
        self.game_controller = game_controller
        self.level_manager = level_manager
        Character.set_managers(
            actor_manager=self, 
            level_manager=self.level_manager,
            effect_manager=GameEffectManager.instance()
        )

    def close(self):
        pass
        
    def get_player(self):
        return self.player
        
    def get_actors(self):
        return self.actors
        
    def clear_actors(self):
        for actor in self.actors:
            self.level_manager.pop_actor(actor)
        self.player = None
        self.actors.clear()
        
    def reset_actors(self):
        self.spawn_timer = 0.0
        self.clear_actors()
        self.spawn_player()
        self.test = True 
        
    def spawn_player(self):
        if not self.player:
            pos = self.level_manager.get_random_pos()
            return self.spawn_actor("player", pos)
       
    def remove_actor(self, actor):
        self.level_manager.pop_actor(actor)
        if actor in self.actors:
            self.actors.remove(actor)

    def spawn_actor(self, actor_data_name, pos=None):
        if pos is None:
            pos = self.level_manager.get_random_pos()
        character_data = GameResourceManager.instance().get_character_data(actor_data_name)  
        character = Character(character_data=character_data, pos=pos)
        self.actors.append(character)
        if character.is_player:
            self.player = character
        self.level_manager.add_actor(character)
        return character
        
    def callback_touch(self, inst, touch):
        touch_pos = Vector(touch.pos)
        actor = self.level_manager.get_collide_point(touch_pos)
        if actor is not None:
            self.get_player().trace_actor(actor)
        else:
            self.get_player().move_to(touch_pos)
            
    def callback_move(self, direction):
        self.get_player().set_move_direction(direction)
        
    def callback_attack(self, inst):
        self.get_player().set_attack()   
        
    def regist_attack_info(self, actor, target, damage, force):
        self.attack_infos.append(AttackInfo(actor, target, damage, force))
    
    def update(self, dt):
        effect_manager = GameEffectManager.instance()

        # spawn test
        if self.test:
            data = [
                'patroller',
                'guardian',
                'stalker',
                'invader',
                'guard',
                'carpenter',
                'merchant',
                'miner',
                'farmer',
                'civilian',
                'castle',
                'dungeon'
            ]
            for data_name in data:
                pos = self.level_manager.get_random_pos()
                self.spawn_actor(data_name, pos)
            self.test = False

        # dead
        for actor in self.dead_characters:
            self.remove_actor(actor)
        self.dead_characters = []

        # update
        for actor in self.actors:
            if actor.is_alive():
                actor.update(dt)
            else:
               self.dead_characters.append(actor)
        
        # attack infos
        for attack_info in self.attack_infos:
            if attack_info.target and \
               attack_info.target.is_alive() and \
               attack_info.target.is_player != attack_info.actor.is_player:
                attack_info.target.set_damage(attack_info.damage, attack_info.force)
                effect_manager.create_effect(
                    effect_name="hit",
                    attach_to=attack_info.target
                )
                if not attack_info.target.is_player:
                    self.game_controller.set_target(attack_info.target)
                if not attack_info.target.is_alive():
                    self.dead_characters.append(attack_info.target)
        self.attack_infos = []
        
            
