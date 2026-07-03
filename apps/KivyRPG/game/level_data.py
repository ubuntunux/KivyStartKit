import pprint
import random
from kivy.vector import Vector
from .constant import *
from utility.kivy_helper import *


class LevelData():
    def __init__(self, resource_manager, name, is_main_level, level_data_info={}):
        self.is_main_level = is_main_level
        self.level_name = name
        self.level_color = TILE_GRASS_COLOR1
        self.num_x = TILE_COUNT
        self.num_y = TILE_COUNT
        self.tile_create_infos = []
        self.actors = []
        self.spawn_pos = Vector(0.0, 0.0)

        for (key, value) in level_data_info.items():
            setattr(self, key, value)

        self.update_tile_create_infos()

    def update_tile_create_infos(self):
        self.tile_create_infos = []
        for y in range(self.num_y):
            for x in range(self.num_x):
                tile_create_info = ('', '')
                if 0.99 < random.random():
                    tile_create_info = ("tile_set_00", "grass")
                self.tile_create_infos.append(tile_create_info)

    def __repr__(self):
        return pprint.pformat(self.__dict__)
