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

    def test_trace_dict_state_indices_trivial(self):
        traced_state = StateSeparator.trace_dict_state(qkop.One ^ qkop.One, [0])
        assert isinstance(traced_state, qkop.DictStateFn)
        assert traced_state.primitive.get("0") is None
        assert traced_state.primitive["1"] == pytest.approx(1)

        traced_state = StateSeparator.trace_dict_state(qkop.One ^ qkop.One, [1])
        assert isinstance(traced_state, qkop.DictStateFn)
        assert traced_state.primitive.get("0") is None
        assert traced_state.primitive["1"] == pytest.approx(1)

    def test_trace_dict_state_over_one_qubit(self):
        state = qkop.DictStateFn({"10": 1 / math.sqrt(2), "00": 1 / math.sqrt(2)})
        s0 = StateSeparator.trace_dict_state(state, [0])
        s1 = StateSeparator.trace_dict_state(state, [1])

        assert isinstance(s0.primitive, dict)
        assert s0.primitive["0"] == pytest.approx(complex(1 / math.sqrt(2)))
        assert s0.primitive["1"] == pytest.approx(complex(1 / math.sqrt(2)))

        assert isinstance(s1.primitive, dict)
        assert s1.primitive["0"] == pytest.approx(complex(1))
        assert s1.primitive.get("1") is None

    def test_trace_dict_state_test_indices(self):
        traced_state = StateSeparator.trace_dict_state(qkop.One ^ qkop.Zero ^ qkop.Plus, [1, 2])
        assert traced_state.primitive["0"] == pytest.approx(1 / math.sqrt(2))
        assert traced_state.primitive["1"] == pytest.approx(1 / math.sqrt(2))

        traced_state = StateSeparator.trace_dict_state(qkop.One ^ qkop.Zero ^ qkop.Plus, [0, 2])
        assert traced_state.primitive["0"] == pytest.approx(1)
        assert traced_state.primitive.get("1") is None

        traced_state = StateSeparator.trace_dict_state(qkop.One ^ qkop.Zero ^ qkop.Plus, [0, 1])
        assert traced_state.primitive.get("0") is None
        assert traced_state.primitive["1"] == pytest.approx(1)

    def test_trace_dict_state_test_leave_one_qubit(self):
        traced_state = StateSeparator.trace_dict_state(qkop.One ^ qkop.Zero ^ qkop.Plus, [0])
        assert traced_state.primitive.get("0") is None
        assert traced_state.primitive.get("1") is None

        assert traced_state.primitive.get("00") is None
        assert traced_state.primitive["10"] == pytest.approx(1)
        assert traced_state.primitive.get("01") is None
        assert traced_state.primitive.get("11") is None

    def test_trace_dict_state_test_leave_superposition(self):
        traced_state = StateSeparator.trace_dict_state(qkop.One ^ qkop.Zero ^ qkop.Plus, [2])
        assert traced_state.primitive.get("0") is None
        assert traced_state.primitive.get("1") is None

        assert traced_state.primitive["00"] == pytest.approx(1 / math.sqrt(2))
        assert traced_state.primitive["01"] == pytest.approx(1 / math.sqrt(2))
        assert traced_state.primitive.get("10") is None
        assert traced_state.primitive.get("11") is None

    def test_trace_dict_state_fail(self):
        with pytest.raises(QiskitError):
            StateSeparator.trace_dict_state(bell_pair, [1])

    def test_trace_dict_state_bell_pair_otimes_bell_pair(self):
        bell_pair_otimes_bell_pair = bell_pair ^ bell_pair
        traced23 = StateSeparator.trace_dict_state(bell_pair_otimes_bell_pair, [0, 1])
        traced01 = StateSeparator.trace_dict_state(bell_pair_otimes_bell_pair, [2, 3])

        assert isinstance(traced23.primitive, dict)
        assert traced23.primitive["00"] == pytest.approx(1 / math.sqrt(2))
        assert traced23.primitive["11"] == pytest.approx(1 / math.sqrt(2))

        assert isinstance(traced01.primitive, dict)
        assert traced01.primitive["00"] == pytest.approx(1 / math.sqrt(2))
        assert traced01.primitive["11"] == pytest.approx(1 / math.sqrt(2))

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
            (qkop.Zero ^ qkop.Plus ^ qkop.One, [0, 1], qkop.Zero),
            (qkop.Zero ^ qkop.Plus ^ qkop.One, [1, 2], qkop.One),
            (qkop.Zero ^ qkop.Plus ^ qkop.One, [0, 2], qkop.Plus),
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

    def test_trace_to_density_op_non_separable_states(self, state, trace_over, desired_state):
        pass
