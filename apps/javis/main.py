import os
import sys
import traceback
from kivy.logger import Logger
from kivy.config import Config
from kivy.core.window import Window
from kivy import metrics
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from core.base_app import BaseApp
from core import constants

from .chairman import ChairMan
from .commands import Commander
from .constants import *
from .evaluator import Evaluator
from .listener import Listener
from .memory import Memory


class JavisApp(BaseApp):
    app_name = "JAVIS"
    orientation = "all" # all, landscape, portrait

    def __init__(self, *args, **kargs):
        super(JavisApp, self).__init__(*args, **kargs)
        self.output_directory = os.path.join(os.path.split(__file__)[0], '.log')
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
        self.output_file = os.path.join(self.output_directory, 'output.log')
        
        self.memory = Memory()
        self.chairman = ChairMan(self.memory)
        self.evaluator = Evaluator(self.memory)
        self.listener = Listener(self.memory)
        self.commander = Commander(self)
        self.screen_helper = None
        self.screen = None
        self.listener_widget = None
        self.output = None
        self.output_line_index = 0
        self.output_layout = None
        self.output_scroll_view = None
        self.is_first_update = True
        self.save_text_list = []

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
        
    def initialize(self):
        self.build()
        self.print_output("Python " + sys.version.strip(), save=False)
        self.print_output(os.path.abspath("."), save=False)
        self.load_output()  

    def build(self):
        layout = BoxLayout(orientation='vertical', size=(1, 1))
        self.add_widget(layout)

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
        self.listener_widget = self.listener.initialize(self)
        layout.add_widget(self.listener_widget)
    
    def on_stop(self):
        self.listener.destroy()
        self.save_output()
        Config.write()
    
    def on_resize(self, window, width, height):
        pass
        
    def load_output(self):
        try:
            outputs = []
            if os.path.exists(self.output_file):
                with open(self.output_file, 'r') as f:
                    outputs = eval(f.read())
            for output in outputs:
                self.print_output(output)
        except:
            self.print_output(traceback.format_exc())

    def save_output(self):
        dir_name = os.path.split(self.output_file)[0]
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        with open(self.output_file, 'w') as f:
            f.write(repr(self.save_text_list))

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
            width = line_labels.size[0] + self.output.font_size
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

    def update(self, dt):
        pass
