import random
from kivy.vector import Vector
from ..constant import *
from ..character_data import ActorType
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
        self.effect_manager.create_effect(
            effect_name=FX_PICK_ITEM,
            attach_to=self.actor
        )
        if self.actor.actor_type is ActorType.HP:
            item_hp = self.actor.property.property_data.extra_property_data.hp
            actor.add_hp(item_hp)
        return True
