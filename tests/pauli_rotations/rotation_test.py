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

from lsqecc.pauli_rotations import Measurement, PauliOperator, PauliRotation

I = PauliOperator.I  # noqa: E741
X = PauliOperator.X
Y = PauliOperator.Y
Z = PauliOperator.Z


class TestPauliRotation:
    """Tests for PauliRotation"""

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


class TestMeasurement:
    """Tests for Measurement class"""

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

    @pytest.mark.parametrize("input, expected", [((Z, X), Y), ((Z, Y), X), ((Y, X), Z)])
    def test_multiply_operators_non_commuting(self, input, expected):
        assert PauliOperator.multiply_operators(*input) == (1j, expected)
        assert PauliOperator.multiply_operators(*reversed(input)) == (-1j, expected)
