from typing import *
import enum

class Orientation(enum.Enum):
    Top = "Top"
    Bottom = "Bottom"
    Left = "Left"
    Right = "Right"

class EdgeType(enum.Enum):
    Solid = "Solid"
    Dashed = "Dashed"


class PatchType(enum.Enum):
    Qubit = "Qubit"
    Ancilla = "Ancilla"


class Edge:
    def __init__(self, edge_type: EdgeType, cell: Tuple[int, int], orientation: List[str]):
        self.cell = cell
        self.orientation = orientation
        self.border_type = edge_type


class Patch:
    def __init__(self, patch_type: PatchType, cells: List[Tuple[int,int]], edges: List[Edge]):
        self.patch_type = patch_type
        self.cells = cells
        self.edges = edges
        # TODO sanity check


class Lattice:
    def __init__(self, patches: List[Patch]):
        self.patches = patches




