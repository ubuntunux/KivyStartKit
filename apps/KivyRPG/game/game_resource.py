import pickle
import pprint
import os
from uuid import UUID
from kivy.logger import Logger
from utility.singleton import SingletonInstance
from utility.resource import ResourceManager
from .character_data import CharacterData
from .tile import TileData, TileDataSet
from .weapon_data import WeaponData
from .level_data import LevelData

class GameResourceManager(ResourceManager):
    def __init__(self, game_path):
        super(GameResourceManager, self).__init__()
        self.tile_data_set = {}
        self.character_data = {}
        self.weapon_data = {}
        self.game_data = {}
        
        self.save_path = os.path.join(game_path, "data/save")
        self.sounds_path = os.path.join(game_path, "data/sounds")
        self.effects_path = os.path.join(game_path, "data/effects")
        self.images_path = os.path.join(game_path, "data/images")
        self.maps_path = os.path.join(game_path, "data/maps")
        self.tile_data_path = os.path.join(game_path, "data/tiles")
        self.character_data_path = os.path.join(game_path, "data/characters")
        self.weapon_data_path = os.path.join(game_path, "data/weapons")
        self.game_data_path = os.path.join(game_path, "data/save")

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
        self.register_resources(self.game_data_path, [".data"], self.game_data, self.game_data_loader, None)

    def close(self):
        pass
        
    def destroy(self):
        self.unregister_resources(self.game_data)
        self.unregister_resources(self.tile_data_set)
        self.unregister_resources(self.character_data)
        self.unregister_resources(self.weapon_data)
        super().destroy()

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
                
    # game
    def register_game_data(self, game_name, data):
        return self.create_resource(
            self.game_data_path, 
            '.data', 
            self.game_data, 
            self.game_data_loader, 
            None,
            game_name,
            data
        )
            
    def get_game_data(self, resource_name):
        return self.get_resource(self.game_data, resource_name)
    
    def game_data_loader(self, name, filepath):
        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                return pickle.load(f)

    def save_game_data(self, resource_name, data):
        filepath = os.path.join(self.game_data_path, resource_name + '.data')
        with open(filepath, "wb") as f:
            pickle.dump(data, f)
        # debug
        filepath = os.path.join(self.game_data_path, resource_name + '.json')
        with open(filepath, 'w') as f:
            f.write(pprint.pformat(data, indent=4))
