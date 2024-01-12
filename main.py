from core.main_app import MainApp

if __name__ == '__main__':
    from core.platform import *
    api = get_platform_api()
    main_app = MainApp.instance("Kivy Start Kit")
    main_app.run()
