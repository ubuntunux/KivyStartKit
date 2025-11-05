from .behavior import *
from .behavior_patroller import *
from .behavior_player import *
from .behavior_dungeon import *

def get_behavior_class(actor_type):
    if actor_type == ActorType.PLAYER:
        return BehaviorPlayer
    elif actor_type == ActorType.PATROLLER:
        return BehaviorPatroller
    elif actor_type == ActorType.DUNGEON:
        return BehaviorDungeon
    return BehaviorPatroller
    assert False, "not implemented"

def create_behavior(cls, owner, actor_type):
    behavior_class = get_behavior_class(actor_type)
    return behavior_class(owner)


