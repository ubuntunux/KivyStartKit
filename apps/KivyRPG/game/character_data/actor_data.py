from enum import Enum

class ActorCategory(Enum):
    CHARACTER = 0
    MONSTER = 1
    BUILDING = 2
    MONSTER_BUILDING = 3
    RESOURCE_GENERATOR = 4
    RESOURCE = 5
    ITEM = 6
    SCROLL = 7
    WEAPON = 8

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
    GATE = 2003
    # resource generators
    FOREST = 3000
    FARM = 3001
    MINE = 3002
    # resources
    GOLD = 4000
    ORE = 4001
    WOOD = 4002
    GRAIN = 4003
    # items
    HP = 5000
    # scrolls
    SCROLL = 6000
    # weapons
    WEAPON = 7000

__category_map__ = {
    # character
    ActorType.PLAYER: ActorCategory.CHARACTER,
    ActorType.PATROLLER: ActorCategory.MONSTER,
    ActorType.GUARDIAN: ActorCategory.MONSTER,
    ActorType.STALKER: ActorCategory.MONSTER,
    ActorType.INVADER: ActorCategory.MONSTER,
    ActorType.GUARD: ActorCategory.CHARACTER,
    ActorType.CARPENTER: ActorCategory.CHARACTER,
    ActorType.CIVILIAN: ActorCategory.CHARACTER,
    ActorType.MERCHANT: ActorCategory.CHARACTER,
    ActorType.MINER: ActorCategory.CHARACTER,
    ActorType.FARMER: ActorCategory.CHARACTER,
    # building
    ActorType.CASTLE: ActorCategory.BUILDING,
    ActorType.DUNGEON: ActorCategory.BUILDING,
    ActorType.INN: ActorCategory.BUILDING,
    ActorType.GATE: ActorCategory.BUILDING,
    # resource generator
    ActorType.FOREST: ActorCategory.RESOURCE_GENERATOR,
    ActorType.FARM: ActorCategory.RESOURCE_GENERATOR,
    ActorType.MINE: ActorCategory.RESOURCE_GENERATOR,
    # resource
    ActorType.GOLD: ActorCategory.RESOURCE,
    ActorType.ORE: ActorCategory.RESOURCE,
    ActorType.WOOD: ActorCategory.RESOURCE,
    ActorType.GRAIN: ActorCategory.RESOURCE,
    # item
    ActorType.HP: ActorCategory.ITEM,
    # scroll
    ActorType.SCROLL: ActorCategory.SCROLL,
    # weapon
    ActorType.WEAPON: ActorCategory.WEAPON,
}

def get_actor_category(actor_type):
    return __category_map__[actor_type]

__blockable_actor_categories__ = [
    ActorCategory.CHARACTER,
    ActorCategory.MONSTER,
    ActorCategory.BUILDING, 
    ActorCategory.RESOURCE_GENERATOR
]

def get_is_blockable_actor_category(actor_category):
    return actor_category in __blockable_actor_categories__

class ActorID(Enum):
    NONE = 0
    # item
    HP_A = 1
    HP_B = 2
    # weapon
    WEAPON_AXE = 1000
    # scrolls
    RESURRECTION_SCROLL = 2000

class ActorKey(Enum):
    GOLD = (ActorType.GOLD, ActorID.NONE)
    RESURRECTION_SCROLL = (ActorType.SCROLL, ActorID.RESURRECTION_SCROLL)
     
