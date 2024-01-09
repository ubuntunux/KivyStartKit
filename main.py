from glob import glob

from app.constants import *


def run():
    try:
        # android permission
        from kivy.utils import platform
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
    except:
        pass
          
    # Note: Config must be set before import kivy.logger
    from kivy.config import Config
    Config.read(CONFIG_FILE)
    Config.set('kivy', 'log_level', 'info')
    Config.set('kivy', 'log_enable', 1)
    Config.set('kivy', 'log_name', '%Y%m%d_%H%M%S_%_.log')
    Config.set('kivy', 'log_dir', LOG_FOLDER)
    Config.set('kivy', 'log_maxfiles', MAX_LOG_NUM)
    #Config.set('graphics', 'width', '1920')
    #Config.set('graphics', 'height', '1080')
    Config.write()

    # clear old log
    logs = list(glob("{}/*.log".format(LOG_FOLDER)))
    logs.sort()
    log_count = len(logs)
    if MAX_LOG_NUM <= log_count:
        remove_count = log_count - MAX_LOG_NUM + 1
        for log_file in logs[:remove_count]:
            os.remove(log_file)

    # create main app
    from kivy.logger import Logger
    from app.app import MainApp
    main_app = MainApp.instance("Kivy Start Kit")
 
    # run application
    main_app.run()
    Logger.info("Bye")
    Config.write()


if __name__ == '__main__':
    run()
