import os
from functools import partial
from io import StringIO
import sys
from threading import Thread
import time
import traceback

from kivy import metrics
from kivy.core.window import Window
from kivy.config import Config
from kivy.graphics import Color, Rectangle
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.codeinput import CodeInput
from kivy.extras.highlight import KivyLexer

from javis.constants import *
from utility.kivy_helper import create_rect, create_dynamic_rect


class Listener:
    def __init__(self, memory):
        self.app = None
        self.memory = memory
        self.globals = {}
        self.root_layout = None
        self.history = []
        self.history_index = -1
        self.is_indent_mode = False
        self.text_input = None
        self.input_layout = None
        self.top_layout = None

        # initialize config
        if not Config.has_section(section_listener):
            Config.add_section(section_listener)

        if not Config.has_option(*config_listener_pos):
            Config.set(*config_listener_pos, (0, 0))
        Config.write()
        
    def refresh_auto_compmete(self):
        text_font_size = metrics.dp(14)
        text_padding_y = metrics.dp(10)
        text_height = text_font_size + text_padding_y * 2.0
        self.auto_complete_layout.height = self.auto_complete_vertical_layout.padding[0] * 2.0
        
        def func_auto_complete(text, inst):
            self.text_input.text = text
        
        for text in self.app.commander.get_commands():
            btn = Button(text=text, size_hint=(1.0, None), font_size=text_font_size, height=text_height, padding_y=text_padding_y)
            btn.bind(on_press=partial(func_auto_complete, text))
            self.auto_complete_vertical_layout.add_widget(btn)
            self.auto_complete_layout.height += text_height

    def initialize(self, app):
        self.app = app
        text_font_size = metrics.dp(14)
        text_padding_y = metrics.dp(10)
        text_height = text_font_size + text_padding_y * 2.0
        root_layout_padding = metrics.dp(4)
        root_layout_height = (text_height + root_layout_padding) * 2.0

        # inner layout
        self.root_layout = BoxLayout(orientation='vertical', size_hint=(1, None), height=root_layout_height, padding=root_layout_padding)
        create_dynamic_rect(self.root_layout, color=(1, 1, 1, 0.1))

        # top layout
        self.top_layout = BoxLayout(orientation='horizontal', size_hint=(1.0, None), height=text_height)
        self.root_layout.add_widget(self.top_layout)

        # input_layout
        self.input_layout = BoxLayout(orientation='horizontal', size_hint=(1.0, 1.0), height=text_height)
        self.root_layout.add_widget(self.input_layout)
        
        # auto complete
        self.auto_complete_layout = ScatterLayout(
            size_hint=(None, None),
            width=text_font_size * 10.0 + text_padding_y * 2.0, 
            height=text_height
        )
        create_dynamic_rect(self.auto_complete_layout, color=(0.1, 0.1, 0.1, 1.0))
        self.auto_complete_layout.pos = (
            Window.size[0] - self.auto_complete_layout.width,
            self.auto_complete_layout.height
        )
        self.auto_complete_vertical_layout = BoxLayout(orientation='vertical', size_hint=(1, 1), padding=metrics.dp(10))
        self.auto_complete_layout.add_widget(self.auto_complete_vertical_layout)
        app.screen.add_widget(self.auto_complete_layout)
        self.refresh_auto_compmete()
        
        # text layout
        def on_enter(text_input, is_force_run, instance):
            cmd = text_input.text.strip()
            if cmd:
                prev_stdout = sys.stdout
                sys.stdout = StringIO()

                cmd_lines = cmd.split("\n")
                # indent mode - continue input but not run
                if not is_force_run:
                    is_cursor_at_end = len(text_input.text) == text_input.cursor_index()
                    num_lines_of_cmd = text_input.text.lstrip().count('\n')
                    run_code = is_cursor_at_end and 1 <= (num_lines_of_cmd - len(cmd_lines))
                    lastline = cmd_lines[-1]
                    if not run_code and (not is_cursor_at_end or lastline[-1] in ("\\", ":") or self.is_indent_mode):
                        self.is_indent_mode = True
                        text_input.height = text_input.minimum_height
                        return

                # prepare running command
                self.is_indent_mode = False

                # display command
                results = []
                for line_index, cmd_line in enumerate(cmd_lines):
                    results.append((">>> " if line_index == 0 else "... ") + cmd_line)
                results = "\n".join(results)
                app.print_output(results)

                # regist to histroy
                if 0 == len(self.history) or self.history[-1] != cmd:
                    self.history.append(cmd)
                    self.history_index = -1

                # run command
                if app.commander.run_command(cmd):
                    pass
                else:
                    try:
                        print(eval(cmd, self.globals))
                    except:
                        try:
                            exec(cmd, self.globals)
                        except:
                            print(traceback.format_exc())

                # display output
                output_text = sys.stdout.getvalue().rstrip()
                if output_text:
                    app.print_output(output_text)

                # reset
                sys.stdout = prev_stdout
                text_input.text = ''
                text_input.height = text_input.minimum_height
                text_input.focus = True

        # input widget
        self.text_input = TextInput(
            text='',
            size_hint=(3, None),
            height=text_height,
            multiline=True,
            auto_indent=True,
            font_name=app_font_name,
            font_size=text_font_size,
            padding_x=metrics.dp(10),
            padding_y=text_padding_y,
        )
        # self.text_input.bind(on_text_validate=partial(on_enter, self.text_input, False))
        self.input_layout.add_widget(self.text_input)

        # button run
        btn_enter = Button(text="Run", size_hint=(1, None), height=text_height - 2.0, background_color=(1.3, 1.3, 2,2))
        btn_enter.bind(on_press=partial(on_enter, self.text_input, True))
        self.input_layout.add_widget(btn_enter)

        def on_press_prev(inst):
            num_history = len(self.history)
            if 0 < num_history:
                if self.history_index < 0:
                    self.history_index = num_history - 1
                elif 0 < self.history_index:
                    self.history_index -= 1
                self.text_input.text = self.history[self.history_index]
                self.is_indent_mode = self.text_input.text.find("\n") > -1

        def on_press_next(inst):
            num_history = len(self.history)
            if 0 < num_history and 0 <= self.history_index < num_history:
                self.history_index += 1
                if self.history_index == num_history:
                    self.text_input.text = ''
                else:
                    self.text_input.text = self.history[self.history_index]
                self.is_indent_mode = self.text_input.text.find("\n") > -1

        def on_key_down(keyboard, keycode, key, modifiers):
            key_name = keycode[1]
            if key_name == 'enter' or key_name == 'numpadenter':
                on_enter(self.text_input, False, self.text_input)
            elif key_name == 'up':
                on_press_prev(None)
            elif key_name == 'down':
                on_press_next(None)

        def keyboard_closed(*args):
            pass

        keyboard = Window.request_keyboard(keyboard_closed, self.text_input)
        keyboard.bind(on_key_down=on_key_down)
        self.text_input.focus = True

        # logo
        logo_image = Image(source=logo_file, allow_stretch=True, keep_ratio=True, size_hint_x=None)
        self.top_layout.add_widget(logo_image)

        # prev
        dark_gray = [0.4, 0.4, 0.4, 2]
        btn_prev = Button(size_hint=(1, 1), text="<<", background_color=dark_gray)
        self.top_layout.add_widget(btn_prev)
        btn_prev.bind(on_press=on_press_prev)

        # next
        btn_next = Button(size_hint=(1, 1), text=">>", background_color=dark_gray)
        self.top_layout.add_widget(btn_next)
        btn_next.bind(on_press=on_press_next)

        def on_clear(*args):
            app.clear_output()

        btn_clear = Button(size_hint=(1, 1), text="Clear", background_color=dark_gray)
        btn_clear.bind(on_press=on_clear)
        self.top_layout.add_widget(btn_clear)

        # quit
        def on_press_quit(inst):
            app.stop()
        btn_quit = Button(size_hint=(0.5, 1), text="Quit", background_color=dark_gray)
        self.top_layout.add_widget(btn_quit)
        btn_quit.bind(on_press=on_press_quit)

        return self.root_layout

    def destroy(self):
        Config.set(*config_listener_pos, self.root_layout.pos)

    def update_listener(self):
        while True:
            self.memory.listener_data.listen_data = input("listen: ")
            print(">>", self.memory.listener_data.listen_data)
            if self.memory.machine_state == MachineState.PrepareToExit:
                break
        print("end - listener")
