from .behavior import *
from .behavior_civilian import *
from .behavior_patroller import *
from .behavior_player import *
from .behavior_dungeon import *
from .behavior_item import *
from .behavior_inn import *

behavior_map = {
    ActorType.PLAYER: BehaviorPlayer,

    ActorType.PATROLLER: BehaviorPatroller,
    ActorType.GUARDIAN: BehaviorPatroller,
    ActorType.STALKER: BehaviorPatroller,
    ActorType.INVADER: BehaviorPatroller,

    ActorType.GUARD: BehaviorCivilian,
    ActorType.CARPENTER: BehaviorCivilian,
    ActorType.CIVILIAN: BehaviorCivilian,
    ActorType.MERCHANT: BehaviorCivilian,
    ActorType.MINER: BehaviorCivilian,
    ActorType.FARMER: BehaviorCivilian,

    ActorType.CASTLE: BehaviorCivilian,
    ActorType.DUNGEON: BehaviorDungeon,
    ActorType.INN: BehaviorInn,

    ActorType.FOREST: BehaviorCivilian,
    ActorType.FARM: BehaviorCivilian,
    ActorType.MINE: BehaviorCivilian,

    ActorType.GOLD: BehaviorItem,
    ActorType.HP: BehaviorItem,
    ActorType.ORE: BehaviorItem,
    ActorType.WOOD: BehaviorItem,
    ActorType.GRAIN: BehaviorItem,
}

def create_behavior(actor, actor_type):
    behavior_class = behavior_map.get(actor_type)
    return behavior_class(actor)


