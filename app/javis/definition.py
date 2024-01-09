from enum import Enum


class MachineState(Enum):
    Boot = 0
    Normal = 1
    PrepareToExit = 2
    Exit = 3


class WillingType(Enum):
    Nothing = 0
    ShouldExit = 1
