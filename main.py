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
    app = MainApp.instance("KivyStartKit")
    
    # register apps
    from javis.javis import JavisApp
    app.register_app(JavisApp.instance("Javis"))
    
    from KivyRPG.main import KivyRPGApp
    app.register_app(KivyRPGApp.instance("KivyRPGApp"))
    
    # run application
    app.run()
    Logger.info("Bye")
    Config.write()


if __name__ == '__main__':
    run()
