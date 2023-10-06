class SingletonInstane:
    __instance = None

    @classmethod
    def __getInstance(cls):
        return cls.__instance

    @classmethod
    def instance(cls, *args, **kargs):
        if cls.__instance is None:
            cls.__instance = cls(*args, **kargs)
            cls.instance = cls.__getInstance
        return cls.__instance
