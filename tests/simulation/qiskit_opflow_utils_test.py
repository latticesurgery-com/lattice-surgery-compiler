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
import math

import numpy as np
import pytest
import qiskit.opflow as qkop
import qiskit.quantum_info as qkinfo
from qiskit import QiskitError

from lsqecc.simulation.qiskit_opflow_utils import StateSeparator

bell_pair = qkop.DictStateFn({"11": 1 / math.sqrt(2), "00": 1 / math.sqrt(2)})


# For some reason, sometimes SparseVectorStateFn a nested vector
# ... maybe it's intended to be a column
def to_vector(state: qkop.OperatorBase):
    if len(state.to_matrix().shape) == 2:
        return state.to_matrix()[0]
    return state.to_matrix()


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


# The tracing functionality is delegated to qiskit we mostly check that our interface is working
# correctly and that things such as indexing and corner cases
class TestStateSeparator:
    def test_trace_dict_state_type(self):
        assert isinstance(
            StateSeparator.trace_dict_state(qkop.One ^ qkop.Zero, [1]).primitive, dict
        )

    @pytest.mark.parametrize(
        "state, trace_over, desired_state",
        [
            (qkop.Zero ^ qkop.One, [0], qkop.Zero),
            (qkop.Zero ^ qkop.One, [1], qkop.One),
            (qkop.Zero ^ qkop.Plus, [0], qkop.Zero),
            (qkop.Zero ^ qkop.Plus, [1], qkop.Plus),
            (qkop.Zero ^ qkop.Plus ^ qkop.One, [1], qkop.Zero ^ qkop.One),
            (qkop.Zero ^ qkop.Plus ^ qkop.One, [0], qkop.Zero ^ qkop.Plus),
            (qkop.Zero ^ qkop.Plus ^ qkop.One, [2], qkop.Plus ^ qkop.One),
            (qkop.Zero ^ bell_pair, [2], bell_pair),
            (qkop.Zero ^ qkop.Plus ^ qkop.One, [0, 1], qkop.Zero),
            (qkop.Zero ^ qkop.Plus ^ qkop.One, [1, 2], qkop.One),
            (qkop.Zero ^ qkop.Plus ^ qkop.One, [0, 2], qkop.Plus),
            (bell_pair ^ qkop.One, [1, 2], qkop.One),
        ],
    )
    def test_trace_dict_state_separable_states(self, state, trace_over, desired_state):
        assert_eq_numpy_vectors(
            desired_state.to_matrix(),
            StateSeparator.trace_dict_state(state, trace_over).to_matrix(),
        )

    def test_trace_dict_state_fail(self):
        with pytest.raises(QiskitError):
            StateSeparator.trace_dict_state(bell_pair, [1])

    @pytest.mark.parametrize(
        "state, trace_over, desired_state",
        [
            (qkop.Zero ^ qkop.One, [0], qkop.Zero),
            (qkop.Zero ^ qkop.One, [1], qkop.One),
            (qkop.Zero ^ qkop.Plus, [0], qkop.Zero),
            (qkop.Zero ^ qkop.Plus, [1], qkop.Plus),
            (qkop.Zero ^ qkop.Plus ^ qkop.One, [1], qkop.Zero ^ qkop.One),
            (qkop.Zero ^ qkop.Plus ^ qkop.One, [0], qkop.Zero ^ qkop.Plus),
            (qkop.Zero ^ qkop.Plus ^ qkop.One, [2], qkop.Plus ^ qkop.One),
            (qkop.Zero ^ bell_pair, [2], bell_pair),
            (qkop.Zero ^ qkop.Plus ^ qkop.One, [0, 1], qkop.Zero),
            (qkop.Zero ^ qkop.Plus ^ qkop.One, [1, 2], qkop.One),
            (qkop.Zero ^ qkop.Plus ^ qkop.One, [0, 2], qkop.Plus),
            (bell_pair ^ qkop.One, [1, 2], qkop.One),
        ],
    )
    def test_trace_to_density_op_separable_states(self, state, trace_over, desired_state):
        assert_eq_numpy_matrices(
            qkinfo.DensityMatrix(desired_state).data,
            StateSeparator.trace_to_density_op(state, trace_over).data,
        )

    def test_trace_to_density_op_bell_pair(self):
        traced_state = StateSeparator.trace_to_density_op(bell_pair, [0]).data
        assert traced_state[0, 0] == pytest.approx(1 / 2)
        assert traced_state[0, 1] == pytest.approx(0)
        assert traced_state[1, 0] == pytest.approx(0)
        assert traced_state[1, 1] == pytest.approx(1 / 2)

    @pytest.mark.parametrize(
        "qnum, state, desired_state",
        [
            (0, qkop.Plus ^ qkop.One, qkop.One),
            (1, qkop.Plus ^ qkop.One, qkop.Plus),
            (1, qkop.Plus ^ qkop.Zero ^ qkop.One, qkop.Zero),
            (0, bell_pair, None),
            (1, bell_pair, None),
        ],
    )
    def test_separate(self, qnum, state, desired_state: qkop.StateFn):
        maybe_separated_state = StateSeparator.separate(qnum, state)
        if desired_state is None:
            assert maybe_separated_state is None
        else:
            assert_eq_numpy_vectors(
                to_vector(desired_state.eval()), maybe_separated_state.to_matrix()
            )
