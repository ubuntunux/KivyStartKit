from copy import copy
import random


class RangeVar:
  def __init__(self, v1=None, v2=None):
    if v1 == None:
      return
      
    self.min = v1
      
    if v2 != None:
      self.v1 = v1
      self.v2 = v2
      self.max = v2
      if type(v1) == list or type(v1) == tuple:
        self.get = self.getRandList
      else:
        self.get = self.getRandScalar
    else:
      self.v1 = v1
      self.max = v1
      if type(v1) == list or type(v1) == tuple:
        self.get = self.getList
      else:
        self.get = self.getScalar
    
  def setValue(self, v1=None, v2=None):
    self.__init__(v1, v2)
    
  def getMin(self):
    return self.min
  
  def getMax(self):
    return self.max

  def get(self):
    pass

  def getList(self):
    return copy(self.v1)

  def getScalar(self):
    return self.v1

  def getRandList(self):
    return [random.uniform(self.v1[i],self.v2[i]) for i in range(len(self.v1))]

  def getRandScalar(self):
    return random.uniform(self.v1, self.v2)
