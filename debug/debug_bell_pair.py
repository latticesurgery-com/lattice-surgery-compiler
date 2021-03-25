import circuit
import lattice_surgery_computation_composer as ls
import logical_lattice_ops
import sparse_lattice_to_array
from visual_array_cell import *
import lattice_surgery_compilation_pipeline

from qiskit import circuit as qkcirc
import qiskit.visualization as qkvis
from webgui import lattice_view





if __name__ == "__main__":
    compilation_text = ""

    I = ls.PauliOperator.I
    X = ls.PauliOperator.X
    Y = ls.PauliOperator.Y
    Z = ls.PauliOperator.Z

    qreg = qkcirc.QuantumRegister(2)
    qiskit_circ = qkcirc.QuantumCircuit(qreg)

    qiskit_circ.h(0)
    qiskit_circ.cx(0, 1)

    input_circuit = ls.Circuit.load_from_quasm_string(qiskit_circ.qasm())
    input_circuit.add_pauli_block(ls.Measurement.from_list([Z,I]))
    input_circuit.add_pauli_block(ls.Measurement.from_list([I,Z]))

    logical_computation = logical_lattice_ops.LogicalLatticeComputation(input_circuit)
    lsc = ls.LatticeSurgeryComputation.make_computation_with_simulation(logical_computation, ls.LayoutType.SimplePreDistilledStates)

    lattice_view.render_to_file(lsc.composer.getSlices(), "index.html", template="/home/george/courses/CMPT415_498/code/lattice-surgery-compiler/webgui/templates/lattice_view.mak")


