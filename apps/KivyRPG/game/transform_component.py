from kivy.logger import Logger
from kivy.vector import Vector
from utility.kivy_helper import *
from .constant import *
from .level import LevelManager
    
class TransformComponent():
    def __init__(self, actor, tile_pos, pos, properties):
        self.level_manager = LevelManager.instance()
        self.actor = actor
        self.target_actor = None
        self.target_pos = Vector(0,0)
        self.move_to_target = False
        self.tile_pos = Vector(tile_pos)
        self.pos = Vector(pos)
        self.prev_tile_pos = Vector(tile_pos)
        self.prev_pos = Vector(pos)
        self.front = Vector(1, 0)
        self.move_direction = Vector(0,0)
        self.properties = properties
        
    def get_pos(self):
        return self.pos
        
    def get_tile_pos(self):
        return self.tile_pos
        
    def get_prev_pos(self):
        return self.prev_pos
        
    def get_prev_tile_pos(self):
        return self.prev_tile_pos
        
    def get_front(self):
        return self.front
        
    def set_pos(self, pos):
        self.pos = Vector(pos)
        self.tile_pos = self.level_manager.pos_to_tile(pos)
    
    def set_move_direction(self, direction):
        self.move_direction = direction
        self.set_front(direction)
    
    def set_front(self, front):
        dir_x = sign(front.x)
        dir_y = sign(front.y)
        if abs(dir_x) < abs(dir_y):
            self.front = Vector(0, dir_y)
        elif abs(dir_y) < abs(dir_x):
            self.front = Vector(dir_x, 0)
            
    def path_find(self, level_manager, tile_pos, target_tile_pos, target_dir, checked_list, paths, depth=0):
        if tile_pos == target_tile_pos:
            paths = [Vector(target_tile_pos)]
            return True
        #Logger.info((depth, "tile:", tile_pos, "target: ", target_tile_pos, "dir: ", target_dir))
        if 100 < depth:
            return False
        is_horizontal = abs(target_dir.y) < abs(target_dir.x)
        sign_x = sign(target_dir.x)
        sign_y = sign(target_dir.y)
        if sign_x == 0:
            sign_x = 1
        if sign_y == 0:
            sign_y = 1
        a = level_manager.get_next_tile_pos(tile_pos, Vector(sign_x, 0))
        b = level_manager.get_next_tile_pos(tile_pos, Vector(0, sign_y))
        c = level_manager.get_next_tile_pos(tile_pos, Vector(-sign_x,0))
        d = level_manager.get_next_tile_pos(tile_pos, Vector(0, -sign_y))
        points = sorted([a,b,c,d], key=lambda p: p.distance(target_tile_pos))
        #Logger.info((depth, "points: ", points))
        for p in points:
            if p == target_tile_pos:
                paths.append(p)
                #Logger.info((depth, "arrive", p))
                return True
            is_in_checked_list = p in checked_list
            checked_list.append(p)
            if is_in_checked_list \
                or level_manager.is_blocked(p, self.actor) \
                or not level_manager.is_in_level(p):
                continue
            #Logger.info((">> next_tile_pos: ", p))
            next_target_dir = (target_tile_pos - p)
            find = self.path_find(level_manager, p, target_tile_pos, next_target_dir, checked_list, paths, depth+1)
            if find:
                paths.append(p)
                #Logger.info((depth, "find", p))
                return True
        #Logger.info((depth, "not found"))
        return False
        
    def trace_actor(self, level_manager, actor):
        if actor:
            self.move_to(actor.get_pos())
        self.target_actor = actor
            
    def move_to(self, target_pos):
        self.target_actor = None
        self.target_pos = target_pos
        self.move_to_target = True
        
    def update_transform(self, level_manager, dt):   
        pos = Vector(self.get_pos())
        move_dist = self.properties.get_walk_speed() * dt
        if self.move_to_target:
            if self.target_actor:
                self.move_to(self.target_actor.get_pos())
            
            target_tile_pos = level_manager.pos_to_tile(self.target_pos)
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
        self.prev_tile_pos = self.tile_pos
        self.tile_pos = self.level_manager.pos_to_tile(self.pos)
        return True