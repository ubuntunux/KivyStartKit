from glob import glob
import os
from kivy.config import Config
from .constants import *
Config.set('graphics', 'minimum_width', 320)
Config.set('graphics', 'minimum_height', 240)
log_folder = Config.get('kivy', 'log_dir')
if log_folder != LOG_FOLDER:
    Config.set('kivy', 'log_name', '%Y%m%d_%H%M%S_%_.log')
    Config.set('kivy', 'log_maxfiles', MAX_LOG_NUM)
    Config.set('kivy', 'log_dir', LOG_FOLDER)

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
