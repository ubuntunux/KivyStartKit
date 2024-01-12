import os
import sys
import traceback

from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from core.base_app import BaseApp
from core import constants
from utility.singleton import SingletonInstance

from .chairman import ChairMan
from .commands import Commander
from .constants import *
from .evaluator import Evaluator
from .listener import Listener
from .memory import Memory


class JavisApp(BaseApp, SingletonInstance):
    app_name = "Javis"
    
    def __init__(self):
        super(JavisApp, self).__init__(orientation="all")

        self.output_directory = os.path.join(os.path.split(__file__)[0], 'output')
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
        self.output_file = os.path.join(self.output_directory, 'output.txt')
        
        self.memory = Memory()
        self.chairman = ChairMan(self.memory)
        self.evaluator = Evaluator(self.memory)
        self.listener = Listener(self.memory)
        self.commander = Commander(self)
        self.screen_helper = None
        self.screen = None
        self.listener_widget = None
        self.output_layout = None
        self.output_scroll_view = None
        self.is_first_update = True
        self.ignore_texts = []

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

    def on_stop(self):
        self.listener.destroy()
        self.save_output()
        Config.write()
    
    def on_resize(self, window, width, height):
        pass
        
    def load_output(self):
        # print history 
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
            outputs = [
                output.text for output in self.output_layout.children if output not in self.ignore_texts
            ]
            f.write(repr(outputs))

    def clear_output(self):
        self.ignore_texts.clear()
        self.output_layout.clear_widgets()
        self.output_layout.height = 0
        self.output_scroll_view.scroll_x = 0
        self.output_scroll_view.scroll_y = 0

    def print_output(self, text, save=True):
        # important: keep this form and parameters
        output = TextInput(
            halign='left',
            readonly=True,
            font_name=constants.DEFAULT_FONT_NAME,
            font_size="14dp",
            multiline=True,
            size_hint=(1, None),
            size=(Window.size[0], 0),
            background_color=(1, 1, 1, 0),
            foreground_color=(1, 1, 1, 1)
        )
        output.text = text
        output.height = output.minimum_height

        if not save:
            self.ignore_texts.append(output)

        self.output_layout.add_widget(output)
        self.output_layout.height += output.height
        self.output_scroll_view.height = min(
            self.output_layout.height,
            Window.size[1] - self.listener_widget.height
        )
        self.output_scroll_view.scroll_x = 0
        self.output_scroll_view.scroll_y = 0

    def build(self):
        layout = BoxLayout(orientation='vertical', size=(1, 1))
        self.add_widget(layout)

        self.output_scroll_view = ScrollView(size_hint=(1, None))
        self.output_layout = BoxLayout(orientation="vertical", size_hint=(1,None), height=0)
        self.output_scroll_view.add_widget(self.output_layout)
        layout.add_widget(self.output_scroll_view)

        # initialize listner
        self.listener_widget = self.listener.initialize(self)
        layout.add_widget(self.listener_widget)
    
    def update(self, dt):
        pass
    

def main():
    return JavisApp()