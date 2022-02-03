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
from lsqecc.resource_estimation.resource_estimator import estimate_resources

GUISlice = List[List[Optional[vac.VisualArrayCell]]]  # 2D array of cells

__all__ = ["compile_file", "GUISlice"]


def compile_file(
    circuit_file_name: str,
    apply_litinski_transform: bool = True,
    simulation_type: lssim.SimulatorType = lssim.SimulatorType.FULL_STATE_VECTOR,
) -> Tuple[List[GUISlice], dict, str]:
    """DEPRECATED. compile_str"""
    with open(circuit_file_name) as input_file:
        return compile_str(
            input_file.read(), apply_litinski_transform, simulation_type=simulation_type
        )


def compile_str(
    qasm_circuit: str,
    apply_litinski_transform: bool = True,
    simulation_type: lssim.SimulatorType = lssim.SimulatorType.FULL_STATE_VECTOR,
) -> Tuple[List[GUISlice], dict, str]:
    """Returns gui slices and string JSON of compilation text)"""
    composer_class = lscc.LatticeSurgeryComputation
    layout_types = lscc.LayoutType

    input_circuit = qkvis.circuit_drawer(
        qkcirc.QuantumCircuit.from_qasm_str(qasm_circuit)
    ).single_string()

    parsed_circuit = segmented_qasm_parser.parse_str(qasm_circuit)
    circuit_as_pauli_rotations = parsed_circuit.render_ascii()

    # TODO add user flag
    parsed_circuit = parsed_circuit.get_y_free_equivalent()

    circuit_after_litinski_transform: Optional[str] = None
    if apply_litinski_transform:
        parsed_circuit.apply_transformation()
        parsed_circuit = parsed_circuit.get_y_free_equivalent()
        circuit_after_litinski_transform = parsed_circuit.render_ascii()

    compilation_stages = {
        "input_circuit": input_circuit,
        "circuit_as_pauli_rotations": circuit_as_pauli_rotations,
        "circuit_after_litinski_transform": circuit_after_litinski_transform,
    }

    logical_computation = llops.LogicalLatticeComputation(parsed_circuit)
    lsc = composer_class.make_computation(
        logical_computation, layout_types.SimplePreDistilledStates, simulation_type=simulation_type
    )

    # TODO| when compilation stages are supported, remove the 'Circuit|' from the text
    resource_estimation = {"resource_estimation": estimate_resources(lsc).render_ascii()}

    compilation_stages.update(resource_estimation)

    compilation_text = "\n".join(f"{key}\n{value}\n" for key, value in compilation_stages.items())
    print(type(compilation_text))

    return (
        list(map(sparse_lattice_to_array, lsc.composer.getSlices())),
        compilation_stages,
        compilation_text,
    )


# TODO move this test to the appropriate place
circuit = """OPENQASM 2.0;

include "qelib1.inc";

// this is a basic quantum circuit that creates an entangled pair

qreg q[2];		// create a quantum register with 2 qubits
creg c[2]; 		// create a classical register with 2 bits
h q[0];  		// perform Hadamard gate on one qubit
cx q[0],q[1];  	// perform control-not gate on both qubits

// an entangled state of the Bell-pair form has been created!

measure q[0] -> c[0];	//measure one qubit, and put outcome in one bit
measure q[1] -> c[1];	//measure the other qubit, and put outcome in the other bit"""

output = compile_str(qasm_circuit=circuit, apply_litinski_transform=True)
print(output)
