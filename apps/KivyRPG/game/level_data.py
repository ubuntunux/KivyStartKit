from utility.kivy_helper import *


class LevelData():
    def __init__(self, resource_manager, name, level_data_info):
        self.name = name
        
        self.texture = None
        image = resource_manager.get_image(weapon_data_info.get("image_file", ""))
        if image:
            region = weapon_data_info.get("texture_region", (0,0,1,1))
            self.texture = get_texture_atlas(image.texture, region)
            if weapon_data_info.get("flip_horizontal", False):
                self.texture.flip_horizontal()
        
        self.attack_effect = weapon_data_info.get("attack_effect", "")
        self.damage = weapon_data_info.get("damage", 10)
        self.size = weapon_data_info.get("size", (100,100))
        self.pos = weapon_data_info.get("pos", (50,0))
