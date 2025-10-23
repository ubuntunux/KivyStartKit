from enum import Enum
import random
from kivy.vector import Vector
from .character_data import ActorType 

class BehaviorState(Enum):
    IDLE = 0
    ROAMING = 1
    TRACE_TARGET = 2


class Behavior:
    @staticmethod
    def get_behavior_class(actor_type):
        if actor_type == ActorType.PLAYER:
            return BehaviorPlayer
        elif actor_type == ActorType.MONSTER:
            return BehaviorMonster
        return BehaviorMonster

    @classmethod
    def create_behavior(cls, owner, actor_type):
        behavior_class = cls.get_behavior_class(actor_type)
        return behavior_class(owner)

    def __init__(self, actor):
        self.actor = actor
        self.behavior_state = BehaviorState.IDLE
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


class BehaviorPlayer(Behavior):
    pass


class BehaviorMonster(Behavior):
    def __init__(self, actor):
        super().__init__(actor)
        self.attack_time = 1.0

    def check_near_by_player(self, player):
        tracing_radius = 600.0
        return player.is_alive() and player.get_pos().distance(self.actor.get_pos()) < tracing_radius
    
    def set_behavior_state(self, behavior_state, behavior_time=1.0):
        super().set_behavior_state(behavior_state, behavior_time)
        actor_manager = self.actor.actor_manager
        level_manager = self.actor.level_manager
        player = actor_manager.get_player()
        if behavior_state == BehaviorState.ROAMING:
            pos = level_manager.get_random_pos()
            self.actor.move_to(pos)
            self.actor.set_move_speed(1.0)
        elif behavior_state == BehaviorState.TRACE_TARGET:
            self.actor.trace_actor(player)
            self.actor.set_move_speed(2.0)
               
    def update_behavior(self, dt):
        super().update_behavior(dt)
        actor_manager = self.actor.actor_manager
        level_manager = self.actor.level_manager
        player = actor_manager.get_player()
        is_near_by_player = self.check_near_by_player(player)
        is_behavior_done = self.behavior_time < 0
        if self.is_behavior_state(BehaviorState.IDLE):
            if is_near_by_player:
                self.set_behavior_state(BehaviorState.TRACE_TARGET)
            elif is_behavior_done:
                self.set_behavior_state(BehaviorState.ROAMING)
        elif self.is_behavior_state(BehaviorState.ROAMING):
            if is_near_by_player:
                self.set_behavior_state(BehaviorState.TRACE_TARGET)
            elif is_behavior_done:
                self.set_behavior_state(BehaviorState.IDLE)
        elif self.is_behavior_state(BehaviorState.TRACE_TARGET):        
            target_dist = player.get_pos().distance(self.actor.get_pos())
            attack_range = 400.0
            if self.attack_time < 0 and target_dist < attack_range:
                self.actor.set_attack()
                self.attack_time = 1.0
            else:
                self.attack_time -= dt
            
            if not player.is_alive():
                self.set_behavior_state(BehaviorState.ROAMING)
        
            
