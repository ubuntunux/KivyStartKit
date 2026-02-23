from enum import Enum
import random
from kivy.logger import Logger
from kivy.vector import Vector
from utility.singleton import SingletonInstance
from utility.kivy_helper import *
from .effect import GameEffectManager
from .game_resource import GameResourceManager
from .actor import ActorManager
from .behavior import Behavior
from .character import Character
from .level import LevelManager
from .game_controller import GameController
from .character_data import *
from .constant import *
   
class GameScenario:
    NONE = 'NONE'
    INTRO = 'INTRO'

class GameManager(SingletonInstance):
    def __init__(self, app):
        self.app = app
        self.effect_manager = None
        self.actor_manager = None
        self.level_manager = None 
        self.game_controller = None 
        self.scenarios = []
        self.stalker_spawn_term = 0.0
        self.tod = 0.0
        self.trade_actor = None
        self.castle_actor = None

    def initialize(self):
        self.effect_manager = GameEffectManager.instance()
        self.actor_manager = ActorManager.instance()
        self.level_manager = LevelManager.instance()
        self.game_controller = GameController.instance()
        
        Behavior.set_managers(
            self.actor_manager, 
            self.level_manager, 
            self.effect_manager, 
            self.game_controller,
            self
        )
        Character.set_managers(
            self.actor_manager, 
            self.level_manager, 
            self.effect_manager, 
            self.game_controller,
            self
        )

    def close(self):
        pass

    def game_start(self):
        self.new_game()

    def new_game(self):
        self.level_manager.new_level("default")
        self.reset_actors()

    def load_game(self):
        level_data = self.level_manager.load_level("default")
        self.spawn_actors(level_data)

    def save_game(self):
        level_data = self.level_manager.save_level()
        GameResourceManager.instance().save_level_data(
            level_data.get('level_name'),
            level_data
        ) 

    def spawn_castle(self):
        self.castle_actor = self.actor_manager.spawn_actor('castle', self.level_manager.get_level_center())
        return self.castle_actor

    def spawn_player(self):
        player = self.actor_manager.spawn_actor('player', self.castle_actor.get_pos() + Vector(0, -self.castle_actor.size[1]))
        self.game_controller.update_quick_slot()
        return player
       
    def spawn_actors(self, level_data):
        self.actor_manager.clear_actors()

        for actor_info in level_data.actors:
            self.actor_manager.spawn_actor(
                actor_info.get('actor_data_name'),
                Vector(actor_info.get('actor_pos')),
                actor_info.get('actor_name'),
            )
            
            if actor_info.get('is_player'):
                self.game_controller.update_quick_slot()

    def reset_actors(self):
        self.actor_manager.clear_actors()

        castle_radius_inner = dp(50)
        castle_radius_outter = dp(150)
        dungeon_radius_inner = dp(400)
        dungeon_radius_outter = dp(1000)

        castle = self.spawn_castle()

        self.actor_manager.spawn_around_actor('inn', castle, castle_radius_inner, castle_radius_outter)
        self.actor_manager.spawn_actor('guard', self.castle_actor.get_pos() + Vector(-self.castle_actor.size[0] * 0.5, -self.castle_actor.size[1]))
        self.actor_manager.spawn_actor('guard', self.castle_actor.get_pos() + Vector(self.castle_actor.size[0] * 0.5, -self.castle_actor.size[1]))

        self.spawn_player()

        data = [
            'forest',
            'farm',
            'mine',
        ] * 10
        for data_name in data:
            self.actor_manager.spawn_around_actor(data_name, castle, dungeon_radius_inner, dungeon_radius_outter)

        data = [
            'dungeon',
        ] * 10
        for data_name in data:
            self.actor_manager.spawn_around_actor(data_name, castle, dungeon_radius_inner, dungeon_radius_outter)

    def update_managers(self, dt):
        self.game_controller.update(dt)
        self.effect_manager.update(dt)
        self.actor_manager.update(dt)
        self.level_manager.update(dt)

    def update_scenario(self, dt):
        pass

    def update(self, dt):
        if self.game_controller.is_game_menu_opened() or self.game_controller.is_trade_mode():
            self.game_controller.update(dt)
        else:
            prev_tod = self.tod 
            self.tod = self.level_manager.get_tod()
            
            if self.tod < NIGHT_TOD_END or NIGHT_TOD_START < self.tod:
                stalkers = self.actor_manager.get_actors_by_type(ActorType.STALKER)
                if self.stalker_spawn_term < 0.0 and len(stalkers) < 50:
                    n = random.randint(0, 2)
                    actor = self.actor_manager.spawn_actor("stalker")
                    for i in range(n):
                        self.actor_manager.spawn_around_actor("stalker", actor, 50, 200)
                    self.stalker_spawn_term = 1.0
                self.stalker_spawn_term -= dt
            elif (NIGHT_TOD_START <= prev_tod or prev_tod <= NIGHT_TOD_END) and NIGHT_TOD_END <= self.tod:
                self.actor_manager.remove_actors_by_type(ActorType.STALKER)

            self.update_scenario(dt)
            self.update_managers(dt)

            player = self.actor_manager.get_player()
            if not player or not player.is_alive():
                self.spawn_player()


