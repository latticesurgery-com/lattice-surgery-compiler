
import circuit
import lattice_surgery_computation_composer
import logical_lattice_ops
import sparse_lattice_to_array
from sparse_lattice_to_array import GUISlice
from visual_array_cell import *

from qiskit import circuit as qkcirc
import qiskit.visualization as qkvis


__all__ = ['compile_file','VisualArrayCell','GUISlice']


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


