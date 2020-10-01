from mako.template import Template
from typing import *
import patches


styles_map = {patches.PatchType.Qubit : "darkkhaki",
              patches.PatchType.Ancilla : "aquamarine",
              patches.Orientation.Top : "top",
              patches.Orientation.Bottom : "bottom",
              patches.Orientation.Left : "left",
              patches.Orientation.Right : "right",
              patches.EdgeType.Solid : "solid",
              patches.EdgeType.Dashed : "dashed"
}



class ArrayCell:
    def __init__(self, patch_type: patches.PatchType, edges : Dict[patches.Orientation, patches.EdgeType]):
        self.edges = edges
        self.patch_type = patch_type
        pass

def sparse_lattice_to_array(lattice: patches.Lattice):
    ncols = 1+max(map(lambda patch: max(patch.cells,key=lambda c: c[0])[0], lattice.patches))
    nrows = 1+max(map(lambda patch: max(patch.cells,key=lambda c: c[1])[1], lattice.patches))
    array = [ [None for col in range(ncols)] for row in range(nrows) ]

    for patch in lattice.patches:
        for x,y in patch.cells:
            array[y][x] = ArrayCell(patch.patch_type,{})

        for edge in patch.edges:
            array[edge.cell[1]][edge.cell[0]].edges[edge.orientation] = edge.border_type

    return array


# Construct a sample lattice
lattice = patches.Lattice([
    patches.Patch(patches.PatchType.Qubit, [(2,2)],[
        patches.Edge(patches.EdgeType.Solid, (2, 2), patches.Orientation.Top),
        patches.Edge(patches.EdgeType.Solid, (2, 2), patches.Orientation.Bottom),
        patches.Edge(patches.EdgeType.Dashed, (2, 2), patches.Orientation.Left),
        patches.Edge(patches.EdgeType.Dashed, (2, 2), patches.Orientation.Right)
    ]),
    patches.Patch(patches.PatchType.Ancilla, [(2,3)],[]),
    patches.Patch(patches.PatchType.Qubit, [(3,3),(4,3)],[
        patches.Edge(patches.EdgeType.Solid, (3, 3), patches.Orientation.Top),
        patches.Edge(patches.EdgeType.Solid, (3, 3), patches.Orientation.Bottom),
        patches.Edge(patches.EdgeType.Dashed, (3, 3), patches.Orientation.Left),
        patches.Edge(patches.EdgeType.Solid, (4, 3), patches.Orientation.Top),
        patches.Edge(patches.EdgeType.Solid, (4, 3), patches.Orientation.Bottom),
        patches.Edge(patches.EdgeType.Dashed, (4, 3), patches.Orientation.Right),
    ]),
])


array = sparse_lattice_to_array(lattice)
template = Template(filename='index.mak')
with open('index.html','w') as f:
    f.write(template.render(nrows=len(array),ncols=len(array[0]),array=array,styles_map=styles_map))