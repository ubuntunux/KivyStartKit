from kivy.core.audio import Sound
from kivy.properties import StringProperty, ObjectProperty, NumericProperty


class Audio():
    def __init__(self, sound, volume=1.0, loop=False):
        self.sound = Sound(source=sound, volume=volume, loop=loop)
                 
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