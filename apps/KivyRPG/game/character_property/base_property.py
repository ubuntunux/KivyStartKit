class BaseProperty:
    def __init__(self, owner, property_data):
        self.owner = owner
        self.property_data = property_data

    def reset_property(self):
        pass

    def update_property(self, dt):
        pass


