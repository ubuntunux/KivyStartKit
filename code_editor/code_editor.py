import configparser, tempfile, traceback
from glob import glob
from collections import OrderedDict

from kivy.uix.codeinput import CodeInput
from kivy.uix.textinput import TextInput
from pygments.lexers import CythonLexer
from utility.toast import toast
from utility.singleton import SingletonInstance

class CodeEditorApp(SingletonInstance, CodeInput):
    ui = None
    run_on_enter = None
    dirty = False
    parent_tap = None
    
    def __init__(self, ui, parent_tap, *args, **kargs):
        CodeInput.__init__(self, *args, **kargs)
        self.ui = ui
        self.old_text = ""
        self.parent_tap = parent_tap
        self.filename = ""
        
    def set_filename(self, filename):
        self.filename = filename
        if self.parent_tap:
            if self.filename:
                self.parent_tap.text = os.path.split(filename)[1]
            else:
                self.parent_tap.text = "Untitled"
            if self.dirty:
                self.parent_tap.text += "*"
        
    def set_dirty(self, dirty):
        if self.dirty != dirty:
            self.dirty = dirty
            if dirty:
                self.parent_tap.text += "*"
            else:
                if self.filename and self.parent_tap:
                    self.parent_tap.text = os.path.split(self.filename)[1]
                else:
                    self.parent_tap.text = "Untitled"
        
    def load_file(self, filename):
        try:
            # open file
            f = open(filename, "r")
            lines = list(f)
            f.close()
            self.old_text = self.text = "".join(lines)
            self.set_filename(filename)
            self.set_dirty(False)
            toast("Loaded : " + self.parent_tap.text)
        except:
            toast("Failed to load the file : " + os.path.split(filename)[1])
            log(traceback.format_exc())
            return False
        return True
            
    def save_file(self, force = False):
        if self.dirty or force:
            if self.filename:
                try:
                    f = open(self.filename, "w")
                    f.write(self.text)
                    f.close()
                    self.set_dirty(False)
                    # check already opened document then close
                    gEditorLayout.closeSamedocument(self)
                    toast("Saved : " + self.parent_tap.text)
                except:
                    toast("Failed to save the file : " + os.path.split(filename)[1])
                    log(traceback.format_exc())
            else:
                # untitled.document
                gEditorLayout.setMode(szFileBrowserSaveAs)
    
    def save_as_file(self, filename):
        def do_save():
            self.filename = filename
            self.save_file(force = True)
        # check overwrite
        if self.filename != filename and os.path.isfile(filename):
            gMyRoot.popup("File already exists. Overwrite?", os.path.split(filename)[1], do_save, None)
        else:
            do_save()
    
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        TextInput.keyboard_on_key_down(self, window, keycode, text, modifiers)
        enterKey = 13
        backspaceKey = 8
        key, key_str = keycode
        # set dirty mark
        if not self.dirty and self.old_text != self.text:
            self.set_dirty(True)
            self.old_text = self.text
        if self.run_on_enter and key in (enterKey, backspaceKey):
            self.run_on_enter()
         
   
class EditorLayout():
    document_map = OrderedDict({})
    current_document_tap = None
    text_inputs_scroll_view = None
    editor_input = None
    
    def __init__(self, ui):
        global gEditorLayout
        gEditorLayout = self
        self.ui = ui
        self.reFocusInputText = False
        self.screen = Screen(name = szEditor)
        # document list
        height = kivy.metrics.dp(45)
        self.documentTitlescroll_view = ScrollView(size_hint=(None, None), size=(W, height), pos=(0, H-height))
        self.documentTitleLayout = BoxLayout(size_hint=(None, 1))
        self.documentTitlescroll_view.add_widget(self.documentTitleLayout)
        self.screen.add_widget(self.documentTitlescroll_view)
        
        # menu layout
        height = kivy.metrics.dp(35)
        self.menuLayout = BoxLayout(size_hint=(1, None), height=height)
        self.screen.add_widget(self.menuLayout)
        self.menuDropDown = DropDown(size=(0,0), auto_dismiss=True)
        btn_menu = Button(text="Menu", size_hint_y=None, height=height, background_color=darkGray)
        def menuOpen(inst):
            self.inputBoxForceFocus(False)
            self.menuDropDown.open(inst)
        btn_menu.bind(on_release = menuOpen)
        btn_new = Button(text="New", size_hint_y=None, height=height, background_color=darkGray)
        btn_new.bind(on_release = self.createdocument, on_press=self.menuDropDown.dismiss)
        btn_open = Button(text="Open", size_hint_x=0.3, size_hint_y=None, height=height, background_color=darkGray)
        btn_open.bind(on_release=lambda inst:self.setMode(szFileBrowserOpen), on_press=self.menuDropDown.dismiss)
        btn_close = Button(text="Close", size_hint_y=None, height=height, background_color=darkGray)
        btn_close.bind(on_release=lambda inst:self.closedocument(self.editor_input), on_press=self.menuDropDown.dismiss)
        btn_delete = Button(text="Delete", size_hint_y=None, height=height, background_color=darkGray)
        btn_delete.bind(on_release=lambda inst:self.deletedocument(self.editor_input), on_press=self.menuDropDown.dismiss)
        btn_save = Button(text="Save", size_hint_y=None, height=height, background_color=darkGray)
        btn_save.bind(on_release=lambda inst:self.editor_input.save_file(), on_press=self.menuDropDown.dismiss)
        btn_saveas = Button(text="Save As", size_hint_y=None, height=height, background_color=darkGray)
        btn_saveas.bind(on_release=lambda inst:self.setMode(szFileBrowserSaveAs), on_press=self.menuDropDown.dismiss)
        self.menuDropDown.add_widget(btn_new)
        self.menuDropDown.add_widget(btn_open)
        self.menuDropDown.add_widget(btn_close)
        self.menuDropDown.add_widget(btn_save)
        self.menuDropDown.add_widget(btn_saveas)
        self.menuDropDown.add_widget(btn_delete)
        self.menuLayout.add_widget(self.menuDropDown)
        
        btn_undo = Button(text="Undo", background_color=darkGray)
        btn_undo.bind(on_release=lambda inst:self.editor_input.do_undo())
        btn_redo = Button(text="Redo", background_color=darkGray)
        btn_redo.bind(on_release=lambda inst:self.editor_input.do_redo())
        btn_run = Button(text="Run", background_color=darkGray)
        btn_run.bind(on_release = self.runCode)
        self.menuLayout.add_widget(btn_menu)
        self.menuLayout.add_widget(btn_undo)
        self.menuLayout.add_widget(btn_redo)
        self.menuLayout.add_widget(btn_run)
        
        # screen menu layout
        self.screenMenuLayout = BoxLayout(orientation="horizontal", size_hint=(1, None), height="35dp")
        btn_console = Button(text="Console", background_color=[1.5,0.8,0.8,2])
        btn_editor = Button(text="Code Editor", background_color=[0.8,1.5,0.8,2])
        btn_tutorial = Button(text="Python Tutorial", background_color=[0.8,0.8,1.5,2])
        btn_console.bind(on_release=lambda inst:self.setMode(szConsole))
        btn_tutorial.bind(on_release=lambda inst:self.setMode(szTutorial))
        self.screenMenuLayout.add_widget(btn_console)
        self.screenMenuLayout.add_widget(btn_editor)
        self.screenMenuLayout.add_widget(btn_tutorial)
        self.screen.add_widget(self.screenMenuLayout)
        
        # load last opened document
        self.load_config()
        
        # create document
        if len(self.document_map) == 0:
            self.createdocument()
        self.refreshLayout()
        
    def exit(self):
        self.save_config()
        
    def load_config(self):
        if not os.path.isfile(configFile):
            return
        parser = configparser.Safeconfigparser()
        parser.read(configFile)
        
        # load document section
        doc_section = "documents"
        temp_section = "Tempfiles"
        
        if parser.has_section(doc_section):
            for opt in parser.options(doc_section):
                filename = parser.get(doc_section, opt)             
                # open document
                if os.path.isfile(filename):
                    self.open_file(filename)
                    
                # remove tempfile
                if parser.has_option(temp_section, filename) and self.editor_input and self.editor_input.filename == filename:
                    originFileName = parser.get(temp_section, filename)
                    self.editor_input.set_filename(originFileName)
                    self.editor_input.set_dirty(True)
                    
        # clear temp folder
        for filename in glob(os.path.join(tempDirectory, "*")):
            if os.path.splitext(filename)[1] == "":
                try:
                    os.remove(filename)
                except:
                    log(traceback.format_exc())
        
    def save_config(self):
        # make section
        if len(self.document_map) > 0:
            parser = configparser.Safeconfigparser()
            doc_section = "documents"
            temp_section = "Tempfiles"
            parser.add_section(doc_section)
            parser.add_section(temp_section)
            for i, file_tap in enumerate(self.document_map):
                editor_input = self.document_map[file_tap][1]
                # save temp
                if editor_input.dirty:
                    try:
                        f = tempfile.NamedTemporaryFile(dir = tempDirectory, delete = False)
                        f.write(editor_input.text)
                        f.close()
                        parser.set(doc_section, 'filename%d' % i, f.name)
                        parser.set(temp_section, f.name, editor_input.filename)
                    except:
                        log(traceback.format_exc())
                else:
                    parser.set(doc_section, 'filename%d' % i, editor_input.filename)
            # save config file 
            with open(configFile, 'w') as f:
                parser.write(f)
        
    def createdocument(self, *args):
        # add docjment _tap
        font_size = kivy.metrics.dp(16)
        btn_tap = Button(text="Untitled", size_hint=(None,1), background_color = darkGray)
        btn_tap.width = (len(btn_tap.text) + 2) * font_size
        btn_tap.bind(on_release = self.change_document)
        self.documentTitleLayout.width += btn_tap.width
        self.documentTitleLayout.add_widget(btn_tap)
        self.documentTitlescroll_view.scroll_x = 1
        
        # text input
        editor_input = Editor(ui=self, parent_tap=btn_tap, text = "text", lexer=CythonLexer(), multiline=True, size_hint=(2, None), font_name=defaultFont, auto_indent = True,
            background_color=(.9, .9, .9, 1), font_size="14dp", padding_x="20dp", padding_y="15dp")    
        editor_input.height = editor_input.minimum_height
        editor_input.text = ""
        def refresheditor_inputSize(*args):
            if editor_input.size[1] != editor_input.minimum_height:
                self.refreshLayout()
        editor_input.run_on_enter = refresheditor_inputSize
        editor_input.bind(focus = self.inputBoxFocus)
        
        # textinput scroll view
        text_inputs_scroll_view = ScrollView(size_hint=(None, None), size = (W, editor_input.minimum_height))
        text_inputs_scroll_view.add_widget(editor_input)
        text_inputs_scroll_view.scroll_y = 0
        # add to _map
        self.document_map[btn_tap] = (text_inputs_scroll_view, editor_input)
        # show document
        self.change_document(btn_tap)
        
    def closedocument(self, editor_input, force = False):
        if editor_input:
            _tap = editor_input.parent_tap
            if _tap in self.document_map:
                def close():
                    _tapIndex = self.document_map.keys().index(_tap)
                    scrollView = self.document_map.pop(_tap)[0]
                    if _tap in self.documentTitleLayout.children:
                        self.documentTitleLayout.remove_widget(_tap)
                        self.documentTitleLayout.width -= _tap.width
                    if scrollView.parent:
                        scrollView.parent.remove_widget(scrollView)
                    if len(self.document_map) == 0:
                        self.createdocument()
                    # if current doc, select next document
                    elif self.editor_input == editor_input:
                        _tapIndex = min(_tapIndex, len(self.document_map) -1)
                        self.change_document(self.document_map.keys()[_tapIndex])
                # do close
                if force or not editor_input.dirty:
                    close()
                elif editor_input.dirty:
                    gMyRoot.popup("File has unsaved changes.", "Really close file?", close, None)    
    
    def closeSamedocument(self, editor_input):
        for file_tap in self.document_map:
            cureditor_input = self.document_map[file_tap][1]
            if cureditor_input != editor_input and cureditor_input.filename == editor_input.filename:
                self.closedocument(cureditor_input, force = True)
                break
                
    def deletedocument(self, editor_input):
        if not os.path.isfile(editor_input.filename):
            return 
        filename = os.path.split(editor_input.filename)[1]
        # delete file
        def deleteFile():
            try:
                self.closedocument(editor_input)
                os.remove(editor_input.filename)
                toast("Delete the file : " + filename)
            except:
                log(traceback.format_exc())
        # ask delete?
        gMyRoot.popup("Delete selected file?", filename, deleteFile, None)
            
    def change_document(self, inst):
        if inst in self.document_map and inst != self.current_document_tap:
            # remove keyboard
            self.inputBoxForceFocus(False)
            # old _tap restore color
            if self.current_document_tap:
                self.current_document_tap.background_color = darkGray
            # new _tap color
            inst.background_color = brightBlue
            # set new _tap to current _tap
            self.current_document_tap = inst
            if self.text_inputs_scroll_view and self.text_inputs_scroll_view.parent:
                self.text_inputs_scroll_view.parent.remove_widget(self.text_inputs_scroll_view)
            self.text_inputs_scroll_view, self.editor_input = self.document_map[inst]
            self.screen.add_widget(self.text_inputs_scroll_view)
            self.refreshLayout()
            
    def open_file(self, filename):
        try:
            def load_file():
                result = self.editor_input.load_file(filename)
                if not result:
                    self.closedocument(self.editor_input, True)
            # check opened document
            for file_tap in self.document_map:
                editor_input = self.document_map[file_tap][1]
                if editor_input.filename == filename:
                    self.change_document(file_tap)
                    if editor_input.dirty:
                        gMyRoot.popup("File has unsaved changes.", "Really open file?", load_file, None)
                    break
            else:
                self.createdocument()
                load_file() 
        except:
            log("open file error")    
    
    def save_as(self, filename):
        self.editor_input.save_as_file(filename)
        
    def runCode(self, inst):
        if self.editor_input.text.strip():
            self.ui.onConsoleInput(self.editor_input, True)
            self.setMode(szConsole)
        
    def touchPrev(self):
        if self.editor_input and self.editor_input.focus:
            self.inputBoxForceFocus(False)
        else:
            self.setMode(szConsole)
        
    def setMode(self, mode):
        self.menuDropDown.dismiss()
        self.reFocusInputText = False
        self.inputBoxForceFocus(False)
        self.ui.setMode(mode)
    
    def inputBoxForceFocus(self, bFocus):
        if self.editor_input and bFocus != self.editor_input.focus:
            self.reFocusInputText = False
            self.editor_input.focus = bFocus 
            
    def inputBoxFocus(self, inst, bFocus):
        bAlwaysPreserveFocus = True
        if not bFocus:
            if self.reFocusInputText:
                self.reFocusInputText = bAlwaysPreserveFocus
                inst.focus = True
        self.reFocusInputText = bAlwaysPreserveFocus
        self.refreshLayout()
        
    def refreshLayout(self):
        keyboardHeight = gMyRoot.getKeyboardHeight() if self.editor_input.focus else 0
        height = H - (keyboardHeight + self.menuLayout.height + self.screenMenuLayout.height + self.documentTitlescroll_view.height + topMargin)
        self.documentTitlescroll_view.top = H - topMargin
        self.screenMenuLayout.pos = (0, keyboardHeight)
        self.menuLayout.pos = (0, self.screenMenuLayout.top)
        self.text_inputs_scroll_view.pos = (0, self.menuLayout.top)
        self.text_inputs_scroll_view.size = (W, height)
        self.editor_input.height = max(height, self.editor_input.minimum_height)
        