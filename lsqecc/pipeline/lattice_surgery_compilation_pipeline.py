import qiskit.visualization as qkvis
from logical_lattice_ops import LogicalLatticeComputation, VisualArrayCell
from patches import LatticeSurgeryComputation, LayoutType
from qiskit import circuit as qkcirc
from typing import List, Optional, Tuple

from lsqecc.pauli_rotations import Circuit
import lsqecc.pauli_rotations.segmented_qasm_parser as segmented_qasm_parser
from lsqecc.lattice_array import sparse_lattice_to_array

GUISlice = List[List[Optional[VisualArrayCell]]]  # 2D array of cells

__all__ = ['compile_file', 'VisualArrayCell', 'GUISlice']


def compile_file(circuit_file_name: str,
                 apply_litinski_transform: bool = True) -> Tuple[List[GUISlice], str]:
    """DEPRECATED. compile_str"""
    with open(circuit_file_name) as input_file:
        return compile_str(input_file.read(), apply_litinski_transform)


def compile_str(qasm_circuit: str,
                apply_litinski_transform: bool = True) -> Tuple[List[GUISlice], str]:
    """Returns gui slices and the text of the circuit as processed in various stages"""
    composer_class = LatticeSurgeryComputation
    layout_types = LayoutType

    input_circuit = segmented_qasm_parser.parse_str(qasm_circuit)

    compilation_text = "Input Circuit:\n"

    compilation_text += qkvis.circuit_drawer(qkcirc.QuantumCircuit.from_qasm_str(qasm_circuit)).single_string()

    compilation_text += "\nCircuit as Pauli rotations:\n"
    compilation_text += input_circuit.render_ascii()

    if apply_litinski_transform:
        input_circuit.apply_transformation()
        input_circuit.remove_y_operators_from_circuit()
        compilation_text += "\nCircuit after the Litinski Transform:\n"
        compilation_text += input_circuit.render_ascii()

    logical_computation = LogicalLatticeComputation(input_circuit)
    lsc = composer_class.make_computation_with_simulation(logical_computation, layout_types.SimplePreDistilledStates)

    return list(map(sparse_lattice_to_array, lsc.composer.getSlices())), compilation_text
