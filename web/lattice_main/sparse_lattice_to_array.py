import sys
from . import VisualArrayCell

import patches

def sparse_lattice_to_array(lattice: patches.Lattice): # -> List[List[Optional[VisualArrayCell]]]:
    array = [[None for col in range(lattice.getCols())] for row in range(lattice.getRows())]

    for patch in lattice.patches:
        for cell_idx_in_patch,(x,y) in enumerate(patch.cells):
            array[y][x] = VisualArrayCell(patch.patch_type, {})
            if(patch.state is not None):
                if(cell_idx_in_patch == 0): # Only display the value in the first cell of the patch
                    array[y][x].text = patch.state.ket_repr()
                    if isinstance(patch.state,ActiveState):
                        array[y][x].activity = patch.state.activity

        for edge in patch.edges:
            array[edge.cell[1]][edge.cell[0]].edges[edge.orientation] = edge.border_type

    return array