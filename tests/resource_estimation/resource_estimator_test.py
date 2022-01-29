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
from dataclasses import astuple
from typing import List, cast

import lsqecc.patches.lattice_surgery_computation_composer as lsc
import lsqecc.resource_estimation.resource_estimator as lsest
from lsqecc.patches import patches


class MockComposer_Empty:
    def getSlices(self) -> List[patches.Lattice]:
        return [
            patches.Lattice(
                [patches.Patch(patches.PatchType.Qubit, None, [(1, 1)], [], None)], 0, 0
            )
        ]


def test_estimate_resources():
    class MockPatchComputation:
        def __init__(self):
            self.composer = MockComposer_Empty()

        def get_t_count(self):
            return 3

    res = lsest.estimate_resources(cast(lsc.LatticeSurgeryComputation, MockPatchComputation()))
    for value in astuple(res):
        assert value != 0
        # TODO maybe some sanity check criteria. or consider making it a regression test
    assert res.t_count == 3
