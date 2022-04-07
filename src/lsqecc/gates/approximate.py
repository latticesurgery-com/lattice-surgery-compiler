from fractions import Fraction
from typing import Sequence

from lsqecc.gates import gates
from lsqecc.gates.compress_rotation_approximations import partition_gate_sequence
from lsqecc.gates.gridsynth_interface import GridsynthInterface
from lsqecc.pauli_rotations.rotation import PauliOperator


def approximate_rz(rz_gate: "gates.RZ", compress_rotations: bool = False) -> Sequence["gates.Gate"]:
    """Get the Clifford+T approximation of a an rz gate.
    Currently ony supports arguments of the form pi/2^n.
    """

    approximation_gates = GridsynthInterface.get_approximation(10, rz_gate.phase)
    if compress_rotations:
        approximation_gates = partition_gate_sequence(approximation_gates)
    approx_gates = []

    for gate in approximation_gates:
        if gate == "S":
            approx_gates.append(
                gates.PauliRotations(
                    target_qubit=rz_gate.target_qubit, phase=Fraction(1, 2), axis=PauliOperator.Z
                )
                if compress_rotations
                else gates.S(rz_gate.target_qubit)
            )
        elif gate == "T":
            approx_gates.append(
                gates.PauliRotations(
                    target_qubit=rz_gate.target_qubit, phase=Fraction(1, 4), axis=PauliOperator.Z
                )
                if compress_rotations
                else gates.T(rz_gate.target_qubit)
            )
        elif gate == "X":
            approx_gates.append(gates.X(rz_gate.target_qubit))
        elif gate == "H":
            approx_gates.append(gates.H(rz_gate.target_qubit))
        elif len(gate) > 1:
            approx_gates.append(from_gate_string(rz_gate.target_qubit, gate))
        else:
            raise Exception(f"Cannot decompose gate: {gate}")

    # Note that it might be possible to simplify these a little further
    return approx_gates


def count_s_and_t_to_phase(gate_string: str) -> Fraction:
    s_count = gate_string.count("S")
    t_count = gate_string.count("T")
    phase = s_count * Fraction(1, 2) + t_count * Fraction(1, 4)
    return phase


def from_gate_string(target_qubit: int, gate_string: str):
    if gate_string.startswith("H") and gate_string.endswith("H"):
        return gates.PauliRotations(
            target_qubit, phase=count_s_and_t_to_phase(gate_string), axis=PauliOperator.X
        )
    else:
        return gates.PauliRotations(
            target_qubit, phase=count_s_and_t_to_phase(gate_string), axis=PauliOperator.Z
        )
