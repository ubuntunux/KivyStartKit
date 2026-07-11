class InnPropertyData:
    def __init__(self, property_data):
        self.items = []
        for (key, value) in property_data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def get_items(self):
        return self.items
