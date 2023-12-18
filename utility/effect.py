import copy
import math
from kivy.core.window import Window
from kivy.graphics import Scale, Rotate, PushMatrix, PopMatrix, Translate, UpdateNormalMatrix
from kivy.graphics.texture import Texture
from kivy.logger import Logger
from kivy.uix.scatter import Scatter
from kivy.uix.widget import Widget
from kivy.vector import Vector
from utility.singleton import SingletonInstance
from utility.kivy_helper import *
from utility.range_variable import RangeVar

    
class EffectData():
    default_emitter_data = {
        "particle_count": 10,
    }
    
    default_particle_data = {
        "is_world_space":True,
        "elastin":0.8, 
        "collision":False, 
        "size":[100,100], 
        "image_file":"explosion",
        "loop":-1, 
        "fade":1.0,
        "sequence":[4,4], 
        "play_speed":1.0,
        "color":(1,1,0,1),
        "sequence":[4,4],
        "delay":RangeVar(0.0,1.0), 
        "life_time":RangeVar(0.5,1.5), 
        "gravity":RangeVar(200.0),
        "velocity":RangeVar([-200.0, 200], [200.0, 300]),
        "angular_velocity":RangeVar(360.0), 
        "rotate":RangeVar(0.0, 360), 
        "scaling":RangeVar(1.0),
        "opacity":RangeVar(1.0),
        "offset":RangeVar((-20,20), (-20,20)),
    }

    def __init__(self, resource_manager=None, name="", effect_data_info={}):
        self.name = name
        self.emitter_data = copy.deepcopy(self.default_emitter_data)
        self.particle_data = copy.deepcopy(self.default_particle_data)
        
        for (key, value) in effect_data_info.get("emitter_data", {}).items():
            self.emitter_data[key] = value
            
        for (key, value) in effect_data_info.get("particle_data", {}).items():
            self.particle_data[key] = value
            
            if resource_manager and "image_file" == key:
                src_image = resource_manager.get_image(value)
                if src_image:
                    self.particle_data["texture"] = src_image.texture
    
    def get_particle_data(self):
        return self.particle_data


class EffectManager(SingletonInstance):
    def __init__(self):
        self.emitters = {}
        self.alive_emitters = []
        self.parent_layer = None
        self.active = True
            
    def initialize(self, parent_layer):
        self.set_layer(parent_layer)
    
    def set_layer(self, parent_layer):
        self.parent_layer = parent_layer
        
    def clear(self):
        for i in self.emitters:
            self.emitters[i].destroy()
        self.alive_emitters = []
        
    def reset(self):
        self.clear()
        self.emitters = {}

    def get_emitter(self, emitter_id):
        return self.emitters.get(emitter_id, None)
        
    def example_effect(self):
        effect_data = EffectData("explosion", {})
        self.create_emitter(
            emitter_name='explosion',
            attach_to=None,
            pos=(50,50),
            size=(100,100),
            effect_data=effect_data
        )
        emitter = self.get_emitter('explosion')
        emitter.play()
        return emitter
        
    def create_emitter(
        self,
        emitter_name,
        effect_data,
        parent_layer=None,
        attach_to=None,
        **kargs
    ):
        if not self.parent_layer:
            raise AttributeError("Has no parent, first run set_layer..")

        emitter = Emitter(
            self,
            emitter_name,
            parent_layer=parent_layer or self.parent_layer,
            attach_to=attach_to,
            effect_data=effect_data,
            **kargs
        )
        self.emitters[id(emitter)] = emitter
        return emitter
        
    def remove_emitter(self, emitter):
        if id(emitter) in self.emitters:
            emitter = self.emitters[id(emitter)]
            emitter.destroy()
            if emitter in self.alive_emitters:
                self.alive_emitters.remove(emitter)
     
    def stop_emitters(self):
        for i in self.emitters:
            self.emitters[i].stop_particles()
        
    def register_emitter(self, emitter):
        if not emitter in self.alive_emitters:
            self.alive_emitters.append(emitter)
    
    def unregister_emitter(self, emitter):
        if emitter in self.alive_emitters:
            self.alive_emitters.remove(emitter)

    def update(self, dt):
        if not self.active:
            return
        for emitter in self.alive_emitters:
            emitter.update(dt)


class Emitter(Scatter):
    def __init__(
        self, 
        effect_manager,
        emitter_name,
        effect_data,
        parent_layer=None, 
        attach_to=None,
        **kargs
    ):
        Scatter.__init__(self, **kargs)
        self.emitter_name = emitter_name
        self.particles = []
        self.effect_manager = effect_manager
        self.parent_layer = parent_layer
        self.attach_to = attach_to
        self.emitter_data = effect_data.emitter_data
        self.particle_data = effect_data.particle_data
        self.alive_particles = []
        self.attach_offset = Vector(self.pos)
        particle_count = self.emitter_data.get("particle_count", 10)
        self.create_particles(self.particle_data, particle_count)

    def create_particles(self, particle_data, particle_count):
        for i in range(particle_count):
            particle = Particle(self)
            particle.create(**particle_data)
            self.particles.append(particle)
    
    def destroy(self):
        for particle in self.particles:
            particle.destroy()
        self.alive_particles = []
        self.particles = []

        if self.parent:
            self.parent.remove_widget(self)
        
    def play(self):
        self.effect_manager.register_emitter(self)
        
        if self.parent is None:
            self.parent_layer.add_widget(self)
            
        for particle in self.particles:
            particle.play()
            
    def stop(self):
        for particle in self.alive_particles:
            particle.stop(True)
    
    def register_particle(self, particle):
        if not particle in self.alive_particles:
            self.alive_particles.append(particle)
    
    def unregister_particle(self, particle):
        if particle in self.alive_particles:
            self.alive_particles.remove(particle)
        if self.alive_particles == []:
            self.effect_manager.unregister_emitter(self)

    def update(self, dt):
        if self.attach_to:
            self.pos = add(self.attach_to.pos, self.attach_offset)
        for particle in self.alive_particles:
            particle.update(dt)


class Particle(Widget):
    def __init__(self, emitter):
        Widget.__init__(self)
        self.emitter = emitter
        self.is_first_time = True
        self.is_alive = False
        self.elapse_time = 0.0
        self.acc_time = 0.0
        self.curr_texture = None
        self.curr_sequence = [0,0]
        self.cell_size = [1.0, 1.0]
        self.cell_count = 1
        self.old_sequence = -1
        self.area = [0,0,Window.width,Window.height]
        self.box_rot = None
        self.box_pos = None
        self.num_loop = -1
        
        # variation
        self.texture = None
        self.is_world_space = False
        self.collision = False
        self.loop = -1 # -1 is infinite
        self.fade = 0.0
        self.sequence = [1,1]
        self.play_speed = 1.0
        self.elastin = 0.8
        
        # range variable
        self.delay = 0.0
        self.life_time = 1.0
        self.gravity = 980.0
        self.velocity = [0.0, 0.0]
        self.angular_velocity = 0.0
        self.rotate = 0.0
        self.scaling = 1.0
        self.opacity = 1.0
        self.offset = (0.0, 0.0)
        self.variables = {
            'delay':RangeVar(self.delay),
            'life_time':RangeVar(self.life_time),
            'gravity':RangeVar(self.gravity),
            'velocity':RangeVar(self.velocity),
            'angular_velocity':RangeVar(self.angular_velocity),
            'rotate':RangeVar(self.rotate),
            'scaling':RangeVar(self.scaling),
            'opacity':RangeVar(self.opacity),
            'offset':RangeVar(self.offset)
        }
            
    def create(self,
            is_world_space=True,
            elastin=0.8, 
            collision=False, 
            size=[100,100], 
            texture=None,
            loop=1, 
            fade=0.0,
            sequence=[1,1], 
            play_speed=1.0,
            color=(1,1,1,1),
            **kargs):
        self.is_world_space = is_world_space
        self.collision = collision
        self.elastin = max(min(elastin, 1.0), 0.0)
        self.size = size
        self.loop = loop
        self.fade = fade
        self.texture = texture
        self.sequence = sequence
        self.play_speed = play_speed 
        if self.sequence[0]==1 and self.sequence[1]==1:
            self.play_speed = 0

        # range variables
        for (key, value) in kargs.items():
            if hasattr(self, key):
                self.variables[key] = value
            
        # create rectangle
        texture_size = self.texture.size if self.texture else self.size
        self.cell_count = self.sequence[0] * self.sequence[1]
        self.cell_size = div(texture_size, self.sequence)
        curr_texture = None
        if self.texture:
            self.texture.get_region(0.0, 0.0, * self.cell_size)
        with self.canvas:
            Color(*color)
            self.box = Rectangle(texture=curr_texture, pos=(0,0), size=self.size)
        with self.canvas.before:
            PushMatrix()
            self.box_pos = Translate(0,0)
            self.box_rot = Rotate(angle=0, axis=(0,0,1), origin=mul(mul(self.size, 0.5), self.scaling))
            self.box_scale = Scale(1,1,1)
        with self.canvas.after:
            PopMatrix()
    
    def play(self):
        self.emitter.register_particle(self)
        self.area = (
            0,
            0,
            self.emitter.parent_layer.size[0],
            self.emitter.parent_layer.size[1]
        )
        self.is_alive = True
        self.num_loop = self.loop
        self.elapse_time = 0.0
        self.old_sequence = -1
        if self.parent:
            self.parent.remove_widget(self)
        self.spawn_particle()

    def spawn_particle(self, is_update_only_translate = False):
        if not is_update_only_translate:
            for key in self.variables:
                setattr(self, key, self.variables[key].get()) 
            self.velocity = div(self.velocity, self.scaling)
            self.real_size = mul(self.size, self.scaling)
            self.box_rot.origin = mul(mul(self.size, 0.5), self.scaling)
            self.box_rot.angle = self.rotate
            self.box_scale.xyz = (self.scaling, self.scaling, self.scaling)
        # reset translate
        self.box_pos.x = -self.real_size[0] * 0.5 + self.offset[0]
        self.box_pos.y = -self.real_size[1] * 0.5 + self.offset[1]
        if self.is_world_space:
            self.box_pos.x += self.emitter.center[0]
            self.box_pos.y += self.emitter.center[1]
        else:
            self.box_pos.x += self.emitter.size[0] * 0.5
            self.box_pos.y += self.emitter.size[1] * 0.5

    def update_sequence(self):
        if self.texture and self.cell_count > 1 and self.play_speed > 0:
            ratio = self.elapse_time / self.life_time
            ratio *= self.play_speed
            ratio %= 1.0
            index = int(math.floor(self.cell_count * ratio))
            if index == self.old_sequence:
                return
            if index == self.cell_count:
                index = self.cell_count - 1
            self.old_sequence = index
            self.curr_sequence = [index % self.sequence[0], self.sequence[1]-int(index / self.sequence[0])-1]
            self.curr_sequence = mul(self.curr_sequence, self.cell_size)
            self.box.texture = self.texture.get_region(*(self.curr_sequence + self.cell_size))

    def update(self, dt):
        if not self.is_alive:
            return
    
        if not self.parent:
            self.delay -= dt
            if self.delay < 0.0:
                if self.is_world_space:
                    self.emitter.parent_layer.add_widget(self)
                else:
                    self.emitter.add_widget(self) 
                self.spawn_particle(is_update_only_translate = True)
            else:
                return
        
        self.acc_time += dt
        self.elapse_time += dt
        
        if self.elapse_time > self.life_time:
            self.elapse_time -= self.life_time
            if self.num_loop > 0:
                self.num_loop -= 1
            if self.num_loop == 0:
                self.destroy()
                return
            self.spawn_particle()
        
        if self.life_time > 0: 
            life_ratio = self.elapse_time / self.life_time
        
        self.update_sequence()
        
        if self.gravity != 0:
            self.velocity[1] -= self.gravity * dt
        
        # adjust velocity, move
        if self.collision:
            self.box_pos.x += self.velocity[0] * dt
            self.box_pos.y += self.velocity[1] * dt
            if self.box_pos.x < self.area[0]:
                self.box_pos.x = -self.box_pos.x
                self.velocity[0] = -self.velocity[0] * self.elastin
            elif self.box_pos.x > self.area[2] - self.size[0]:
                self.box_pos.x = (self.area[2] - self.size[0])* 2.0 - self.box_pos.x
                self.velocity[0] = -self.velocity[0] * self.elastin
            if self.box_pos.y < self.area[1]:
                self.box_pos.y = -self.box_pos.y
                self.velocity[1] = -self.velocity[1] * self.elastin
            elif self.box_pos.y > self.area[3] - self.size[1]:
                self.box_pos.y = (self.area[3] - self.size[1]) * 2.0 - self.box_pos.y
                self.velocity[1] = -self.velocity[1] * self.elastin
        else:
            if self.velocity[0] != 0:
                self.box_pos.x += self.velocity[0] * dt
            if self.velocity[1] != 0:
                self.box_pos.y += self.velocity[1] * dt

        if self.angular_velocity != 0.0:
            self.box_rot.angle += self.angular_velocity * dt
            
        if self.fade:
            opacity = 1.0 - life_ratio
            opacity = max(min(opacity,1.0), 0.0)
            self.opacity = pow(opacity, self.fade)
            
    def stop(self, is_stop):
        self.is_alive = not is_stop
        
    def destroy(self):
        self.is_alive = False
        self.emitter.unregister_particle(self)
        if self.parent:
            self.parent.remove_widget(self)     
