

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


CIRCUIT="""
OPENQASM 2.0;
include "qelib1.inc";

qreg q[1];
rz(pi/8) q[0];
"""


if __name__ == "__main__":
    composer_class = lscc.LatticeSurgeryComputation
    layout_types = lscc.LayoutType

    input_circuit = segmented_qasm_parser.parse_str(CIRCUIT)

    print("Input Circuit:\n")

    print(qkvis.circuit_drawer(
        qkcirc.QuantumCircuit.from_qasm_str(CIRCUIT)
    ).single_string())

    print("\nCircuit as Pauli rotations:\n")
    print(input_circuit.render_ascii())

    print("\nCircuit as Pauli rotations with only pi/2, pi/4, pi/8:\n")
    input_circuit = input_circuit.get_basic_form()
    print(input_circuit.render_ascii())
    print(f"Rotation count: {len(input_circuit.ops)}")
    print(f"Magic state count: {input_circuit.count_direct_magic_states()}")

    print("\nGrouping together same axes:\n")
    input_circuit = input_circuit.group_rotations_with_the_same_axis()
    print(input_circuit.render_ascii())
    print(f"Rotation count: {len(input_circuit.ops)}")
    print(f"Magic state count: {input_circuit.count_direct_magic_states()}")

    print("\nTo basic form:\n")
    input_circuit = input_circuit.get_basic_form()
    print(input_circuit.render_ascii())
    print(f"Rotation count: {len(input_circuit.ops)}")
    print(f"Magic state count: {input_circuit.count_direct_magic_states()}")


    print("\nY free equivalent:\n")
    input_circuit = input_circuit.get_y_free_equivalent()
    print(input_circuit.render_ascii())


    logical_computation = llops.LogicalLatticeComputation(input_circuit)
    lsc = composer_class.make_computation(
        logical_computation, layout_types.SimplePreDistilledStates, simulation_type=lssim.SimulatorType.NOOP
    )

    # TODO| when compilation stages are supported, remove the 'Circuit|' from the text
    print("\nCircuit| " + estimate_resources(lsc).render_ascii())


