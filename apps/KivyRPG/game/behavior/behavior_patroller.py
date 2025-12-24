import random
from kivy.vector import Vector
from ..character_data import ActorCategory
from .behavior import *

class BehaviorPatroller(Behavior):
    def __init__(self, actor):
        super().__init__(actor)
        self.attack_time = 1.0
        self.attack_range = 400.0
        self.tracing_start_radius = 600.0
        self.tracing_end_radius = 1200.0
        self.patroll_radius = 200.0
        self.move_speed = 1.0
        self.tracing_speed = 3.0
        self.spawn_pos = Vector(0,0) 
        self.target = None
   
    def set_behavior_state(self, behavior_state, behavior_time=1.0, random_time=3.0):
        actor_manager = self.actor.actor_manager
        level_manager = self.actor.level_manager
        if behavior_state == BehaviorState.ROAMING:
            pos = Vector(random.random() - 0.5, random.random() - 0.5).normalize()
            pos = self.spawn_pos + pos * self.patroll_radius 
            bound_min = pos - self.actor.get_size() * 2.0
            bound_max = pos + self.actor.get_size() * 2.0
            pos = level_manager.clamp_pos_to_level_bound(pos, bound_min, bound_max)
            to_pos = pos - self.spawn_pos
            distance = self.spawn_pos.distance(pos)
            move_speed = self.tracing_speed if distance > self.patroll_radius else self.move_speed 
            self.actor.set_move_speed(move_speed)
            self.actor.move_to(pos)
        elif behavior_state == BehaviorState.TRACE_TARGET:
            self.actor.set_move_speed(self.tracing_speed)
        super().set_behavior_state(behavior_state, behavior_time)
               
    def update_behavior(self, dt):
        super().update_behavior(dt)
        actor_manager = self.actor.actor_manager
        level_manager = self.actor.level_manager
        size = (self.actor.get_size() * 2.0 + Vector(self.patroll_radius, self.patroll_radius))
        bound_min = self.actor.get_pos() - size
        bound_max = self.actor.get_pos() + size
        target = level_manager.get_nearest_enemy(
            bound_min, 
            bound_max, 
            self.actor.get_actor_category()
        )
        if not target and self.is_behavior_state(BehaviorState.TRACE_TARGET):
            target = self.target
        else:
            self.target = target
        target_distance = 0
        is_near_by_target = False
        if target and target.is_alive():
            target_distance = target.get_pos().distance(self.actor.get_pos())
            is_near_by_target = target_distance < self.tracing_start_radius 
        is_behavior_done = self.behavior_time < 0

        if self.is_behavior_state(BehaviorState.NONE):
            self.spawn_pos = Vector(self.actor.get_pos()) 
            self.set_behavior_state(BehaviorState.IDLE)
        elif self.is_behavior_state(BehaviorState.IDLE):
            if is_near_by_target:
                self.set_behavior_state(BehaviorState.TRACE_TARGET)
            elif is_behavior_done:
                self.set_behavior_state(BehaviorState.ROAMING)
        elif self.is_behavior_state(BehaviorState.ROAMING):
            if is_near_by_target:
                self.set_behavior_state(BehaviorState.TRACE_TARGET)
            elif is_behavior_done:
                self.set_behavior_state(BehaviorState.IDLE)
        elif self.is_behavior_state(BehaviorState.TRACE_TARGET):
            if not target or not target.is_alive() or not self.actor.get_actor_type() is ActorType.STALKER and self.tracing_end_radius <= target_distance:
                self.set_behavior_state(BehaviorState.ROAMING)
            else:
                self.actor.trace_actor(target)
                target_dist = target.get_pos().distance(self.actor.get_pos())
                if self.attack_time < 0 and target_dist < self.attack_range:
                    self.actor.set_attack()
                    self.attack_time = 1.0
                else:
                    self.attack_time -= dt
     
