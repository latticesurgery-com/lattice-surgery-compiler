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

from dataclasses import dataclass
from typing import Optional

from lsqecc.external.opensurgery.resanalysis.cube_to_physical import Qentiana
from lsqecc.external.opensurgery.resanalysis.experiment import (
    Experiment as OpenSurgeryExperiment,
)
from lsqecc.logical_lattice_ops import logical_lattice_ops as llops


@dataclass
class ResourceEstimationConfig:
    # From qentiana:
    # target_error_per_T_gate = 1 / (self.parameters["safety_factor"] * local_t_count)
    # TODO why do we prefer to specify it in this way, instead of a global target error rate?
    safety_factor: float = 99
    physical_error_rate: float = 0.001
    prefer_depth_over_t_count = True  # TODO decide


@dataclass
class ResourcesEstimatedFromLLOPS:
    code_distance: int = 7  # update from
    time_secs: float = 0


#
# vvvv THIS IS WHAT WE WANT TO COMPLETE TODAY vvvv
#
# Left some TODOs
#
def estimate(
    logical_lattice_computation: llops.LogicalLatticeComputation,
    config: ResourceEstimationConfig = ResourceEstimationConfig(),
) -> Optional[ResourcesEstimatedFromLLOPS]:

    # Set up Qentiana with all of its parameters
    ex1 = OpenSurgeryExperiment()

    # Computation related:
    ex1.props["footprint"] = logical_lattice_computation.circuit.qubit_num  # i.e. logical qubits
    ex1.props["depth_units"] = len(logical_lattice_computation.ops)
    ex1.props["t_count"] = logical_lattice_computation.count_magic_states()

    # Config related
    ex1.props["physical_error_rate"] = config.physical_error_rate
    ex1.props["safety_factor"] = config.safety_factor
    ex1.props["prefer_depth_over_t_count"] = config.prefer_depth_over_t_count

    qentiana = Qentiana(ex1.props)

    try:
        results = qentiana.compute_physical_resources()
        return ResourcesEstimatedFromLLOPS(
            code_distance=results["distance"], time_secs=results["time"]
        )
    except TypeError:
        return None
