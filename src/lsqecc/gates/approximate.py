from collections import Sequence

from lsqecc.gates import gates
from lsqecc.gates.pi_over_2_to_the_n_rz_gate_approximations import (
    get_pi_over_2_to_the_n_rz_gate,
)
from lsqecc.utils import is_power_of_two


def approximate_rz(rz_gate: gates.RZ) -> Sequence[gates.Gate]:
    if not (
        is_power_of_two(rz_gate.phase.denominator) and rz_gate.phase.denominator.numerator == 1
    ):
        raise Exception(f"Can only approximate pi/2^n phase gates, got rz(pi*{rz_gate.phase})")

    approximation_gates = []
    for gate_name in get_pi_over_2_to_the_n_rz_gate[rz_gate.phase]:
        if gate_name == "S":
            approximation_gates.append(gates.S(rz_gate.target_qubit))
        elif gate_name == "T":
            approximation_gates.append(gates.T(rz_gate.target_qubit))
        elif gate_name == "X":
            approximation_gates.append(gates.X(rz_gate.target_qubit))
        elif gate_name == "H":
            approximation_gates.append(gates.H(rz_gate.target_qubit))
        else:
            raise Exception(f"Cannot decompose gate: {gate_name}")

    # Note that it might be possible to simplify these a little further
    return approximation_gates
