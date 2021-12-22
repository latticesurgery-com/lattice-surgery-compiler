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

import pytest
import qiskit.opflow as qkop
import qiskit.quantum_info as qkinfo
from qiskit import QiskitError

from lsqecc.simulation.qiskit_opflow_utils import StateSeparator

bell_pair = qkop.DictStateFn({"11": 1 / math.sqrt(2), "00": 1 / math.sqrt(2)})


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
        traced_state = StateSeparator.trace_dict_state(state, trace_over).to_matrix()
        desired_state_as_matrix = desired_state.to_matrix()

        assert traced_state.shape == desired_state_as_matrix.shape
        for j in range(traced_state.shape[0]):
            assert traced_state[j] == pytest.approx(desired_state_as_matrix[j])

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
        traced_state = StateSeparator.trace_to_density_op(state, trace_over)

        desired_state_as_density_matrix = qkinfo.DensityMatrix(desired_state).data
        assert traced_state.data.shape == desired_state_as_density_matrix.data.shape

        rows, cols = traced_state.data.shape
        for row in range(rows):
            for col in range(cols):
                assert traced_state.data[row, col] == pytest.approx(
                    desired_state_as_density_matrix[row, col]
                )

    @pytest.mark.skip
    def test_trace_to_density_op_non_separable_states(self, state, trace_over, desired_state):
        pass
