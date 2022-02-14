from dataclasses import dataclass
from fractions import Fraction


@dataclass
class Gate:
    target_qubit: int = 0

    def to_clifford_plus_t(self):
        return self


@dataclass
class H(Gate):
    pass


@dataclass
class X(Gate):
    pass


@dataclass
class CNOT(Gate):
    control_qubit: int = 0


@dataclass
class Z(Gate):
    pass


@dataclass
class S(Gate):
    pass


@dataclass
class T(Gate):
    pass


@dataclass
class RZ(Gate):
    phase: Fraction = Fraction(1, 1)


@dataclass
class CRZ(RZ):
    control_qubit: int = 0
