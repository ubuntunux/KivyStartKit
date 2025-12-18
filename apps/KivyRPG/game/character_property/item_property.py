from .base_property import BaseProperty

class ItemProperty(BaseProperty):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.item_count = 1

    def reset_property(self):
        self.item_count = self.property_data.item_count

    def add_item_count(self, item_count):
        self.item_count = max(0, self.item_count + item_count)

    def set_item_count(self, item_count):
        self.item_count = max(0, item_count)

    def get_item_count(self):
        return self.item_count

    def get_item_price(self):
        return self.property_data.extra_property_data.price

