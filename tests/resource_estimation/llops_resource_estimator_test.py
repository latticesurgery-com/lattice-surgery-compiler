# Copyright (C) 2020-2021 - George Watkins, Alex Nguyen and Varun Seshadri
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
import uuid
from typing import cast

import pytest

from lsqecc import utils
from lsqecc.logical_lattice_ops import logical_lattice_ops as llops
from lsqecc.resource_estimation import llops_resource_estimator


class MockLLComputattion:
    def __init__(self, n_magic_states: int):
        class MockCircuit:
            def __init__(self):
                self.qubit_num = 117

        self.circuit = MockCircuit()
        self.n_magic_states = n_magic_states
        self.ops = [llops.MagicStateRequest(uuid.uuid4()) for i in range(n_magic_states)]

    def count_magic_states(self):
        return self.n_magic_states


@pytest.mark.parametrize("n_magic_states", [1, 2, 3, 5, 7, 9])
def test_estimate(n_magic_states, snapshot):
    computation = cast(llops.LogicalLatticeComputation, MockLLComputattion(n_magic_states))
    snapshot.assert_match(
        utils.dataclass_render_ascii(llops_resource_estimator.estimate(computation)),
        "estimate_dump.txt",
    )


@pytest.mark.parametrize("n_magic_states", [10, 100, 100])
def test_estimate_qentiana_no_distillation(n_magic_states, snapshot):
    computation = cast(llops.LogicalLatticeComputation, MockLLComputattion(n_magic_states))
    assert llops_resource_estimator.estimate(computation) is None
    snapshot.assert_match(
        utils.dataclass_render_ascii(
            llops_resource_estimator.estimate(
                computation,
                llops_resource_estimator.ResourceEstimationConfig(physical_error_rate=0.0001),
            )
        ),
        "estimate_dump.txt",
    )
