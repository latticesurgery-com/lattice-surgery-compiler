from fractions import Fraction

import pytest

from lsqecc.pauli_rotations import Measurement, PauliOperator, PauliRotation
from lsqecc.pauli_rotations.circuit import PauliOpCircuit

I = PauliOperator.I  # noqa: E741
X = PauliOperator.X
Y = PauliOperator.Y
Z = PauliOperator.Z


def generate_test_pauli_op_circuit(case: str) -> PauliOpCircuit:
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


@pytest.mark.parametrize(
    "pauli_op_circuit_1, pauli_op_circuit_2", generate_test_pauli_op_circuit("eq")
)
def test_pauli_op_circuit_eq(pauli_op_circuit_1, pauli_op_circuit_2):
    assert pauli_op_circuit_1 == pauli_op_circuit_1


@pytest.mark.parametrize(
    "pauli_op_circuit_1, pauli_op_circuit_2", generate_test_pauli_op_circuit("ne")
)
def test_pauli_op_circuit_ne(pauli_op_circuit_1, pauli_op_circuit_2):
    assert pauli_op_circuit_1 != pauli_op_circuit_2
