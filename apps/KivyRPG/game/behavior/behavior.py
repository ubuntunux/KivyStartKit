from enum import Enum
import random
from kivy.vector import Vector
from ..character_data import ActorType 

class BehaviorState(Enum):
    NONE = 0
    IDLE = 1
    ROAMING = 2
    TRACE_TARGET = 3


class Behavior:
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
    
    def __init__(self, actor):
        self.actor = actor
        self.behavior_state = BehaviorState.NONE
        self.behavior_time = -1
        
    def is_behavior_state(self, behavior_state):
        return behavior_state == self.behavior_state
    
    def get_behavior_state(self):
        return self.behavior_state
    
    def set_behavior_state(self, behavior_state, behavior_time=1.0, random_time=3.0):
        self.behavior_state = behavior_state
        self.set_behavior_time(behavior_time, random_time)

    def set_behavior_time(self, behavior_time, random_time=0.0):
        self.behavior_time = behavior_time + random_time * random.random()
    
    def update_behavior(self, dt):
        if 0 < self.behavior_time:
            self.behavior_time -= dt

    def on_collide_actor(self, other_actor):
        pass

    def on_interaction(self, actor):
        return False

