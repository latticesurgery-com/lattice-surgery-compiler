import cmath
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
        return ActiveState(self, DefaultSymbolicStates.UnknownState, QubitActivity(op, ActivityType.Unitary))

    def apply_measurement(self, basis: PauliOperator):
        return ActiveState(self,
                           DefaultSymbolicStates.UnknownState,
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




class DefaultSymbolicStates():

    Zero = SymbolicState('|0>')
    One = SymbolicState('|1>')
    Plus = SymbolicState('|+>')
    Minus = SymbolicState('|->')
    YPosEigenState = SymbolicState('|Y_+>')
    YNegEigenState = SymbolicState('|Y_->')
    Magic = SymbolicState('|m>')
    UnknownState = SymbolicState('|?>')

    @staticmethod
    def from_amplitudes(zero_ampl: complex, one_ampl: complex) -> SymbolicState:
        # normalize
        mag = cmath.sqrt(zero_ampl*zero_ampl.conjugate() + one_ampl*one_ampl.conjugate())
        zero_ampl /= mag
        one_ampl  /= mag

        # TODO set global phase to 0

        close = lambda a,b: cmath.isclose(a,b,rel_tol=10**(-9))

        if close(zero_ampl,0): return DefaultSymbolicStates.One
        if close(one_ampl,0):  return DefaultSymbolicStates.Zero
        if close(zero_ampl,cmath.sqrt(2)):
            if close(one_ampl, cmath.sqrt(2)):            return DefaultSymbolicStates.Plus
            if close(one_ampl,-cmath.sqrt(2)):            return DefaultSymbolicStates.Minus
            if close(one_ampl, cmath.sqrt(2)*1j):         return DefaultSymbolicStates.YPosEigenState
            if close(one_ampl,-cmath.sqrt(2)*1j):         return DefaultSymbolicStates.YNegEigenState
            if close(one_ampl, cmath.exp(1j*cmath.pi/4)): return DefaultSymbolicStates.YNegEigenState

        return SymbolicState("{:.2f}|0>\n{:+.2f}|1>".format(zero_ampl,one_ampl))





