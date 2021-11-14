from fractions import Fraction
from typing import List, Tuple

from lsqecc.pauli_rotations.circuit import PauliOpCircuit
from lsqecc.pauli_rotations.rotation import PauliRotation, Measurement, PauliOperator

I = PauliOperator.I  # noqa: E741
X = PauliOperator.X
Y = PauliOperator.Y
Z = PauliOperator.Z


def generate_tests_circuit_has_measurements() -> List[Tuple[bool, bool]]:
    c1 = PauliOpCircuit(4)
    c1.add_pauli_block(PauliRotation.from_list([Z, X, I, Y], Fraction(1, 8)))
    c1.add_pauli_block(PauliRotation.from_list([Z, X, I, Y], Fraction(-1, 8)))

    c2 = PauliOpCircuit(7)
    c2.add_pauli_block(PauliRotation.from_list([X, Y, Z, I, X, Z, Y], Fraction(-1, 4)))
    c2.add_pauli_block(PauliRotation.from_list([I, Z, Z, I, X, X, X], Fraction(1, 8)))
    c2.add_pauli_block(Measurement.from_list([Z, X, I, Z, I, I, I]))
    c2.add_pauli_block(Measurement.from_list([I, I, Z, I, X, X, Z]))

    c3 = PauliOpCircuit(2)
    c3.add_pauli_block(PauliRotation.from_list([Z, Z], Fraction(1, 4)))
    c3.add_pauli_block(Measurement.from_list([X, X]))

    return [
        (c1.circuit_has_measurements(), False),
        (c2.circuit_has_measurements(), True),
        (c3.circuit_has_measurements(), True),
    ]


def generate_tests_pauli_op_circuit_equality(
    case: str,
) -> List[Tuple[PauliOpCircuit, PauliOpCircuit]]:
    c1 = PauliOpCircuit(4)
    c1.add_pauli_block(PauliRotation.from_list([I, X, I, I], Fraction(1, 8)))
    c2 = PauliOpCircuit(4)
    c2.add_pauli_block(PauliRotation.from_list([X, Y, Z, I], Fraction(-1, 4)))
    c2.add_pauli_block(PauliRotation.from_list([I, Z, Z, I], Fraction(1, 8)))
    c3 = PauliOpCircuit(4)
    c3.add_pauli_block(PauliRotation.from_list([X, Y, Z, I], Fraction(-1, 4)))
    c3.add_pauli_block(PauliRotation.from_list([I, Z, Z, I], Fraction(1, 8)))
    c3.add_pauli_block(Measurement.from_list([Y, X, I, I]))
    if case == "eq":
        return [(c1, c1), (c2, c2), (c3, c3)]
    elif case == "ne":
        return [(c1, c2), (c2, c3), (c3, c1)]
    else:
        assert False
