import random
from .constant import *
from utility.kivy_helper import *


class LevelData():
    def __init__(self, resource_manager, name, level_data_info={}):
        self.level_name = name
        self.level_color = TILE_GRASS_COLOR1
        self.day = 1
        self.tod = 8.0
        self.num_x = TILE_COUNT
        self.num_y = TILE_COUNT
        self.tile_create_infos = []
        self.actors = []
        for y in range(self.num_y):
            for x in range(self.num_x):
                tile_create_info = ('', '')
                if 0.99 < random.random():
                    tile_create_info = ("tile_set_00", "grass")
                self.tile_create_infos.append(tile_create_info)

        for (key, value) in level_data_info.items():
            setattr(self, key, value)

