from enum import Enum

class ActionState(Enum):
    IDLE = 0
    ATTACK = 1


class Action:
    def __init__(self, action_data):
        self.action_data = action_data
        self.action_state = ActionState.IDLE
        self.action_time = 0.0
        self.action_time_map = {
            ActionState.IDLE: 0,
            ActionState.ATTACK: 0.1
        }
   
    def is_action_state(self, action_state):
        return self.action_state == action_state
     
    def get_action_state(self):
        return self.action_state
    
    def set_action_state(self, action_state):
        self.action_state = action_state
        self.action_time = self.action_time_map.get(action_state, 1.0)
        
    def get_current_texture(self):
        action_data = self.action_data.get("idle")
        if action_data:
            return action_data.texture
        return None
        
    def update_action(self, dt):
        if ActionState.IDLE != self.action_state:
            if self.action_time < 0:
                self.set_action_state(ActionState.IDLE)
            self.action_time -= dt
 
