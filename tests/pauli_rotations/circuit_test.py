import pytest

from .generate_tests_circuit import *


@pytest.mark.parametrize(
    "pauli_op_circuit_1, pauli_op_circuit_2", generate_tests_pauli_op_circuit_equality("eq")
)
def test_pauli_op_circuit_eq(pauli_op_circuit_1, pauli_op_circuit_2):
    assert pauli_op_circuit_1 == pauli_op_circuit_1


@pytest.mark.parametrize(
    "pauli_op_circuit_1, pauli_op_circuit_2", generate_tests_pauli_op_circuit_equality("ne")
)
def test_pauli_op_circuit_ne(pauli_op_circuit_1, pauli_op_circuit_2):
    assert pauli_op_circuit_1 != pauli_op_circuit_2


@pytest.mark.parametrize("output, expected", generate_tests_circuit_has_measurements())
def test_circuit_has_measurement(output, expected):
    assert output == expected


@pytest.mark.parametrize("output, expected", generate_tests_are_commuting())
def test_are_commuting(output, expected):
    assert output == expected


@pytest.mark.parametrize("output, expected", generate_tests_apply_transformation())
def test_apply_transformation(output, expected):
    assert output == expected


# def test_remove_y_operators_from_circuit(output, expected):
#     raise NotImplementedError
#     # assert output == expected


# def test_commute_pi_over_four_rotations(output, expected):
#     raise NotImplementedError
#     # assert output == expected


# def test_join(output, expected):
#     raise NotImplementedError
#     # assert output == expected


# def test_count_rotations_by(output, expected):
#     raise NotImplementedError
#     # assert output == expected
