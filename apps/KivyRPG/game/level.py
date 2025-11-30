import random
from kivy.graphics import Color, Rectangle
from kivy.graphics.texture import Texture
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from utility.kivy_helper import *
from utility.singleton import SingletonInstance
from .game_resource import GameResourceManager
from .tile import Tile
from .constant import *


class LevelManager(SingletonInstance):
    def __init__(self, app):
        self.level_name = ""
        self.tile_map_widget = None
        self.character_layer = None
        self.effect_layout = None
        self.top_layer = None
        self.scroll_view = None
        self.goal_scroll_x = -1
        self.goal_scroll_y = -1
        self.tiles = []
        self.actors = []
        self.actor_tile_map = {}
        self.app = app
        self.actor_manager = None
        self.num_x = 8
        self.num_y = 8
        self.num_tiles = self.num_x * self.num_y
        self.day = 1
        self.time = 0
        self.tod_update_time = 0.0

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
        tile_pos.x = max(0, min(self.num_x - 1, int(tile_pos[0])))
        tile_pos.y = max(0, min(self.num_y - 1, int(tile_pos[1])))
        return tile_pos
    
    def tile_to_pos(self, tile_pos):
        pos = Vector(
            max(0, min(self.num_x - 1, int(tile_pos[0]))),
            max(0, min(self.num_y - 1, int(tile_pos[1])))
        ) * TILE_SIZE
        pos.x += TILE_WIDTH * 0.5
        pos.y += TILE_HEIGHT * 0.5
        return pos
    
    def index_to_pos(self, index):
        y = int(index / self.num_x)
        x = index - y
        return (x, y)
        
    def pos_to_index(self, pos):
        return int(pos[1] * self.num_x + pos[0])
        
    def get_random_tile_pos(self):
        return (random.randint(1, self.num_x) - 1, random.randint(1, self.num_y) - 1)
    
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
         
    def get_collide_actor(self, bound_min, bound_max, filter=None):
        targets = []
        for target in self.actor_manager.get_actors():
            if target and target is not filter:
                if target.collide_actor(bound_min, bound_max):
                    targets.append(target)
        return targets

    def get_collide_point(self, point, radius=0.0, filters=[]):
        targets = []
        for actor in self.actor_manager.get_actors():
            if actor and actor not in filters:
                if (radius + actor.get_radius()) >= (point.distance(actor.get_pos())):
                    targets.append(actor)
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
        tile_data_set = GameResourceManager.instance().get_tile_data_set(tile_set_name)  
        if tile_data_set:
            tile_data = tile_data_set.get_tile_data(tile_name)
            if tile_data:
                return Tile(tile_data, tile_pos)
      
    def generate_tile_map(self, level_name):
        self.level_name = level_name
        self.num_x = TILE_COUNT
        self.num_y = TILE_COUNT
        self.num_tiles = self.num_x * self.num_y
        
        texture_size = 32
        stride = 4
        row_data_length = texture_size * stride
        width = self.num_x * texture_size
        height = self.num_y * texture_size
        texture_data_size = width * height * stride   
        # create texture
        texture = Texture.create(size=(width, height), colorfmt='rgba')
        color = TILE_GRASS_COLOR1
        data = [color[x % 4] for x in range(texture_data_size)]
        # set layout
        self.tile_map_widget.width = self.num_x * TILE_WIDTH
        self.tile_map_widget.height = self.num_y * TILE_HEIGHT
        self.update_layer_size(self.tile_map_widget.size)
        for y in range(self.num_y):
            tiles = []
            actor_sets = []
            for x in range(self.num_x):
                # create tile
                tile = self.create_tile(
                    tile_set_name="tile_set_00",
                    tile_name="grass",
                    tile_pos=(x, y)
                )
                # blit texture
                if False:
                    pixels = tile.get_pixels()
                    for py in range(texture_size):
                        pixel_offset = py * texture_size * stride
                        data_offset = ((y * texture_size + py) * self.num_x + x) * texture_size * stride
                        data[data_offset: data_offset + row_data_length] = pixels[pixel_offset: pixel_offset + row_data_length] 
                tiles.append(tile)
                actor_sets.append(set())
            self.tiles.append(tiles)
            self.actors.append(actor_sets)
        data = bytes(data)
        texture.blit_buffer(data, colorfmt='rgba', bufferfmt='ubyte')
        with self.tile_map_widget.canvas:
            Rectangle(texture=texture, size=self.tile_map_widget.size)
        
    def open_level(self, level_name):
        self.close_level()
        self.generate_tile_map(level_name)
        
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
            
