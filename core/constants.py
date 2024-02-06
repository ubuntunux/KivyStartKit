import os

DATA_FOLDER = 'data'
APP_DATA_FOLDER = os.path.join('data', 'apps')
DEFAULT_FONT_NAME = os.path.join(DATA_FOLDER, 'fonts/NanumGothic_Coding.ttf')
ICON_FILE = os.path.join(DATA_FOLDER, "icons/icon.png")
LOGO_FILE = os.path.join(DATA_FOLDER, "icons/logo_image.png")
CONFIG_FILE = os.path.join(DATA_FOLDER, 'config.ini')
LOG_FOLDER = os.path.abspath('.log')
MAX_LOG_NUM = 8
