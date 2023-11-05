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
