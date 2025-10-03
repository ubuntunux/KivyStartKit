from kivy.clock import Clock
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.metrics import dp as DP
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView

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
    opened_popup = None

    def __init__(self):
        self.is_popup = False
        self.popup_layout = None
        self.content_widget = None
        self.btn_layout = None
        self.initial_size = (100, 100)

    def initialize_popup(
        self,
        title,
        auto_dismiss=True,
        callback_open=None,
        callback_close=None,
        content_widget=None,
        buttons=[],
        size_hint=(None, None),
        width=min(DP(400), Window.width - DP(20)),
        height=DP(50)
    ):
        if self.is_popup:
            self.dismiss()
            
        self.initial_size = (width, height)
        
        content_layout = BoxLayout(orientation="vertical", size_hint=(1, 1))
        self.popup_layout = Popup(title=title, content=content_layout, auto_dismiss=auto_dismiss, size_hint=size_hint, size=(width, height))
        
        if content_widget:
            content_widget.height = max(DP(50), content_widget.height)
            #layout_height += content_widget.height

            scroll_view = ScrollView(size_hint=(1, 1))
            scroll_view.add_widget(content_widget)
            content_layout.add_widget(scroll_view)
            self.content_widget = content_widget

        if buttons:
            max_button_height = DP(50)
            self.btn_layout = BoxLayout(orientation="horizontal", size_hint=(1, None), spacing=DP(5))
            content_layout.add_widget(self.btn_layout)
            for button in buttons:
                max_button_height = max(max_button_height, button.height)
                self.btn_layout.add_widget(button)
            self.btn_layout.height = max_button_height
                
        def on_open(inst):
            if KivyPopup.opened_popup is None:
                KivyPopup.opened_popup = self
                if callback_open:
                    callback_open()
                self.is_popup = True
        
        def on_dismiss(inst):
            if KivyPopup.opened_popup is self: 
                KivyPopup.opened_popup = None
            if callback_close:
                callback_close()
            self.is_popup = False
 
        self.popup_layout.bind(on_open=on_open)
        self.popup_layout.bind(on_dismiss=on_dismiss)
        self.update_layout()
    
    def set_title(self, title):
        self.popup_layout.title = title

    def update_layout(self):
        self.popup_layout.size = self.initial_size
        if self.content_widget:
            self.popup_layout.height += self.content_widget.height
        if self.btn_layout:
            self.popup_layout.height += self.btn_layout.height

    def open(self):
        if not KivyPopup.opened_popup:
            self.popup_layout.open() 
    
    def dismiss(self):
        if self.is_popup:
            self.popup_layout.dismiss()
    
    def is_opened(self):
        return self.is_popup

