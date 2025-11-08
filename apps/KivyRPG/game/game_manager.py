from enum import Enum
from kivy.logger import Logger
from kivy.vector import Vector
from utility.singleton import SingletonInstance
from utility.kivy_helper import *
from .effect import GameEffectManager
from .game_resource import GameResourceManager
from .actor import ActorManager
from .level import LevelManager
from .game_controller import GameController
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
        self.scenario = ''

    def initialize(self):
        self.effect_manager = GameEffectManager.instance()
        self.actor_manager = ActorManager.instance()
        self.level_manager = LevelManager.instance()
        self.game_controller = GameController.instance()

    def close(self):
        pass

    def game_start(self):
        self.level_manager.open_level("default")
        self.set_scenario(GameScenario.INTRO)

    def reset(self):
        #self.actor_manager.reset_actor()
        self.set_scenario(GameScenario.INTRO)

    def callback_reset(self, *args):
        self.reset()

    def set_scenario(self, scenario):
        if self.scenario != scenario:
            self.update_scenario_end()
            self.scenario = scenario
            self.update_scenario_begin()
       
    def update_scenario_begin(self):
        if self.scenario == GameScenario.INTRO:
            pass

    def update_scenario_end(self):
        pass

    def update_scenario(self, dt):
        if self.scenario == GameScenario.INTRO:
            self.actor_manager.clear_actors()

            self.actor_manager.spawn_player()

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
                'dungeon',
                'inn',
                'forest',
                'farm',
                'mine',
            ]
            for data_name in data:
                pos = self.level_manager.get_random_pos()
                self.actor_manager.spawn_actor(data_name, pos)
            self.set_scenario(GameScenario.NONE)
   
                
    def update(self, dt):
        self.update_scenario(dt)
