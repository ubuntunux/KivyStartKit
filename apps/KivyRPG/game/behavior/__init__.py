from .behavior import *
from .behavior_civilian import *
from .behavior_patroller import *
from .behavior_player import *
from .behavior_dungeon import *


def get_behavior_class(actor_type):
    if actor_type == ActorType.PLAYER:
        return BehaviorPlayer
    elif actor_type == ActorType.PATROLLER:
        return BehaviorPatroller
    elif actor_type == ActorType.GUARDIAN:
        return BehaviorPatroller
    elif actor_type == ActorType.STALKER:
        return BehaviorPatroller
    elif actor_type == ActorType.INVADER:
        return BehaviorPatroller
    elif actor_type == ActorType.GUARD:
        return BehaviorCivilian
    elif actor_type == ActorType.CARPENTER:
        return BehaviorCivilian
    elif actor_type == ActorType.CIVILIAN:
        return BehaviorCivilian
    elif actor_type == ActorType.MERCHANT:
        return BehaviorCivilian
    elif actor_type == ActorType.MINER:
        return BehaviorCivilian
    elif  actor_type == ActorType.FARMER:
        return BehaviorCivilian
    elif actor_type == ActorType.CASTLE: 
        return BehaviorCivilian
    elif actor_type == ActorType.DUNGEON:
        return BehaviorDungeon
    elif actor_type == ActorType.INN:
        return BehaviorCivilian
    elif actor_type == ActorType.FOREST: 
        return BehaviorCivilian
    elif actor_type == ActorType.FARM: 
        return BehaviorCivilian
    elif actor_type == ActorType.MINE: 
        return BehaviorCivilian
    assert False, "not implemented"

def create_behavior(owner, actor_type):
    behavior_class = get_behavior_class(actor_type)
    return behavior_class(owner)


