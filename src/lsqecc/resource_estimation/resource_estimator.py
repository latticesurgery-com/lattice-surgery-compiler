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

from dataclasses import asdict, dataclass
from typing import List

from lsqecc.patches import patches


@dataclass
class EstimatedResources:
    physical_qubit_rows: int = 0
    physical_qubit_cols: int = 0
    time_ms: float = 0.0

    def render_ascii(self) -> str:
        return "Estimated resources needed for computation:\n" + "\n".join(
            [f"{name.replace('_',' ')}: {value}" for name, value in asdict(self).items()]
        )


def estimate_resources(
    slices: List[patches.Lattice],
    code_distance: int = 17,
    error_decoding_time_ms: float = 10 ** (-3),
    decoding_cycles_by_code_distance_multiplier: float = 1,
):

    return EstimatedResources(
        physical_qubit_rows=slices[0].getRows() * code_distance,
        physical_qubit_cols=slices[0].getCols() * code_distance,
        time_ms=len(slices) * error_decoding_time_ms * decoding_cycles_by_code_distance_multiplier,
    )
