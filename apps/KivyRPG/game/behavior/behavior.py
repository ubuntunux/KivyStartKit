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
    def __init__(self, actor):
        self.actor = actor
        self.behavior_state = BehaviorState.NONE
        self.behavior_time = -1
        
    def is_behavior_state(self, behavior_state):
        return behavior_state == self.behavior_state
    
    def get_behavior_state(self):
        return self.behavior_state
    
    def set_behavior_state(self, behavior_state, behavior_time=3.0):
        self.behavior_state = behavior_state
        self.behavior_time = 1.0 + behavior_time * random.random()
    
    def update_behavior(self, dt):
        if 0 < self.behavior_time:
            self.behavior_time -= dt
