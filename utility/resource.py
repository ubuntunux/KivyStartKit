import os
from kivy.logger import Logger
from kivy.uix.image import Image
from utility.singleton import SingletonInstance


class Resource:
    def __init__(self, name, filepath, loader):
        self.name = name
        self.is_loaded = False
        self.loader = loader
        self.filepath = filepath
        self.source = None
        
    def get_resource(self):
        if self.is_loaded:
            return self.source
        self.is_loaded = True
        Logger.info(f"Load {self.name}: {self.filepath}")             
        self.source = self.loader(self.name, self.filepath)
        if self.source is None:
            Logger.warning(f"failed to load {resource_name}: {self.filepath}") 
        return self.source
        

class ResourceManager(SingletonInstance):
    def __init__(self):
        super(ResourceManager, self).__init__()
        
    def initialize(self):
        raise Exception('must implement')
        
    def register_resources(self, resource_path, resource_exts, resource_map, resource_loader):
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
                        resource_loader
                    )
                    
    def get_resource(self, resource_map, resource_name):
        if resource_name in resource_map:
            resource = resource_map[resource_name]
            return resource.get_resource()
        Logger.warning(f"not found resource: {resource_name}")
        
    