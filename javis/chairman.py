import time

from javis.definition import WillingType, MachineState


class ChairMan:
    def __init__(self, memory):
        self.memory = memory

    def update_chairman(self):
        while True:
            time.sleep(0)
            if self.memory.evaluator_data.willing_type == WillingType.ShouldExit:
                self.memory.machine_state = MachineState.PrepareToExit
                break
        print("end - chairman")
