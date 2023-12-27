from kivy.core.audio import Sound, SoundLoader
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from utility.kivy_helper import *


class Audio():
    def __init__(self, sound, volume=1.0, loop=False):
        self.sound = None
        if sound:
            self.sound = SoundLoader.load(sound.source)
        
    def play_audio(self):
        if self.sound:
            if self.sound.status != 'stop':
                self.sound.stop()
            self.sound.play()
        
    def release_audio(self):
        if self.sound:
            self.sound.stop()
            self.sound = None

    def set_volume(self, volume):
        if self.sound:
            self.sound.volume = volume