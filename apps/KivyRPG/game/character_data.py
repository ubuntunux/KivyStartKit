import os
from enum import Enum
from .constant import *
from utility.kivy_helper import *

class ActorType(Enum):
    PLAYER = 0
    MONSTER = 1
    SPAWNER = 2

class ActionData():
    def __init__(self, character_name, action_name, texture, region):
        self.action_data_path = os.path.join(character_name, action_name)
        self.name = action_name
        self.texture = get_texture_atlas(texture, region)

class CharacterPropertyData():
    def __init__(self, property_data):
        self.walk_speed = 100.0
        self.max_hp = 100.0
        self.max_mp = 100.0
        self.max_sp = 100.0
        for (key, value) in property_data.items():
            if hasattr(self, key):
                setattr(self, key, value)


class CharacterData():
    def __init__(self, resource_manager, name, character_data_info):
        src_image = resource_manager.get_image(character_data_info["source"])
        action_data_infos = character_data_info.get("actions")      
        
        self.name = name
        self.actor_type = getattr(ActorType, character_data_info.get("actor_type"))
        self.action_data = {}
        for (action_name, action_data_info) in action_data_infos.items():
            self.action_data[action_name] = ActionData(
                name,
                action_name,
                src_image.texture,
                action_data_info["region"]
            )
        self.property_data = CharacterPropertyData(character_data_info.get("properties", {}))
        self.weapon_data = resource_manager.get_weapon_data(character_data_info.get("weapon"))
