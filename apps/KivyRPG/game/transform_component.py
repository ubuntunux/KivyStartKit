from kivy.logger import Logger
from kivy.vector import Vector
from utility.kivy_helper import *
from .constant import *
from .level import LevelManager
from .character_data import *

class TransformComponent():
    def __init__(self, actor, pos, property):
        self.level_manager = LevelManager.instance()
        self.actor = actor
        self.collide_actors = []
        self.is_blocked = False
        self.target_actor = None
        self.target_pos = Vector(0,0)
        self.move_to_target = False
        self.pos = Vector(pos)
        self.prev_pos = Vector(pos)
        self.size = Vector(actor.size)
        self.bound_min = Vector(pos) - self.size * 0.5
        self.bound_max = Vector(pos) + self.size * 0.5
        self.front = Vector(1, 0)
        self.move_direction = Vector(0,0)
        self.property = property
        self.attack_force = Vector(0,0)        
    
    def get_size(self):
        return self.size

    def get_pos(self):
        return self.pos
        
    def get_prev_pos(self):
        return self.prev_pos
          
    def get_front(self):
        return self.front
        
    def set_pos(self, pos):
        self.pos = Vector(pos)
        self.bound_min = self.pos - self.size * 0.5
        self.bound_max = self.pos + self.size * 0.5
    
    def set_move_direction(self, direction):
        self.target_actor = None
        self.move_to_target = False
        self.move_direction = direction
        self.set_front(direction)
    
    def set_front(self, front):
        dir_x = sign(front.x)
        dir_y = sign(front.y)
        if dir_x == 0 and dir_y == 0:
            return
        if abs(front.x) < abs(front.y):
            self.front = Vector(0, dir_y)
        else:
            self.front = Vector(dir_x, 0)
    
    def set_attack_force(self, attack_force):
        self.attack_force = attack_force

    def get_target_actor(self):
        return self.target_actor

    def get_collide_actors(self):
        return self.collide_actors
    
    def trace_actor(self, level_manager, actor):
        if actor:
            self.move_to(actor.get_pos())
        self.target_actor = actor
            
    def collide_actor(self, bound_min, bound_max):
        if bound_max.x < self.bound_min.x or \
            bound_max.y < self.bound_min.y or \
            self.bound_max.x < bound_min.x or \
            self.bound_max.y < bound_min.y:
            return False
        return True

    def move_to(self, target_pos):
        self.target_actor = None
        self.target_pos = target_pos
        self.move_to_target = True
        
    def update_transform(self, dt):
        level_manager = self.actor.level_manager  
        pos = Vector(self.get_pos())
        move_dist = self.property.get_walk_speed() * dt
        was_blocked = self.is_blocked
        self.is_blocked = False

        if self.move_to_target:
            if self.target_actor:
                self.target_pos = self.target_actor.get_pos()
            to_target = self.target_pos - self.pos
            if to_target.length() <= move_dist:
                self.move_direction = Vector(0,0)
                pos = Vector(self.target_pos)
            elif was_blocked:
                self.move_direction = to_target.normalize()
            else:
                is_horizontal = self.front.x != 0
                if is_horizontal:
                    movd_dist = min(abs(to_target.x), move_dist)
                    if abs(to_target.x) <= move_dist:
                        self.move_direction = Vector(0, sign(to_target.y))
                    else:
                        self.move_direction = Vector(sign(to_target.x), 0)
                else:
                    move_dist = min(abs(to_target.y), move_dist)
                    if abs(to_target.y) <= move_dist:
                        self.move_direction = Vector(sign(to_target.x), 0)
                    else:
                        self.move_direction = Vector(0, sign(to_target.y))
            self.set_front(self.move_direction)
        pos.x += self.move_direction.x * move_dist
        pos.y += self.move_direction.y * move_dist 

        self.move_direction = Vector(0,0) # reset
        self.prev_pos = Vector(self.pos)
        bound_min = pos - self.size * 0.5
        bound_max = pos + self.size * 0.5 
        self.collide_actors = level_manager.get_actors_on_tiles(bound_min, bound_max, filters=[self.actor])
        if self.collide_actors:
            for actor in self.collide_actors:
                if ActorCategory.CHARACTER == ActorType.get_actor_category(actor.get_actor_type()):
                    continue
                if not actor.collide_actor(bound_min, bound_max):
                    continue
                dx_l = actor.get_bound_max().x - bound_min.x 
                dx_r = actor.get_bound_min().x - bound_max.x 
                dy_b = actor.get_bound_max().y - bound_min.y 
                dy_t = actor.get_bound_min().y - bound_max.y
                if min(abs(dx_l), abs(dx_r)) < min(abs(dy_b), abs(dy_t)):
                    dx = dx_l if abs(dx_l) < abs(dx_r) else dx_r
                    bound_min.x += dx
                    bound_max.x += dx
                else:
                    dy = dy_b if abs(dy_b) < abs(dy_t) else dy_t
                    bound_min.y += dy
                    bound_max.y += dy
                self.is_blocked = True
            pos = (bound_min + bound_max) * 0.5 
        if self.attack_force.x != 0 or self.attack_force.y != 0:
            pos += self.attack_force * dt
            f = max(0, self.attack_force.length() - 2500.0 * dt)
            self.attack_force = self.attack_force.normalize() * f
        pos = level_manager.clamp_pos_to_level_bound(pos, bound_min, bound_max)
        self.set_pos(pos)
        level_manager.update_actor_on_tile(self.actor)
        return self.prev_pos != self.pos
