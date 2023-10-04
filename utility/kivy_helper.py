from functools import partial

from kivy.config import Config
from kivy.graphics import Color, Rectangle
from kivy.uix.scatter import Scatter
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition

from utility.singleton import SingletonInstane


class ScreenHelper(SingletonInstane):
    def __init__(self, *args, **kwargs):
        self.name = "ScreenManager"
        self.screen_manager = ScreenManager(*args, **kwargs)
        self.transition = WipeTransition()
        self.empty_screen = Screen(name="empty screen")
        self.add_screen(self.empty_screen)
        self.current_screen(self.empty_screen)

    def prev_screen(self):
        prev_screen = self.screen_manager.previous()
        if prev_screen:
            self.screen_manager.current = prev_screen

    def add_screen(self, screen):
        if screen.name not in self.screen_manager.screen_names:
            self.screen_manager.add_widget(screen)

    def current_screen(self, screen):
        if True or self.screen_manager.current != screen.name and self.screen_manager.has_screen(screen.name):
            self.screen_manager.current = screen.name

    def remove_screen(self, screen):
        if screen.name in self.screen_manager.screen_names:
            self.screen_manager.remove_widget(screen)
            self.prev_screen()

    def get_current_screen(self):
        return self.screen_manager.current


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
