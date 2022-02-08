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
from typing import Union

import lsqecc.patches.lattice_surgery_computation_composer as lscc
from lsqecc.external.opensurgery.resanalysis.cube_to_physical import Qentiana
from lsqecc.external.opensurgery.resanalysis.experiment import (
    Experiment as OpenSurgeryExperiment,
)


@dataclass
class ResourcesEstimatedFromSlices:
    t_count: int = 0

    core_space_qubits: int = 0
    core_timesteps: int = 0
    core_time_ns: float = 0.0
    core_space_time_volume_ns_qubits: float = 0.0

    distillation_box_space_qubits: int = 0
    distillation_box_time_ns: float = 0.0
    distillation_box_volume: float = 0.0
    distillation_total_time_ns: float = 0.0
    distillation_total_volume: float = 0.0

    total_space_qubits: int = 0
    time_ms: float = 0.0
    total_space_time_volume_ns_qubits: float = 0

    def render_ascii(self) -> str:
        return "Estimated resources needed for computation:\n" + "\n".join(
            [f"{name.replace('_',' ')}: {value}" for name, value in asdict(self).items()]
        )


def estimate_resources(
    computation: lscc.LatticeSurgeryComputation,
    # Device features
    code_distance: int = 7,  # NOTE: this value matches the 7 in qentiana
    error_decoding_time_ns: float = (10**3),
    decoding_time_by_code_distance_multiplier: float = 1,
    physical_error_rate: float = 0.0001,  # As expressed in quentiana, TODO find units
):
    slices = computation.composer.getSlices()
    layout_slice = slices[0]
    e = ResourcesEstimatedFromSlices()  # Result

    # Set up Qentiana
    ex1 = OpenSurgeryExperiment()
    ex1.props["footprint"] = layout_slice.getRows() * layout_slice.getCols()
    ex1.props["depth_units"] = len(slices)
    ex1.props["physical_error_rate"] = physical_error_rate
    ex1.props["safety_factor"] = 99 # 1% error rate.
    ex1.props["t_count"] = computation.get_t_count()
    ex1.props["prefer_depth_over_t_count"] = True
    qentiana = Qentiana(ex1.props)

    qentiana.compute_physical_resources()
    # Gives all the numbers

    # Core is the part of the lattice where the patches for logical qubits are
    e.core_space_qubits = layout_slice.getRows() * layout_slice.getCols() * code_distance**2
    e.core_timesteps = len(slices)
    e.core_time_ns = (
        len(slices)
        * error_decoding_time_ns
        * decoding_time_by_code_distance_multiplier
        * code_distance
    )
    e.core_space_time_volume_ns_qubits = e.core_time_ns * e.core_space_qubits

    # T-count from the logical computation
    e.t_count = computation.get_t_count()

    # Distillation box sizes are computed from quentiana
    qentiana_footprint: Union[str, int] = qentiana.compute_footprint_distillation_qubits()
    assert isinstance(qentiana_footprint, int)
    e.distillation_box_space_qubits = qentiana_footprint # if (isinstance(qentiana_footprint,int)) else 1000
    qentiana.compute_distillation_box_distance()
    e.distillation_box_time_ns = qentiana.dist_box_dimensions["depth_distance"]


    # Total Distillation values
    e.distillation_box_volume = e.distillation_box_time_ns * e.distillation_box_space_qubits
    e.distillation_total_time_ns = e.distillation_box_time_ns * e.t_count
    e.distillation_total_volume = e.distillation_box_volume * e.t_count

    # Total values
    e.total_space_qubits = e.core_space_qubits + e.distillation_box_space_qubits
    e.time_ms = e.distillation_box_time_ns * e.t_count + e.core_time_ns
    e.total_space_time_volume_ns_qubits = (
        e.core_space_qubits + e.distillation_box_space_qubits
    ) * (e.distillation_box_time_ns + e.core_time_ns)

    return e
