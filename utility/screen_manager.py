from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition

from utility.singleton import SingletonInstane


class ScreenHelper(SingletonInstane):
    def __init__(self, *args, **kwargs):
        self.name = "ScreenManager"
        self.screen_manager = ScreenManager(*args, **kwargs)
        self.transition = WipeTransition()
        self.screen_map = {}
        #empty_screen = Screen(name="empty screen")
        #self.add_screen(empty_screen, True)
        
    def prev_screen(self):
        prev_screen = self.screen_manager.previous()
        if prev_screen:
            self.screen_manager.current = prev_screen

    def add_screen(self, screen, set_current_screen):
        if screen is not None and not self.screen_manager.has_screen(screen.name):
            self.screen_manager.add_widget(screen)
            self.screen_map[screen.name] = screen
            if set_current_screen:
                self.current_screen(screen)

    def current_screen(self, screen):
        if screen is not None and self.screen_manager.current != screen.name and self.screen_manager.has_screen(screen.name):
            self.screen_manager.current = screen.name    
    
    def cycle_screen(self):
        current = self.get_current_screen_name()
        screen_names = self.get_screen_names()
        num_screen = len(screen_names)
        if 0 < num_screen and current is not None: 
            index = screen_names.index(current) + 1
            if index == num_screen:
                index = 0
            screen_name = screen_names[index]
            screen = self.get_screen(screen_name)
            self.current_screen(screen)
            return screen
        return self.screen_manager.current
        
    def remove_screen(self, screen):
        if screen.name in self.screen_manager.screen_names:
            self.screen_manager.remove_widget(screen)
            self.prev_screen()
            
    def get_screen(self, screen_name):
        return self.screen_map.get(screen_name)

    def get_screen_names(self):
        return self.screen_manager.screen_names
        
    def get_current_screen_name(self):
        return self.screen_manager.current
