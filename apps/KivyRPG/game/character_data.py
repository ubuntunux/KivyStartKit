import os
from enum import Enum
from kivy.metrics import dp

from .constant import *
from utility.kivy_helper import *

class ActorType(Enum):
    PLAYER = 0
    PATROLLER = 1
    GUARDIAN = 2
    STALKER = 3
    INVADER = 4
    # npc
    GUARD = 1000
    CARPENTER = 1001
    CIVILIAN = 1002
    MERCHANT = 1003
    MINER = 1004
    FARMER = 1005
    # props
    CASTLE = 2000
    DUNGEON = 2001


class ActionData():
    def __init__(self, character_name, action_name, texture, region):
        self.action_data_path = os.path.join(character_name, action_name)
        self.name = action_name
        self.texture = get_texture_atlas(texture, region)

class DungeonPropertyData:
    def __init__(self, property_data):
        self.spawn_data = []
        self.spawn_term = 3.0
        self.limit_spawn_count = 5
        for (key, value) in property_data.items():
            if hasattr(self, key):
                setattr(self, key, value)

class CharacterPropertyData():
    def __init__(self, actor_type, property_data):
        self.walk_speed = 0
        self.max_hp = 0
        self.max_mp = 0
        self.max_sp = 0
        for (key, value) in property_data.items():
            if hasattr(self, key):
                setattr(self, key, value)

        self.extra_property_data = None
        extra_property_data = property_data.get('extra_property', {})
        if actor_type == ActorType.DUNGEON:
            self.extra_property_data = DungeonPropertyData(extra_property_data) 


class CharacterData():
    def __init__(self, resource_manager, name, character_data_info):       
        self.name = name
        self.size = tuple(character_data_info.get("size", TILE_SIZE))
        self.actor_type = getattr(ActorType, character_data_info.get("actor_type"))
        self.action_data = {}
        self.weapon_data = None
        self.property_data = None

        src_image = resource_manager.get_image(character_data_info["source"])
        default_action = {'idle': {'region': (0,0,1,1)}}
        action_data_infos = character_data_info.get("actions", default_action)      
        
        for (action_name, action_data_info) in action_data_infos.items():
            self.action_data[action_name] = ActionData(
                name,
                action_name,
                src_image.texture,
                action_data_info["region"]
            )
        self.property_data = CharacterPropertyData(self.actor_type, character_data_info.get("property", {}))
        weapon_data = character_data_info.get("weapon", {})
        if weapon_data:
            self.weapon_data = resource_manager.get_weapon_data(weapon_data)
