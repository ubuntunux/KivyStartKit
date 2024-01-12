import kivy
from kivy import platform

def get_platform_api():
    if platform == 'android':
        from .android import AndroidPlatformAPI
        return AndroidPlatformAPI.instance()
    return BasePlatformAPI.instance()