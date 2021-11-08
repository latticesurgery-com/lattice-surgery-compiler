from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from lsqecc.patches.patches import EdgeType, Orientation, PatchType
    from lsqecc.simulation.qubit_state import QubitActivity


class VisualArrayCell:
    def __init__(self, patch_type: PatchType, edges: Dict[Orientation, EdgeType]):
        self.edges = edges
        self.patch_type = patch_type
        self.text = None
        self.activity: Optional[QubitActivity] = None
