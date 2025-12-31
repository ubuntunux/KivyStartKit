from .character_data import ActorType

class Reward:
    def __init__(self, item_data_name):
        self.item_data_name = item_data_name

def get_reward_monster(player, actor):
    reward_data = [
        Reward('items/gold_a'),
        Reward('items/gold_b'),
        Reward('items/gold_c'),
        Reward('items/gold_d'),
        Reward('items/weapon_axe'),
    ]
    return reward_data

def get_reward_forest(player, actor):
    reward_data = [
        Reward('items/wood_a'),
    ]
    return reward_data
 
def get_reward_farm(player, actor):
    reward_data = [
        Reward('items/grain_a'),
    ]
    return reward_data
         
def get_reward_mine(player, actor):
    reward_data = [
        Reward('items/ore_a'),
    ]
    return reward_data
 
__reward_map__ = {
    ActorType.PATROLLER: get_reward_monster,
    ActorType.FOREST: get_reward_forest,
    ActorType.FARM: get_reward_farm,
    ActorType.MINE: get_reward_mine,
}

def get_rewards(actor_manager, player, actor):
    if actor.is_player:
        return []
    func_reward = __reward_map__.get(actor.get_actor_type(), get_reward_monster)
    reward_data = func_reward(player, actor)
    rewards = []
    for reward in reward_data:
        item_actor = actor_manager.spawn_actor(reward.item_data_name)
        rewards.append(item_actor)
    return rewards
