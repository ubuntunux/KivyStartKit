from kivy.logger import Logger
from kivy.vector import Vector
from kivy.metrics import dp
from utility.kivy_helper import *

TILE_GRASS_COLOR0 = (153, 191, 115, 255)
TILE_GRASS_COLOR1 = (121, 166, 77, 255)
TILE_GRASS_COLOR2 = (94, 142, 47, 255)

TILE_COUNT = 64
TILE_WIDTH = 128
TILE_HEIGHT = TILE_WIDTH
TILE_SIZE = Vector(TILE_WIDTH, TILE_HEIGHT)
GRID_BASED_MOVEMENT = True
MOVEMENT_1D = False 
ATTACK_FORCE = 1000.0

FX_PICK_ITEM = 'pick_item'
FX_HIT = 'hit'
FX_WARN = 'warn'

DAY_TIME = 86400.0
TIME_OF_DAY_SPEED = 24 * 60 / 10
NIGHT_TOD_START = 18.0
NIGHT_TOD_END = 4.0
MORNING_TOD = 8.0

MAX_CRIMINAL = 5.0
CRIMINAL_TIME_RATIO = 10.0
CRIMINAL_TIMES = [0.0, 10.0, 30.0, 60.0, 100.0, 150.0]

ITEM_HP_A = 'items/hp_a'
ITEM_HP_B = 'items/hp_b'
