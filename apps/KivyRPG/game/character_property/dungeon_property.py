from .base_property import BaseProperty

class DungeonProperty(BaseProperty):
    def get_spawn_data(self):
        return self.property_data.spawn_data

    def get_spawn_term(self):
        return self.property_data.spawn_term

    def get_limit_spawn_count(self):
        return self.property_data.limit_spawn_count

    def get_spawn_data(self):
        return self.property_data.spawn_data

