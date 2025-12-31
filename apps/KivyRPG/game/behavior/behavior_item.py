import random
from kivy.vector import Vector
from ..constant import *
from ..character_data import ActorType
from ..game_resource import GameResourceManager
from .behavior import *

class BehaviorItem(Behavior):
    def on_collide_actor(self, other_actor):
        if other_actor.get_is_player():
            self.effect_manager.create_effect(
                effect_name=FX_PICK_ITEM,
                attach_to=self.actor
            )
            other_actor.add_item(self.actor.data)
            self.actor.set_dead()

    def on_interaction(self, actor):
        resource_manager = GameResourceManager.instance()
        is_interaction = False
        if self.actor.actor_type is ActorType.HP:
            item_hp = self.actor.property.property_data.extra_property_data.hp
            actor.add_hp(item_hp)
            is_interaction = True
        elif self.actor.actor_type is ActorType.WEAPON:
            weapon_data_name = self.actor.property.property_data.extra_property_data.weapon_data
            weapon_data = resource_manager.get_weapon_data(weapon_data_name)
            actor.set_weapon(weapon_data)
            is_interaction = True

        if is_interaction:
            self.effect_manager.create_effect(
                effect_name=FX_PICK_ITEM,
                attach_to=self.actor
            )
        return is_interaction

    def update_behavior(self, dt):
        super().update_behavior(dt)
        lifetime = self.actor.get_extra_property().update_lifetime(dt)
        if lifetime <= 0:
            self.actor.set_dead()
