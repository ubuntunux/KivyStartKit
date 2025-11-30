class HpPropertyData:
    def __init__(self, property_data):
        self.gold = 1 
        self.hp = 100
        for (key, value) in property_data.items():
            if hasattr(self, key):
                setattr(self, key, value)
