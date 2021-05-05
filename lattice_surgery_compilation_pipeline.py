
import segmented_qasm_parser
import lattice_surgery_computation_composer
import logical_lattice_ops
import sparse_lattice_to_array
from visual_array_cell import *
import compiler_options

from qiskit import circuit as qkcirc
import qiskit.visualization as qkvis


__all__ = ['compile_file','VisualArrayCell','GUISlice']

def compile_file(circuit_file_name : str ,
                 options : compiler_options.CompilerOptions
                 ) -> Tuple[List[GUISlice], str]:
    """Returns gui slices and the text of the circuit as processed in various stages"""

    composer_class = lattice_surgery_computation_composer.LatticeSurgeryComputation

    input_circuit = segmented_qasm_parser.parse_file(circuit_file_name)

    compilation_text = "Input Circuit:\n"
    compilation_text += qkvis.circuit_drawer(qkcirc.QuantumCircuit.from_qasm_file(circuit_file_name)).single_string()
    compilation_text += "\nCircuit as Pauli rotations:\n"
    compilation_text += input_circuit.render_ascii()

    if options.apply_stabilizer_commuting_transform:
        input_circuit.apply_transformation()
        input_circuit.remove_y_operators_from_circuit()

        compilation_text += "\nCircuit after the Litinski Transform:\n"
        compilation_text += input_circuit.render_ascii()

    logical_computation = logical_lattice_ops.LogicalLatticeComputation(input_circuit)
    lsc = composer_class.make_computation_with_simulation(logical_computation, compiler_options.co.SimplePreDistilledStates)


    return sparse_lattice_to_array.render_slices(lsc.composer.getSlices()), compilation_text