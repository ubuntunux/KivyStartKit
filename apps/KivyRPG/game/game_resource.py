import os
from kivy.logger import Logger
from utility.singleton import SingletonInstance
from utility.resource import ResourceManager
from .character_data import CharacterData
from .tile import TileData, TileDataSet
from .weapon_data import WeaponData


class GameResourceManager(ResourceManager):
    def __init__(self, game_path):
        super(GameResourceManager, self).__init__()
        self.tile_data_set = {}
        self.character_data = {}
        self.weapon_data = {}
        
        self.sounds_path = os.path.join(game_path, "data/sounds")
        self.effects_path = os.path.join(game_path, "data/effects")
        self.images_path = os.path.join(game_path, "data/images")
        self.maps_path = os.path.join(game_path, "data/maps")
        self.tile_data_path = os.path.join(game_path, "data/tiles")
        self.character_data_path = os.path.join(game_path, "data/characters")
        self.weapon_data_path = os.path.join(game_path, "data/weapons")
    
    def initialize(self):
        super().initialize(
            images_path=self.images_path, 
            effects_path=self.effects_path,
            sounds_path=self.sounds_path,
            preload_images=False,
            preload_effects=False,
            preload_sounds=False
        )  
        self.register_resources(self.tile_data_path, [".data"], self.tile_data_set, self.tile_data_set_loader, None)
        self.register_resources(self.weapon_data_path, [".data"], self.weapon_data, self.weapon_data_loader, None)
        self.register_resources(self.character_data_path, [".data"], self.character_data, self.character_data_loader, None)

    def close(self):
        pass
        
    def destroy(self):
        super().destroy()
        self.unregister_resources(self.tile_data_set)
        self.unregister_resources(self.character_data)
        self.unregister_resources(self.weapon_data)
        
    # tile
    def get_tile_data_set(self, resource_name):
        return self.get_resource(self.tile_data_set, resource_name)
        
    def tile_data_set_loader(self, name, filepath):
        if os.path.exists(filepath):
            with open(filepath) as f:
                tile_data_set_info = eval(f.read())
                return TileDataSet(self, name, tile_data_set_info)
    
    # character
    def get_character_data(self, resource_name):
        return self.get_resource(self.character_data, resource_name)
        
    def character_data_loader(self, name, filepath):
        if os.path.exists(filepath):
            with open(filepath) as f:
                character_data_info = eval(f.read())
                return CharacterData(self, name, character_data_info)
                
    # weapon
    def get_weapon_data(self, resource_name):
        return self.get_resource(self.weapon_data, resource_name, WeaponData(self, resource_name, {}))
        
    def weapon_data_loader(self, name, filepath):
        if os.path.exists(filepath):
            with open(filepath) as f:
                weapon_data_info = eval(f.read())
                return WeaponData(self, name, weapon_data_info)
                
                
