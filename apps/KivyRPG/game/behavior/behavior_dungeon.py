from .behavior import *

class BehaviorDungeon(Behavior):
    def __init__(self, actor):
        super().__init__(actor)
        self.spawn_time = -1.0

    def get_behavior_save_data(self):
        save_data = super().get_behavior_save_data()
        save_data['spawn_time'] = self.spawn_time

    def load_behavior_save_data(self, save_data):
        super().load_behavior_save_data(save_data)
        for (key, value) in save_data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def post_behavior_load_processing(self):
        super().post_behavior_load_processing()

    def update_behavior(self, dt):
        super().update_behavior(dt)
        extra_property = self.actor.property.extra_property
        if extra_property.is_spawnable():
            while self.spawn_time < 0 and extra_property.is_spawnable():
                extra_property.spawn_actor()
                self.spawn_time = extra_property.get_spawn_term()
            self.spawn_time -= dt
