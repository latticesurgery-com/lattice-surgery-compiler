from typing import List, Optional, Tuple

import qiskit.visualization as qkvis
from qiskit import circuit as qkcirc

import lsqecc.logical_lattice_ops.logical_lattice_ops as llops
import lsqecc.patches.lattice_surgery_computation_composer as lscc
import lsqecc.pauli_rotations.segmented_qasm_parser as segmented_qasm_parser
import lsqecc.simulation.logical_patch_state_simulation as lssim

SAMPLE_CIRCUIT_1 = """
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

SAMPLE_CIRCUIT_2 = """
OPENQASM 2.0;
include "qelib1.inc";

qreg q[2];

h q[0];
t q[0];
h q[0];
cx q[0],q[1];
"""

if __name__ == "__main__":

    input_circuit = segmented_qasm_parser.parse_str(SAMPLE_CIRCUIT_2)

    compilation_text = "Input Circuit:\n"

    compilation_text += qkvis.circuit_drawer(
        qkcirc.QuantumCircuit.from_qasm_str(SAMPLE_CIRCUIT_2)
    ).single_string()

    compilation_text += "\nCircuit as Pauli rotations:\n"
    compilation_text += input_circuit.render_ascii()

    # TODO add user flag
    print("input")
    print(input_circuit.render_ascii())
    input_circuit = input_circuit.to_y_free_equivalent()
    print("removed y")
    print(input_circuit.render_ascii())
    input_circuit.apply_transformation()
    print("done litinski")
    print(input_circuit.render_ascii())
    input_circuit = input_circuit.to_y_free_equivalent()
    print("removed y again")
    print(input_circuit.render_ascii())

    logical_computation = llops.LogicalLatticeComputation(input_circuit)
    lsc = lscc.LatticeSurgeryComputation.make_computation_with_simulation(
        logical_computation,
        lscc.LayoutType.SimplePreDistilledStates
    )

    print(compilation_text)