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
SAMPLE_CIRCUIT = """
OPENQASM 2.0;
include "qelib1.inc";

qreg q[2];

h q[0];
cx q[0],q[1];
h q[0];
t q[1];
s q[0];
x q[0];
"""

if __name__ == "__main__":

    input_circuit = segmented_qasm_parser.parse_str(SAMPLE_CIRCUIT)

    compilation_text = "Input Circuit:\n"

    compilation_text += qkvis.circuit_drawer(
        qkcirc.QuantumCircuit.from_qasm_str(SAMPLE_CIRCUIT)
    ).single_string()

    compilation_text += "\nCircuit as Pauli rotations:\n"
    compilation_text += input_circuit.render_ascii()

    # TODO add user flag
    input_circuit = input_circuit.get_y_free_equivalent()

    logical_computation = llops.LogicalLatticeComputation(input_circuit)
    lsc = lscc.LatticeSurgeryComputation.make_computation_with_simulation(
        logical_computation, lscc.LayoutType.SimplePreDistilledStates
    )

    # TODO| when compilation stages are supported, remove the 'Circuit|' from the text
    compilation_text += "\nCircuit| " + estimate_resources(lsc).render_ascii()

    print(compilation_text)


