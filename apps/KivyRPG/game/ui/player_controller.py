from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scatter import Scatter
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.utils import platform 
from ..actor import ActorManager
from ..game_resource import GameResourceManager
from ..constant import *

class PlayerController:
    def __init__(self, app, game_controller):
        self.app = app
        self.game_controller = game_controller
        self.button_active_opacity = 0.5
        self.button_deactive_opacity = 0.2
        self.button_size = dp(70)
        self.bound_size = self.button_size * 2.0
        self.bound_offset = dp(30)
        self.dead_zone_size = dp(10)
        self.button_neutral_pos = (
            self.bound_offset + self.bound_size * 0.5,
            self.bound_offset + self.bound_size * 0.5
        )
        self.button = None
        self.button_color = Color(1,1,1,1)
        self.touch_id = None
        if platform != 'android':
            self.text_input = TextInput()
            self.keyboard = Window.request_keyboard(self.keyboard_closed, self.text_input)
            self.keyboard.bind(on_key_down=self.on_key_down)
            self.keyboard.bind(on_key_up=self.on_key_up)
        self.key_pressed = {}
        self.key_hold = {}
        self.key_released = {}
        
    def initialize(self, controller_layer):
        actor_manager = ActorManager.instance()
        resource_manager = GameResourceManager.instance()
        # button bound
        self.bound = Scatter(
            do_rotation=False,
            do_scale=False,
            do_translation=False,
            pos=(self.bound_offset, self.bound_offset),
            size_hint=(None, None),
            size=(self.bound_size, self.bound_size)
        )
        self.bound.bind(
            on_touch_down=self.on_touch_down,
            on_touch_move=self.on_touch_move,
            on_touch_up=self.on_touch_up
        )
        with self.bound.canvas:
            Color(1,1,1, self.button_deactive_opacity)
            Rectangle(size=self.bound.size)
        
        # button
        button_size = (self.button_size, self.button_size)
        self.button = Scatter(
            do_rotation=False,
            do_scale=False,
            do_translation=False,
            pos=mul(sub(self.bound.size, button_size), 0.5),
            size_hint=(None, None),
            size=button_size
        )
        with self.button.canvas:
            self.button_color = Color(1,1,1, self.button_deactive_opacity)
            Rectangle(size=self.button.size)
        
        # button image
        add_image = True
        if add_image:
            point = resource_manager.get_image("ui/point")
            img_pos = mul(self.button.size, -0.5)
            img_size = mul(self.button.size, 2.0)
            img = Image(texture=point.texture, pos=img_pos, size=img_size, keep_ratio=False, allow_stretch=True)
            self.button.add_widget(img)      
        self.bound.add_widget(self.button)
        controller_layer.add_widget(self.bound)

        # attack button
        layout = BoxLayout(pos_hint={"right":1}, size_hint=(None, None), size=(dp(180), dp(180)), padding=dp(30)) 
        btn = Button(text="Attack", size_hint=(1,1), opacity=0.5)
        btn.bind(on_press=actor_manager.callback_attack)
        layout.add_widget(btn)
        controller_layer.add_widget(layout)

    def close(self):
        self.keyboard_closed()

    def on_resize(self, window, width, height):
        pass

    def keyboard_closed(self):
        if platform != 'android':
            if self.keyboard:
                self.keyboard.unbind(on_key_down=self.on_key_down)
                self.keyboard = None
        self.key_pressed = {}
        self.key_hold = {}
        self.key_released = {}

    def on_key_down(self, keyboard, keycode, text, modifiers):
        key_value = keycode[0]
        self.key_pressed[key_value] = True
        self.key_hold[key_value] = True
        self.key_released[key_value] = False

    def on_key_up(self, keyboard, keycode):
        key_value = keycode[0]
        self.key_pressed[key_value] = False
        self.key_hold[key_value] = False
        self.key_released[key_value] = True

    def update_key_pressed(self):
        for key, pressed in self.key_pressed.items():
            if pressed:
                self.key_pressed[key] = False
                self.key_hold[key] = True
        
    def on_touch_down(self, inst, touch):
        if self.touch_id is None and inst.collide_point(*touch.pos):
            self.set_button_center(touch.pos)
            self.button_color.a = self.button_active_opacity
            self.touch_id = touch.id
            return True
        return False
    
    def on_touch_move(self, inst, touch):
        if self.touch_id == touch.id:
            self.set_button_center(touch.pos)
            return True
        return False
        
    def on_touch_up(self, inst, touch):
        if self.touch_id == touch.id:
            self.set_button_center(self.button_neutral_pos)
            self.button_color.a = self.button_deactive_opacity
            self.touch_id = None
            return True
        return False
    
    def set_button_center(self, pos):
        new_pos = sub(self.bound.to_local(*pos), self.button_size * 0.5)
        self.button.pos = (
            max(0, min(self.bound.size[0] - self.button.size[0], new_pos[0])),
            max(0, min(self.bound.size[1] - self.button.size[1], new_pos[1]))
        )
        
    def update(self, dt):
        self.update_key_pressed()

        if self.touch_id is not None:
            diff = sub(add(self.bound.pos, self.button.center), self.button_neutral_pos)
            if diff[0] == 0 and diff[1] == 0:
                return
            mag_x = min(1, max(0, abs(diff[0]) - self.dead_zone_size))
            mag_y = min(1, max(0, abs(diff[1]) - self.dead_zone_size))
            direction = Vector(diff[0] * mag_x, diff[1] * mag_y).normalize()
            if MOVEMENT_1D:
                dir_x = sign(direction.x)
                dir_y = sign(direction.y)
                if abs(direction.x) < abs(direction.y):
                    direction = Vector(0, dir_y)
                else:
                    direction = Vector(dir_x, 0)
            self.game_controller.pressed_direction(direction)

        if self.key_hold.get(97):
            self.game_controller.pressed_direction(Vector(-1, 0))
        elif self.key_hold.get(100):
            self.game_controller.pressed_direction(Vector(1, 0))
        elif self.key_hold.get(119):
            self.game_controller.pressed_direction(Vector(0, 1))
        elif self.key_hold.get(115):
            self.game_controller.pressed_direction(Vector(0, -1))

