import random
from kivy.vector import Vector
from ..constant import *
from .behavior import *

class BehaviorInn(Behavior):
    def on_interaction(self, actor):
       self.game_manager.set_trade_actor(self.actor)
