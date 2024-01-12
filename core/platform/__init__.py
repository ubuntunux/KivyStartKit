import kivy
from kivy import platform

from .default import BasePlatformAPI

def get_platform_api():
    return BasePlatformAPI.instance()