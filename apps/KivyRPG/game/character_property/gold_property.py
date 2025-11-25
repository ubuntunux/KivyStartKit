from .base_property import BaseProperty

class GoldProperty(BaseProperty):
    def get_gold(self):
        return self.property_data.gold

