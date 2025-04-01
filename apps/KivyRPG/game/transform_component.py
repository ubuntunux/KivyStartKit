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
        self.tile_pos = Vector(tile_pos)
        self.pos = Vector(pos)
        self.prev_tile_pos = Vector(tile_pos)
        self.prev_pos = Vector(pos)
        self.front = Vector(1, 0)
        self.target_positions = []
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
        
    def get_coverage_tile_pos(self):
        tile_to_actor = self.pos - self.level_manager.tile_to_pos(self.tile_pos)
        return self.level_manager.get_next_tile_pos(self.tile_pos, tile_to_actor)
        
    def set_pos(self, pos):
        self.pos = Vector(pos)
        self.tile_pos = self.level_manager.pos_to_tile(pos)
    
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
        self.target_actor = actor
        if actor is not None:
            self.move_to(level_manager, actor.get_tile_pos())
        
    def move_to(self, level_manager, target_tile_pos):
        target_pos = level_manager.tile_to_pos(target_tile_pos)
        if GRID_BASED_MOVEMENT:
            tile_world_pos = level_manager.tile_to_pos(self.tile_pos)
            to_tile = tile_world_pos - self.pos
            is_vertical_line = abs(to_tile.x) < abs(to_tile.y)
            is_origin = (tile_world_pos == self.pos)
            to_target = target_pos - tile_world_pos
            checked_list = [Vector(self.tile_pos)]
            paths = []
            result = False
            if is_origin:
                result = self.path_find(level_manager, self.tile_pos, target_tile_pos, to_target, checked_list, paths) 
            else:
                next_tile_pos = Vector(self.tile_pos)
                component = 1 if is_vertical_line else 0
                if self.tile_pos[component] != target_tile_pos[component]:
                    next_tile_pos[component] += sign(to_target[component])
                    if level_manager.is_blocked(next_tile_pos, self.actor):
                        next_tile_pos = Vector(self.tile_pos)
                result = self.path_find(level_manager, next_tile_pos, target_tile_pos, to_target, checked_list, paths)
                paths.append(next_tile_pos)     
            self.target_positions = []
            if result:
                for p in paths:
                    self.target_positions.append(level_manager.tile_to_pos(p))
            #Logger.info(("Result: ", self.target_positions))
        
    def update_transform(self, level_manager, dt, force_update=False):   
        if self.target_positions or force_update:
            # calc target pos
            target_pos = self.target_positions[-1] if self.target_positions else Vector(self.pos)
            target_tile_pos = level_manager.pos_to_tile(target_pos)
            to_target = (target_pos - self.pos).normalize()
            move_dist = self.properties.get_walk_speed() * dt
            dist = target_pos.distance(self.pos)
            # calc next pos
            next_pos = self.pos + to_target * move_dist
            tile_world_pos = level_manager.tile_to_pos(self.tile_pos)
            to_tile = (tile_world_pos - self.pos)
            next_to_tile = (tile_world_pos - next_pos)    
            # move 
            self.prev_pos = Vector(self.pos)
            self.prev_tile_pos = Vector(self.tile_pos)
            if dist <= move_dist:
                self.set_pos(target_pos)
                if self.target_positions:
                    self.target_positions.pop()
            else:
                self.set_pos(next_pos)
            self.set_front(to_target)
            # check blocked
            coverage_tile_pos = self.get_coverage_tile_pos()
            if level_manager.is_blocked(coverage_tile_pos, self.actor):
                self.set_pos(self.prev_pos)
                if self.target_positions:
                    target_tile_pos = level_manager.pos_to_tile(self.target_positions[0])
                    self.move_to(level_manager, target_tile_pos)
            # regist actor
            if self.prev_pos != self.pos or force_update:
                level_manager.set_actor(self.actor)
            # trace target  
            if self.target_actor \
                and target_tile_pos != self.target_actor.get_tile_pos() \
                and self.prev_tile_pos != self.tile_pos:
                self.move_to(level_manager, self.target_actor.get_tile_pos())
            return True
        return False