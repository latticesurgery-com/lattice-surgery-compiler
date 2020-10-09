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
              patches.EdgeType.Dashed : "dashed",
              'edge_color_by_patch_type': {
                   patches.PatchType.Qubit : 'black',
                   patches.PatchType.DistillationQubit : 'black',
                   patches.PatchType.Ancilla : 'blue',
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


# Construct a sample lattice
lattice = patches.Lattice([
    patches.Patch(patches.PatchType.Qubit, patches.PatchQubitState(1,0), [(2,2)],[
        patches.Edge(patches.EdgeType.Solid, (2, 2), patches.Orientation.Top),
        patches.Edge(patches.EdgeType.Solid, (2, 2), patches.Orientation.Bottom),
        patches.Edge(patches.EdgeType.Dashed, (2, 2), patches.Orientation.Left),
        patches.Edge(patches.EdgeType.Dashed, (2, 2), patches.Orientation.Right)
    ]),
    patches.Patch(patches.PatchType.Ancilla, None, [(2,3)],[]),
    patches.Patch(patches.PatchType.Qubit, patches.PatchQubitState(1/sqrt(2),1/sqrt(2)) , [(3,3),(4,3)],[
        patches.Edge(patches.EdgeType.Solid, (3, 3), patches.Orientation.Top),
        patches.Edge(patches.EdgeType.Solid, (3, 3), patches.Orientation.Bottom),
        patches.Edge(patches.EdgeType.Dashed, (3, 3), patches.Orientation.Left),
        patches.Edge(patches.EdgeType.Solid, (4, 3), patches.Orientation.Top),
        patches.Edge(patches.EdgeType.Solid, (4, 3), patches.Orientation.Bottom),
        patches.Edge(patches.EdgeType.Dashed, (4, 3), patches.Orientation.Right),
    ]),
],0,0)

# Construct a sample lattice
lattice1= patches.Lattice([
    patches.Patch(patches.PatchType.Qubit, patches.PatchQubitState(1,0), [(2,2)],[
        patches.Edge(patches.EdgeType.Solid, (2, 2), patches.Orientation.Top),
        patches.Edge(patches.EdgeType.Solid, (2, 2), patches.Orientation.Bottom),
        patches.Edge(patches.EdgeType.Dashed, (2, 2), patches.Orientation.Left),
        patches.Edge(patches.EdgeType.Dashed, (2, 2), patches.Orientation.Right)
    ])
],0,0)


array = sparse_lattice_to_array(lattice)
array1 = sparse_lattice_to_array(lattice1)

slices = [array,array1]


template = Template(filename='index.mak')
with open('index.html','w') as f:
    f.write(template.render(
        slices=[sparse_lattice_to_array(topological_assembly.LatticeLayoutInitializer.simpleLayout(5))],
        styles_map=styles_map))