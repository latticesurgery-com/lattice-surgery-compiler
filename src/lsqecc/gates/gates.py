from collections import Sequence
from dataclasses import dataclass
from fractions import Fraction

# TODO freeze the gate class
from typing import List

from lsqecc.gates import approximate


@dataclass
class Gate:
    target_qubit: int = 0

    def to_clifford_plus_t(self) -> Sequence["Gate"]:
        return [self]


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

    def to_clifford_plus_t(self) -> Sequence[Gate]:
        if self.phase == Fraction(1, 1):
            return [Z(self.target_qubit)]
        elif self.phase == Fraction(1, 2):
            return [S(self.target_qubit)]
        elif self.phase == Fraction(1, 4):
            return [S(self.target_qubit)]
        else:
            return approximate.approximate_rz(self)


@dataclass
class CRZ(RZ):
    control_qubit: int = 0

    def to_clifford_plus_t(self) -> Sequence[Gate]:
        """
        Use the follwing identity:
        q_0: ─────■─────               ┌───────────┐
             ┌────┴────┐    ---   q_0: ┤ Rz(π/(2n))├──■──────────────────■──
        q_1: ┤ Rz(π/n) ├    ---        ├───────────┤┌─┴─┐┌────────────┐┌─┴─┐
             └─────────┘          q_1: ┤ Rz(π/(2n))├┤ X ├┤ Rz(-π/(2n))├┤ X ├
                                       └───────────┘└───┘└────────────┘└───┘
        """

        gates: List[Gate] = []
        gates.extend(RZ(self.control_qubit, self.phase / 2).to_clifford_plus_t())
        gates.extend(RZ(self.target_qubit, self.phase / 2).to_clifford_plus_t())
        gates.append(CNOT(control_qubit=self.control_qubit, target_qubit=self.target_qubit))
        gates.extend(RZ(self.target_qubit, self.phase / 2).to_clifford_plus_t())
        gates.append(CNOT(control_qubit=self.control_qubit, target_qubit=self.target_qubit))
        return gates
