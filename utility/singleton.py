class SingletonInstance:
    __instance = None

    @classmethod
    def __get_instance(cls):
        return cls.__instance

    @classmethod
    def instance(cls, *args, **kargs):
        if cls.__instance is None:
            cls.__instance = cls(*args, **kargs)
        return cls.__instance
        
    @classmethod
    def clear_instance(cls):
        cls.__instance = None
