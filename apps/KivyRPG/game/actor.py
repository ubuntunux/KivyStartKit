from kivy.logger import Logger
from kivy.vector import Vector
from utility.singleton import SingletonInstance
from utility.kivy_helper import *
from .effect import GameEffectManager
from .game_resource import GameResourceManager
from .behavior import Monster
from .character import Character
from .constant import *


class AttackInfo():
    def __init__(self, actor, target, damage):
        self.actor = actor
        self.target = target
        self.damage = damage
        
    
class ActorManager(SingletonInstance):
    def __init__(self, app):
        self.app = app
        self.level_manager = None
        self.actors = []
        self.dead_characters = []
        self.attack_infos = []
        self.player = None
        self.spawn_term = 3.0
             
    def initialize(self, level_manager):
        self.level_manager = level_manager
        Character.set_managers(
            actor_manager=self, 
            level_manager=self.level_manager,
            effect_manager=GameEffectManager.instance()
        )
        
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
        self.clear_actors()
        self.spawn_player()
        self.spawn_monster()
        self.spawn_monster()
    
    def spawn_player(self):
        if not self.player:
            character_data = GameResourceManager.instance().get_character_data("player")  
            tile_pos = self.level_manager.get_random_tile_pos()
            return self.create_actor(character_data, tile_pos, is_player=True)
        
    def spawn_monster(self):
        character_data = GameResourceManager.instance().get_character_data("monster")  
        tile_pos = self.level_manager.get_random_tile_pos()
        return self.create_actor(character_data, tile_pos, is_player=False)   
        
    def remove_actor(self, actor):
        self.level_manager.pop_actor(actor)
        if actor in self.actors:
            self.actors.remove(actor)
        
    def create_actor(self, character_data, tile_pos, is_player):
        character = Character(
            character_data=character_data,
            tile_pos=tile_pos,
            pos=self.level_manager.tile_to_pos(tile_pos),
            size=TILE_SIZE,
            is_player=is_player
        )
        self.actors.append(character)
        if is_player:
            self.player = character
        self.level_manager.add_actor(character)
        return character
        
    def callback_touch(self, inst, touch):
        actor = self.level_manager.get_collide_point(Vector(touch.pos))
        if actor is not None:
            self.get_player().trace_actor(actor)
        else:
            self.get_player().move_to(touch.pos)
            
    def callback_move(self, direction):
        self.get_player().set_move_direction(direction)
        
    def callback_attack(self, inst):
        self.get_player().set_attack()   
        
    def regist_attack_info(self, actor, target, damage):
        self.attack_infos.append(AttackInfo(actor, target, damage))
    
    def update(self, dt):
        effect_manager = GameEffectManager.instance()
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
            if attack_info.target and attack_info.target.is_alive():
                attack_info.target.set_damage(attack_info.damage)
                effect_manager.create_effect(
                    effect_name="hit",
                    attach_to=attack_info.target
                )
                if not attack_info.target.is_alive():
                    self.dead_characters.append(attack_info.target)
        self.attack_infos = []
        
            