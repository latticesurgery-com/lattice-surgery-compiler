"""
Quantum gates based on the wires they are applied onto.
"""

from dataclasses import dataclass
from fractions import Fraction

# TODO freeze the gate class
from typing import List, Sequence

from lsqecc.gates import approximate
from lsqecc.pauli_rotations.rotation import PauliOperator


@dataclass
class Gate:
    target_qubit: int = 0

    def to_clifford_plus_t(self, compress_rotations: bool = False) -> Sequence["Gate"]:
        """
        args:
            compress_rotations: bool -> Setting this to true will compress H,S,T to PauliRotations
             while approximating RZ rotations
        """
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
class PauliRotations(Gate):
    phase: Fraction = Fraction(1, 1)
    axis: PauliOperator = PauliOperator.Z

    def to_clifford_plus_t(self, compress_rotations: bool = False) -> Sequence["Gate"]:
        if self.axis == PauliOperator.Z:
            if self.phase == Fraction(1, 1):
                return [Z(self.target_qubit)]
            elif self.phase == Fraction(1, 2):
                return [S(self.target_qubit)]
            elif self.phase == Fraction(1, 4):
                return [T(self.target_qubit)]
            else:
                return approximate.approximate_rz(RZ(phase=self.phase), compress_rotations)

        elif self.axis == PauliOperator.X:
            if self.phase == Fraction(1, 1):
                return [X(self.target_qubit)]
            elif self.phase == Fraction(1, 2):
                return [H(self.target_qubit), S(self.target_qubit), H(self.target_qubit)]
            elif self.phase == Fraction(1, 4):
                return [H(self.target_qubit), T(self.target_qubit), H(self.target_qubit)]
            else:
                return (
                    [H(self.target_qubit)]
                    + approximate.approximate_rz(RZ(phase=self.phase), compress_rotations)
                    + [H(self.target_qubit)]
                )
        else:
            raise (Exception("Only X/Z axes are supported as of now!"))


@dataclass
class RZ(Gate):
    phase: Fraction = Fraction(1, 1)

    def to_clifford_plus_t(self, compress_rotations: bool = False) -> Sequence[Gate]:
        if self.phase == Fraction(1, 1):
            return [Z(self.target_qubit)]
        elif self.phase == Fraction(1, 2):
            return [S(self.target_qubit)]
        elif self.phase == Fraction(1, 4):
            return [T(self.target_qubit)]
        else:
            return approximate.approximate_rz(self, compress_rotations)


@dataclass
class CRZ(RZ):
    control_qubit: int = 0

    def to_clifford_plus_t(self, compress_rotations: bool = False) -> Sequence[Gate]:
        # Use the follwing identity:
        # q_0: ─────■─────               ┌───────────┐
        #      ┌────┴────┐    ---   q_0: ┤ Rz(π/(2n))├──■──────────────────■──
        # q_1: ┤ Rz(π/n) ├    ---        ├───────────┤┌─┴─┐┌────────────┐┌─┴─┐
        #      └─────────┘          q_1: ┤ Rz(π/(2n))├┤ X ├┤ Rz(-π/(2n))├┤ X ├
        #                                └───────────┘└───┘└────────────┘└───┘

        gates: List[Gate] = []
        gates.extend(RZ(self.control_qubit, self.phase / 2).to_clifford_plus_t(compress_rotations))
        gates.extend(RZ(self.target_qubit, self.phase / 2).to_clifford_plus_t(compress_rotations))
        gates.append(CNOT(control_qubit=self.control_qubit, target_qubit=self.target_qubit))
        gates.extend(RZ(self.target_qubit, self.phase / 2).to_clifford_plus_t(compress_rotations))
        gates.append(CNOT(control_qubit=self.control_qubit, target_qubit=self.target_qubit))
        return gates
