from kivy.logger import Logger
from kivy.vector import Vector
from utility.kivy_helper import *

TILE_WIDTH = 128
TILE_HEIGHT = TILE_WIDTH
TILE_SIZE = Vector(TILE_WIDTH, TILE_HEIGHT)

def pos_to_tile(pos):
    tile_pos = Vector(pos) / TILE_SIZE
    tile_pos.x = int(tile_pos.x)
    tile_pos.y = int(tile_pos.y)
    return tile_pos
    
def tile_to_pos(tile_pos):
    pos = Vector(tile_pos) * TILE_SIZE
    pos.x += TILE_WIDTH * 0.5
    pos.y += TILE_HEIGHT * 0.5
    return pos
    
def get_next_tile_pos(tile_pos, front):
    next_tile_pos = Vector(tile_pos)
    if abs(front.x) < abs(front.y):
        next_tile_pos.y += sign(front.y)
    else:
        next_tile_pos.x += sign(front.x)
    #Logger.info((tile_pos, front))
    return next_tile_pos