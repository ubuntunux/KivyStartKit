from kivy.logger import Logger
from kivy.vector import Vector
from utility.kivy_helper import *
from .constant import *
from .level import LevelManager
    
class TransformComponent():
    def __init__(self, actor, pos, properties):
        self.level_manager = LevelManager.instance()
        self.actor = actor
        self.target_actor = None
        self.target_pos = Vector(0,0)
        self.move_to_target = False
        self.pos = Vector(pos)
        self.prev_pos = Vector(pos)
        self.front = Vector(1, 0)
        self.move_direction = Vector(0,0)
        self.properties = properties
        
    def get_pos(self):
        return self.pos
        
    def get_prev_pos(self):
        return self.prev_pos
          
    def get_front(self):
        return self.front
        
    def set_pos(self, pos):
        self.pos = Vector(pos)
    
    def set_move_direction(self, direction):
        self.move_direction = direction
        self.set_front(direction)
    
    def set_front(self, front):
        dir_x = sign(front.x)
        dir_y = sign(front.y)
        if abs(front.x) < abs(front.y):
            self.front = Vector(0, dir_y)
        else:
            self.front = Vector(dir_x, 0)
        
    def trace_actor(self, level_manager, actor):
        if actor:
            self.move_to(actor.get_pos())
        self.target_actor = actor
            
    def move_to(self, target_pos):
        self.target_actor = None
        self.target_pos = target_pos
        self.move_to_target = True
        
    def update_transform(self, dt):
        level_manager = self.actor.level_manager  
        pos = Vector(self.get_pos())
        move_dist = self.properties.get_walk_speed() * dt
        if self.move_to_target:
            if self.target_actor:
                self.target_pos = self.target_actor.get_pos()
            to_target = self.target_pos - self.pos
            is_horizontal = self.front.x != 0
            if is_horizontal:
                pos.x += sign(to_target.x) * min(abs(to_target.x), move_dist)
                self.set_front(Vector(sign(to_target.x), 0))
                if abs(to_target.x) <= move_dist:
                    self.set_front(Vector(0, sign(to_target.y)))
            else:
                pos.y += sign(to_target.y) * min(abs(to_target.y), move_dist)
                self.set_front(Vector(0, sign(to_target.y)))
                if abs(to_target.y) <= move_dist:
                    self.set_front(Vector(sign(to_target.x), 0))
        else:
            pos.x += self.move_direction.x * move_dist
            pos.y += self.move_direction.y * move_dist 
        self.move_direction = Vector(0,0) # reset
        self.prev_pos = Vector(self.pos)
        self.pos = pos
        return self.prev_pos != self.pos