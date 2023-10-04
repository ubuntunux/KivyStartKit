import os
import traceback 
from kivy.graphics import Color
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.widget import Widget
import numpy as np

from javis import javis
from utility.kivy_helper import *

class Commander:
    def __init__(self, app):
        self.app = app
        self.commands = {}
        self.regist_command(app)
        
    def get_commands(self):
        keys = list(self.commands.keys())
        keys.sort()
        return keys
        
    def run_command(self, cmd_text):
        app = javis.JavisApp.instance()
        cmds = cmd_text.strip().split()
        cmd = cmds[0]
        if cmd in self.commands:
            self.commands[cmd](cmds)
            return True
        return False

    def regist_command(self, app):
        # perceptron
        def cmd_perceptron(args):
            if 5 == len(args):
                y,x,eta,n = [eval(x) for x in args[1:]]
                y = np.array(y)
                x = np.array(x)
                rgen = np.random.RandomState(1)
                w = rgen.normal(loc=0.0, scale=0.01, size=1+x.shape[1])
                
                for i in range(n):
                    net_input = np.dot(x, w[1:]) + w[0]
                    errors = y - net_input
                    w[1:] += eta * x.T.dot(errors)
                    w[0] += eta * errors.sum()
                    cost = (errors**2).sum() / 2.0
                    print("[{0}] Goal: {1}, Predict: {2}, Cost: {3}, Input: {4}, Weights: {5}".format(i,y,net_input,errors,x,w))
                return (w[1:],w[0])      
            else:
                print("ex) perceptron y(goal) x(init) w(weight) r(learning ratio) n(traning num)")
                print("perceptron [-1,1] [[0.1,0.2],[0.3,0.4]] 0.5 20")
            return (0,0)
        self.commands["perceptron"] = cmd_perceptron
   
        # sum of arithmetic sequence
        def cmd_arithmetic_sequence(args):
            if 5 == len(args):
                target = args[1]
                s = lambda a, r, n, m: (m-n+1)*(2*a+r*(n+m-2))/2
                print(s(*[eval(x) for x in args[1:]]))
            else:
                print("ex) arithmetic_sequence a r n m = (m-n+1)*(2*a+r*(n+m-2))/2")
        self.commands["arithmetic_sequence"] = cmd_arithmetic_sequence
        
        # sum of geometric sequence
        def cmd_geometric_sequence(args):
            if 5 == len(args):
                target = args[1]
                s = lambda a, r, n, m: a * (r**m - r**(n-1)) / (r - 1)
                print(s(*[eval(x) for x in args[1:]]))
            else:
                print("ex) geometric_sequence a r n m = a * (r**m - r**(n-1)) / (1 - r)")
        self.commands["geometric_sequence"] = cmd_geometric_sequence
        
        # clear
        def cmd_clear(*args):
            app.clear_output()
        self.commands["clear"] = cmd_clear
        self.commands["cls"] = cmd_clear
        
        # dir
        def cmd_dir(*args):
            for content in os.listdir():
                print(content)
        self.commands["dir"] = cmd_dir
        self.commands["ls"] = cmd_dir
        
        # change dir           
        def cmd_change_directory(cmds):
            if 1 < len(cmds):
                target = cmds[1]
                try:
                    os.chdir(target)
                    print(os.getcwd())
                except:
                    print("No such file or directory: " + target)
            else:
                print("usage: cd directory")
        self.commands["cd"] = cmd_change_directory
        
        # memo
        def cmd_memo(*args):
            memo = MemoApp(app)
            app.screen.add_widget(memo)
        self.commands["memo"] = cmd_memo
        
        return True

class MemoApp(Widget):
    def __init__(self, app):
        super(MemoApp, self).__init__()
        layout = ScatterLayout(size=(500, 400))
        create_rect(layout, (0.2, 0.1, 0.2, 0.9))
        self.add_widget(layout)
        #btn = Button(text='memo', size_hint=(1,1))
        #layout.add_widget(btn)
        
        
    
