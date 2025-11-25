class DungeonPropertyData:
    def __init__(self, property_data):
        self.spawn_data = []
        self.spawn_term = 3.0
        self.limit_spawn_count = 5
        for (key, value) in property_data.items():
            if hasattr(self, key):
                setattr(self, key, value)
