from mako.template import Template
from typing import *
import patches
from qubit_state import *

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
              patches.EdgeType.AncillaJoin : "solid",
              'edge_color': {
                   patches.EdgeType.Solid : "black",
                   patches.EdgeType.SolidStiched : "#37beff",
                   patches.EdgeType.Dashed : "black",
                   patches.EdgeType.DashedStiched : "#37beff",
                   patches.EdgeType.AncillaJoin : "aquamarine",
              },
              'activity_color':
                  {
                      ActivityType.Unitary : "#00baff",
                      ActivityType.Measurement : "#ff0000",
                  }
}



class VisualArrayCell:
    def __init__(self, patch_type: patches.PatchType, edges : Dict[patches.Orientation, patches.EdgeType]):
        self.edges = edges
        self.patch_type = patch_type
        self.text = None
        self.activity: Optional[QubitActivity] = None

def sparse_lattice_to_array(lattice: patches.Lattice) -> List[List[Optional[VisualArrayCell]]]:
    array = [[None for col in range(lattice.getCols())] for row in range(lattice.getRows())]

    for patch in lattice.patches:
        for cell_idx_in_patch,(x,y) in enumerate(patch.cells):
            array[y][x] = VisualArrayCell(patch.patch_type, {})
            if(patch.state is not None):
                if(cell_idx_in_patch == 0): # Only display the value in the first cell of the patch
                    array[y][x].text = patch.state.ket_repr().replace("\n","<br>")
                    if isinstance(patch.state,ActiveState):
                        array[y][x].activity = patch.state.activity

        for edge in patch.edges:
            array[edge.cell[1]][edge.cell[0]].edges[edge.orientation] = edge.border_type

    return array





def render_to_file(slices : List[patches.Lattice],
                   output_file_name : str,
                   template='templates/lattice_view.mak') -> str:
    template = Template(filename=template)
    with open(output_file_name, 'w') as f:
        f.write(template.render(
            slices=list(map(sparse_lattice_to_array, slices)),
            styles_map=styles_map,
            patches=patches
        ))

def render_html(slices : List[patches.Lattice]) -> str:
    template = Template(filename='templates/lattice_view.mak')
    return template.render(
        slices=list(map(sparse_lattice_to_array, slices)),
        styles_map=styles_map,
        patches=patches
    )