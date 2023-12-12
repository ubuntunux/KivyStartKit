import math
from kivy.core.window import Window
from kivy.graphics import Scale, Rotate, PushMatrix, PopMatrix, Translate, UpdateNormalMatrix
from kivy.graphics.texture import Texture
from kivy.uix.scatter import Scatter
from kivy.uix.widget import Widget
from kivy.vector import Vector
from utility.singleton import SingletonInstance
from utility.kivy_helper import *
from utility.range_variable import RangeVar


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

    def get_emitter(self, name):
        return self.emitters[name]
        
    def create_emitter(self, name, info, num, **kargs):
        if not self.parent_layer:
            raise AttributeError("Has no parent, first run set_layer..")

        emitter = Emitter(self, self.parent_layer, info, num, **kargs)
        self.emitters[name] = emitter
        return emitter
    
    def create_emitter_with(self, name, info, num, parent_layer):
        emitter = Emitter(self, parent_layer, info, num)
        self.emitters[name] = emitter
        return emitter
        
    def remove_emitter(self, name):
        if name in self.emitters:
            emitter = self.emitters[name]
            emitter.destroy()
            if emitter in self.alive_emitters:
                self.alive_emitters.remove(emitter)
     
    def stop_emitters(self):
        for i in self.emitters:
            self.emitters[i].stop_particles()
        
    def notify_play_emitter(self, emitter):
        if not emitter in self.alive_emitters:
            self.alive_emitters.append(emitter)
    
    def notify_stop_emitter(self, emitter):
        if emitter in self.alive_emitters:
            self.alive_emitters.remove(emitter)

    def update(self, dt):
        if not self.active:
            return
        for emitter in self.alive_emitters:
            emitter.update(dt)


class Emitter(Scatter):
    def __init__(self, effect_manager, parent_layer, particle_info, num, **kargs):
        Scatter.__init__(self, **kargs)
        self.particles = []
        self.effect_manager = effect_manager
        self.create_particle(particle_info, num)
        self.parent_layer = parent_layer
        self.alive_particles = []

    def create_particle(self, info, num):
        self.info = info
        for i in range(num):
            particle = Particle(self)
            particle.create(**info)
            self.particles.append(particle)
    
    def destroy(self):
        for particle in self.particles:
            particle.destroy()
        self.alive_particles = []
        self.particles = []

        if self.parent:
            self.parent.remove_widget(self)
        
    def play_particle(self, parent=None, is_world_space=True):
        self.effect_manager.notify_play_emitter(self)
        emitter_parent = parent if parent else self.parent_layer
        if self.parent and self.parent != emitter_parent:
            self.parent.remove_widget(self)
            
        if self.parent is None:
            emitter_parent.add_widget(self)
            
        attach_to = parent if parent else self
        for particle in self.particles:
            particle.play(attach_to, is_world_space)
            
    def stop_particles(self):
        for particle in self.alive_particles:
            particle.stop(True)
    
    def notify_play_particle(self, particle):
        if not particle in self.alive_particles:
            self.alive_particles.append(particle)
    
    def notify_stop_particle(self, particle):
        if particle in self.alive_particles:
            self.alive_particles.remove(particle)
        if self.alive_particles == []:
            self.effect_manager.notify_stop_emitter(self)

    def update(self, dt):
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
        self.texture = None
        self.curr_texture = None
        self.curr_sequence = [0,0]
        self.cell_size = [1.0, 1.0]
        self.cell_count = 1
        self.old_sequence = -1
        self.attach_to = None
        self.is_world_space = False
        self.box_rot = None
        self.box_pos = None
        self.area = [0,0,Window.width,Window.height]
        
        # variation
        self.collision = False
        self.loop = 1 # -1 is infinite
        self.loop_left = self.loop
        self.fade = 0.0
        self.sequence = [1,1]
        self.play_speed = 1.0
        self.elastin = 0.8
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
            'vel':RangeVar(self.velocity),
            'angular_velocity':RangeVar(self.angular_velocity),
            'rotate':RangeVar(self.rotate),
            'scaling':RangeVar(self.scaling),
            'opacity':RangeVar(self.opacity),
            'offset':RangeVar(self.offset)
        }
            
    def create(self, 
            elastin=0.8, 
            collision=False, 
            size=[100,100], 
            source=None, 
            texture=None, 
            loop=1, 
            fade=0.0,
            sequence=[1,1], 
            play_speed=1.0,
            color=(1,1,1,1),
            **kargs):
        self.collision = collision
        self.elastin = max(min(elastin, 1.0), 0.0)
        self.size = size
        self.loop = loop
        self.fade = fade
        self.sequence = sequence
        self.play_speed = play_speed
        
        if texture == None:
            if source != None:
                self.texture = Image(source=source).texture
        else:
            self.texture=texture
            
        if self.sequence[0]==1 and self.sequence[1]==1:
            self.play_speed = 0

        for key in kargs:
            if not hasattr(self, key):
                raise AttributeError(self.__class__.__name__ + " has not attribue " + key)
            self.variables[key] = kargs[key]
            
        if True:
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

    def play(self, attach_to, is_world_space):
        self.emitter.notify_play_particle(self)
        self.attach_to = attach_to
        self.is_world_space = is_world_space
        self.is_alive = True
        self.loop_left = self.loop
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
        
        if self.attach_to:
            if self.is_world_space:
                parent_center = self.attach_to.to_parent(*mul(self.attach_to.size, 0.5))
                self.box_pos.x += parent_center[0]
                self.box_pos.y += parent_center[1]
            else:
                self.box_pos.x += self.attach_to.size[0] * 0.5
                self.box_pos.y += self.attach_to.size[1] * 0.5

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
            if self.loop_left > 0:
                self.loop_left -= 1
            if self.loop_left == 0:
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
        self.emitter.notify_stop_particle(self)
        if self.parent:
            self.parent.remove_widget(self)     
