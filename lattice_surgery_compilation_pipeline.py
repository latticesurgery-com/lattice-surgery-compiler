
import circuit
import lattice_surgery_computation_composer
import logical_lattice_ops
import sparse_lattice_to_array
from visual_array_cell import *


GUISlice = List[List[Optional[VisualArrayCell]]] # 2D array of cells

__all__ = ['compile_file','VisualArrayCell','GUISlice']

def compile_file(circuit_file_name : str ,
                 apply_litinski_transform:bool=True) -> List[GUISlice]:

    composer_class = lattice_surgery_computation_composer.LatticeSurgeryComputation
    layout_types = lattice_surgery_computation_composer.LayoutType

    input_circuit = circuit.Circuit.load_from_file(circuit_file_name)

    print(input_circuit.render_ascii())

    if apply_litinski_transform:
        input_circuit.apply_transformation()
        input_circuit.remove_y_operators_from_circuit()
        print("Applied Litinski Transform")
        print(input_circuit.render_ascii())

    logical_computation = logical_lattice_ops.LogicalLatticeComputation(input_circuit)
    lsc = composer_class.make_computation_with_simulation(logical_computation, layout_types.SimplePreDistilledStates)


    return list(map(sparse_lattice_to_array.sparse_lattice_to_array, lsc.composer.getSlices()))