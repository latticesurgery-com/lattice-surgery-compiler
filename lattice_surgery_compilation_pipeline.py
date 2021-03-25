
import circuit
import lattice_surgery_computation_composer
import logical_lattice_ops
import sparse_lattice_to_array
from sparse_lattice_to_array import GUISlice
from visual_array_cell import *

from qiskit import circuit as qkcirc
import qiskit.visualization as qkvis


__all__ = ['compile_file','VisualArrayCell','GUISlice','bell_state_example']


_composer_class = lattice_surgery_computation_composer.LatticeSurgeryComputation
_layout_types = lattice_surgery_computation_composer.LayoutType


def compile_file(circuit_file_name : str ,
                 apply_litinski_transform:bool=True) -> Tuple[List[GUISlice], str]:
    """Returns gui slices and the text of the circuit as processed in various stages"""

    input_circuit = circuit.Circuit.load_from_file(circuit_file_name)

    compilation_text = "Input Circuit:\n"

    compilation_text += qkvis.circuit_drawer(qkcirc.QuantumCircuit.from_qasm_file(circuit_file_name)).single_string()

    compilation_text += "\nCircuit as Pauli rotations:\n"
    compilation_text += input_circuit.render_ascii()

    if apply_litinski_transform:
        input_circuit.apply_transformation()
        input_circuit.remove_y_operators_from_circuit()
        compilation_text += "\nCircuit after the Litinski Transform:\n"
        compilation_text += input_circuit.render_ascii()

    logical_computation = logical_lattice_ops.LogicalLatticeComputation(input_circuit)
    lsc = _composer_class.make_computation_with_simulation(logical_computation, _layout_types.SimplePreDistilledStates)


    return list(map(sparse_lattice_to_array.sparse_lattice_to_array, lsc.composer.getSlices())), compilation_text


def bell_state_example():
    compilation_text = ""

    I = lattice_surgery_computation_composer.PauliOperator.I
    X = lattice_surgery_computation_composer.PauliOperator.X
    Y = lattice_surgery_computation_composer.PauliOperator.Y
    Z = lattice_surgery_computation_composer.PauliOperator.Z

    qreg = qkcirc.QuantumRegister(2)
    qiskit_circ = qkcirc.QuantumCircuit(qreg, qkcirc.ClassicalRegister(2))

    qiskit_circ.h(0)
    qiskit_circ.cx(0, 1)

    input_circuit = lattice_surgery_computation_composer.Circuit.load_from_quasm_string(qiskit_circ.qasm())

    qiskit_circ.measure(0,0)
    input_circuit.add_pauli_block(lattice_surgery_computation_composer.Measurement.from_list([Z, I]))

    qiskit_circ.measure(1,1)
    input_circuit.add_pauli_block(lattice_surgery_computation_composer.Measurement.from_list([I, Z]))

    compilation_text = "Input Circuit:\n"
    compilation_text += qkvis.circuit_drawer(qiskit_circ).single_string()

    compilation_text += "\nCircuit as Pauli rotations:\n"
    compilation_text += input_circuit.render_ascii()


    logical_computation = logical_lattice_ops.LogicalLatticeComputation(input_circuit)
    lsc = lattice_surgery_computation_composer.LatticeSurgeryComputation.make_computation_with_simulation(logical_computation,
                                                                        lattice_surgery_computation_composer.LayoutType.SimplePreDistilledStates)
    return list(map(sparse_lattice_to_array.sparse_lattice_to_array, lsc.composer.getSlices())), compilation_text

