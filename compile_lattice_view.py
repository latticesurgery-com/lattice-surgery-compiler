from mako.template import Template
from typing import *
import patches
import topological_assembly
from math import sqrt


# TODO separate
styles_map = {patches.PatchType.Qubit : "darkkhaki",
              patches.PatchType.DistillationQubit : "orchid",
              patches.PatchType.Ancilla : "aquamarine",
              patches.Orientation.Top : "top",
              patches.Orientation.Bottom : "bottom",
              patches.Orientation.Left : "left",
              patches.Orientation.Right : "right",
              patches.EdgeType.Solid : "solid",
              patches.EdgeType.SolidStiched : "solid",
              patches.EdgeType.Dashed : "dotted",
              patches.EdgeType.DashedStiched : "dotted",
              'edge_color': {
                   patches.EdgeType.Solid : "black",
                   patches.EdgeType.SolidStiched : "#37beff",
                   patches.EdgeType.Dashed : "black",
                   patches.EdgeType.DashedStiched : "#37beff",
              }
}



class VisualArrayCell:
    def __init__(self, patch_type: patches.PatchType, edges : Dict[patches.Orientation, patches.EdgeType]):
        self.edges = edges
        self.patch_type = patch_type
        self.text = None

def sparse_lattice_to_array(lattice: patches.Lattice):
    array = [[None for col in range(lattice.getCols())] for row in range(lattice.getRows())]

    for patch in lattice.patches:
        for cell_idx_in_patch,(x,y) in enumerate(patch.cells):
            array[y][x] = VisualArrayCell(patch.patch_type, {})
            if(patch.state is not None):
                if(cell_idx_in_patch == 0): # Only display the value in the first cell of the patch
                    array[y][x].text = patch.state.ket_repr()

        for edge in patch.edges:
            array[edge.cell[1]][edge.cell[0]].edges[edge.orientation] = edge.border_type

    return array



# Example
tac = topological_assembly.TopologicalAssemblyComposer(topological_assembly.LatticeLayoutInitializer.simpleLayout(5))
tac.measureMultiPatch({
    (0,0):patches.PauliMatrix.X,
    (4,0):patches.PauliMatrix.Z,
    (6,0):patches.PauliMatrix.X
})

template = Template(filename='index.mak')
with open('index.html','w') as f:
    f.write(template.render(
        slices=map(sparse_lattice_to_array,tac.getSlices()),
        styles_map=styles_map))