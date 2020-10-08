from mako.template import Template
from typing import *
import patches
from math import sqrt


# TODO separate
styles_map = {patches.PatchType.Qubit : "darkkhaki",
              patches.PatchType.Ancilla : "aquamarine",
              patches.Orientation.Top : "top",
              patches.Orientation.Bottom : "bottom",
              patches.Orientation.Left : "left",
              patches.Orientation.Right : "right",
              patches.EdgeType.Solid : "solid",
              patches.EdgeType.Dashed : "dashed"
}



class VisualArrayCell:
    def __init__(self, patch_type: patches.PatchType, edges : Dict[patches.Orientation, patches.EdgeType]):
        self.edges = edges
        self.patch_type = patch_type
        self.text = None

def sparse_lattice_to_array(lattice: patches.Lattice):
    ncols = 1+max(map(lambda patch: max(patch.cells, key=lambda c: c[0])[0], lattice.patches))
    nrows = 1+max(map(lambda patch: max(patch.cells, key=lambda c: c[1])[1], lattice.patches))
    array = [ [None for col in range(ncols)] for row in range(nrows) ]

    for patch in lattice.patches:
        for x,y in patch.cells:
            array[y][x] = VisualArrayCell(patch.patch_type, {})
            if(patch.state is not None):
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
])

# Construct a sample lattice
lattice1= patches.Lattice([
    patches.Patch(patches.PatchType.Qubit, patches.PatchQubitState(1,0), [(2,2)],[
        patches.Edge(patches.EdgeType.Solid, (2, 2), patches.Orientation.Top),
        patches.Edge(patches.EdgeType.Solid, (2, 2), patches.Orientation.Bottom),
        patches.Edge(patches.EdgeType.Dashed, (2, 2), patches.Orientation.Left),
        patches.Edge(patches.EdgeType.Dashed, (2, 2), patches.Orientation.Right)
    ])
])


array = sparse_lattice_to_array(lattice)
array1 = sparse_lattice_to_array(lattice1)

slices = [array,array1]


template = Template(filename='index.mak')
with open('index.html','w') as f:
    f.write(template.render(
        slices=slices,
        styles_map=styles_map))