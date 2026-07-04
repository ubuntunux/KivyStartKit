from kivy.vector import Vector
from .base_property import BaseProperty

class GateProperty(BaseProperty):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.parent_level_name = ''
        self.enter_pos = Vector(0.0, 0.0)

    def get_parent_level_name(self):
        return self.parent_level_name

    def set_parent_level_name(self, level_name):
        self.parent_level_name = level_name

    def get_enter_pos(self):
        return self.enter_pos

    def set_enter_pos(self, pos):
        self.enter_pos = Vector(pos)

    def get_property_save_data(self):
        save_data = super().get_property_save_data()
        save_data['parent_level_name'] = self.parent_level_name
        save_data['enter_pos'] = self.enter_pos
        return save_data
