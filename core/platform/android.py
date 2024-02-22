import traceback
import android
from android.permissions import request_permissions, Permission
from android.runnable import run_on_ui_thread
from android.storage import primary_external_storage_path
from jnius import autoclass
from kivy.logger import Logger
from utility.kivy_helper import log_info
from .default import BasePlatformAPI


class AndroidPlatformAPI(BasePlatformAPI): 
    def __init__(self):
        try:
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])
        except:
            Logger.info(traceback.format_exc())
        self.AndroidString = autoclass('java.lang.String')
        self.AndroidActivityInfo = autoclass('android.content.pm.ActivityInfo')
        self.AndroidPythonActivity = autoclass('org.kivy.android.PythonActivity')
        self.activity = self.AndroidPythonActivity.mActivity
        
    def get_app_directory(self):
        sd_card = primary_external_storage_path()
        return sd_card
    
    def get_home_directory(self):
        return primary_external_storage_path()
        
    @run_on_ui_thread      
    def set_orientation(self, orientation="all"):
        request_orientation = self.AndroidActivityInfo.SCREEN_ORIENTATION_SENSOR
        if "landscape" == orientation:
            request_orientation = self.AndroidActivityInfo.SCREEN_ORIENTATION_LANDSCAPE
        elif "portrait" == orientation:
            request_orientation = self.AndroidActivityInfo.SCREEN_ORIENTATION_PORTRAIT
        self.activity.setRequestedOrientation(request_orientation)
        
