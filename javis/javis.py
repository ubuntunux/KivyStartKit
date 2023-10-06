import os
import sys
import traceback

from kivy.app import App
from kivy.core.window import Window
from kivy.config import Config
from kivy.clock import Clock
from kivy.metrics import Metrics
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.vkeyboard import VKeyboard
from kivy.logger import Logger

from app.app import BaseApp
from utility.kivy_helper import *

from javis.constants import *
from javis.commands import Commander
from javis.memory import Memory
from javis.chairman import ChairMan
from javis.evaluator import Evaluator
from javis.listener import Listener

class JavisApp(BaseApp):
    def __init__(self, app_name):
        super(JavisApp, self).__init__(app_name)
        
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
        self.load_output()

    def destroy(self):
        self.save_output()

    def on_stop(self):
        self.listener.destroy()
        self.destroy()
        Config.write()

    def load_output(self):
        # print history 
        try:
            outputs = []
            if os.path.exists(javis_output_file):
                with open(javis_output_file, 'r') as f:
                    outputs = eval(f.read())
            for output in outputs:
                self.print_output(output)
        except:
            self.print_output(traceback.format_exc())

    def save_output(self):
        with open(javis_output_file, 'w') as f:
            outputs = [
                output.text for output in self.output_layout.children
                if output not in self.ignore_texts
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
            font_name=app_font_name,
            font_size="14dp",
            multiline=True,
            size_hint=(None, None),
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
    
