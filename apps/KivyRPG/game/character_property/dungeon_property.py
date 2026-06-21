import random
from kivy.vector import Vector
from .base_property import BaseProperty

class DungeonProperty(BaseProperty):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.actors = []       
        self.spawn_count = 0
        self.temp_actor_uuid_list = []

    def get_property_save_data(self):
        save_data = {
            'actor_uuid_list': [actor.get_actor_uuid() for actor in self.actors],
            'spawn_count': self.spawn_count,
        }
        return save_data

    def load_property_save_data(self, save_data):
        for (key, value) in save_data.items():
            if key == 'actor_uuid_list':
                self.temp_actor_uuid_list = value
            elif hasattr(self, key):
                setattr(self, key, value)

    def post_property_load_processing(self):
        for actor_uuid in self.temp_actor_uuid_list:
            actor = self.actor.actor_manager.get_actor(actor_uuid)
            self.actors.append(actor)
        self.temp_actor_uuid_list = []

    def get_spawn_data(self):
        return self.property_data.spawn_data

    def get_spawn_term(self):
        return self.property_data.spawn_term

    def get_active_actor_count(self):
        return self.property_data.active_actor_count

    def get_limit_spawn_count(self):
        return self.property_data.limit_spawn_count

    def get_spawn_data(self):
        return self.property_data.spawn_data

    def is_spawnable(self):
        return self.spawn_count < self.get_limit_spawn_count() and len(self.actors) < self.get_active_actor_count()

    def spawn_actor(self):
        actor_manager = self.actor.actor_manager
        spawn_data_name = random.choice(self.get_spawn_data())
        pos = Vector(random.random() - 0.5, random.random() - 0.5).normalize()
        pos = pos * self.actor.get_radius() * 2.0 + self.actor.get_pos()
        actor = actor_manager.spawn_actor(spawn_data_name, pos)
        self.actors.append(actor)
        self.spawn_count += 1

    def update_property(self, dt):
        if self.actors:
            self.actors = [actor for actor in self.actors if actor.is_alive()]

