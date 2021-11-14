from fractions import Fraction
from typing import List, Tuple

from lsqecc.pauli_rotations.circuit import PauliOpCircuit
from lsqecc.pauli_rotations.rotation import PauliRotation, Measurement, PauliOperator

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


def generate_tests_apply_transformation():
    """
    Three Litinski Rules
    1. Test one --> P, P` commute - Litinski 4a
    2. Test two --> P, P` anti commute - Litinski 4a
    3. Test three --> P, P' commute - Litinski 4b
    4. Test four --> P,P' anti commute - Litinski 4b
    5. Test five --> Controlled Operations, commute - Litinski 4c
    6. Test six --> Controlled Operations, anticommute - Litinski 4c
    """
    tests_list = list()

    # Test 3
    input = PauliOpCircuit(3)
    input.add_single_operator(0, Z, Fraction(1, 4))
    input.add_single_operator(1, X, Fraction(-1, 4))
    input.add_single_operator(2, Z, Fraction(1, 4))
    input.add_pauli_block(Measurement.from_list([Z, I, I]))
    input.add_pauli_block(Measurement.from_list([I, X, I]))
    input.add_pauli_block(Measurement.from_list([I, I, Z]))
    input.apply_transformation()

    print(input)

    expected = PauliOpCircuit(3)
    expected.add_pauli_block(Measurement.from_list([Z, I, I]))
    expected.add_pauli_block(Measurement.from_list([I, X, I], isNegative=True))
    expected.add_pauli_block(Measurement.from_list([I, I, Z]))
    print(expected)
    tests_list.append((input, expected))

    return tests_list
