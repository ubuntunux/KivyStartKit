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
from .level_data import LevelData
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
        self.current_game_name = 'default'
        self.game_data = {}

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
        level_data = LevelData(GameResourceManager.instance(), MAIN_LEVEL_NAME, True)
        self.level_manager.new_level(level_data)
        self.level_manager.set_day(1)
        self.level_manager.set_tod(MORNING_TOD)
        self.reset_actors()
        self.save_game(save_file=False) 

    def load_game(self):
        self.level_manager.close_level()
        self.game_controller.on_close_level()

        self.game_data = GameResourceManager.instance().get_game_data(self.current_game_name)
        level_name = self.game_data['current_level_name'] 
        level_data = self.game_data['level_data'].get(level_name)
        self.level_manager.load_level(level_data)
        self.level_manager.set_day(self.game_data['day'])
        self.level_manager.set_tod(self.game_data['tod'])

        self.actor_manager.load_actor_save_data(self.game_data['player_data'])
        self.actor_manager.post_actor_load_processing()   
        self.level_manager.post_level_load_processing()
        self.game_controller.post_controller_load_processing()

    def save_game(self, save_file=True):
        player_data = self.actor_manager.get_player_save_data()
        level_data = self.level_manager.save_level()

        self.game_data['player_data'] = player_data
        self.game_data['day'] = self.level_manager.get_day()
        self.game_data['tod'] = self.level_manager.get_tod()
        self.game_data['current_level_name'] = level_data.level_name
        if 'level_data' not in self.game_data:
            self.game_data['level_data'] = {}
        self.game_data['level_data'][level_data.level_name] = level_data

        if save_file:
            GameResourceManager.instance().save_game_data(
                self.current_game_name,
                self.game_data
            ) 
      
    def clear_actors(self):
        self.actor_manager.clear_actors()
        self.game_controller.refresh_player_inventory()

    def reset_actors(self):
        self.clear_actors()

        castle_radius_inner = dp(50)
        castle_radius_outter = dp(150)
        dungeon_radius_inner = dp(400)
        dungeon_radius_outter = dp(1000)

        # spawn at first
        castle = self.actor_manager.spawn_actor('castle', self.level_manager.get_level_center())

        self.actor_manager.spawn_around_actor('inn', castle, castle_radius_inner, castle_radius_outter)
        self.actor_manager.spawn_actor('guard', castle.get_pos() + Vector(-castle.size[0] * 0.5, -castle.size[1]))
        self.actor_manager.spawn_actor('guard', castle.get_pos() + Vector(castle.size[0] * 0.5, -castle.size[1]))

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

        spawn_pos = castle.get_pos() + Vector(0, -castle.size[1])
        self.level_manager.set_spawn_pos(spawn_pos)
        self.actor_manager.spawn_actor('player', spawn_pos)

    def goto_level(self, level_name, spawn_pos=None):
        if self.level_manager.get_level_name() == level_name: 
            player = self.actor_manager.get_player()
            if player:
                if not spawn_pos:
                    spawn_pos = self.level_manager.get_spawn_pos()
                player.set_pos(spawn_pos)
        else:
            # save previous level status
            self.save_game(save_file=False) 
             
            # close level
            self.level_manager.close_level()
            self.game_controller.on_close_level()

            # load level
            self.game_data['current_level_name'] = level_name
            level_data = self.game_data['level_data'].get(level_name)
            self.level_manager.load_level(level_data)

            player_data = self.game_data['player_data'] 
            player_data['actor_pos'] = spawn_pos if spawn_pos else level_data['spawn_pos'] 
            self.actor_manager.load_actor_save_data(player_data)
            self.actor_manager.post_actor_load_processing()   
            self.level_manager.post_level_load_processing()
            self.game_controller.post_controller_load_processing()

    def enter_dungeon(self, dungeon_actor):
        level_name = dungeon_actor.actor_uuid

        # already exists the dungeon
        if level_name in self.game_data['level_data']:
            self.goto_level(level_name)
            return

        # save previoud level status
        self.save_game(save_file=False) 
        player_data = self.game_data['player_data'] 
        parent_level_name = self.game_data['current_level_name']
 
        # close level
        self.level_manager.close_level()
        self.game_controller.on_close_level()

        # new level
        level_data = LevelData(GameResourceManager.instance(), level_name, False)
        level_data.level_color = TILE_DARK_DUNGEON0
        level_data.num_x = DUNGEON_TILE_COUNT
        level_data.num_y = DUNGEON_TILE_COUNT
        self.level_manager.new_level(level_data)
        self.game_data['current_level_name'] = level_name

        data = [
            'forest',
            'farm',
            'mine',
        ] * 5
        for data_name in data:
            self.actor_manager.spawn_actor(data_name)

        data = [
            'patroller',
            'stalker',
        ] * 3
        for data_name in data:
            self.actor_manager.spawn_actor(data_name)

        self.actor_manager.spawn_actor('guardian')
        gate_pos = self.level_manager.tile_to_pos(Vector(level_data.num_x / 2, level_data.num_y / 2))
        gate = self.actor_manager.spawn_actor('gate', pos=gate_pos)
        gate.get_extra_property().set_parent_level_name(parent_level_name)

        enter_pos = dungeon_actor.get_pos() + Vector(0, -dungeon_actor.size[1])
        gate.get_extra_property().set_enter_pos(enter_pos)

        spawn_pos = gate.get_pos() + Vector(0, -gate.size[1])
        self.level_manager.set_spawn_pos(spawn_pos)
        player_data['actor_pos'] = spawn_pos
        
        self.actor_manager.load_actor_save_data(player_data)
        self.actor_manager.post_actor_load_processing()   
        self.level_manager.post_level_load_processing()
        self.game_controller.post_controller_load_processing()

    def exit_dungeon(self, gate_actor):
        spawn_pos = gate_actor.get_extra_property().get_enter_pos()
        level_name = gate_actor.get_extra_property().get_parent_level_name()
        self.goto_level(level_name, spawn_pos)

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
            is_main_level = self.level_manager.get_is_main_level() 
            if is_main_level:
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
            if player and not player.is_alive():
                player.respawn()
                self.goto_level(MAIN_LEVEL_NAME) 
