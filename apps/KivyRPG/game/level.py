import random
import numpy as np
from kivy.graphics import Color, Rectangle
from kivy.graphics.texture import Texture
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from utility.kivy_helper import *
from utility.singleton import SingletonInstance
from .character_data import *
from .game_resource import GameResourceManager
from .tile import Tile
from .level_data import LevelData
from .constant import *

USE_TILE_TEXTURE = True

class Level:
    pass

class LevelManager(SingletonInstance):
    def __init__(self, app):
        self.tile_map_widget = None
        self.character_layer = None
        self.effect_layout = None
        self.top_layer = None
        self.scroll_view = None
        self.goal_scroll_x = -1
        self.goal_scroll_y = -1
        self.level_data = None
        self.tiles = []
        self.actors = []
        self.actor_tile_map = {}
        self.app = app
        self.actor_manager = None
        self.num_tiles = 0 
        self.day = 1
        self.time = 0
        self.tod_update_time = 0.0
        self.main_stage = None

    def initialize(self, parent_widget, actor_manager, fx_manager):
        self.actor_manager = actor_manager
        self.fx_manager = fx_manager
        self.tile_map_widget = Widget(size_hint=(None, None))
        self.tile_map_widget.bind(on_touch_down=self.on_touch_down)
        self.character_layer = Widget(size_hint=(None, None))
        self.effect_layer = Widget(size_hint=(None, None))
        self.tod_layer = Widget(size_hint=(None, None))
        create_dynamic_rect(self.tod_layer, (0,0,0,0))
        self.top_layer = Widget(size_hint=(None, None))
        self.scroll_view = ScrollView(do_scroll=False, size_hint=(1,1))
        # link
        self.top_layer.add_widget(self.tile_map_widget)
        self.top_layer.add_widget(self.character_layer)
        self.top_layer.add_widget(self.effect_layer)
        self.top_layer.add_widget(self.tod_layer)
        self.scroll_view.add_widget(self.top_layer)
        parent_widget.add_widget(self.scroll_view)
        self.update_layer_size(self.top_layer.size)

        self.day = 1
        self.set_tod(MORNING_TOD)

    def close(self):
        pass
        
    def on_touch_down(self, inst, touch):
        if inst.collide_point(*touch.pos):
            self.actor_manager.callback_touch(inst, touch)
            return True
        return False
    
    def get_character_layout(self):
        return self.character_layer
        
    def get_effect_layout(self):
        return self.effect_layer
        
    def pos_to_tile(self, pos):
        tile_pos = Vector(pos) / TILE_SIZE
        tile_pos.x = max(0, min(self.level_data.num_x - 1, int(tile_pos[0])))
        tile_pos.y = max(0, min(self.level_data.num_y - 1, int(tile_pos[1])))
        return tile_pos
    
    def tile_to_pos(self, tile_pos):
        pos = Vector(
            max(0, min(self.level_data.num_x - 1, int(tile_pos[0]))),
            max(0, min(self.level_data.num_y - 1, int(tile_pos[1])))
        ) * TILE_SIZE
        pos.x += TILE_WIDTH * 0.5
        pos.y += TILE_HEIGHT * 0.5
        return pos
    
    def index_to_pos(self, index):
        y = int(index / self.level_data.num_x)
        x = index - y
        return (x, y)
        
    def pos_to_index(self, pos):
        return int(pos[1] * self.level_data.num_x + pos[0])
        
    def get_random_tile_pos(self):
        return (random.randint(1, self.level_data.num_x) - 1, random.randint(1, self.level_data.num_y) - 1)
    
    def get_random_pos(self):
        return self.tile_to_pos(self.get_random_tile_pos())

    def get_level_center(self):
        return Vector(self.tile_map_widget.center)
        
    def clamp_pos_to_level_bound(self, pos, bound_min, bound_max):
        offset = Vector(0,0)
        if bound_min.x < 0:
           offset.x = -bound_min.x
        elif self.tile_map_widget.width < bound_max.x:
           offset.x = self.tile_map_widget.width - bound_max.x 
        if bound_min.y < 0:
           offset.y = -bound_min.y
        elif self.tile_map_widget.height < bound_max.y:
           offset.y = self.tile_map_widget.height - bound_max.y
        return pos + offset

    def is_in_level(self, actor):
        return 0 <= actor.get_bound_min().x and \
            actor.get_bound_max().x < self.tile_map_widget.width and \
            0 <= actor.get_bound_min().y and \
            actor.get_bound_max().y < self.tile_map_widget.height
        
    def is_blocked(self, pos, filter_actor=None):
        actor = self.get_actor(pos)
        return actor is not filter_actor and actor is not None
    
    def get_actors_on_tiles_with_actor(self, actor):
        return self.get_actors_on_tiles(
            actor.get_bound_min(),
            actor.get_bound_max(),
            [actor])

    def get_actors_on_tiles(self, bound_min, bound_max, filters=[]):
        actors = set()
        tile_pos_min = self.pos_to_tile(bound_min)
        tile_pos_max = self.pos_to_tile(bound_max)
        for y in range(tile_pos_min.y, tile_pos_max.y + 1):
            for x in range(tile_pos_min.x, tile_pos_max.x + 1):
                actors.update(self.actors[y][x])
        for filter in filters:
            if filter and filter in actors:
                actors.remove(filter)
        #self.app.debug_print(f'{bound_min, bound_max, tile_pos_min, tile_pos_max, [x.name for x in actors]}')
        return actors

    def update_actor_on_tile(self, actor):
        self.unregister_actor(actor)
        tile_pos_min = self.pos_to_tile(actor.get_bound_min())
        tile_pos_max = self.pos_to_tile(actor.get_bound_max())
        for y in range(tile_pos_min.y, tile_pos_max.y + 1):
            for x in range(tile_pos_min.x, tile_pos_max.x + 1):
                self.actors[y][x].add(actor)
                self.actor_tile_map[actor] = (tile_pos_min, tile_pos_max)

    def unregister_actor(self, actor):
        (tile_pos_min, tile_pos_max) = self.actor_tile_map.get(actor, (None, None))
        if tile_pos_min and tile_pos_max:
            for y in range(tile_pos_min.y, tile_pos_max.y + 1):
                for x in range(tile_pos_min.x, tile_pos_max.x + 1):
                    self.actors[y][x].remove(actor)

    def get_nearest_enemy(self, actor, bound_min, bound_max):
        nearest_target = None
        min_dist = -1.0
        center = (bound_min + bound_max) * 0.5
        for target in self.get_actors_on_tiles(bound_min, bound_max):
            if actor.is_attackable_target(target) and target.collide_actor(bound_min, bound_max):
                to_enemy = center - target.get_pos()
                dist = to_enemy.dot(to_enemy)
                if dist < min_dist or min_dist < 0.0:
                    min_dist = dist
                    nearest_target = target 
        return nearest_target

    def get_collide_enemy(self, actor, bound_min, bound_max):
        targets = []
        for target in self.get_actors_on_tiles(bound_min, bound_max):
            if actor.is_attackable_target(target) and target.collide_actor(bound_min, bound_max):
                targets.append(target)
        return targets

    def get_collide_actor(self, bound_min, bound_max, filter=None):
        targets = []
        for target in self.get_actors_on_tiles(bound_min, bound_max):
            if target and target is not filter:
                if target.collide_actor(bound_min, bound_max):
                    targets.append(target)
        return targets

    def get_collide_point(self, point, radius=0.0, filters=[]):
        bound_min = point - Vector(radius, radius)
        bound_max = point + Vector(radius, radius)
        targets = []
        for target in self.get_actors_on_tiles(bound_min, bound_max, filters):
            if (radius + target.get_radius()) >= (point.distance(target.get_pos())):
                targets.append(target)
        return targets
                
    def pop_actor(self, actor):
        if actor and actor.parent is self.character_layer:
            self.unregister_actor(actor)
            self.character_layer.remove_widget(actor)
    
    def add_actor(self, actor, layer_index=0):
        if actor and actor.parent is not self.character_layer:
            self.character_layer.add_widget(actor, layer_index)
            self.update_actor_on_tile(actor)
            
    def update_layer_size(self, layer_size):
        self.top_layer.size = layer_size
        self.effect_layer.size = layer_size
        self.character_layer.size = layer_size
        self.tod_layer.size = layer_size

    def create_tile(self, tile_set_name, tile_name, tile_pos):
        tile_data = None
        tile_data_set = GameResourceManager.instance().get_tile_data_set(tile_set_name)  
        if tile_data_set:
            tile_data = tile_data_set.get_tile_data(tile_name)
        return Tile(tile_data_set, tile_data, tile_pos)
      
    def generate_tile_map(self):
        self.day = self.level_data.day
        self.set_tod(self.level_data.tod)
        self.num_tiles = self.level_data.num_x * self.level_data.num_y
        
        # set layout
        self.tile_map_widget.width = self.level_data.num_x * TILE_WIDTH
        self.tile_map_widget.height = self.level_data.num_y * TILE_HEIGHT
        self.update_layer_size(self.tile_map_widget.size)
        create_dynamic_rect(self.tile_map_widget, self.level_data.level_color)

        for y in range(self.level_data.num_y):
            tiles = []
            actor_sets = []
            for x in range(self.level_data.num_x):
                # create tile
                tile_create_info = self.level_data.tile_create_infos[y * self.level_data.num_x + x]
                tile = self.create_tile(
                    tile_set_name=tile_create_info[0],
                    tile_name=tile_create_info[1],
                    tile_pos=(x, y)
                )
                
                if tile.tile_data:
                    image = Image(
                        texture=tile.tile_data.texture,
                        allow_stretch=True,
                        keep_ratio=False,
                        size_hint=(None, None),
                        size=(TILE_WIDTH, TILE_HEIGHT),
                        pos=(x * TILE_WIDTH, y * TILE_HEIGHT)
                    )
                    self.tile_map_widget.add_widget(image)

                tiles.append(tile)
                actor_sets.append(set())
            self.tiles.append(tiles)
            self.actors.append(actor_sets)

    def new_level(self, level_name):
        self.close_level()
        self.level_data = LevelData(GameResourceManager.instance(), level_name)
        GameResourceManager.instance().register_level_data(level_name, self.level_data)  
        self.generate_tile_map()

    def load_level(self, level_name):
        self.close_level()
        self.level_data = GameResourceManager.instance().get_level_data(level_name)  
        self.generate_tile_map()
        return self.level_data
       
    def save_level(self):
        level_data_info = {
            'level_name': self.level_data.level_name,
            'level_color': self.level_data.level_color,
            'num_x': self.level_data.num_x,
            'num_y': self.level_data.num_y,
            'tile_create_infos': [tile.get_tile_create_info() for tiles in self.tiles for tile in tiles],
            'tod': self.get_tod(),
            'day': self.day,
            'actors': self.actor_manager.get_save_data()
        }
        return level_data_info

    def close_level(self):
        self.character_layer.clear_widgets()
        self.actors.clear()
        self.actor_tile_map.clear()
        self.tiles.clear()
        self.tile_map_widget.clear_widgets()
    
    def get_day(self):
        return self.day

    def get_time(self):
        return self.time

    def get_tod(self):
        return self.time / 3600.0
    
    def set_tod(self, tod):
        self.time = tod * 3600.0

    def callback_night_time(self, *args):
        tod = self.get_tod()
        if tod < NIGHT_TOD_END or NIGHT_TOD_START < tod:
            self.set_tod(MORNING_TOD)
        else:
            self.set_tod(NIGHT_TOD_START)

    def update_tod(self, dt):
        self.tod_update_time += dt
        self.time += dt * TIME_OF_DAY_SPEED
        tod = self.get_tod()
        if DAY_TIME <= self.time:
            self.time = self.time % DAY_TIME
            self.day += 1
        if 0.1 < self.tod_update_time:
            self.tod_update_time = 0.0
            night = [0.0, 0.0, 0.2, 0.6]
            dawn = [0.1, 0.0, 0.0, 0.6]
            noon = [0.3, 0.3, 0.3, 0.0]
            color0 = [0,0,0,0]
            color1 = [0,0,0,0]
            t = 0.0
            if 4.0 <= tod and tod <= 6.0:
                t = (tod - 4.0) / 2.0
                color0 = night
                color1 = dawn
            elif 6.0 <= tod and tod <= 8.0:
                t = (tod - 6.0) / 2.0
                color0 = dawn
                color1 = noon
            elif 8.0 <= tod and tod <= 16.0:
                t = (tod - 8.0) / 8.0
                color0 = noon
                color1 = noon
            elif 16.0 <= tod and tod <= 20.0:
                t = (tod - 16.0) / 4.0
                color0 = noon
                color1 = night
            else:
                color0 = night
                color1 = night
            
            inv_t = 1.0 - t
            self.tod_layer.color.r = color0[0] * inv_t + color1[0] * t 
            self.tod_layer.color.g = color0[1] * inv_t + color1[1] * t 
            self.tod_layer.color.b = color0[2] * inv_t + color1[2] * t 
            self.tod_layer.color.a = color0[3] * inv_t + color1[3] * t 

    def update(self, dt):
        self.update_tod(dt)

        player = self.actor_manager.get_player()
        if player and player.is_alive():
            pos = player.get_pos()
            half_window = mul(Window.size, 0.5)
            scroll_x = (pos[0] - half_window[0]) / (self.tile_map_widget.width - 1.0 - Window.size[0])
            scroll_y = (pos[1] - half_window[1]) / (self.tile_map_widget.height - 1.0 - Window.size[1])
            self.scroll_view.scroll_x = min(1.0, max(0.0, scroll_x))
            self.scroll_view.scroll_y = min(1.0, max(0.0, scroll_y))
            
