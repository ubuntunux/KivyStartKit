import os
from enum import Enum
from kivy.metrics import dp

from utility.kivy_helper import *
from ..constant import *
from .dungeon_property_data import DungeonPropertyData
from .gold_property_data import GoldPropertyData
from .inn_property_data import InnPropertyData
from .hp_property_data import HpPropertyData

class ActorCategory(Enum):
    CHARACTER = 0
    BUILDING = 1
    RESOURCE = 2
    ITEM = 3

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
    # buildings
    CASTLE = 2000
    DUNGEON = 2001
    INN = 2002
    # resources
    FOREST = 3000
    FARM = 3001
    MINE = 3002
    # items
    GOLD = 4000
    HP = 4001

    @classmethod
    def get_actor_category(cls, actor_type):
        if not hasattr(cls, 'category_map'):
            cls.category_map = {
                # character
                cls.PLAYER: ActorCategory.CHARACTER,
                cls.PATROLLER: ActorCategory.CHARACTER,
                cls.GUARDIAN: ActorCategory.CHARACTER,
                cls.STALKER: ActorCategory.CHARACTER,
                cls.INVADER: ActorCategory.CHARACTER,
                cls.GUARD: ActorCategory.CHARACTER,
                cls.CARPENTER: ActorCategory.CHARACTER,
                cls.CIVILIAN: ActorCategory.CHARACTER,
                cls.MERCHANT: ActorCategory.CHARACTER,
                cls.MINER: ActorCategory.CHARACTER,
                cls.FARMER: ActorCategory.CHARACTER,
                # building
                cls.CASTLE: ActorCategory.BUILDING,
                cls.DUNGEON: ActorCategory.BUILDING,
                cls.INN: ActorCategory.BUILDING,
                # resource
                cls.FOREST: ActorCategory.RESOURCE,
                cls.FARM: ActorCategory.RESOURCE,
                cls.MINE: ActorCategory.RESOURCE,
                # item
                cls.GOLD: ActorCategory.ITEM,
                cls.HP: ActorCategory.ITEM
            }
        return cls.category_map[actor_type]

    @classmethod
    def get_actor_extra_property_data(cls, actor_type):
        if not hasattr(cls, 'extra_property_data_map'):
            cls.extra_property_data_map = {
                # building
                cls.DUNGEON: DungeonPropertyData,
                cls.INN: InnPropertyData,
                # item
                cls.GOLD: GoldPropertyData,
                cls.HP: HpPropertyData,
            }
        return cls.extra_property_data_map.get(actor_type)

class ActionData():
    def __init__(self, character_name, action_name, texture, region):
        self.action_data_path = os.path.join(character_name, action_name)
        self.name = action_name
        self.texture = get_texture_atlas(texture, region)

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
        property_data_class = ActorType.get_actor_extra_property_data(actor_type)
        if property_data_class:
            self.extra_property_data = property_data_class(extra_property_data)


class CharacterData():
    def __init__(self, resource_manager, name, character_data_info):       
        self.name = name
        self.display_name = character_data_info.get('display_name', name)
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
