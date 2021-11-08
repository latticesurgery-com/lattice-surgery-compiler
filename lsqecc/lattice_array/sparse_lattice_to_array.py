from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

import lsqecc.simulation.qubit_state as qs
from lsqecc.lattice_array import visual_array_cell as vac

if TYPE_CHECKING:
    from lsqecc.patches.patches import Lattice


def sparse_lattice_to_array(lattice: Lattice) -> List[List[Optional[vac.VisualArrayCell]]]:
    array: List[List[Optional[vac.VisualArrayCell]]] = [
        [None for col in range(lattice.getCols())] for row in range(lattice.getRows())
    ]

    for patch in lattice.patches:
        for cell_idx_in_patch, (x, y) in enumerate(patch.cells):
            new_cell = vac.VisualArrayCell(patch.patch_type, {})

            if patch.state is not None:
                if cell_idx_in_patch == 0:  # Only display the value in the first cell of the patch
                    new_cell.text = patch.state.ket_repr()
                    if isinstance(patch.state, qs.ActiveState):
                        new_cell.activity = patch.state.activity
            array[y][x] = new_cell

        for edge in patch.edges:
            cell_bounded_by_edge = array[edge.cell[1]][edge.cell[0]]
            assert cell_bounded_by_edge is not None  # Because it would have been set above
            cell_bounded_by_edge.edges[edge.orientation] = edge.border_type

    return array
