import os
from utility.singleton import SingletonInstance


class BasePlatformAPI(SingletonInstance):
    def __init__(self):
        super(BasePlatformAPI, self).__init__()
    
    def get_app_directory(self):
        return os.path.abspath(".")
        
    def get_home_directory(self):
        return os.path.expanduser('~')
    
    def set_orientation(self, orientation="all"):
        pass
