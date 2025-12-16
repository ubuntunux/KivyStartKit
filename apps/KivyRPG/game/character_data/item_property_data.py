from .actor_data import *

class ItemPropertyData:
    def __init__(self, property_data):
        self.item_count = 1 
        self.price = {}
        self.hp = 100
        for (key, value) in property_data.items():
            if hasattr(self, key):
                if key == 'price':
                    for (actor_key_str, price_value) in value.items():
                        self.price[getattr(ActorKey, actor_key_str).value] = price_value
                else:
                    setattr(self, key, value)

    def get_item_count(self):
        return self.item_count
