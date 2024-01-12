from glob import glob
import os

import kivy
from kivy.config import Config
from kivy.core.window import Window
from kivy.logger import Logger

from .constants import *

Config.read(CONFIG_FILE)
Config.set('kivy', 'log_level', 'info')
Config.set('kivy', 'log_enable', 1)
Config.set('kivy', 'log_name', '%Y%m%d_%H%M%S_%_.log')
Config.set('kivy', 'log_dir', LOG_FOLDER)
Config.set('kivy', 'log_maxfiles', MAX_LOG_NUM)

# clear old log
logs = list(glob("{}/*.log".format(LOG_FOLDER)))
logs.sort()
log_count = len(logs)
if MAX_LOG_NUM <= log_count:
    remove_count = log_count - MAX_LOG_NUM + 1
    for log_file in logs[:remove_count]:
        try:
            os.remove(log_file)
        except:
            pass
