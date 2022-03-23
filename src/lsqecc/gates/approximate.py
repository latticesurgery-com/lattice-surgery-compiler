import math
from fractions import Fraction
from typing import Sequence

from lsqecc.gates import gates
from lsqecc.gates.compress_rotation_approximations import partition_gate_sequence
from lsqecc.gates.pi_over_2_to_the_n_rz_gate_approximations import (
    get_pi_over_2_to_the_n_rz_gate,
)
from lsqecc.pauli_rotations.rotation import PauliOperator
from lsqecc.utils import is_power_of_two


def approximate_rz(rz_gate: "gates.RZ", compress_rotations: bool = False) -> Sequence["gates.Gate"]:
    """Get the Clifford+T approximation of a an rz gate.
    Currently ony supports arguments of the form pi/2^n.
    """

    if not (is_power_of_two(rz_gate.phase.denominator) and rz_gate.phase.numerator == 1):
        raise Exception(f"Can only approximate pi/2^n phase gates, got rz(pi*{rz_gate.phase})")

    denominator_exponent = int(math.log2(rz_gate.phase.denominator))

    approximation_gates = get_pi_over_2_to_the_n_rz_gate[denominator_exponent]
    if compress_rotations:
        approximation_gates = partition_gate_sequence(approximation_gates)
    approx_gates = []

    for gate in approximation_gates:
        if gate == "S":
            approx_gates.append(gates.S(rz_gate.target_qubit))
        elif gate == "T":
            approx_gates.append(gates.T(rz_gate.target_qubit))
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
