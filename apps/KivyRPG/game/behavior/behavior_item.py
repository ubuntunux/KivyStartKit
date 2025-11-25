import random
from kivy.vector import Vector
from ..effect import GameEffectManager
from ..constant import *
from .behavior import *

class BehaviorItem(Behavior):
    def on_collide_actor(self, other_actor):
        if other_actor.get_is_player():
            effect_manager = GameEffectManager.instance()
            effect_manager.create_effect(
                effect_name=FX_PICK_ITEM,
                attach_to=self.actor
            )
            gold = self.actor.property.extra_property.get_gold()
            other_actor.property.add_gold(gold)
            self.actor.set_dead()
