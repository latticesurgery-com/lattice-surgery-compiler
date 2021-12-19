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
import qiskit.opflow as qk
from qiskit import QiskitError

from lsqecc.simulation.qiskit_opflow_utils import StateSeparator

bell_pair = qk.DictStateFn({"11": 1 / math.sqrt(2), "00": 1 / math.sqrt(2)})


class TestStateSeparator:
    def test_trace_dict_state_type(self):
        assert isinstance(StateSeparator.trace_dict_state(qk.One ^ qk.Zero, [1]).primitive, dict)

    def test_trace_dict_state_indices_trivial(self):
        traced_state = StateSeparator.trace_dict_state(qk.One ^ qk.One, [0])
        assert isinstance(traced_state, qk.DictStateFn)
        assert traced_state.primitive.get("0") is None
        assert traced_state.primitive["1"] == pytest.approx(1)

        traced_state = StateSeparator.trace_dict_state(qk.One ^ qk.One, [1])
        assert isinstance(traced_state, qk.DictStateFn)
        assert traced_state.primitive.get("0") is None
        assert traced_state.primitive["1"] == pytest.approx(1)

    def test_trace_dict_state_over_one_qubit(self):
        state = qk.DictStateFn({"10": 1 / math.sqrt(2), "00": 1 / math.sqrt(2)})
        s0 = StateSeparator.trace_dict_state(state, [0])
        s1 = StateSeparator.trace_dict_state(state, [1])

        assert isinstance(s0.primitive, dict)
        assert s0.primitive["0"] == pytest.approx(complex(1 / math.sqrt(2)))
        assert s0.primitive["1"] == pytest.approx(complex(1 / math.sqrt(2)))

        assert isinstance(s1.primitive, dict)
        assert s1.primitive["0"] == pytest.approx(complex(1))
        assert s1.primitive.get("1") is None

    def test_trace_dict_state_test_indices(self):
        traced_state = StateSeparator.trace_dict_state(qk.One ^ qk.Zero ^ qk.Plus, [1, 2])
        assert traced_state.primitive["0"] == pytest.approx(1 / math.sqrt(2))
        assert traced_state.primitive["1"] == pytest.approx(1 / math.sqrt(2))

        traced_state = StateSeparator.trace_dict_state(qk.One ^ qk.Zero ^ qk.Plus, [0, 2])
        assert traced_state.primitive["0"] == pytest.approx(1)
        assert traced_state.primitive.get("1") is None

        traced_state = StateSeparator.trace_dict_state(qk.One ^ qk.Zero ^ qk.Plus, [0, 1])
        assert traced_state.primitive.get("0") is None
        assert traced_state.primitive["1"] == pytest.approx(1)

    def test_trace_dict_state_test_leave_one_qubit(self):
        traced_state = StateSeparator.trace_dict_state(qk.One ^ qk.Zero ^ qk.Plus, [0])
        assert traced_state.primitive.get("0") is None
        assert traced_state.primitive.get("1") is None

        assert traced_state.primitive.get("00") is None
        assert traced_state.primitive["10"] == pytest.approx(1)
        assert traced_state.primitive.get("01") is None
        assert traced_state.primitive.get("11") is None

    def test_trace_dict_state_test_leave_superposition(self):
        traced_state = StateSeparator.trace_dict_state(qk.One ^ qk.Zero ^ qk.Plus, [2])
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
