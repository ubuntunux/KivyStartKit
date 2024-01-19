import sys
import traceback
from functools import partial
from io import StringIO

from kivy import metrics
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.textinput import TextInput

from utility.kivy_helper import create_dynamic_rect
from core import constants
from .constants import *


dark_gray = [0.4, 0.4, 0.4, 2]

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
        self.keyboard = None

        # initialize config
        if not Config.has_section(SECTION_LISTENER):
            Config.add_section(SECTION_LISTENER)

        if not Config.has_option(*CONFIG_LISTENER_POS):
            Config.set(*CONFIG_LISTENER_POS, (0, 0))
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
        root_layout_padding = metrics.dp(0)
        root_layout_height = (text_height + root_layout_padding) * 2.0

        # inner layout
        self.root_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=root_layout_height,
            padding=root_layout_padding,
            spacing=root_layout_padding
        )
        create_dynamic_rect(self.root_layout, color=(0, 0, 0, 0.2))

        # top layout
        self.top_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1.0, None),
            height=text_height
        )
        self.root_layout.add_widget(self.top_layout)

        # input_layout
        px = metrics.dp(20)
        self.input_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1.0, 1.0),
            height=text_height
        )
        self.root_layout.add_widget(self.input_layout)
        
        # undo
        btn_undo = Button(size_hint=(None, 1), width=metrics.dp(40), text="<")
        btn_undo.bind(on_press=self.on_press_undo)
        
        # redo
        btn_redo = Button(size_hint=(None, 1), width=metrics.dp(40), text=">")
        btn_redo.bind(on_press=self.on_press_redo)

        # input widget
        px = metrics.dp(10)
        py = text_padding_y
        self.text_input = TextInput(
            text='',
            size_hint=(1, None),
            height=text_height,
            multiline=True,
            auto_indent=True,
            font_name=constants.DEFAULT_FONT_NAME,
            font_size=text_font_size,
            padding=(px,py,px,py),
            do_wrap=False
        )
        self.keyboard = Window.request_keyboard(self.keyboard_closed, self.text_input)
        self.keyboard.bind(on_key_down=self.on_key_down)
        
        self.input_layout.add_widget(btn_undo)
        self.input_layout.add_widget(self.text_input)
        self.input_layout.add_widget(btn_redo)
        
        
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
        #app.add_widget(self.auto_complete_layout)
        self.refresh_auto_compmete()

        # logo
        logo_image = Image(source=ICON_FILE, fit_mode="fill", size_hint_x=None)
        
        # prev
        btn_prev = Button(size_hint=(1, 1), text="<<", background_color=dark_gray)
        btn_prev.bind(on_press=self.on_press_prev)

        # next
        btn_next = Button(size_hint=(1, 1), text=">>", background_color=dark_gray)
        btn_next.bind(on_press=self.on_press_next)
        
        # clear
        def on_clear(*args):
            app.clear_output()
        
        btn_clear = Button(size_hint=(1, 1), text="Clear", background_color=dark_gray)
        btn_clear.bind(on_press=on_clear)
        
        # run
        btn_enter = Button(text="Run", size_hint=(1, 1), background_color=(1.3, 1.3, 2,2))
        btn_enter.bind(on_press=partial(self.execute_command, self.text_input, True))
        
        # quit
        '''
        def on_press_quit(inst):
            app.stop()
        btn_quit = Button(size_hint=(0.5, 1), text="Quit", background_color=dark_gray)
        self.top_layout.add_widget(btn_quit)
        btn_quit.bind(on_press=on_press_quit)
        '''
        
        self.top_layout.add_widget(logo_image)
        self.top_layout.add_widget(btn_prev)
        self.top_layout.add_widget(btn_next)
        self.top_layout.add_widget(btn_clear)
        self.top_layout.add_widget(btn_enter)
        
        self.on_resize(Window, Window.width, Window.height)
        
        return self.root_layout
 
    def execute_command(self, text_input, is_force_run, instance):
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
            self.app.print_output(results)

            # regist to histroy
            if 0 == len(self.history) or self.history[-1] != cmd:
                self.history.append(cmd)
                self.history_index = -1

            # run command
            if self.app.commander.run_command(cmd):
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
                self.app.print_output(output_text)

            # reset
            sys.stdout = prev_stdout
            text_input.text = ''
            text_input.height = text_input.minimum_height
            #text_input.focus = True
    
    def on_key_down(self, keyboard, keycode, key, modifiers):
        key_name = keycode[1]
        if key_name == 'enter' or key_name == 'numpadenter':
            self.execute_command(self.text_input, False, self.text_input)
        elif key_name == 'up':
            self.on_press_prev(None)
        elif key_name == 'down':
            self.on_press_next(None)

    def keyboard_closed(self, *args):
        pass
            
    def on_press_undo(self, inst):
        self.text_input.do_undo()
    
    def on_press_redo(self, inst):
        self.text_input.do_redo()
    
    def on_press_prev(self, inst):
        num_history = len(self.history)
        if 0 < num_history:
            if self.history_index < 0:
                self.history_index = num_history - 1
            elif 0 < self.history_index:
                self.history_index -= 1
            self.text_input.text = self.history[self.history_index]
            self.text_input.height = self.text_input.minimum_height
            self.is_indent_mode = self.text_input.text.find("\n") > -1

    def on_press_next(self, inst):
            num_history = len(self.history)
            if 0 < num_history and 0 <= self.history_index < num_history:
                self.history_index += 1
                if self.history_index == num_history:
                    self.text_input.text = ''
                else:
                    self.text_input.text = self.history[self.history_index]
                self.text_input.height = self.text_input.minimum_height
                self.is_indent_mode = self.text_input.text.find("\n") > -1
    
    def on_resize(self, window, width, height):
        pass

    def destroy(self):
        Config.set(*CONFIG_LISTENER_POS, self.root_layout.pos)

    def update_listener(self):
        while True:
            self.memory.listener_data.listen_data = input("listen: ")
            print(">>", self.memory.listener_data.listen_data)
            if self.memory.machine_state == MachineState.PrepareToExit:
                break
        print("end - listener")
