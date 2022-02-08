# Copyright (C) 2020-2021 - George Watkins and Alex Nguyen
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
# USA

from fractions import Fraction
from typing import List

import pytest

from lsqecc.pauli_rotations import (
    Measurement,
    PauliOperator,
    PauliProductOperation,
    PauliRotation,
)

I = PauliOperator.I  # noqa: E741
X = PauliOperator.X
Y = PauliOperator.Y
Z = PauliOperator.Z


def test_cases_get_y_free_equivalent_rotations():
    # TODO: Add more cases here
    case_1 = (
        PauliRotation.from_list([Y, I, Y, Z, Y, Y], Fraction(1, 8)),
        [
            PauliRotation.from_list([Z, I, I, I, I, I], Fraction(1, 4)),
            PauliRotation.from_list([I, I, Z, I, Z, Z], Fraction(1, 4)),
            PauliRotation.from_list([X, I, X, Z, X, X], Fraction(1, 8)),
            PauliRotation.from_list([Z, I, I, I, I, I], Fraction(-1, 4)),
            PauliRotation.from_list([I, I, Z, I, Z, Z], Fraction(-1, 4)),
        ],
    )
    case_2 = (
        PauliRotation.from_list([Y, I, Y, Z, Y, Y], Fraction(1, 2)),
        [
            PauliRotation.from_list([Z, I, I, I, I, I], Fraction(1, 4)),
            PauliRotation.from_list([I, I, Z, I, Z, Z], Fraction(1, 4)),
            PauliRotation.from_list([X, I, X, Z, X, X], Fraction(1, 2)),
            PauliRotation.from_list([Z, I, I, I, I, I], Fraction(-1, 4)),
            PauliRotation.from_list([I, I, Z, I, Z, Z], Fraction(-1, 4)),
        ],
    )
    case_3 = (
        PauliRotation.from_list([Y, Y, Y, Z], Fraction(1, 8)),
        [
            PauliRotation.from_list([Z, Z, Z, I], Fraction(1, 4)),
            PauliRotation.from_list([X, X, X, Z], Fraction(1, 8)),
            PauliRotation.from_list([Z, Z, Z, I], Fraction(-1, 4)),
        ],
    )
    case_4 = (
        PauliRotation.from_list([Y, Y, Y, Z], Fraction(-1, 4)),
        [
            PauliRotation.from_list([Z, Z, Z, I], Fraction(1, 4)),
            PauliRotation.from_list([X, X, X, Z], Fraction(-1, 4)),
            PauliRotation.from_list([Z, Z, Z, I], Fraction(-1, 4)),
        ],
    )

    return [case_1, case_2, case_3, case_4]


class TestPauliRotation:
    """Tests for PauliRotation"""

    @pytest.mark.parametrize(
        "input, fraction",
        [
            ([X], Fraction(1, 8)),
            ([X, Z], Fraction(1, 4)),
            ([X, Z, I, Y, Z], Fraction(1, 2)),
        ],
    )
    def test_from_list(self, input, fraction):
        pauli_rotation = PauliRotation.from_list(input, fraction)
        assert pauli_rotation.ops_list == input
        assert pauli_rotation.qubit_num == len(input)
        assert pauli_rotation.rotation_amount == fraction

    def test_from_list_empty(self):
        with pytest.raises(ValueError):
            PauliRotation.from_list([], Fraction(1, 2))

    def test_from_list_invalid_pauli_operator(self):
        with pytest.raises(TypeError):
            PauliRotation.from_list([X, "X"], Fraction(1, 2))

    @pytest.mark.parametrize(
        "pauli_rotation_1, pauli_rotation_2",
        [
            (PauliRotation(3, Fraction(1, 2)), PauliRotation(3, Fraction(1, 2))),
            (
                PauliRotation.from_list([X, Z], Fraction(1, 4)),
                PauliRotation.from_list([X, Z], Fraction(1, 4)),
            ),
            (
                PauliRotation.from_list([X, Z, Y], Fraction(1, 8)),
                PauliRotation.from_list([X, Z, Y], Fraction(1, 8)),
            ),
        ],
    )
    def test_pauli_rotation_eq(self, pauli_rotation_1, pauli_rotation_2):
        assert pauli_rotation_1 == pauli_rotation_2

    @pytest.mark.parametrize(
        "pauli_rotation_1, pauli_rotation_2",
        [
            (PauliRotation(3, Fraction(1, 2)), PauliRotation(4, Fraction(1, 2))),
            (
                PauliRotation.from_list([X, Z], Fraction(1, 4)),
                PauliRotation.from_list([X, Y], Fraction(1, 4)),
            ),
            (
                PauliRotation.from_list([X, Z, Y], Fraction(1, 8)),
                PauliRotation.from_list([Z, X, Y], Fraction(1, 4)),
            ),
        ],
    )
    def test_pauli_rotation_ne(self, pauli_rotation_1, pauli_rotation_2):
        assert pauli_rotation_1 != pauli_rotation_2

    @pytest.mark.parametrize(
        "input, expected",
        [
            (PauliRotation.from_list([Y], Fraction(1, 2)), "1/2: [Y]"),
            (PauliRotation.from_list([I, X], Fraction(4, 2)), "2: [I, X]"),
            (PauliRotation.from_list([Y, X], Fraction(-0, 5)), "0: [Y, X]"),
            (PauliRotation.from_list([X, Z, Y], Fraction(-6, 8)), "-3/4: [X, Z, Y]"),
        ],
    )
    def test_str(self, input, expected):
        assert str(input) == expected

    def test_hash_equal(self):
        # Equal but distinct object have equal hashes
        assert hash(PauliRotation.from_list([Y, X, Z], Fraction(1, 2))) == hash(
            PauliRotation.from_list([Y, X, Z], Fraction(1, 2))
        )

    @pytest.mark.parametrize(
        "rotation1, rotation2",
        [
            # Different everything
            (([I, X, Z, Y], Fraction(1, 2)), ([Y, X, Z], Fraction(1, 4))),
            # Different angle
            (([Y, X, Z], Fraction(1, 2)), ([Y, X, Z], Fraction(1, 4))),
            # Same angle different ops
            (([Y, X, Z], Fraction(1, 2)), ([Y, X, X], Fraction(1, 2))),
            # Same angle same ops in different order
            (([Y, X, Z], Fraction(1, 2)), ([Y, Z, X], Fraction(1, 2))),
        ],
    )
    def test_hash_not_equal(self, rotation1, rotation2):
        a = PauliRotation.from_list(*rotation1)
        b = PauliRotation.from_list(*rotation2)
        assert hash(a) != hash(b)

    @pytest.mark.parametrize(
        "rotation, expected_decomposition",
        [
            (PauliRotation.from_list([X], Fraction(1, 1)), []),
            (PauliRotation.from_list([X], Fraction(2, 1)), []),
            (
                PauliRotation.from_list([X], Fraction(1, 4)),
                [PauliRotation.from_list([X], Fraction(1, 4))],
            ),
            (
                PauliRotation.from_list([X], Fraction(3, 4)),
                [
                    PauliRotation.from_list([X], Fraction(1, 2)),
                    PauliRotation.from_list([X], Fraction(1, 4)),
                ],
            ),
            (
                PauliRotation.from_list([X], Fraction(7, 8)),
                [
                    PauliRotation.from_list([X], Fraction(1, 2)),
                    PauliRotation.from_list([X], Fraction(1, 4)),
                    PauliRotation.from_list([X], Fraction(1, 8)),
                ],
            ),
            (
                PauliRotation.from_list([X], Fraction(15, 8)),
                [
                    PauliRotation.from_list([X], Fraction(1, 2)),
                    PauliRotation.from_list([X], Fraction(1, 4)),
                    PauliRotation.from_list([X], Fraction(1, 8)),
                ],
            ),
        ],
    )
    def test_to_basic_form_decomposition_cancel_out(
        self, rotation: PauliRotation, expected_decomposition: List[PauliRotation]
    ):
        assert rotation.to_basic_form_decomposition() == expected_decomposition

    def test_to_basic_form_decomposition_with_approximation(self, snapshot):
        snapshot.assert_match(
            repr(PauliRotation.from_list([Z], Fraction(1, 16)).to_basic_form_decomposition()),
            "list_repr.txt",
        )

    @pytest.mark.parametrize(
        "rotation",
        [
            PauliRotation.from_list([Z], Fraction(1, 2)),
            PauliRotation.from_list([X], Fraction(1, 2)),
            PauliRotation.from_list([Z], Fraction(1, 4)),
            PauliRotation.from_list([X], Fraction(1, 8)),
            PauliRotation.from_list([Z], Fraction(1, 8)),
            PauliRotation.from_list([Z], Fraction(1, 16)),
            PauliRotation.from_list([X], Fraction(1, 16)),
            PauliRotation.from_list([I, Z], Fraction(1, 16)),
            PauliRotation.from_list([Z, I], Fraction(1, 16)),
            PauliRotation.from_list([Z], Fraction(1, 2**30)),
        ],
    )
    def test_to_basic_form_approximation(self, rotation: PauliRotation, snapshot):
        snapshot.assert_match(repr(rotation.to_basic_form_approximation()), "list_repr.txt")

    def test_to_basic_form_arbitrary_angle(self):
        with pytest.raises(Exception):
            PauliRotation.from_list([X], Fraction(1, 3)).to_basic_form_approximation()

    @pytest.mark.parametrize(
        "num_qubits, target_qubit, phase_type, phase, expected_rotation",
        [
            (1, 0, PauliOperator.Z, Fraction(1, 1), PauliRotation.from_list([Z], Fraction(1, 2))),
            (1, 0, PauliOperator.X, Fraction(1, 1), PauliRotation.from_list([X], Fraction(1, 2))),
            (1, 0, PauliOperator.Z, Fraction(1, 2), PauliRotation.from_list([Z], Fraction(1, 4))),
            (1, 0, PauliOperator.Z, Fraction(1, 4), PauliRotation.from_list([Z], Fraction(1, 8))),
            (1, 0, PauliOperator.Z, Fraction(1, 8), PauliRotation.from_list([Z], Fraction(1, 16))),
            (1, 0, PauliOperator.Z, Fraction(1, 17), PauliRotation.from_list([Z], Fraction(1, 34))),
            (
                2,
                0,
                PauliOperator.X,
                Fraction(1, 1),
                PauliRotation.from_list([X, I], Fraction(1, 2)),
            ),
            (
                2,
                1,
                PauliOperator.X,
                Fraction(1, 1),
                PauliRotation.from_list([I, X], Fraction(1, 2)),
            ),
            (
                3,
                1,
                PauliOperator.X,
                Fraction(1, 1),
                PauliRotation.from_list([I, X, I], Fraction(1, 2)),
            ),
        ],
    )
    def test_from_r_gate(
        self,
        num_qubits: int,
        target_qubit: int,
        phase_type: PauliOperator,
        phase: Fraction,
        expected_rotation: PauliRotation,
    ):
        assert (
            PauliRotation.from_r_gate(num_qubits, target_qubit, phase_type, phase)
            == expected_rotation
        )

    @pytest.mark.parametrize(
        "num_qubits, target_qubit, expected_rotation",
        [
            (1, 0, PauliRotation.from_list([Z], Fraction(1, 8))),
            (2, 0, PauliRotation.from_list([Z, I], Fraction(1, 8))),
            (2, 1, PauliRotation.from_list([I, Z], Fraction(1, 8))),
            (3, 1, PauliRotation.from_list([I, Z, I], Fraction(1, 8))),
        ],
    )
    def test_from_t_gate(
        self, num_qubits: int, target_qubit: int, expected_rotation: PauliRotation
    ):
        assert PauliRotation.from_t_gate(num_qubits, target_qubit) == expected_rotation

    @pytest.mark.parametrize(
        "num_qubits, target_qubit, expected_rotation",
        [
            (1, 0, PauliRotation.from_list([Z], Fraction(1, 4))),
            (2, 0, PauliRotation.from_list([Z, I], Fraction(1, 4))),
            (2, 1, PauliRotation.from_list([I, Z], Fraction(1, 4))),
            (3, 1, PauliRotation.from_list([I, Z, I], Fraction(1, 4))),
        ],
    )
    def test_from_s_gate(
        self, num_qubits: int, target_qubit: int, expected_rotation: PauliRotation
    ):
        assert PauliRotation.from_s_gate(num_qubits, target_qubit) == expected_rotation

    @pytest.mark.parametrize(
        "num_qubits, target_qubit, expected_rotations",
        [
            (
                1,
                0,
                [
                    PauliRotation.from_list([Z], Fraction(1, 4)),
                    PauliRotation.from_list([X], Fraction(1, 4)),
                    PauliRotation.from_list([Z], Fraction(1, 4)),
                ],
            ),
            (
                2,
                0,
                [
                    PauliRotation.from_list([Z, I], Fraction(1, 4)),
                    PauliRotation.from_list([X, I], Fraction(1, 4)),
                    PauliRotation.from_list([Z, I], Fraction(1, 4)),
                ],
            ),
            (
                2,
                1,
                [
                    PauliRotation.from_list([I, Z], Fraction(1, 4)),
                    PauliRotation.from_list([I, X], Fraction(1, 4)),
                    PauliRotation.from_list([I, Z], Fraction(1, 4)),
                ],
            ),
            (
                3,
                1,
                [
                    PauliRotation.from_list([I, Z, I], Fraction(1, 4)),
                    PauliRotation.from_list([I, X, I], Fraction(1, 4)),
                    PauliRotation.from_list([I, Z, I], Fraction(1, 4)),
                ],
            ),
        ],
    )
    def test_from_hadamard_gate(
        self, num_qubits: int, target_qubit: int, expected_rotations: PauliRotation
    ):
        assert PauliRotation.from_hadamard_gate(num_qubits, target_qubit) == expected_rotations

    @pytest.mark.parametrize(
        "num_qubits, target_qubit, expected_rotation",
        [
            (1, 0, PauliRotation.from_list([X], Fraction(1, 2))),
            (2, 0, PauliRotation.from_list([X, I], Fraction(1, 2))),
            (2, 1, PauliRotation.from_list([I, X], Fraction(1, 2))),
            (3, 1, PauliRotation.from_list([I, X, I], Fraction(1, 2))),
        ],
    )
    def test_from_x_gate(
        self, num_qubits: int, target_qubit: int, expected_rotation: PauliRotation
    ):
        assert PauliRotation.from_x_gate(num_qubits, target_qubit) == expected_rotation

    @pytest.mark.parametrize(
        "num_qubits, control_qubit, target_qubit, expected_rotations",
        [
            (
                2,
                0,
                1,
                [
                    PauliRotation.from_list([Z, X], Fraction(1, 4)),
                    PauliRotation.from_list([Z, I], Fraction(-1, 4)),
                    PauliRotation.from_list([I, X], Fraction(-1, 4)),
                ],
            ),
            (
                2,
                1,
                0,
                [
                    PauliRotation.from_list([X, Z], Fraction(1, 4)),
                    PauliRotation.from_list([I, Z], Fraction(-1, 4)),
                    PauliRotation.from_list([X, I], Fraction(-1, 4)),
                ],
            ),
            (
                3,
                0,
                1,
                [
                    PauliRotation.from_list([Z, X, I], Fraction(1, 4)),
                    PauliRotation.from_list([Z, I, I], Fraction(-1, 4)),
                    PauliRotation.from_list([I, X, I], Fraction(-1, 4)),
                ],
            ),
            (
                3,
                1,
                2,
                [
                    PauliRotation.from_list([I, Z, X], Fraction(1, 4)),
                    PauliRotation.from_list([I, Z, I], Fraction(-1, 4)),
                    PauliRotation.from_list([I, I, X], Fraction(-1, 4)),
                ],
            ),
            (
                3,
                0,
                2,
                [
                    PauliRotation.from_list([Z, I, X], Fraction(1, 4)),
                    PauliRotation.from_list([Z, I, I], Fraction(-1, 4)),
                    PauliRotation.from_list([I, I, X], Fraction(-1, 4)),
                ],
            ),
            (
                3,
                2,
                0,
                [
                    PauliRotation.from_list([X, I, Z], Fraction(1, 4)),
                    PauliRotation.from_list([I, I, Z], Fraction(-1, 4)),
                    PauliRotation.from_list([X, I, I], Fraction(-1, 4)),
                ],
            ),
        ],
    )
    def test_from_cnot_gate(
        self,
        num_qubits: int,
        control_qubit: int,
        target_qubit: int,
        expected_rotations: PauliRotation,
    ):
        assert (
            PauliRotation.from_cnot_gate(num_qubits, control_qubit, target_qubit)
            == expected_rotations
        )

    @pytest.mark.parametrize(
        "num_qubits, control_qubit, target_qubit, expected_rotations",
        [
            (
                2,
                0,
                1,
                [
                    PauliRotation.from_list([Z, Z], Fraction(1, 4)),
                    PauliRotation.from_list([Z, I], Fraction(-1, 4)),
                    PauliRotation.from_list([I, Z], Fraction(-1, 4)),
                ],
            ),
            (
                2,
                1,
                0,
                [
                    PauliRotation.from_list([Z, Z], Fraction(1, 4)),
                    PauliRotation.from_list([I, Z], Fraction(-1, 4)),
                    PauliRotation.from_list([Z, I], Fraction(-1, 4)),
                ],
            ),
            (
                3,
                0,
                1,
                [
                    PauliRotation.from_list([Z, Z, I], Fraction(1, 4)),
                    PauliRotation.from_list([Z, I, I], Fraction(-1, 4)),
                    PauliRotation.from_list([I, Z, I], Fraction(-1, 4)),
                ],
            ),
            (
                3,
                1,
                2,
                [
                    PauliRotation.from_list([I, Z, Z], Fraction(1, 4)),
                    PauliRotation.from_list([I, Z, I], Fraction(-1, 4)),
                    PauliRotation.from_list([I, I, Z], Fraction(-1, 4)),
                ],
            ),
            (
                3,
                0,
                2,
                [
                    PauliRotation.from_list([Z, I, Z], Fraction(1, 4)),
                    PauliRotation.from_list([Z, I, I], Fraction(-1, 4)),
                    PauliRotation.from_list([I, I, Z], Fraction(-1, 4)),
                ],
            ),
            (
                3,
                2,
                0,
                [
                    PauliRotation.from_list([Z, I, Z], Fraction(1, 4)),
                    PauliRotation.from_list([I, I, Z], Fraction(-1, 4)),
                    PauliRotation.from_list([Z, I, I], Fraction(-1, 4)),
                ],
            ),
        ],
    )
    def test_from_cz_gate(
        self,
        num_qubits: int,
        control_qubit: int,
        target_qubit: int,
        expected_rotations: PauliRotation,
    ):
        assert (
            PauliRotation.from_cz_gate(num_qubits, control_qubit, target_qubit)
            == expected_rotations
        )

    @pytest.mark.parametrize(
        "input, expected",
        [
            (PauliRotation.from_list([Y], Fraction(1, 2)), r"(Y)_{\frac{\pi}{2}}"),
            (PauliRotation.from_list([Z, I], Fraction(-0, 4)), r"(Z \otimes I)_{0}"),
            (PauliRotation.from_list([X, Y], Fraction(-6, 3)), r"(X \otimes Y)_{-2\pi}"),
            (
                PauliRotation.from_list([Y, X, Z], Fraction(-3, 4)),
                r"(Y \otimes X \otimes Z)_{-\frac{3\pi}{4}}",
            ),
            (
                PauliRotation.from_list([Y, X, I, Z], Fraction(8, 6)),
                r"(Y \otimes X \otimes I \otimes Z)_{\frac{4\pi}{3}}",
            ),
        ],
    )
    def test_to_latex(self, input, expected):
        assert input.to_latex() == expected

    def test_get_y_free_equivalent_no_y_op(self):
        r = PauliRotation.from_list([X, Z, I, Z], Fraction(1, 8))
        assert r.to_y_free_equivalent() == [r]

    @pytest.mark.parametrize("input_rotation, output", test_cases_get_y_free_equivalent_rotations())
    def test_get_y_free_equivalent(self, input_rotation, output):
        assert input_rotation.to_y_free_equivalent() == output


def test_cases_get_y_free_equivalent_measurements():
    # TODO: Add more cases here
    case_1 = (
        Measurement.from_list([Y, I, Y, Z, Y, Y], isNegative=False),
        [
            PauliRotation.from_list([Z, I, I, I, I, I], Fraction(1, 4)),
            PauliRotation.from_list([I, I, Z, I, Z, Z], Fraction(1, 4)),
            Measurement.from_list([X, I, X, Z, X, X], isNegative=False),
            PauliRotation.from_list([Z, I, I, I, I, I], Fraction(-1, 4)),
            PauliRotation.from_list([I, I, Z, I, Z, Z], Fraction(-1, 4)),
        ],
    )
    case_2 = (
        Measurement.from_list([Y, Y, Y, Z], isNegative=True),
        [
            PauliRotation.from_list([Z, Z, Z, I], Fraction(1, 4)),
            Measurement.from_list([X, X, X, Z], isNegative=True),
            PauliRotation.from_list([Z, Z, Z, I], Fraction(-1, 4)),
        ],
    )

    return [case_1, case_2]


@pytest.mark.parametrize(
    "block, has_y",
    [
        (PauliRotation.from_list([I, X, Z], Fraction(1, 8)), False),
        (PauliRotation.from_list([Y, X, Z], Fraction(1, 8)), True),
        (Measurement.from_list([I, X, Z]), False),
        (Measurement.from_list([Y, X, Z]), True),
    ],
)
def test_has_y(block: PauliProductOperation, has_y: bool):
    assert block.has_y() == has_y


class TestMeasurement:
    """Tests for Measurement class"""

    @pytest.mark.parametrize(
        "input, isNegative", [([X], True), ([X, Z], False), ([X, Z, I, Y, Z], True)]
    )
    def test_from_list(self, input, isNegative):
        measurement = Measurement.from_list(input, isNegative)
        assert measurement.ops_list == input
        assert measurement.qubit_num == len(input)
        assert measurement.isNegative == isNegative

    def test_from_list_empty(self):
        with pytest.raises(ValueError):
            Measurement.from_list([])

    def test_from_list_invalid_pauli_operator(self):
        with pytest.raises(TypeError):
            Measurement.from_list([X, "X"])

    @pytest.mark.parametrize(
        "measurement_1, measurement_2",
        [
            (Measurement(3, True), Measurement(3, True)),
            (Measurement.from_list([X, Z]), Measurement.from_list([X, Z])),
            (Measurement.from_list([Y, Z, X, I]), Measurement.from_list([Y, Z, X, I])),
        ],
    )
    def test_measurement_eq(self, measurement_1, measurement_2):
        assert measurement_1 == measurement_2

    @pytest.mark.parametrize(
        "measurement_1, measurement_2",
        [
            (Measurement(3, True), Measurement(2, True)),
            (Measurement.from_list([X, Z]), Measurement.from_list([X, Z], True)),
            (Measurement.from_list([Y, X, I, I]), Measurement.from_list([Y, Z, X, I])),
        ],
    )
    def test_measurement_ne(self, measurement_1, measurement_2):
        assert measurement_1 != measurement_2

    @pytest.mark.parametrize(
        "input, expected",
        [
            (Measurement.from_list([Y]), "M: [Y]"),
            (Measurement.from_list([I, X], True), "-M: [I, X]"),
        ],
    )
    def test_str(self, input, expected):
        assert str(input) == expected

    def test_hash_equal(self):
        # Equal but distinct object have equal hashes
        assert hash(Measurement.from_list([Y, X, Z], True)) == hash(
            Measurement.from_list([Y, X, Z], True)
        )

    @pytest.mark.parametrize(
        "measurement1, measurement2",
        [
            # Different everything
            (([I, X, Z, Y], True), ([Y, X, Z], False)),
            # Different sign to the observable
            (([Y, X, Z], True), ([Y, X, Z], False)),
            # Same sign, different ops
            (([Y, X, Z], True), ([Y, X, X], True)),
            # Same sign, same ops in different order
            (([Y, X, Z], True), ([Y, Z, X], True)),
        ],
    )
    def test_hash_not_equal(self, measurement1, measurement2):
        a = Measurement.from_list(*measurement1)
        b = Measurement.from_list(*measurement2)
        assert hash(a) != hash(b)

    @pytest.mark.parametrize(
        "input, expected",
        [
            (Measurement.from_list([Y]), "(Y)_M"),
            (Measurement.from_list([I, X], True), r"(I \otimes X)_{-M}"),
            (Measurement.from_list([X, Y, Z], True), r"(X \otimes Y \otimes Z)_{-M}"),
        ],
    )
    def test_to_latex(self, input, expected):
        assert input.to_latex() == expected

    def test_get_y_free_equivalent_no_y_op(self):
        m = Measurement.from_list([X, Z, I, Z], isNegative=False)
        assert m.to_y_free_equivalent() == [m]

    @pytest.mark.parametrize(
        "input_rotation, output", test_cases_get_y_free_equivalent_measurements()
    )
    def test_get_y_free_equivalent(self, input_rotation, output):
        assert input_rotation.to_y_free_equivalent() == output


class TestPauliProductOperation:
    """Test for methods share by both Measurements and PauliRotation"""

    def test_change_single_op(self):
        r = PauliRotation(5, Fraction(1, 4))
        r.change_single_op(3, X)
        assert r.ops_list[3] == X

    def test_change_single_op_invalid_index(self):
        m = Measurement(5)
        with pytest.raises(IndexError):
            m.change_single_op(5, X)

    def test_change_single_op_invalid_op(self):
        r = PauliRotation(5, Fraction(1, 4))
        with pytest.raises(TypeError):
            r.change_single_op(3, "X")

    def test_get_op(self):
        m = Measurement.from_list([X, Z, I, X, Y, Z])
        assert m.get_op(3) == X

    def test_get_op_invalid_index(self):
        m = Measurement(5)
        with pytest.raises(IndexError):
            m.get_op(5)

    def test_get_ops_map(self):
        m = Measurement.from_list([X, Z, I, X, I, Z])
        assert m.get_ops_map() == {0: X, 1: Z, 3: X, 5: Z}

    def test_pauli_product_op_init(self):
        # Should not be able to initialize an instance of PauliProductOperation
        with pytest.raises(TypeError):
            PauliProductOperation(2)


class TestPauliOperator:
    """Tests for PauliOperator"""

    @pytest.mark.parametrize("input", [(I, Z), (X, I), (I, Y), (I, I)])
    def test_are_commuting(self, input):
        assert PauliOperator.are_commuting(*input)

    @pytest.mark.parametrize("input", [(X, Y), (Y, X), (Z, X), (X, Z)])
    def test_are_not_commuting(self, input):
        assert not PauliOperator.are_commuting(*input)

    def test_are_commuting_raises_type_error(self):
        with pytest.raises(TypeError):
            PauliOperator.are_commuting(1, 2)

    @pytest.mark.parametrize("input", [(X, X), (Y, Y), (Z, Z), (I, I)])
    def test_multiply_operators_same_operators(self, input):
        assert PauliOperator.multiply_operators(*input) == (1, I)

    def mutliply_operators_raise_type_error(self):
        with pytest.raises(TypeError):
            PauliOperator.multiply_operators(1, 2)

    @pytest.mark.parametrize("input", [X, Y, Z])
    def test_multiply_operators_with_I(self, input):
        assert PauliOperator.multiply_operators(input, I) == (1, input)
        assert PauliOperator.multiply_operators(I, input) == (1, input)

    @pytest.mark.parametrize("input, expected", [((Z, X), Y), ((Y, Z), X), ((X, Y), Z)])
    def test_multiply_operators_non_commuting(self, input, expected):
        assert PauliOperator.multiply_operators(*input) == (1j, expected)
        assert PauliOperator.multiply_operators(*reversed(input)) == (-1j, expected)
