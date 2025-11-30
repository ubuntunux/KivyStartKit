import random
from kivy.vector import Vector
from ..constant import *
from .behavior import *

class BehaviorGold(Behavior):
    def on_collide_actor(self, other_actor):
        if other_actor.get_is_player():
            self.effect_manager.create_effect(
                effect_name=FX_PICK_ITEM,
                attach_to=self.actor
            )
            gold = self.actor.property.extra_property.get_gold()
            other_actor.add_gold(gold)
            self.actor.set_dead()

