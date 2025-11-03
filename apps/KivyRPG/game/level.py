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
        self.app = app
        self.actor_manager = None
        self.num_x = 8
        self.num_y = 8
        self.num_tiles = self.num_x * self.num_y
        
    def initialize(self, parent_widget, actor_manager, fx_manager):
        self.actor_manager = actor_manager
        self.fx_manager = fx_manager
        self.tile_map_widget = Widget(size_hint=(None, None))
        self.tile_map_widget.bind(on_touch_down=self.on_touch_down)
        self.character_layer = Widget(size_hint=(None, None))
        self.effect_layer = Widget(size_hint=(None, None))
        self.top_layer = Widget(size_hint=(None, None))
        self.scroll_view = ScrollView(do_scroll=False, size_hint=(1,1))
        # link
        self.top_layer.add_widget(self.tile_map_widget)
        self.top_layer.add_widget(self.character_layer)
        self.top_layer.add_widget(self.effect_layer)
        self.scroll_view.add_widget(self.top_layer)
        parent_widget.add_widget(self.scroll_view)
        self.update_layer_size(self.top_layer.size)

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
        tile_pos.x = int(tile_pos.x)
        tile_pos.y = int(tile_pos.y)
        return tile_pos
    
    def tile_to_pos(self, tile_pos):
        pos = Vector(tile_pos) * TILE_SIZE
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
        
    def clamp_pos_to_level_bound(self, pos, bound_min, bound_max):
        if bound_min.x < 0:
           pos.x -= bound_min.x
        elif self.tile_map_widget.width < bound_max.x:
           pos.x += self.tile_map_widget.width - bound_max.x 
        if bound_min.y < 0:
           pos.y -= bound_min.y
        elif self.tile_map_widget.height < bound_max.y:
           pos.y += self.tile_map_widget.height - bound_max.y
        return pos

    def is_in_level(self, actor):
        return 0 <= actor.get_bound_min().x and \
            actor.get_bound_max().x < self.tile_map_widget.width and \
            0 <= actor.get_bound_min().y and \
            actor.get_bound_max().y < self.tile_map_widget.height
        
    def is_blocked(self, pos, filter_actor=None):
        actor = self.get_actor(pos)
        return actor is not filter_actor and actor is not None
    
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
            self.character_layer.remove_widget(actor)
    
    def add_actor(self, actor):
        if actor and actor.parent is not self.character_layer:
            self.character_layer.add_widget(actor)
            
    def update_layer_size(self, layer_size):
        self.top_layer.size = layer_size
        self.effect_layer.size = layer_size
        self.character_layer.size = layer_size
        
    def create_tile(self, tile_set_name, tile_name, tile_pos):
        tile_data_set = GameResourceManager.instance().get_tile_data_set(tile_set_name)  
        if tile_data_set:
            tile_data = tile_data_set.get_tile_data(tile_name)
            if tile_data:
                return Tile(tile_data, tile_pos)
      
    def generate_tile_map(self, level_name):
        self.level_name = level_name
        self.num_x = 30
        self.num_y = 30
        self.num_tiles = self.num_x * self.num_y
        
        texture_size = 32
        stride = 4
        row_data_length = texture_size * stride
        width = self.num_x * texture_size
        height = self.num_y * texture_size
        texture_data_size = width * height * stride   
        # create texture
        texture = Texture.create(size=(width, height), colorfmt='rgba')
        data = ([int(255) for x in range(texture_data_size)])
        # set layout
        self.tile_map_widget.width = self.num_x * TILE_WIDTH
        self.tile_map_widget.height = self.num_y * TILE_HEIGHT
        self.update_layer_size(self.tile_map_widget.size)
        for y in range(self.num_y):
            tiles = []
            for x in range(self.num_x):
                # create tile
                tile = self.create_tile(
                    tile_set_name="tile_set_00",
                    tile_name="grass",
                    tile_pos=(x, y)
                )
                # blit texture
                pixels = tile.get_pixels()
                for py in range(texture_size):
                    pixel_offset = py * texture_size * stride
                    data_offset = ((y * texture_size + py) * self.num_x + x) * texture_size * stride
                    data[data_offset: data_offset + row_data_length] = pixels[pixel_offset: pixel_offset + row_data_length] 
                tiles.append(tile)
            self.tiles.append(tiles)
        data = bytes(data)
        texture.blit_buffer(data, colorfmt='rgba', bufferfmt='ubyte')
        with self.tile_map_widget.canvas:
            Rectangle(texture=texture, size=self.tile_map_widget.size)
        
    def open_level(self, level_name):
        self.close_level()
        self.generate_tile_map(level_name)
        self.actor_manager.reset_actors()
        
    def close_level(self):
        self.clear_level_actors()
        self.tiles.clear()
        self.tile_map_widget.clear_widgets()
        self.actor_manager.clear_actors()

    def clear_level_actors(self):
        self.character_layer.clear_widgets()
    
    def reset_level(self):
        self.actor_manager.reset_actors()
        
    def callback_reset_level(self, inst):
        self.reset_level()
        
    def update(self, dt):
        player = self.actor_manager.get_player()
        if player and player.is_alive():
            pos = player.get_pos()
            half_window = mul(Window.size, 0.5)
            scroll_x = (pos[0] - half_window[0]) / (self.tile_map_widget.width - 1.0 - Window.size[0])
            scroll_y = (pos[1] - half_window[1]) / (self.tile_map_widget.height - 1.0 - Window.size[1])
            self.scroll_view.scroll_x = min(1.0, max(0.0, scroll_x))
            self.scroll_view.scroll_y = min(1.0, max(0.0, scroll_y))
            
