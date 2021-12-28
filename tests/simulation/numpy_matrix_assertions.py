# Copyright (C) 2020-2021 - George Watkins, Alex Nguyen, Varun Seshadri
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

import numpy as np
import pytest


def assert_eq_numpy_vectors(lhs: np.array, rhs: np.array):
    assert len(rhs.shape) == 1
    assert lhs.shape == rhs.shape
    rows = lhs.shape[0]
    for row in range(rows):
        assert lhs[row] == pytest.approx(rhs[row])


def assert_eq_numpy_matrices(lhs: np.array, rhs: np.array):
    assert len(rhs.shape) == 2
    assert lhs.shape == rhs.shape
    rows, cols = lhs.shape
    for row in range(rows):
        for col in range(cols):
            assert lhs[row, col] == pytest.approx(rhs[row, col])
