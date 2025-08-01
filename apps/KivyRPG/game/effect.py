from kivy.logger import Logger
from kivy.vector import Vector
from utility.effect import EffectManager
from utility.singleton import SingletonInstance
from utility.kivy_helper import *
from utility.range_variable import RangeVar
from .game_resource import GameResourceManager
from .constant import *


class GameEffectManager(EffectManager):
    def __init__(self, app):
        super(GameEffectManager, self).__init__()
        self.app = app
        self.level_manager = None
        
    def initialize(self, level_manager, effect_layout):
        self.level_manager = level_manager
        super(GameEffectManager, self).initialize(effect_layout)

    def close(self):
        pass
        
    def create_effect(self, effect_name, flip_x=False, flip_y=False, attach_to=None, **kargs):
        game_resource = GameResourceManager.instance()
        effect_data = game_resource.get_effect_data(effect_name)
        if effect_data:
            emitter = self.create_emitter(
                emitter_name=effect_name,
                attach_to=attach_to,
                flip_x=flip_x,
                flip_y=flip_y,
                effect_data=effect_data,
                **kargs
            )
            emitter.play()
            return emitter
        return None