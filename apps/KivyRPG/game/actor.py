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
        self.character_layout = None
        self.actors = []
        self.dead_characters = []
        self.attack_infos = []
        self.player = None
             
    def initialize(self, level_manager, character_layout):
        self.level_manager = level_manager
        self.character_layout = character_layout
        Character.set_managers(
            actor_manager=self, 
            level_manager=self.level_manager,
            effect_manager=GameEffectManager.instance()
        )
        
    def get_player(self):
        return self.player
        
    def clear_actors(self):
        for actor in self.actors:
            actor.parent.remove_widget(actor)
        self.actors.clear()
        
    def create_actors(self):
        is_player = True
        tile_pos = (10, 10)
        character_data = GameResourceManager.instance().get_character_data("player")  
        self.create_actor(character_data, tile_pos, is_player)
        
        is_player = False
        monster_positions = [(5, 5), (8, 8)]
        character_data = GameResourceManager.instance().get_character_data("monster")  
        for tile_pos in monster_positions:
            self.create_actor(character_data, Vector(tile_pos), is_player)   
        
    def remove_actor(self, actor):
        if actor is not None:
            actor.parent.remove_widget(actor)
            self.actors.remove(actor)
            self.level_manager.pop_actor(actor)
    
    def create_actor(self, character_data, tile_pos, is_player):
        character = Character(
            character_data=character_data,
            tile_pos=tile_pos,
            pos=self.level_manager.tile_to_pos(tile_pos),
            size=TILE_SIZE,
            is_player=is_player
        )
        self.character_layout.add_widget(character)
        self.level_manager.set_actor(character)
        if is_player:
            self.player = character
        self.actors.append(character)
        
    def callback_touch(self, inst, touch):
        tile_pos = self.level_manager.pos_to_tile(touch.pos)
        actor = self.level_manager.get_actor(tile_pos)
        if actor is not None:
            self.get_player().trace_actor(actor)
        else:
            self.get_player().move_to(tile_pos)
            
    def callback_move(self, direction):
        tile_pos = self.get_player().get_tile_pos()
        if "left" == direction:
            tile_pos = tile_pos + Vector(-1, 0)
        elif "right" == direction:
            tile_pos = tile_pos + Vector(1, 0)
        elif "up" == direction:
            tile_pos = tile_pos + Vector(0, 1)
        elif "down" == direction:
            tile_pos = tile_pos + Vector(0, -1)
        self.get_player().move_to(tile_pos)
        
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
        
            