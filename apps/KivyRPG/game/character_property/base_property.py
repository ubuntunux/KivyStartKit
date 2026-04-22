class BaseProperty:
    def __init__(self, actor, property_data):
        self.actor = actor
        self.property_data = property_data

    def get_property_save_data(self):
        return {}

    def load_property_save_data(self, save_data):
        for (key, value) in save_data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def reset_property(self):
        pass

    def update_property(self, dt):
        pass


