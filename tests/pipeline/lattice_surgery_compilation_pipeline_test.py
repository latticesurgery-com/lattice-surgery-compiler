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
from lsqecc.pipeline.lattice_surgery_compilation_pipeline import Compilation, Stage


def test_compilation_stages():
    expected_compilation_stages = {
        "circuit": "value1",
        "circuit_as_pauli_rotations": "value2",
        "circuit_after_litinski_transform": "value3",
        "resource_estimation": "value4",
    }

    stage1 = Stage("circuit", "value1")
    stage2 = Stage("circuit_as_pauli_rotations", "value2")
    stage3 = Stage("circuit_after_litinski_transform", "value3")
    stage4 = Stage("resource_estimation", "value4")

    actual_compilation_stages = Compilation().stages([stage1, stage2, stage3, stage4])
    assert expected_compilation_stages == actual_compilation_stages
