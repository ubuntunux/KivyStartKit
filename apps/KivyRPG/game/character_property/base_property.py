class BaseProperty:
    def __init__(self, actor, property_data):
        self.actor = actor
        self.property_data = property_data

    def reset_property(self):
        pass

    def update_property(self, dt):
        pass


