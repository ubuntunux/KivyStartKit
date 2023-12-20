import math
import numbers
from functools import partial
from kivy.config import Config
from kivy.graphics import Color, Rectangle
from kivy.graphics.transformation import Matrix
from kivy.uix.scatter import Scatter
from kivy.uix.scatterlayout import ScatterLayout
from kivy.vector import Vector
from kivy.core.window import Window
from kivy.logger import Logger


# log
def log_info(text):
    Logger.info(text)

# window
def get_aspect():
    return Window.width / Window.height

def get_is_vertical_window():
    return Window.width < Window.height

# math
def sign(x):
    if 0 < x:
        return 1
    elif x < 0:
        return -1
    return 0
    
def add(A, B):
  if isinstance(B, numbers.Number):
    return [i+B for i in A]
  else:
    return [A[i]+B[i] for i in range(len(A))]

def sub(A, B):
  if isinstance(B, numbers.Number):
    return [i-B for i in A]
  else:
    return [A[i]-B[i] for i in range(len(A))]

def mul(A, B):
  if isinstance(B, numbers.Number):
    return [i*B for i in A]
  else:
    return [A[i]*B[i] for i in range(len(A))]

def div(A, B):
  if isinstance(B, numbers.Number):
    return [i/B if 0 != B else 0.0 for i in A]
  else:
    return [A[i]/B[i] if 0 != B[i] else 0.0 for i in range(len(A))]

def dot(A, B):
 return sum(mul(A, B))
 
def distance(A, B = None):
  temp = sub(A, B) if B else A
  return math.sqrt(sum([i*i for i in temp]))
  
def normalize(A, dist = None):
  if dist == None:
    dist = distance(A)
  return div(A, dist) if dist > 0.0 else mul(A, 0.0)
  
def get_center_pos(pos, size):
    return (pos[0] + size[0] / 2.0, pos[1] + size[1] / 2.0)

def get_pos(center_pos, size):
    return (center_pos[0] - size[0] / 2.0, center_pos[1] - size[1] / 2.0)

def get_size(size, size_ratio):
    return (size[0] * size_ratio[0], size[1] * size_ratio[1])
    
def get_size_x(size, ratio_x):
    return size[0] * ratio_x
    
def get_size_y(size, ratio_y):
    return size[1] * ratio_y
    
def get_size_hint(size, numerator_size):
    return (numerator_size[0] / size[0], numerator_size[1] / size[1])
    
def get_size_hint_x(size, width):
    return width / size[0]
    
def get_size_hint_y(size, height):
    return height / size[1]


# widgets
def get_texture_atlas(texture, texcoord_area=(0,0,1.0,1.0)):
    region = (
        int(texture.width * texcoord_area[0]),
        int(texture.height * texcoord_area[1]),
        int(math.ceil(texture.width * texcoord_area[2])),
        int(math.ceil(texture.height * texcoord_area[3])),
    )
    return texture.get_region(*region)
    
def flip_widget(widget):
    widget.apply_transform(
        Matrix().scale(-1, 1.0, 1.0),
        post_multiply=True,
        anchor=widget.to_local(*widget.center)
    )

# listen to size and position changes
def update_rect(is_relative, rect, instance, value):
    if not is_relative:
        rect.pos = instance.pos
    rect.size = instance.size


def create_dynamic_rect(instance, color):
    is_relative = type(instance) in (Scatter, ScatterLayout)
    with instance.canvas.before:
        Color(*color)
        pos = (0, 0) if is_relative else instance.pos
        instance.rect = Rectangle(pos=pos, size=instance.size, size_hint=(1, 1))
    instance.bind(pos=partial(update_rect, is_relative, instance.rect), size=partial(update_rect, is_relative, instance.rect))


def create_rect(instance, color):
    with instance.canvas.before:
        Color(*color)
        instance.rect = Rectangle(pos=instance.pos, size=instance.size, size_hint=(1, 1))
        
        
def config_set_default(section, option, value):
    if not Config.has_section(section):
        Config.add_section(section)

    if not Config.has_option(section, option):
        Config.set(section, option, value)
