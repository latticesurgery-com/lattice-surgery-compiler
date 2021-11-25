from fractions import Fraction
from typing import List, Tuple, Union

from lsqecc.pauli_rotations.circuit import PauliOpCircuit
from lsqecc.pauli_rotations.rotation import Measurement, PauliOperator, PauliRotation

I = PauliOperator.I  # noqa: E741
X = PauliOperator.X
Y = PauliOperator.Y
Z = PauliOperator.Z


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


def generate_tests_circuit_has_measurements() -> List[Tuple[PauliOpCircuit, bool]]:
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
        (c1, False),
        (c2, True),
        (c3, True),
    ]


def generate_tests_are_commuting() -> List[
    Tuple[Union[PauliRotation, Measurement], Union[PauliRotation, Measurement], bool]
]:
    tests_list = list()
    block1 = PauliRotation.from_list([X, I, Z, I], Fraction(1, 4))
    block2 = PauliRotation.from_list([I, Z, I, X], Fraction(-1, 4))
    block3 = Measurement.from_list([Z, X, I, Z])
    tests_list.append((block1, block1, True))
    tests_list.append((block1, block2, True))
    tests_list.append((block1, block3, False))
    tests_list.append((block2, block3, True))

    return tests_list


def generate_tests_apply_transformation() -> List[Tuple[PauliOpCircuit, PauliOpCircuit]]:
    """
    Three Litinski Rules
    1. Test 1 --> P, P` commute - Litinski 4a
        Note: Whenever two PauliRotation block are checked from commutation, they always
        commute in the implemented test case
    2. Test 2 --> P, P` anti commute - Litinski 4a
        Note: Whenever two PauliRotation block are checked from commutation, they always
        anti-commute in the implemented test case
    3. Test 3 --> P, P' commute - Litinski 4b
    4. Test 4 --> P,P' anti commute - Litinski 4b
    5. Test 5 --> Controlled Operations, commute - Litinski 4c
        Tests for this is implicitly included in tests 1 and 2, as controlled operations
        are converted Pauli Rotations in load_*() methods
    6. Test 6 --> Controlled Operations, anticommute - Litinski 4c
        Tests for this is implicitly included in tests 1 and 2, as controlled operations
        are converted Pauli Rotations in load_*() methods

    `PauliOpCircuit.commute_pi_over_four_rotations()` are also implicitly tested through these tests
    """
    tests_list = list()
    # Test 1:
    input = PauliOpCircuit(4)
    input.add_pauli_block(PauliRotation.from_list([X, I, Z, I], Fraction(1, 4)))
    input.add_pauli_block(PauliRotation.from_list([I, Z, I, X], Fraction(-1, 8)))
    input.add_pauli_block(PauliRotation.from_list([X, X, I, I], Fraction(-1, 4)))
    input.add_pauli_block(PauliRotation.from_list([I, I, Z, X], Fraction(1, 8)))
    # input.apply_transformation()

    expected = PauliOpCircuit(4)
    expected.add_pauli_block(PauliRotation.from_list([I, Z, I, X], Fraction(-1, 8)))
    expected.add_pauli_block(PauliRotation.from_list([I, I, Z, X], Fraction(1, 8)))
    expected.add_pauli_block(PauliRotation.from_list([X, X, I, I], Fraction(-1, 4)))
    expected.add_pauli_block(PauliRotation.from_list([X, I, Z, I], Fraction(1, 4)))

    tests_list.append((input, expected))
    del input, expected

    # Test 2:
    input = PauliOpCircuit(5)
    input.add_pauli_block(PauliRotation.from_list([X, I, Z, I, I], Fraction(1, 4)))
    input.add_pauli_block(PauliRotation.from_list([Z, Z, I, X, I], Fraction(-1, 8)))
    input.add_pauli_block(PauliRotation.from_list([Y, X, I, Y, I], Fraction(1, 8)))
    input.add_pauli_block(PauliRotation.from_list([Z, Z, Z, Z, Z], Fraction(-1, 4)))
    # input.apply_transformation()

    expected = PauliOpCircuit(5)
    expected.add_pauli_block(PauliRotation.from_list([Y, Z, Z, X, I], Fraction(1, 8)))
    expected.add_pauli_block(PauliRotation.from_list([Z, X, Z, Y, I], Fraction(-1, 8)))
    expected.add_pauli_block(PauliRotation.from_list([Y, Z, I, Z, Z], Fraction(1, 4)))
    expected.add_pauli_block(PauliRotation.from_list([X, I, Z, I, I], Fraction(1, 4)))
    tests_list.append((input, expected))
    del input, expected

    # TODO: Fix tests for Case 3 and Case 4
    # Test 3
    input = PauliOpCircuit(3)
    input.add_single_operator(0, Z, Fraction(1, 4))
    input.add_single_operator(1, X, Fraction(-1, 4))
    input.add_single_operator(2, Z, Fraction(1, 4))
    input.add_pauli_block(Measurement.from_list([Z, I, I]))
    input.add_pauli_block(Measurement.from_list([I, X, I]))
    input.add_pauli_block(Measurement.from_list([I, I, Z]))
    # input.apply_transformation()

    expected = PauliOpCircuit(3)
    expected.add_pauli_block(Measurement.from_list([Z, I, I]))
    expected.add_pauli_block(Measurement.from_list([I, X, I]))
    expected.add_pauli_block(Measurement.from_list([I, I, Z]))
    print(expected)
    tests_list.append((input, expected))
    del input, expected

    return tests_list


def generate_tests_join_same_qubit_num() -> List[
    Tuple[PauliOpCircuit, PauliOpCircuit, PauliOpCircuit]
]:

    tests_list = list()
    c1 = PauliOpCircuit(4)
    c1.add_pauli_block(PauliRotation.from_list([X, I, Z, I], Fraction(1, 4)))
    c1.add_pauli_block(PauliRotation.from_list([I, Z, I, X], Fraction(-1, 8)))
    c1.add_pauli_block(PauliRotation.from_list([X, X, I, I], Fraction(-1, 4)))
    c1.add_pauli_block(PauliRotation.from_list([I, I, Z, X], Fraction(1, 8)))

    c2 = PauliOpCircuit(4)
    c2.add_pauli_block(PauliRotation.from_list([I, Z, I, X], Fraction(-1, 8)))
    c2.add_pauli_block(PauliRotation.from_list([I, I, Z, X], Fraction(1, 8)))
    c2.add_pauli_block(PauliRotation.from_list([X, X, I, I], Fraction(-1, 4)))
    c2.add_pauli_block(PauliRotation.from_list([X, I, Z, I], Fraction(1, 4)))

    c3 = PauliOpCircuit(4)
    c3.add_pauli_block(PauliRotation.from_list([Z, X, Z, Y], Fraction(-1, 8)))
    c3.add_pauli_block(PauliRotation.from_list([Y, Z, Z, X], Fraction(1, 8)))
    c3.add_pauli_block(PauliRotation.from_list([Y, Z, I, Z], Fraction(1, 4)))

    j1 = PauliOpCircuit(4)
    j1.add_pauli_block(PauliRotation.from_list([X, I, Z, I], Fraction(1, 4)))
    j1.add_pauli_block(PauliRotation.from_list([I, Z, I, X], Fraction(-1, 8)))
    j1.add_pauli_block(PauliRotation.from_list([X, X, I, I], Fraction(-1, 4)))
    j1.add_pauli_block(PauliRotation.from_list([I, I, Z, X], Fraction(1, 8)))
    j1.add_pauli_block(PauliRotation.from_list([I, Z, I, X], Fraction(-1, 8)))
    j1.add_pauli_block(PauliRotation.from_list([I, I, Z, X], Fraction(1, 8)))
    j1.add_pauli_block(PauliRotation.from_list([X, X, I, I], Fraction(-1, 4)))
    j1.add_pauli_block(PauliRotation.from_list([X, I, Z, I], Fraction(1, 4)))

    j2 = PauliOpCircuit(4)
    j2.add_pauli_block(PauliRotation.from_list([I, Z, I, X], Fraction(-1, 8)))
    j2.add_pauli_block(PauliRotation.from_list([I, I, Z, X], Fraction(1, 8)))
    j2.add_pauli_block(PauliRotation.from_list([X, X, I, I], Fraction(-1, 4)))
    j2.add_pauli_block(PauliRotation.from_list([X, I, Z, I], Fraction(1, 4)))
    j2.add_pauli_block(PauliRotation.from_list([Z, X, Z, Y], Fraction(-1, 8)))
    j2.add_pauli_block(PauliRotation.from_list([Y, Z, Z, X], Fraction(1, 8)))
    j2.add_pauli_block(PauliRotation.from_list([Y, Z, I, Z], Fraction(1, 4)))

    j3 = PauliOpCircuit(4)
    j3.add_pauli_block(PauliRotation.from_list([Z, X, Z, Y], Fraction(-1, 8)))
    j3.add_pauli_block(PauliRotation.from_list([Y, Z, Z, X], Fraction(1, 8)))
    j3.add_pauli_block(PauliRotation.from_list([Y, Z, I, Z], Fraction(1, 4)))
    j3.add_pauli_block(PauliRotation.from_list([X, I, Z, I], Fraction(1, 4)))
    j3.add_pauli_block(PauliRotation.from_list([I, Z, I, X], Fraction(-1, 8)))
    j3.add_pauli_block(PauliRotation.from_list([X, X, I, I], Fraction(-1, 4)))
    j3.add_pauli_block(PauliRotation.from_list([I, I, Z, X], Fraction(1, 8)))

    tests_list.append((c1, c2, j1))
    tests_list.append((c2, c3, j2))
    tests_list.append((c3, c1, j3))

    return tests_list


def generate_tests_join_different_qubit_num() -> List[Tuple[PauliOpCircuit, PauliOpCircuit]]:
    tests_list = list()
    c1 = PauliOpCircuit(4)
    c1.add_pauli_block(PauliRotation.from_list([X, I, Z, I], Fraction(1, 4)))
    c1.add_pauli_block(PauliRotation.from_list([I, Z, I, X], Fraction(-1, 8)))
    c1.add_pauli_block(PauliRotation.from_list([X, X, I, I], Fraction(-1, 4)))
    c1.add_pauli_block(PauliRotation.from_list([I, I, Z, X], Fraction(1, 8)))

    c2 = PauliOpCircuit(3)
    c2.add_pauli_block(PauliRotation.from_list([Z, I, X], Fraction(-1, 8)))
    c2.add_pauli_block(PauliRotation.from_list([I, Z, X], Fraction(1, 8)))
    c2.add_pauli_block(PauliRotation.from_list([X, I, I], Fraction(-1, 4)))
    c2.add_pauli_block(PauliRotation.from_list([I, Z, I], Fraction(1, 4)))

    c3 = PauliOpCircuit(5)
    c3.add_pauli_block(PauliRotation.from_list([Z, X, Z, Y, X], Fraction(-1, 8)))
    c3.add_pauli_block(PauliRotation.from_list([Y, Z, Z, X, I], Fraction(1, 8)))
    c3.add_pauli_block(PauliRotation.from_list([Y, Z, I, Z, Y], Fraction(1, 4)))

    tests_list.append((c1, c2))
    tests_list.append((c2, c3))
    tests_list.append((c3, c1))

    return tests_list


def generate_tests_count_rotations_by() -> List[Tuple[PauliOpCircuit, Fraction, int]]:

    tests_list = list()

    c1 = PauliOpCircuit(4)
    c1.add_pauli_block(PauliRotation.from_list([X, I, Z, I], Fraction(1, 4)))
    c1.add_pauli_block(PauliRotation.from_list([I, Z, I, X], Fraction(-1, 8)))
    c1.add_pauli_block(PauliRotation.from_list([X, X, I, I], Fraction(-1, 4)))
    c1.add_pauli_block(PauliRotation.from_list([I, I, Z, X], Fraction(1, 8)))
    c1.add_pauli_block(Measurement.from_list([Z, Z, I, I]))

    tests_list.append((c1, Fraction(1, 4), 1))
    tests_list.append((c1, Fraction(-1, 4), 1))
    tests_list.append((c1, Fraction(1, 8), 1))
    tests_list.append((c1, Fraction(1, -8), 1))

    return tests_list
