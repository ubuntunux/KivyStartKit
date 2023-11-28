class StateMachine(object):
    state_count = 0
    state_list = {}
    current_state = None
    previous_state = None
    
    def __init__(self):
        object.__init__(self)
        self.state_count = 0
        self.state_list = {}
        self.current_state = None
        self.previous_state = None
        
    def add_state(self, stateItem):
        self.state_list[stateItem] = stateItem()
        self.state_count = len(self.state_list)
        stateItem.stateMgr = self
    
    def get_count(self):
        return self.state_count
        
    def is_state(self, index):
        return index == self.current_state
        
    def get_state(self):
        return self.current_state

    def get_stateItem(self):
        if self.current_state:
            return self.state_list[self.current_state]

    def set_state(self, index, reset=False):
        if index:
            if index != self.current_state:
                self.previous_state = self.current_state
                self.current_state = index
                if self.previous_state:
                    self.state_list[self.previous_state].onExit()
                self.state_list[index].onEnter()
            elif reset:
                self.state_list[index].onEnter()

    def update_state(self, *args):
        if self.current_state:
            self.state_list[self.current_state].onUpdate()
    
    def update(self, dt):
        '''must override'''
        pass