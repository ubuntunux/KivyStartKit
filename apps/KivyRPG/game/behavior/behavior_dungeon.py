from .behavior import *

class BehaviorDungeon(Behavior):
    def __init__(self, actor):
        super().__init__(actor)
        self.spawn_time = -1.0
        self.actors = []
        self.is_first_time = True

    def update_behavior(self, dt):
        super().update_behavior(dt)
        extra_property = self.actor.property.extra_property
        if extra_property.is_spawnable():
            while (self.spawn_time < 0 or self.is_first_time) and extra_property.is_spawnable():
                extra_property.spawn_actor()
                self.spawn_time = extra_property.get_spawn_term()
            self.spawn_time -= dt
            self.is_first_time = False
