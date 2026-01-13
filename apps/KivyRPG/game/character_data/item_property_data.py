from .actor_data import *

class ItemPropertyData:
    def __init__(self, property_data):
        self.item_count = 1 
        self.price = {}
        self.hp = 100
        self.weapon_data = ''
        for (key, value) in property_data.items():
            if hasattr(self, key):
                if key == 'price':
                    for (item_data_name, price_value) in value.items():
                        self.price[item_data_name] = price_value
                else:
                    setattr(self, key, value)

    def get_item_count(self):
        return self.item_count
