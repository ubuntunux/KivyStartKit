import json
import os
import sys
import traceback
import kivy
from kivy.logger import Logger
from kivy.config import Config
from kivy.core.window import Window
from kivy import metrics
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from core.base_app import BaseApp
from core import constants

from .chairman import ChairMan
from .commands import Commander
from .constants import *
from .evaluator import Evaluator
from .listener import Listener
from .memory import Memory
from .code_editor import EditorLayout

class JarvisApp(BaseApp):
    app_name = "Python"
    orientation = "all" # all, landscape, portrait
    allow_multiple_instance = False
    
    def __init__(self, *args, **kargs):
        super(JarvisApp, self).__init__(*args, **kargs)
        self.output_directory = os.path.join(os.path.split(__file__)[0], 'data')
        self.output_file = os.path.join(self.output_directory, 'output.ini')
        self.history_file = os.path.join(self.output_directory, 'history.ini')
        
        self.memory = Memory()
        self.chairman = ChairMan(self.memory)
        self.evaluator = Evaluator(self.memory)
        self.listener = Listener(self, self.memory)
        self.commander = Commander(self)
        self.screen_helper = None
        self.screen = None
        self.listener_widget = None
        self.output = None
        self.output_line_index = 0
        self.output_layout = None
        self.output_scroll_view = None
        self.main_layout = None 
        self.is_first_update = True
        self.save_text_list = []

        self.code_editor = EditorLayout(self) 
      
        # # create
        # chairman_thread = Thread(target=chairman, args=[memory])
        # listener_thread = Thread(target=listener, args=[memory])
        # evaluator_thread = Thread(target=evaluator, args=[memory])
        #
        # # start
        # chairman_thread.start()
        # evaluator_thread.start()
        # listener_thread.start()
        #
        # # end
        # listener_thread.join(0.1)
        # evaluator_thread.join(0.1)
        # chairman_thread.join(0.1)
        # initialize config
        
    def on_initialize(self):
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
                 
        self.listener.initialize()

        # build gui
        self.build()
        
        # run
        self.print_output(f"Python {sys.version.strip()}", save=False)
        self.print_output(f"Kivy v{kivy.__version__}", save=False)
        self.print_output(f'Working directory: {os.path.abspath(".")}', save=False)
        self.load_data()  

    def build(self):
        self.build_console()
        self.code_editor.build()
        self.open_console()

    def build_console(self):
        layout = BoxLayout(orientation='vertical', size=(1, 1))
        self.main_layout = layout

        self.output_scroll_view = ScrollView(size_hint=(1, None))
        self.output_layout = BoxLayout(size_hint=(None,None))
        self.output = TextInput(
            halign='left',
            readonly=True,
            font_name=constants.DEFAULT_FONT_NAME,
            font_size=metrics.dp(14),
            padding=metrics.dp(14),
            multiline=True,
            size_hint=(None, None),
            size=(0,0),
            background_color=(1, 1, 1, 0),
            foreground_color=(1, 1, 1, 1),
            do_wrap=False
        )
        self.output_layout.add_widget(self.output)
        self.output_scroll_view.add_widget(self.output_layout)
        layout.add_widget(self.output_scroll_view)

        # initialize listner
        self.listener_widget = self.listener.build()
        layout.add_widget(self.listener_widget)
    
    def on_stop(self):
        self.listener.destroy()
        self.save_data()
        Config.write()
        
    def on_back(self):
        return False
    
    def on_resize(self, window, width, height):
        pass
        
    def open_console(self, code=''):
        if self.code_editor.main_layout.parent:
            self.remove_widget(self.code_editor.main_layout)
        if not self.main_layout.parent:
            self.add_widget(self.main_layout)
            self.listener.execute_code(code)

    def open_editor(self):
        if self.main_layout.parent:
            self.remove_widget(self.main_layout) 
        if not self.code_editor.main_layout.parent:
          self.add_widget(self.code_editor.main_layout)

    def load_data(self):
        try:
            # load history
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    history_data = eval(f.read())
                    self.listener.load_history_data(history_data)
        
            # load output
            outputs = []
            if os.path.exists(self.output_file):
                with open(self.output_file, 'r') as f:
                    outputs = eval(f.read())
            for output in outputs:
                self.print_output(output)
        except:
            self.print_output(traceback.format_exc())

    def save_data(self):
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

        with open(self.output_file, 'w') as f:
            f.write(json.dumps(self.save_text_list, indent=4))
        
        with open(self.history_file, 'w') as f:
            f.write(json.dumps(self.listener.get_history_data(), indent=4))

    def clear_output(self):
        self.save_text_list.clear()
        self.output_line_index = 0
        self.output.text = ""
        self.output.size = (0,0)
        self.output_layout.size = (0,0)
        self.output_scroll_view.scroll_x = 0
        self.output_scroll_view.scroll_y = 0

    def print_output(self, text, save=True):
        if save:
            self.save_text_list.append(text)
        
        prev_line_index = self.output_line_index
        if self.output.text:
            self.output.text = "\n".join([self.output.text, text])
        else:
            self.output.text = text
        
        # fit size
        num_lines = len(self.output._lines_labels)
        for i in range(prev_line_index,num_lines):
            line_labels = self.output._lines_labels[i]
            width = line_labels.size[0] + self.output.font_size * 3
            self.output.width = max(self.output.width, width)
        self.output_line_index = num_lines - 1
        self.output.height = self.output.minimum_height
        self.output_layout.size = self.output.size
        
        # update scrollview
        self.output_scroll_view.height = min(
            self.output_layout.height,
            Window.size[1] - self.listener_widget.height
        )
        self.output_scroll_view.scroll_x = 0
        self.output_scroll_view.scroll_y = 0

    def on_update(self, dt):
        pass
