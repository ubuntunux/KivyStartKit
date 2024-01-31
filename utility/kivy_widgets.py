from kivy.clock import Clock
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.metrics import dp as DP
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

class KivyLabel(TextInput):
    def __init__(
        self, 
        readonly=True,
        use_bubble=False,
        use_handles=False,
        allow_copy=False,
        multiline=True,
        background_color=(1,1,1,0),
        foreground_color=(1,1,1,1),
        **kargs
    ):     
        super().__init__(
            readonly=readonly,
            use_bubble=use_bubble,
            use_handles=use_handles,
            allow_copy=allow_copy,
            multiline=multiline,
            background_color=background_color,
            foreground_color=foreground_color,
            **kargs
        )
    
    def on_touch_down(self, *args):
        return False


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
        
class KivyPopup:
    def __init__(self):
        self.is_popup = False
        self.popup_layout = None
        
    def initialize_popup(
        self,
        title,
        auto_dismiss=False,
        callback_open=None,
        callback_close=None,
        content_widget=None,
        buttons=[]
    ):
        if self.is_popup:
            self.dismiss()
            
        layout_width = min(DP(400), Window.width - DP(20))
        layout_height = DP(50)
        content = BoxLayout(orientation="vertical", size_hint=(1, 1))
        self.popup_layout = Popup(title=title, content=content, auto_dismiss=auto_dismiss, size_hint=(None, None), size=(layout_width, layout_height))
        
        if content_widget:
            layout_height += DP(50)
            content.add_widget(content_widget)
        
        if buttons:
            layout_height += DP(50)
            btn_layout = BoxLayout(orientation="horizontal", size_hint=(1, 1), spacing=DP(5))
            content.add_widget(btn_layout)
            for button in buttons:
                btn_layout.add_widget(button)
                
        def on_open(inst):
            if callback_open:
                callback_open()
            self.is_popup = True
                
        def on_dismiss(inst):
            if callback_close:
                callback_close()
            self.is_popup = False

        self.popup_layout.height = layout_height
        self.popup_layout.bind(on_open=on_open)
        self.popup_layout.bind(on_dismiss=on_dismiss)
        
    def open(self):
        self.popup_layout.open()
    
    def dismiss(self):
        if self.is_popup:
            self.popup_layout.dismiss()
    
    def is_opened(self):
        return self.is_popup

