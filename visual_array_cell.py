import patches
from typing import *


class VisualArrayCell:
    def __init__(self, patch_type: patches.PatchType, edges: Dict[patches.Orientation, patches.EdgeType]):
        self.edges = edges
        self.patch_type = patch_type
        self.text = None
        self.activity: Optional['QubitActivity'] = None


GUISlice = List[List[Optional[VisualArrayCell]]] # 2D array of cells
