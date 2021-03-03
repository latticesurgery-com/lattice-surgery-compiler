import enum
from rotation import *
from typing import *


class ActivityType(enum.Enum):
    Unitary = "Unitary"
    Measurement = "Measurement"

class QubitActivity:
    # TODO refactor to simplify here and remove QubitInMeasurementActivity
    def __init__(self, op:PauliOperator, activity_type: ActivityType):
        self.op = op
        self.activity_type = activity_type
    def ket_repr(self):
        if self.activity_type == ActivityType.Unitary: return self.op.value
        if self.activity_type == ActivityType.Measurement: return self.op.value + "->"

class QubitState:
    def ket_repr(self):
        raise Exception("Method not implemented")

    def compose_operator(self, op: PauliOperator):
        return self # Do nothing

    def apply_measurement(self, basis: PauliOperator):
        raise Exception("Method not implemented")

class SymbolicState(QubitState):
    def __init__(self, name : str):
        super().__init__()
        self.name = name

    def ket_repr(self):
        return self.name

    def compose_operator(self, op: PauliOperator):
        return ActiveState(self, InitializeableState.UnknownState, QubitActivity(op,ActivityType.Unitary))

    def apply_measurement(self, basis: PauliOperator):
        return ActiveState(self,
                           InitializeableState.UnknownState,
                           QubitActivity(basis,ActivityType.Measurement))

class ActiveState(QubitState):
    def __init__(self, prev: QubitState, next: QubitState, activity: QubitActivity):
        self.prev = prev
        self.next = next
        self.activity = activity

    def ket_repr(self):
        return self.activity.ket_repr() + self.prev.ket_repr()

    def disappears(self):
        return self.activity.activity_type == ActivityType.Measurement



class InitializeableState(SymbolicState):

    Zero = SymbolicState('|0>')
    Plus = SymbolicState('|+>')
    YEigenState = SymbolicState('|Y>')
    UnknownState = SymbolicState('|?>')
    Magic = SymbolicState('|m>') # magic state (|0>+e^(pi*i/4)|1>)/sqrt(2)

