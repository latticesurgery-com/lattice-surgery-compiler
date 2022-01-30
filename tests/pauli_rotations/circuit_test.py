from fractions import Fraction
from typing import List

import pytest

from lsqecc.pauli_rotations.circuit import PauliOpCircuit, PauliOperator, PauliRotation
from lsqecc.pauli_rotations.rotation import Measurement, PauliProductOperation

from .generate_tests_circuit import (
    generate_tests_are_commuting,
    generate_tests_circuit_has_measurements,
    generate_tests_count_rotations_by,
    generate_tests_join_different_qubit_num,
    generate_tests_join_same_qubit_num,
    generate_tests_pauli_op_circuit_equality,
)

I = PauliOperator.I  # noqa: E741
X = PauliOperator.X
Y = PauliOperator.Y
Z = PauliOperator.Z


def test_str():
    c = PauliOpCircuit(4)
    assert str(c) == "PauliOpCircuit : 4 qubit(s), 0 block(s)"

    c.name = "test"
    assert str(c) == "PauliOpCircuit test: 4 qubit(s), 0 block(s)"

    c.add_pauli_block(PauliRotation.from_list([I, X, Y, Z], Fraction(1, 2)))
    assert str(c) == "PauliOpCircuit test: 4 qubit(s), 1 block(s)"


@pytest.mark.parametrize(
    "pauli_op_circuit_1, pauli_op_circuit_2", generate_tests_pauli_op_circuit_equality(for_eq=True)
)
def test_pauli_op_circuit_eq(pauli_op_circuit_1, pauli_op_circuit_2):
    assert pauli_op_circuit_1 == pauli_op_circuit_2


@pytest.mark.parametrize(
    "pauli_op_circuit_1, pauli_op_circuit_2", generate_tests_pauli_op_circuit_equality(for_eq=False)
)
def test_pauli_op_circuit_ne(pauli_op_circuit_1, pauli_op_circuit_2):
    assert pauli_op_circuit_1 != pauli_op_circuit_2


@pytest.mark.parametrize("input, expected", generate_tests_circuit_has_measurements())
def test_circuit_has_measurement(input, expected):
    assert input.circuit_has_measurements() == expected


@pytest.mark.parametrize("input1, input2, expected", generate_tests_are_commuting())
def test_are_commuting(input1, input2, expected):
    assert PauliOpCircuit.are_commuting(input1, input2) == expected


def test_are_commuting_diferent_qubit_num():
    block1 = PauliRotation.from_list([I, X, Y, Z], Fraction(1, 2))
    block2 = PauliRotation.from_list([I, X, Y, Z, Y], Fraction(1, 4))

    with pytest.raises(Exception):
        PauliOpCircuit.are_commuting(block1, block2)


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


def test_add_pauli_block():
    circuit = PauliOpCircuit(4)
    circuit.add_pauli_block(PauliRotation.from_list([X, I, Y, Z], Fraction(1, 4)))
    assert circuit.ops[0] == PauliRotation.from_list([X, I, Y, Z], Fraction(1, 4))

    circuit.add_pauli_block(PauliRotation.from_list([Y, X, Z, I], Fraction(1, 4)), 0)
    assert circuit.ops[0] == PauliRotation.from_list([Y, X, Z, I], Fraction(1, 4))


def test_add_pauli_block_different_qubit_num():
    circuit = PauliOpCircuit(1)
    with pytest.raises(Exception):
        circuit.add_pauli_block(PauliRotation.from_list([X, Z], Fraction(1, 4)))


def test_add_single_operator():
    circuit = PauliOpCircuit(4)
    circuit.add_pauli_block(PauliRotation.from_list([X, I, Y, Z], Fraction(1, 4)))
    circuit.add_pauli_block(PauliRotation.from_list([Y, X, Z, I], Fraction(1, 4)))

    circuit.add_single_operator(2, X, Fraction(1, 2))
    assert circuit.ops[2] == PauliRotation.from_list([I, I, X, I], Fraction(1, 2))

    circuit.add_single_operator(1, Y, Fraction(1, 4), 1)
    assert circuit.ops[1] == PauliRotation.from_list([I, Y, I, I], Fraction(1, 4))


@pytest.mark.parametrize(
    "input_circuit_blocks, expected_output_circuit_blocks",
    [
        (
            [PauliRotation.from_list([X], Fraction(1, 2))],
            [PauliRotation.from_list([X], Fraction(1, 2))],
        ),
        (
            [PauliRotation.from_list([X], Fraction(1, 4))],
            [PauliRotation.from_list([X], Fraction(1, 4))],
        ),
        (
            [PauliRotation.from_list([X], Fraction(1, 8))],
            [PauliRotation.from_list([X], Fraction(1, 8))],
        ),
        ([Measurement.from_list([X])], [Measurement.from_list([X])]),
        (
            [PauliRotation.from_list([Y], Fraction(1, 2))],
            [
                PauliRotation.from_list([Z], Fraction(1, 4)),
                PauliRotation.from_list([X], Fraction(1, 2)),
                PauliRotation.from_list([Z], Fraction(-1, 4)),
            ],
        ),
        (
            [PauliRotation.from_list([Y], Fraction(1, 4))],
            [
                PauliRotation.from_list([Z], Fraction(1, 4)),
                PauliRotation.from_list([X], Fraction(1, 4)),
                PauliRotation.from_list([Z], Fraction(-1, 4)),
            ],
        ),
        (
            [PauliRotation.from_list([Y], Fraction(1, 8))],
            [
                PauliRotation.from_list([Z], Fraction(1, 4)),
                PauliRotation.from_list([X], Fraction(1, 8)),
                PauliRotation.from_list([Z], Fraction(-1, 4)),
            ],
        ),
        (
            [Measurement.from_list([Y])],
            [
                PauliRotation.from_list([Z], Fraction(1, 4)),
                Measurement.from_list([X]),
                PauliRotation.from_list([Z], Fraction(-1, 4)),
            ],
        ),
    ],
)
def test_get_y_free_equivalent(
    input_circuit_blocks: List[PauliProductOperation],
    expected_output_circuit_blocks: List[PauliProductOperation],
):
    c = PauliOpCircuit(input_circuit_blocks[0].qubit_num)
    for b in input_circuit_blocks:
        c.add_pauli_block(b)

    output_circuit = c.get_y_free_equivalent()
    assert len(output_circuit.ops) == len(expected_output_circuit_blocks)
    for i, expected_block in enumerate(expected_output_circuit_blocks):
        assert output_circuit.ops[i] == expected_block


@pytest.mark.parametrize(
    "rotation1, rotation2",
    [
        (([X], Fraction(1, 4)), ([I], Fraction(1, 4))),
        (([I, X], Fraction(1, 4)), ([Y, X], Fraction(-1, 8))),
        (([X, Z, Y], Fraction(1, 4)), ([Y, X, Y], Fraction(1, 8))),
        (([I, Z, I, X], Fraction(-1, 4)), ([Z, X, I, Z], Fraction(-1, 8))),
    ],
)
def test_swap_rotation_to_rotation_commuting(rotation1, rotation2):
    # Before commuting: rotation1 ---- rotation2
    test_circuit = PauliOpCircuit(len(rotation1[0]))
    test_circuit.add_pauli_block(PauliRotation.from_list(*rotation1))
    test_circuit.add_pauli_block(PauliRotation.from_list(*rotation2))

    # After commuting: rotation2 ---- rotation1
    test_circuit.swap_adjacent_blocks(0)

    assert test_circuit.ops[0].ops_list == rotation2[0]
    assert test_circuit.ops[0].rotation_amount == rotation2[1]
    assert test_circuit.ops[1].ops_list == rotation1[0]
    assert test_circuit.ops[1].rotation_amount == rotation1[1]


@pytest.mark.parametrize(
    "rotation1, rotation2, rotation2_after",
    [
        (([X], Fraction(1, 4)), ([Z], Fraction(1, 4)), ([Y], Fraction(1, 4))),
        (([Y], Fraction(-1, 4)), ([X], Fraction(-1, 8)), ([Z], Fraction(-1, 8))),
        (([Z, X], Fraction(-1, 4)), ([Y, X], Fraction(1, 8)), ([X, I], Fraction(1, 8))),
        (([X, Z, Y], Fraction(1, 4)), ([Y, X, Z], Fraction(-1, 8)), ([Z, Y, X], Fraction(-1, 8))),
        (([X, Z, Z], Fraction(1, 4)), ([Y, X, Y], Fraction(-1, 8)), ([Z, Y, X], Fraction(1, 8))),
        (
            ([X, Y, X, Z, Z], Fraction(1, 4)),
            ([Z, Y, I, X, Y], Fraction(1, 8)),
            ([Y, I, X, Y, X], Fraction(1, 8)),
        ),
    ],
)
def test_swap_rotation_rotation_anti_commuting(rotation1, rotation2, rotation2_after):
    # Before commuting: rotation1 ---- rotation2
    test_circuit = PauliOpCircuit(len(rotation1[0]))
    test_circuit.add_pauli_block(PauliRotation.from_list(*rotation1))
    test_circuit.add_pauli_block(PauliRotation.from_list(*rotation2))

    # After commuting: rotation2_after ---- rotation1
    test_circuit.swap_adjacent_blocks(0)

    assert test_circuit.ops[0].ops_list == rotation2_after[0]
    assert test_circuit.ops[0].rotation_amount == rotation2_after[1]
    assert test_circuit.ops[1].ops_list == rotation1[0]
    assert test_circuit.ops[1].rotation_amount == rotation1[1]


@pytest.mark.parametrize(
    "rotation, measurement",
    [
        (([X], Fraction(1, 4)), ([I], False)),
        (([I, X], Fraction(1, 4)), ([Y, X], True)),
        (([X, Z, Y], Fraction(1, 4)), ([Y, X, Y], False)),
        (([I, Z, I, X], Fraction(-1, 4)), ([Z, X, I, Z], True)),
    ],
)
def test_swap_rotation_measurement_commuting(rotation, measurement):
    # Before commuting: rotation ---- measurement
    test_circuit = PauliOpCircuit(len(rotation[0]))
    test_circuit.add_pauli_block(PauliRotation.from_list(*rotation))
    test_circuit.add_pauli_block(Measurement.from_list(*measurement))

    # After commuting: measurement ---- rotation
    test_circuit.swap_adjacent_blocks(0)

    assert test_circuit.ops[0].ops_list == measurement[0]
    assert test_circuit.ops[0].isNegative == measurement[1]
    assert test_circuit.ops[1].ops_list == rotation[0]
    assert test_circuit.ops[1].rotation_amount == rotation[1]


@pytest.mark.parametrize(
    "rotation, measurement, measurement_after",
    [
        (([X], Fraction(1, 4)), ([Z], False), ([Y], False)),
        (([Y], Fraction(-1, 4)), ([X], True), ([Z], True)),
        (([Z, X], Fraction(-1, 4)), ([Y, X], False), ([X, I], False)),
        (([X, Z, Y], Fraction(1, 4)), ([Y, X, Z], True), ([Z, Y, X], True)),
        (([X, Z, Z], Fraction(1, 4)), ([Y, X, Y], True), ([Z, Y, X], False)),
        (
            ([X, Y, X, Z, Z], Fraction(1, 4)),
            ([Z, Y, I, X, Y], False),
            ([Y, I, X, Y, X], False),
        ),
    ],
)
def test_swap_rotation_measurement_anticommute(rotation, measurement, measurement_after):
    # Before commuting: rotation ---- measurement
    test_circuit = PauliOpCircuit(len(rotation[0]))
    test_circuit.add_pauli_block(PauliRotation.from_list(*rotation))
    test_circuit.add_pauli_block(Measurement.from_list(*measurement))

    # After commuting: measurement_after ---- rotation
    test_circuit.swap_adjacent_blocks(0)

    assert test_circuit.ops[0].ops_list == measurement_after[0]
    assert test_circuit.ops[0].isNegative == measurement_after[1]
    assert test_circuit.ops[1].ops_list == rotation[0]
    assert test_circuit.ops[1].rotation_amount == rotation[1]


@pytest.mark.parametrize(
    "block1, block2",
    [
        (([X], Fraction(1, 4)), ([Z], False)),
        (([Y], Fraction(-1, 4)), ([X], True)),
        (([Z, X], Fraction(-1, 4)), ([Y, X], Fraction(1, 2))),
        (([X, Z, Y], Fraction(1, 4)), ([Y, X, Z], Fraction(1, 2))),
    ],
)
def test_swap_commute_exception(block1, block2):
    test_circuit = PauliOpCircuit(len(block1[0]))
    test_circuit.add_pauli_block(PauliRotation.from_list(*block1))
    test_circuit.add_pauli_block(Measurement.from_list(*block2))

    with pytest.raises(Exception):
        test_circuit._swap_adjacent_commuting_blocks(0)


@pytest.mark.parametrize(
    "block1, block2",
    [
        (([X], Fraction(1, 4)), ([I], Fraction(1, 4))),
        (([I, X], Fraction(1, 4)), ([Y, X], Fraction(-1, 8))),
        (([X, Z, Y], Fraction(1, 4)), ([Y, X, Y], False)),
        (([I, Z, I, X], Fraction(-1, 4)), ([Z, X, I, Z], True)),
    ],
)
def test_swap_anticommute_exception(block1, block2):
    test_circuit = PauliOpCircuit(len(block1[0]))
    test_circuit.add_pauli_block(PauliRotation.from_list(*block1))
    test_circuit.add_pauli_block(Measurement.from_list(*block2))

    with pytest.raises(Exception):
        test_circuit._swap_adjacent_anticommuting_blocks(0)


def test_swap_no_next_block():
    circuit = PauliOpCircuit(1)
    circuit.add_pauli_block(PauliRotation.from_list([X], Fraction(1, 4)))

    with pytest.raises(Exception):
        circuit.swap_adjacent_blocks(0)


def test_swap_non_pi_over_4_rotation():
    circuit = PauliOpCircuit(1)
    circuit.add_pauli_block(PauliRotation.from_list([X], Fraction(1, 8)))
    circuit.add_pauli_block(PauliRotation.from_list([Y], Fraction(1, 4)))

    with pytest.raises(Exception):
        circuit.swap_adjacent_blocks(0)


def test_render_ascii():
    c = PauliOpCircuit(4)

    c.add_pauli_block(PauliRotation.from_list([I, X, Y, Z], Fraction(1, 2)))
    c.add_pauli_block(PauliRotation.from_list([I, X, Y, Z], Fraction(1, 4)))
    c.add_pauli_block(PauliRotation.from_list([I, X, Y, Z], Fraction(1, 8)))
    c.add_pauli_block(PauliRotation.from_list([I, X, Y, Z], Fraction(-1, 8)))
    c.add_pauli_block(PauliRotation.from_list([I, X, Y, Z], Fraction(1, 16)))
    c.add_pauli_block(PauliRotation.from_list([I, X, Y, Z], Fraction(-1, 16)))
    c.add_pauli_block(Measurement.from_list([I, X, Y, Z]))
    c.add_pauli_block(Measurement.from_list([I, X, Y, Z], True))

    expected_output = (
        " q0--|I|--|I|--|I|--|I|---|I|---|I|--|I|--|I|\n"
        " q1--|X|--|X|--|X|--|X|---|X|---|X|--|X|--|X|\n"
        " q2--|Y|--|Y|--|Y|--|Y|---|Y|---|Y|--|Y|--|Y|\n"
        " q3--|Z|--|Z|--|Z|--|Z|---|Z|---|Z|--|Z|--|Z|\n"
        "pi*  1/2  1/4  1/8 -1/8  1/16 -1/16   M   -M \n"
    )

    assert c.render_ascii() == expected_output
