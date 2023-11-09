
from  lsqecc.pauli_rotations import segmented_qasm_parser
import lsqecc.pipeline.lattice_surgery_compilation_pipeline as lscp
import lsqecc.logical_lattice_ops.logical_lattice_ops as llops
from lsqecc.logical_lattice_ops import ls_instructions

import qiskit

CIRCUIT="""
OPENQASM 2.0;
include "qelib1.inc";

qreg q[1];
rz(pi/8) q[0];
"""

if __name__ == "__main__":

    print("Circuit as Pauli rotations:")
    input_circuit = segmented_qasm_parser.parse_str(CIRCUIT)
    # print(input_circuit.render_ascii())
    higher_ord_rotations = len(input_circuit.ops)
    print(f"{higher_ord_rotations} rotations")

    print("Circuit as Pauli rotations with only pi/2, pi/4, pi/8:")
    input_circuit = input_circuit.get_basic_form()
    # print(input_circuit.render_ascii())
    total_rotations=len(input_circuit.ops)
    magic_states=input_circuit.count_direct_magic_states()
    print(f"{total_rotations} rotations of which "\
            +f"{magic_states} pi/8")

    print("\nConverting to logical lattice computation\n")
    logical_computation = llops.LogicalLatticeComputation(input_circuit)
    total_ops = len(logical_computation.ops)
    print(ls_instructions.from_logical_lattice_ops(logical_computation))
    print(f"{total_ops} operations")
