
import segmented_qasm_parser
import lattice_surgery_computation_composer
import logical_lattice_ops
import sparse_lattice_to_array
import dependency_graph
from visual_array_cell import *
import compiler_options
import circuit

from qiskit import circuit as qkcirc
import qiskit.visualization as qkvis


__all__ = ['compile_file','VisualArrayCell','GUISlice']

_make_computation_with_simulation = lattice_surgery_computation_composer.LatticeSurgeryComputation.make_computation_with_simulation


def compile_file(circuit_file_name : str ,
                 options : compiler_options.CompilerOptions
                 ) -> Tuple[List[GUISlice], str]:
    """Returns gui slices and the text of the circuit as processed in various stages"""

    pauli_circuit = segmented_qasm_parser.parse_file(circuit_file_name)
    compilation_text = "Input Circuit:\n"
    compilation_text += qkvis.circuit_drawer(qkcirc.QuantumCircuit.from_qasm_file(circuit_file_name)).single_string()

    return compile_circuit(pauli_circuit, options, compilation_text=compilation_text)


def compile_circuit(input_pauli_circuit: circuit.Circuit,
                    options : compiler_options.CompilerOptions,
                    compilation_text : str = ""
                    ) ->  Tuple[List[GUISlice], str]:

    compilation_text += "\nCircuit as Pauli rotations:\n"
    compilation_text += input_pauli_circuit.render_ascii()

    if options.apply_stabilizer_commuting_transform:
        input_pauli_circuit.apply_transformation()
        input_pauli_circuit.remove_y_operators_from_circuit()

        compilation_text += "\nCircuit after the Litinski Transform:\n"
        compilation_text += input_pauli_circuit.render_ascii()


    if options.scheduling_mode == compiler_options.SchedulingMode.Sequential:
        logical_computation = logical_lattice_ops.LinearLogicalLatticeComputation(input_pauli_circuit)
    else:
        assert options.scheduling_mode == compiler_options.SchedulingMode.Parallel
        dag = dependency_graph.DependencyGraph.from_circuit_by_commutation(input_pauli_circuit)
        logical_computation = logical_lattice_ops.ParallelLogicalLatticeComputation(dag)

    lsc = _make_computation_with_simulation(logical_computation, options)


    return sparse_lattice_to_array.slices(lsc.composer.getSlices()), compilation_text