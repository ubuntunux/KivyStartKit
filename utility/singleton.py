class SingletonInstance:
    __instance = None
    allow_multiple_instance = False

    @classmethod
    def instance(cls, *args, **kargs):
        if cls.__instance is None or cls.allow_multiple_instance:
            cls.__instance = cls(*args, **kargs)
        return cls.__instance
        
    @classmethod
    def clear_instance(cls):
        cls.__instance = None
