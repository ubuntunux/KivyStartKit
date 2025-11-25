class GoldPropertyData:
    def __init__(self, property_data):
        self.gold = 1 
        for (key, value) in property_data.items():
            if hasattr(self, key):
                setattr(self, key, value)
