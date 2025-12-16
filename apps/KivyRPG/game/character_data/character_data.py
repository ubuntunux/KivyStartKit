import os
from utility.kivy_helper import *
from ..constant import *
from .actor_data import *
from .dungeon_property_data import *
from .item_property_data import *
from .inn_property_data import *

__extra_property_data_map__ = {
    # building
    ActorType.DUNGEON: DungeonPropertyData,
    ActorType.INN: InnPropertyData,
    # item
    ActorType.GOLD: ItemPropertyData,
    ActorType.HP: ItemPropertyData,
    ActorType.ORE: ItemPropertyData,
    ActorType.WOOD: ItemPropertyData,
    ActorType.GRAIN: ItemPropertyData,
}

def get_actor_extra_property_data(actor_type): 
    return __extra_property_data_map__.get(actor_type)


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
        property_data_class = get_actor_extra_property_data(actor_type)
        if property_data_class:
            self.extra_property_data = property_data_class(extra_property_data)

    def get_extra_property_data(self):
        return self.extra_property_data

class CharacterData():
    def __init__(self, resource_manager, name, character_data_info):       
        self.name = name
        self.display_name = character_data_info.get('display_name', name)
        self.size = tuple(character_data_info.get("size", TILE_SIZE))
        self.actor_type = getattr(ActorType, character_data_info.get("actor_type"))
        self.actor_id = getattr(ActorID, character_data_info.get("actor_id", 'NONE'))
        self.actor_key = (self.actor_type, self.actor_id)
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

    def get_property_data(self):
        return self.property_data

    def get_extra_property_data(self):
        return self.property_data.extra_property_data
