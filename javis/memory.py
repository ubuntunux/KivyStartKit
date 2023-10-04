from javis.definition import WillingType, MachineState


class EvaluatorData:
    def __init__(self):
        self.willing_type = WillingType.Nothing


class ListenerData:
    def __init__(self):
        self.listen_data = None


class Memory:
    def __init__(self):
        self.master_name = None
        self.machine_state = MachineState.Boot
        self.listener_data = ListenerData()
        self.evaluator_data = EvaluatorData()
