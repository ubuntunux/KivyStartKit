from kivy.clock import Clock
from kivy.uix.textinput import TextInput

class KivyLabel(TextInput):
    def __init__(self, **kargs):
        if "readonly" not in kargs:
            kargs["readonly"] = True
        if "use_bubble" not in kargs:
            kargs["use_bubble"] = False
        if "use_handles" not in kargs:
            kargs["use_handles"] = False
        if "allow_copy" not in kargs:
            kargs["allow_copy"] = False
        if "multiline" not in kargs:
            kargs["multiline"] = True
        if "background_color" not in kargs:
            kargs["background_color"] = (1,1,1,0)
        if "foreground_color" not in kargs:
            kargs["foreground_color"] = (1,1,1,1)
            
        super(KivyLabel, self).__init__(**kargs)


class DebugLabel(KivyLabel):
    def __init__(self, show_fps=True, display_count=5, display_time=3.0,**kargs):
        super(DebugLabel, self).__init__(**kargs)
        self.show_fps = show_fps
        self.display_count = display_count
        self.display_time = display_time
        self.debug_text = []
        
    def debug_print(self, text):
        self.remained_display_time = self.display_time
        if self.display_count < len(self.debug_text):
            self.debug_text.pop()
        self.debug_text.insert(0, text)
        
    def update(self, dt):
        fps = Clock.get_fps()
        time = 1000.0 / fps if 0 < fps else 0
        self.text = f"fps: {format(fps, '0.2f')}\ntime(ms): {format(time, '0.2f')}"
        if self.debug_text:
            self.text += "\n"
            self.text += "\n".join(self.debug_text)
            self.remained_display_time -= dt
            if self.remained_display_time < 0.0:
                self.debug_text = []
        self.height = self.minimum_height
        