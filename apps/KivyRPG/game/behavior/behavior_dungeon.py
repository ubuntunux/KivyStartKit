import random
from kivy.vector import Vector
from .behavior import *

class BehaviorDungeon(Behavior):
    def __init__(self, actor):
        super().__init__(actor)
        self.spawn_time = 0.0
        self.spawn_count = 0

    def update_behavior(self, dt):
        super().update_behavior(dt)
        actor_manager = self.actor.actor_manager
        extra_property = self.actor.property.extra_property
        if self.spawn_count < extra_property.get_limit_spawn_count() and extra_property.get_spawn_data():
            if self.spawn_time < 0.0:
                self.spawn_count += 1 
                self.spawn_time = max(1, extra_property.get_spawn_term())
                spawn_data_name = random.choice(extra_property.get_spawn_data())
                pos = Vector(random.random() - 0.5, random.random() - 0.5).normalize()
                pos = pos * self.actor.get_radius() * 2.0 + self.actor.get_pos()
                actor_manager.spawn_actor(spawn_data_name, pos)
            self.spawn_time -= dt
