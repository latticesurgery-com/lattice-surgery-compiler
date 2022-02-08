import lsqecc.pipeline.lattice_surgery_compilation_pipeline as lscp

import qiskit.visualization as qkvis
import qiskit
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
from qiskit.compiler import transpile

from qiskit.circuit.library import TGate, HGate, SGate
# from qiskit.transpiler.passes import SolovayKitaevDecomposition


CIRCUIT="""
OPENQASM 2.0;
include "qelib1.inc";

qreg q[1];
rz(pi/8) q[0];
"""

if __name__=="__main__":

    c = QuantumCircuit.from_qasm_str(CIRCUIT)
    print(qkvis.circuit_drawer(c).single_string())
    print(qkvis.circuit_drawer(transpile(c,basis_gates=['u','cx'])).single_string())

    slices, text = lscp.compile_str(CIRCUIT,
                                    simulation_type=lscp.lssim.SimulatorType.NOOP,
                                    apply_litinski_transform=False)