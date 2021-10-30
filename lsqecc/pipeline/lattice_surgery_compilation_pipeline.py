from typing import List, Optional, Tuple

import lsqecc.logical_lattice_ops.logical_lattice_ops as llops
import lsqecc.logical_lattice_ops.visual_array_cell as vac
import lsqecc.patches.lattice_surgery_computation_composer as lscc
import lsqecc.pauli_rotations.segmented_qasm_parser as segmented_qasm_parser
import qiskit.visualization as qkvis
from lsqecc.lattice_array import sparse_lattice_to_array
from qiskit import circuit as qkcirc

GUISlice = List[List[Optional[vac.VisualArrayCell]]]  # 2D array of cells

__all__ = ["compile_file", "VisualArrayCell", "GUISlice"]


def compile_file(
    circuit_file_name: str, apply_litinski_transform: bool = True
) -> Tuple[List[GUISlice], str]:
    """DEPRECATED. compile_str"""
    with open(circuit_file_name) as input_file:
        return compile_str(input_file.read(), apply_litinski_transform)


def compile_str(
    qasm_circuit: str, apply_litinski_transform: bool = True
) -> Tuple[List[GUISlice], str]:
    """Returns gui slices and the text of the circuit as processed in various stages"""
    composer_class = lscc.LatticeSurgeryComputation
    layout_types = lscc.LayoutType

    input_circuit = segmented_qasm_parser.parse_str(qasm_circuit)

    compilation_text = "Input Circuit:\n"

    compilation_text += qkvis.circuit_drawer(
        qkcirc.QuantumCircuit.from_qasm_str(qasm_circuit)
    ).single_string()

    compilation_text += "\nCircuit as Pauli rotations:\n"
    compilation_text += input_circuit.render_ascii()

    if apply_litinski_transform:
        input_circuit.apply_transformation()
        input_circuit.remove_y_operators_from_circuit()
        compilation_text += "\nCircuit after the Litinski Transform:\n"
        compilation_text += input_circuit.render_ascii()

    logical_computation = llops.LogicalLatticeComputation(input_circuit)
    lsc = composer_class.make_computation_with_simulation(
        logical_computation, layout_types.SimplePreDistilledStates
    )

    return list(map(sparse_lattice_to_array, lsc.composer.getSlices())), compilation_text
