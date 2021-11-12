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
def test_pauli_rotation_eq(pauli_rotation_1, pauli_rotation_2):
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
def test_pauli_rotation_ne(pauli_rotation_1, pauli_rotation_2):
    assert pauli_rotation_1 != pauli_rotation_2


@pytest.mark.parametrize(
    "measurement_1, measurement_2",
    [
        (Measurement(3, True), Measurement(3, True)),
        (Measurement.from_list([X, Z]), Measurement.from_list([X, Z])),
        (Measurement.from_list([Y, Z, X, I]), Measurement.from_list([Y, Z, X, I])),
    ],
)
def test_measurement_eq(measurement_1, measurement_2):
    assert measurement_1 == measurement_2


@pytest.mark.parametrize(
    "measurement_1, measurement_2",
    [
        (Measurement(3, True), Measurement(2, True)),
        (Measurement.from_list([X, Z]), Measurement.from_list([X, Z], True)),
        (Measurement.from_list([Y, X, I, I]), Measurement.from_list([Y, Z, X, I])),
    ],
)
def test_measurement_ne(measurement_1, measurement_2):
    assert measurement_1 != measurement_2
