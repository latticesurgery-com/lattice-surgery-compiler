import pytest

from lsqecc.pauli_rotations.circuit import PauliOpCircuit

from .generate_tests_circuit import (
    generate_tests_are_commuting,
    generate_tests_circuit_has_measurements,
    generate_tests_count_rotations_by,
    generate_tests_join_different_qubit_num,
    generate_tests_join_same_qubit_num,
    generate_tests_pauli_op_circuit_equality,
)


@pytest.mark.parametrize(
    "pauli_op_circuit_1, pauli_op_circuit_2", generate_tests_pauli_op_circuit_equality(for_eq=True)
)
def test_pauli_op_circuit_eq(pauli_op_circuit_1, pauli_op_circuit_2):
    assert pauli_op_circuit_1 == pauli_op_circuit_2


@pytest.mark.parametrize(
    "pauli_op_circuit_1, pauli_op_circuit_2", generate_tests_pauli_op_circuit_equality("ne")
)
def test_pauli_op_circuit_ne(pauli_op_circuit_1, pauli_op_circuit_2):
    assert pauli_op_circuit_1 != pauli_op_circuit_2


@pytest.mark.parametrize("input, expected", generate_tests_circuit_has_measurements())
def test_circuit_has_measurement(input, expected):
    assert input.circuit_has_measurements() == expected


@pytest.mark.parametrize("input1, input2, expected", generate_tests_are_commuting())
def test_are_commuting(input1, input2, expected):
    assert PauliOpCircuit.are_commuting(input1, input2) == expected


# @pytest.mark.parametrize("input, expected", generate_tests_apply_transformation())
# def test_apply_transformation(input, expected):
#     assert input.apply_transformation() == expected


@pytest.mark.parametrize("circuit1, circuit2, expected", generate_tests_join_same_qubit_num())
def test_join_same_qubit_num(circuit1, circuit2, expected):
    assert PauliOpCircuit.join(circuit1, circuit2) == expected


@pytest.mark.parametrize("circuit1, circuit2", generate_tests_join_different_qubit_num())
def test_join_different_qubit_num(circuit1, circuit2):
    with pytest.raises(Exception):
        PauliOpCircuit.join(circuit1, circuit2)


@pytest.mark.parametrize("circuit, fraction, expected", generate_tests_count_rotations_by())
def test_count_rotations_by(circuit, fraction, expected):
    assert circuit.count_rotations_by(fraction) == expected


# def test_remove_y_operators_from_circuit(output, expected):
#     raise NotImplementedError
#     # assert output == expected
