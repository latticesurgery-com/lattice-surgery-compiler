from typing import *
import enum


class PatchQubitState:
    def __init__(self,zero_amplitude,one_amplitude):
        self.zero_amplitude = zero_amplitude
        self.one_amplitude = one_amplitude
        # TODO check normalization

    def ket_repr(self):
        out = []
        if self.zero_amplitude != 0: out.append("%1.2f|0>"%self.zero_amplitude)
        if self.one_amplitude != 0: out.append("%1.2f|1>"%self.one_amplitude)
        return "<br>".join(out)

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
    def __init__(self, patch_type: PatchType, state: PatchQubitState, cells: List[Tuple[int,int]], edges: List[Edge]):
        self.patch_type = patch_type
        self.cells = cells
        self.edges = edges
        self.state = state

        # TODO sanity check


class Lattice:
    def __init__(self, patches: List[Patch]):
        self.patches = patches




