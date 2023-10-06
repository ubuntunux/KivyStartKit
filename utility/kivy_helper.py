from functools import partial

from kivy.config import Config
from kivy.graphics import Color, Rectangle
from kivy.uix.scatter import Scatter
from kivy.uix.scatterlayout import ScatterLayout


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
