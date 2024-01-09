from kivy.uix.button import Button
from app.app import BaseApp
from utility.singleton import SingletonInstance

class ExampleApp(BaseApp, SingletonInstance):
    def __init__(self, app_name="ExampleApp"):
        super(ExampleApp, self).__init__(app_name)
        
    def initialize(self):
        btn = Button(text=self.app_name, size_hint=(1, 1))
        self.add_widget(btn)

    def on_stop(self):
        pass

    def update(self, dt):
        pass
    
