from utility.singleton import SingletonInstance


class BasePlatformAPI(SingletonInstance):
    def __init__(self):
        super(BasePlatformAPI, self).__init__()
    
    def initialize(self):
        pass
    
    def set_orientation(self, orientation="all"):
        pass
