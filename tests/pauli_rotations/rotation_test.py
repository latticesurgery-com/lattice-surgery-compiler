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

    @pytest.mark.parametrize(
        "input, expected",
        [
            (PauliRotation.from_list([Y], Fraction(1, 2)), r"(Y)_\frac{\pi}{2}"),
            (PauliRotation.from_list([Z, I], Fraction(-0, 4)), r"(Z \otimes I)_0"),
            (PauliRotation.from_list([X, Y], Fraction(-6, 3)), r"(X \otimes Y)_-2\pi"),
            (
                PauliRotation.from_list([Y, X, Z], Fraction(-3, 4)),
                r"(Y \otimes X \otimes Z)_-\frac{3\pi}{4}",
            ),
            (
                PauliRotation.from_list([Y, X, I, Z], Fraction(8, 6)),
                r"(Y \otimes X \otimes I \otimes Z)_\frac{4\pi}{3}",
            ),
        ],
    )
    def test_to_latex(self, input, expected):
        assert input.to_latex() == expected


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
