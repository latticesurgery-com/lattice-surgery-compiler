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

from typing import List, Optional, Tuple

import qiskit.visualization as qkvis
from qiskit import circuit as qkcirc

import lsqecc.lattice_array.visual_array_cell as vac
import lsqecc.logical_lattice_ops.logical_lattice_ops as llops
import lsqecc.patches.lattice_surgery_computation_composer as lscc
import lsqecc.pauli_rotations.segmented_qasm_parser as segmented_qasm_parser
import lsqecc.simulation.logical_patch_state_simulation as lssim
from lsqecc.lattice_array import sparse_lattice_to_array
from lsqecc.resource_estimation.slice_resource_estimator import estimate_resources

GUISlice = List[List[Optional[vac.VisualArrayCell]]]  # 2D array of cells

__all__ = ["compile_file", "GUISlice"]


def compile_file(
    circuit_file_name: str,
    apply_litinski_transform: bool = True,
    simulation_type: lssim.SimulatorType = lssim.SimulatorType.FULL_STATE_VECTOR,
) -> Tuple[List[GUISlice], str]:
    """DEPRECATED. compile_str"""
    with open(circuit_file_name) as input_file:
        return compile_str(
            input_file.read(), apply_litinski_transform, simulation_type=simulation_type
        )


def compile_str(
    qasm_circuit: str,
    apply_litinski_transform: bool = True,
    simulation_type: lssim.SimulatorType = lssim.SimulatorType.FULL_STATE_VECTOR,
) -> Tuple[List[GUISlice], str]:
    """Returns gui slices and the text of the circuit as processed in various stages"""
    composer_class = lscc.LatticeSurgeryComputation
    layout_types = lscc.LayoutType

    input_circuit = segmented_qasm_parser.parse_str(qasm_circuit)

    compilation_text = "Input Circuit:\n"

    compilation_text += qkvis.circuit_drawer(
        qkcirc.QuantumCircuit.from_qasm_str(qasm_circuit)
    ).single_string()

    compilation_text += "\nCircuit as Pauli rotations:\n"
    compilation_text += input_circuit.render_ascii()

    # TODO add user flag
    input_circuit = input_circuit.to_y_free_equivalent()

    if apply_litinski_transform:
        input_circuit.apply_transformation()
        input_circuit = input_circuit.to_y_free_equivalent()
        compilation_text += "\nCircuit after the Litinski Transform:\n"
        compilation_text += input_circuit.render_ascii()

    logical_computation = llops.LogicalLatticeComputation(input_circuit)
    lsc = composer_class.make_computation(
        logical_computation, layout_types.SimplePreDistilledStates, simulation_type=simulation_type
    )

    # TODO| when compilation stages are supported, remove the 'Circuit|' from the text
    compilation_text += "\nCircuit| " + estimate_resources(lsc).render_ascii()

    return list(map(sparse_lattice_to_array, lsc.composer.getSlices())), compilation_text
