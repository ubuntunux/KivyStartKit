import os
import traceback
from pathlib import Path

import kivy
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.logger import Logger
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from utility.toast import toast
from utility.kivy_helper import *
from utility.kivy_widgets import *

directory = os.path.split(__file__)[0]
configFile = os.path.join(directory, "pyinterpreter.cfg")
tempDirectory = os.path.join(directory, "temp")
pythonLogo = os.path.join(directory, "python_logo.png")
defaultFont = kivy.resources.resource_find(os.path.join(directory, "fonts", "DroidSansMonoDotted.ttf"))

global gFileBrowser

#---------------------#
# CLASS : TouchableLabel
#---------------------#  
class TouchableLabel(Label):
  isDirType = False
  def on_touch_down(self, touch):
    if self.collide_point(*touch.pos):
      selectfile = os.path.join(gFileBrowser.lastDir, self.text[2:] if self.isDirType else self.text)
      if os.path.isdir(selectfile):
        gFileBrowser.open_directory(selectfile)
      elif os.path.isfile(selectfile):
        gFileBrowser.select_file(selectfile)
      
  def setType(self, isDir):
    self.isDirType = isDir
    if isDir:
      self.color = [1,1,0.5,2]
      self.text = "> " + self.text
    else:
      self.color = [1,1,1,1]
       
#---------------------#
# CLASS : FileBrowser
#---------------------#    
class FileBrowser:
  def __init__(self, code_editor):
    global gFileBrowser
    gFileBrowser = self
    self.lastDir = os.path.abspath(".")
    self.is_file_open = False
    self.code_editor = code_editor

  def build_file_browser(self):
    W, H = Window.size 

    # filename input layout
    self.filenameLayout = BoxLayout(orientation = "horizontal", size_hint=(1, None))
    self.filenameInput = TextInput(text="input filename", multiline = False, padding_y="15dp", size_hint=(1,None))
    self.filenameInput.height = kivy.metrics.dp(50)
    self.filenameLayout.height = self.filenameInput.height
    self.filenameInput.bind(focus=self.inputBoxFocus)
    self.btn_ok = Button(text="Ok", size_hint=(0.2,1), background_color=[1,1,1,2])
    def func_ok(inst):
      if self.is_file_open:
        self.open_file()
      else:
        self.save_as()
    self.btn_ok.bind(on_release = func_ok)
    self.filenameLayout.add_widget(self.filenameInput)
    self.filenameLayout.add_widget(self.btn_ok)
    
    # file browser
    self.fileLayout = BoxLayout(orientation="vertical", size_hint=(1,None))
    self.fileSV = ScrollView(size_hint=(1,1))
    self.fileSV.add_widget(self.fileLayout)
    
    # current directory
    self.curDir = Label(text="", text_size=(W * 0.9, None), size_hint_y=None, height=kivy.metrics.dp(50))
    
    # browser layout
    self.browserLayout = BoxLayout(orientation="vertical", pos_hint={"top":1}, size_hint=(1,1))
    self.browserLayout.add_widget(self.curDir)
    self.browserLayout.add_widget(self.fileSV)
    self.browserLayout.add_widget(self.filenameLayout)
    
    self.popup = KivyPopup()
    self.popup.initialize_popup(
        title="File Browser",
        content_widget=self.browserLayout,
        auto_dismiss=True,
        size_hint=(1, 1)
    )
  def open_directory(self, lastDir):
    W, H = (Window.width, Window.height)
    absPath = os.path.abspath(lastDir)
    try:
      lastDir, dirList, fileList = list(os.walk(absPath))[0]
    except:
      Logger.info(traceback.format_exc())
      toast(f"Cannot open directory: {absPath}")
      return False
    self.lastDir = absPath
    self.curDir.text = self.lastDir
    self.fileLayout.clear_widgets()
    fileList = sorted(fileList, key=lambda x:x.lower())
    dirList = sorted(dirList, key=lambda x:x.lower())
    fileList = dirList + fileList
    fileList.insert(0, "..")
    labelHeight = kivy.metrics.dp(25)
    for filename in fileList:
      absFilename = os.path.join(self.lastDir, filename)
      label = TouchableLabel(text=filename, font_size="15dp", size_hint_y = None, size=(W*0.9, labelHeight), shorten=True, shorten_from="right", halign="left")
      label.text_size = label.size
      label.setType(os.path.isdir(absFilename))
      self.fileLayout.add_widget(label)
    self.fileLayout.height = labelHeight * len(self.fileLayout.children)

  def open_file(self):
    self.close()
    if self.filenameInput.text:
      filename = os.path.join(self.lastDir, self.filenameInput.text)
      self.code_editor.open_file(filename)
    
  def save_as(self):
    self.close()
    if self.filenameInput.text:
      filename = os.path.join(self.lastDir, self.filenameInput.text)
      self.code_editor.save_as(filename)
    
  def select_file(self, selectfile):
    # lastdir
    self.lastDir, filename = os.path.split(selectfile)
    if not os.path.isdir(self.lastDir):
      self.lastDir = os.path.abspath(".")
    # set filename
    self.filenameInput.text = filename
    if self.is_file_open:
        self.open_file()
      
  def showOpenLayout(self):
    self.is_file_open = True
    self.btn_ok.text = "Open"
    self.filenameInput.text = ""
    self.popup.open()
    self.open_directory(self.lastDir)
  
  def showSaveAsLayout(self, filepath):
    filepath = Path(filepath)
    if filepath.is_file():
        self.filenameInput.text = filepath.name
        self.lastDir = filepath.parent
    else:
        self.filenameInput.text = ""
    self.is_file_open = False
    self.btn_ok.text = "Save"
    self.popup.open()
    self.open_directory(self.lastDir)
     
  def close(self):
    self.inputBoxForceFocus(False)
    self.popup.dismiss()
     
  def touchPrev(self):
    if self.filenameInput.focus:
      self.inputBoxForceFocus(False)
    else:
      self.close()
    
  def inputBoxForceFocus(self, bFocus):
    if self.filenameInput and bFocus != self.filenameInput.focus:
      self.reFocusInputText = False
      self.filenameInput.focus = bFocus 
      
  def inputBoxFocus(self, inst, bFocus):
    self.refreshLayout(bFocus)
    
  def refreshLayout(self, is_keyboard_open=False):
    return
