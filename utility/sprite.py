import math

from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Scale, Rotate, PushMatrix, PopMatrix, Translate, UpdateNormalMatrix
from kivy.logger import Logger
from kivy.uix.image import Image
from kivy.uix.widget import Widget

from utility.kivy_helper import *
from utility.singleton import SingletonInstance


class Sprite(Widget):
  def __init__(self, **kargs):
    Widget.__init__(self)
    # properties
    self.touchable = True
    self.throwable = False
    self.color = Color(1,1,1,1)
    self.source = None
    self.texture_region = None
    self.collision = False
    self.collision_space = (0.0, 0.0, Window.size[0], Window.size[1])
    self.elastin = 0.3
    self.friction = 0.8
    self.gravity = 0.0
    self.velocity = [0.0, 0.0]
    self.rotate = 0.0
    self.angular_velocity = 0.0
    self.scaling = 1.0
    self.opacity = 1.0
    self.offset = (0.0, 0.0)
    # variables
    self.radius = 0
    self.image = None
    self.texture = None
    self.box = None
    self.old_pos = None
    self.box_pos = None
    self.box_rotation = None
    self.box_scale = None
    self.real_size = (0,0)
    self.is_ground = False
    self.is_touched = False
    self.is_attached = False
    self.touch_offset = (0,0)
    self.update_rotation = True
    self.update_translate = True
    self.attach_offsets = {}
    self.delta_time = 0.0
    
    # set argment
    for key in kargs:
      if not hasattr(self, key):
        raise AttributeError(self._class__.__name__ + " not found " + key)
      setattr(self, key, kargs[key])
    # if vel is maybe tuple, convert to list
    self.velocity = list(self.velocity)
      
    # clamp
    self.elastin = max(min(self.elastin, 1.0), 0.0)
    
    # texture region
    if self.source != None:
      self.image = Image(source=self.source)
      if self.image.texture is not None and self.texture_region is not None:
          self.texture = self.image.texture.get_region(*self.texture_region)
      else:
          self.texture = self.image.texture       
    
    with self.canvas:
      self.color = self.color
      self.box = Rectangle(texture=self.texture, pos=(0,0), size=self.size)
    with self.canvas.before:
      PushMatrix()
      self.box_pos = Translate(0,0)
      self.box_rotation = Rotate(angle=0, axis=(0,0,1), origin=mul(mul(self.size, 0.5), self.scaling))
      self.box_scale = Scale(1,1,1)
    with self.canvas.after:
      PopMatrix()
        
    self.box_pos.x = self.pos[0] + (-self.size[0] * 0.5)
    self.box_pos.y = self.pos[1] + (-self.size[1] * 0.5)
    self.pos = (0,0)
    self.old_pos = (self.box_pos.x, self.box_pos.y)
    self.box_rotation.origin = mul(mul(self.size, 0.5), self.scaling)
    self.box_rotation.angle = self.rotate
    self.box_scale.xyz = (self.scaling, self.scaling, self.scaling) 
    self.real_size = mul(self.size, self.scaling)
    self.radius = distance(mul(self.real_size, 0.5))
    
  def on_touch_down(self, touch):
    if not touch.grab_current and not self.is_touched:
      if self.touchable and not self.is_attached:
        if touch.pos[0] > self.box_pos.x and touch.pos[1] > self.box_pos.y and \
          touch.pos[0] < self.box_pos.x + self.real_size[0] and touch.pos[1] < self.box_pos.y + self.real_size[1]:
            self.is_touched = True
            self.set_velocity(0,0)
            self.touch_offset = sub((self.box_pos.x, self.box_pos.y), touch.pos)
            self.set_update_translate(False)
            touch.grab_current = self
          
  def on_touch_move(self, touch):
    if touch.grab_current is self:
      self.set_pos(*add(touch.pos, self.touch_offset))
      self.update_attached_object()
  
  def on_touch_up(self, touch):
    if touch.grab_current is self:
      self.is_touched = False 
      self.set_pos(*add(touch.pos, self.touch_offset))
      if touch.time_update > 0 and self.throwable:
        self.set_velocity(*add(self.velocity, div((touch.dx, touch.dy), self.delta_time)))
      self.set_update_translate(True)
      touch.ungrab(self)
      
  def set_update_translate(self, update):
    self.update_translate = update
    
  @property
  def center(self):
    return (self.box_pos.x + self.real_size[0] * 0.5, self.box_pos.y + self.real_size[1] * 0.5)
    
  @center.setter
  def center(self, center_pos):
    self.box_pos.x = center_pos[0] - self.real_size[0] * 0.5
    self.box_pos.y = center_pos[1] - self.real_size[1] * 0.5
    
  def get_pos(self):
    return (self.box_pos.x, self.box_pos.y)
      
  def set_pos(self, x, y):
    self.old_pos = (self.box_pos.x, self.box_pos.y)
    self.box_pos.x = x
    self.box_pos.y = y
    
  def get_dir(self):
    return normalize(self.velocity)
    
  def get_velocity(self):
    return (self.velocity[0], self.velocity[1])
    
  def set_velocity(self, vx, vy):
    self.velocity[0] = vx
    self.velocity[1] = vy
    
  def get_rotate(self):
    return self.box_rotation.angle
    
  def set_rotate(self, angle):
    self.box_rotation.angle = angle
    
  def get_angular_velocity(self):
    return self.angular_velocity
    
  def set_angular_velocity(self, vel):
    self.angular_velocity = vel
    
  def get_scale(self):
    return self.scaling
    
  def set_scale(self, scale):
    self.scaling = scale
    self.real_size = mul(self.size, self.scaling)
    self.box_scale.xyz = (scale, scale, scale)
  
  def set_attached(self, is_attached):
    self.is_attached = is_attached
    
  def attach(self, child, offset = None):
    if not isinstance(child, Sprite):
      raise TypeError("It is not instance of Sprite")
    if child not in self.attach_offsets:
      child.set_attached(True)
      if offset == None:
        offset = sub(child.get_pos(), self.get_pos())
      self.attach_offsets[child] = offset
      
  def detach(self, child):
    if child in self.attach_offsets:
      child.set_attached(False)
      self.attach_offsets.pop(child)
      
  def detach_all(self):
    while self.attach_offsets:
      self.detach(self.attach_offsets.keys()[0])
      
  def update_attached_object(self):
    for child in self.attach_offsets:
      child.set_pos(*add(self.get_pos(), self.attach_offsets[child]))

  def update(self, dt):
    self.delta_time = dt
    if self.update_translate and not self.is_attached:
      # apply gravity
      if self.gravity != 0:
        self.velocity[1] -= self.gravity * dt
      
      # adjust velocity, move
      self.old_pos = (self.box_pos.x, self.box_pos.y)
      if self.velocity[0] != 0:
        self.box_pos.x += self.velocity[0] * dt
      if self.velocity[1] != 0:
        self.box_pos.y += self.velocity[1] * dt
      
      if self.collision:
        if self.box_pos.x < self.collision_space[0]:
          self.box_pos.x = self.collision_space[0] * 2.0 - self.box_pos.x
          self.velocity[0] = -self.velocity[0] * self.friction
        elif self.box_pos.x > self.collision_space[2] - self.real_size[0]:
          self.box_pos.x = (self.collision_space[2] - self.real_size[0]) * 2.0 - self.box_pos.x
          self.velocity[0] = -self.velocity[0] * self.friction
        if self.box_pos.y < self.collision_space[1]:
          self.box_pos.y = self.collision_space[1] * 2.0 - self.box_pos.y
          self.velocity[1] = -self.velocity[1] * self.elastin
          if self.elastin == 0.0 or self.velocity[1] > 0.0 and self.velocity[1] <= abs(self.gravity * dt):
            self.velocity[1] = 0.0
            self.box_pos.y = self.collision_space[1]
        elif self.box_pos.y > self.collision_space[3] - self.real_size[1]:
          self.box_pos.y = (self.collision_space[3] - self.real_size[1]) * 2.0 - self.box_pos.y
          self.velocity[1] = -self.velocity[1] * self.elastin
      
      if self.old_pos[1] == self.box_pos.y and self.velocity[1] == 0.0:
        self.is_ground = True
      else:
        self.is_ground = False
        
      # update children
      update_attached_object()
          
    if self.update_rotation:
      if self.angular_velocity != 0.0:
        self.box_rotation.angle += self.angular_velocity * dt
