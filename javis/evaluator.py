import time

from javis.definition import WillingType, MachineState


class Evaluator:
    def __init__(self, memory):
        self.memory = memory

    def update_evaluator(self):
        while True:
            time.sleep(0)

            if type(self.memory.listener_data.listen_data) is str and self.memory.listener_data.listen_data.lower().startswith("quit"):
                self.memory.evaluator_data.willing_type = WillingType.ShouldExit

            if self.memory.machine_state == MachineState.PrepareToExit:
                break
        print("end - evaluator")
