from glob import glob
import os

from javis.constants import *

def run_app():     
    log_folder = os.path.abspath('.log')
    log_maxfiles = 10

    # Note: Config must be set before import kivy.logger
    from kivy.config import Config
    Config.read(javis_config_file)
    Config.set('kivy', 'log_level', 'info')
    Config.set('kivy', 'log_enable', 1)
    Config.set('kivy', 'log_name', '%Y%m%d_%H%M%S_%_.log')
    Config.set('kivy', 'log_dir', log_folder)
    Config.set('kivy', 'log_maxfiles', log_maxfiles)
    Config.write()

    # clear old log
    logs = list(glob("{}/*.log".format(log_folder)))
    logs.sort()
    log_count = len(logs)
    if log_maxfiles <= log_count:
        remove_count = log_count - log_maxfiles + 1
        for log_file in logs[:remove_count]:
            os.remove(log_file)

    try:
        # android permission
        from kivy.utils import platform
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
    except:
        pass

    # run app
    from kivy.logger import Logger
    from javis.javis import JavisApp
    javis_app = JavisApp.instance()
    javis_app.run()
    Logger.info("Bye")
    Config.write()


if __name__ == '__main__':
    run_app()
