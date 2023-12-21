import os
from kivy.core.audio import SoundLoader
from kivy.logger import Logger
from kivy.uix.image import Image
from utility.effect import EffectData
from utility.singleton import SingletonInstance
from utility.range_variable import RangeVar


class Resource:
    def __init__(self, name, filepath, loader, unloader):
        self.name = name
        self.is_loaded = False
        self.loader = loader
        self.unloader = unloader
        self.filepath = filepath
        self.source = None
        
    def get_resource(self):
        if self.is_loaded:
            return self.source
        Logger.info(f"Load {self.name}: {self.filepath}")             
        self.is_loaded = True
        if self.loader:
            self.source = self.loader(self.name, self.filepath)
            if self.source is None:
                Logger.warning(f"failed to load {resource_name}: {self.filepath}") 
        return self.source
    
    def unload_resource(self):
        if self.is_loaded:
            Logger.info(f"Unload {self.name}: {self.filepath}")
            self.is_loaded = False
            if self.source and self.unloader:
                self.unloader(self.source)
            self.source = None
        
        
class ResourceManager(SingletonInstance):
    def __init__(self):
        super(ResourceManager, self).__init__()
        self.sounds = {}        
        self.images = {}
        self.effect_data = {}
        
    def initialize(self, images_path=".", effects_path=".", sounds_path="."):
        self.register_resources(sounds_path, [".wav", ".mp3"], self.sounds, self.sound_loader, self.sound_unloader)
        self.register_resources(images_path, [".png", ".jpg"], self.images, self.image_loader, None)
        self.register_resources(effects_path, [".effect"], self.effect_data, self.effect_data_loader, None)
        
    def destroy(self):
        self.unregister_resources(self.effect_data)
        self.unregister_resources(self.images)
        self.unregister_resources(self.sounds)
        
    def register_resources(self, resource_path, resource_exts, resource_map, resource_loader, resource_unloader):
        for dirname, dirnames, filenames in os.walk(resource_path):
            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()
                if ext in resource_exts:
                    filepath = os.path.join(dirname, filename)
                    resource_name = os.path.relpath(filepath, resource_path)
                    resource_name = os.path.splitext(resource_name)[0]
                    Logger.info(f"Register {resource_name}: {filepath}")
                    resource_map[resource_name] = Resource(
                        resource_name,
                        filepath,
                        resource_loader,
                        resource_unloader
                    )
                    
    def unregister_resources(self, resource_map):
        self.unload_resources(resource_map.values())
        resource_map.clear()
        
    def unload_resources(self, resources):
        for resource in resources:
            resource.unload_resource()
        
    def get_resource(self, resource_map, resource_name, default_resource=None):
        if resource_name in resource_map:
            resource = resource_map[resource_name]
            return resource.get_resource()
        Logger.warning(f"not found resource: {resource_name}")
        return default_resource
        
    # sound
    def get_sound(self, resource_name):
        return self.get_resource(self.sounds, resource_name)
        
    def sound_loader(self, name, filepath):
        sound = SoundLoader.load(filepath)
        return sound
    
    def sound_unloader(self, sound):
        if sound:
            sound.stop()
            sound.unload()
    
    # image
    def get_image(self, resource_name):
        return self.get_resource(self.images, resource_name)
        
    def image_loader(self, name, filepath):
        image = Image(source=filepath)
        Logger.info(f"{filepath}: {image.texture.size}")
        return image
    
    # effect
    def get_effect_data(self, resource_name):
        return self.get_resource(self.effect_data, resource_name)
        
    def effect_data_loader(self, name, filepath):
        if os.path.exists(filepath):
            with open(filepath) as f:
                effecf_data_info = eval(f.read())
                return EffectData(self, name, effecf_data_info)
