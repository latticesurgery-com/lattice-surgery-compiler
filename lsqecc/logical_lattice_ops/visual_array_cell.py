from simulation import QubitActivity
from typing import Dict, Optional

from lsqecc.patches import EdgeType, Orientation, PatchType


class VisualArrayCell:
    def __init__(self, patch_type: PatchType, edges: Dict[Orientation, EdgeType]):
        self.edges = edges
        self.patch_type = patch_type
        self.text = None
        self.activity: Optional[QubitActivity] = None
