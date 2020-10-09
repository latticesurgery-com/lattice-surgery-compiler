from typing import *
from enum import Enum


class InitializeableState(Enum):
    Zero = '|0>'
    Plus = '|+>'
    Magic = '|m>' # magic state (|0>+e^(pi*i/4)|1>)/sqrt(2)
    def ket_repr(self):
        return self.value

class NonTrivialState(Enum):
    def ket_repr(self):
        return "|?>"

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

class Orientation(Enum):
    Top = "Top"
    Bottom = "Bottom"
    Left = "Left"
    Right = "Right"

class EdgeType(Enum):
    Solid = "Solid"
    Dashed = "Dashed"


class PatchType(Enum):
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
    def __init__(self, patches: List[Patch], min_rows: int, min_cols: int):
        self.patches = patches
        self.min_rows = min_rows
        self.min_cols = min_cols


    def getCols(self):
        return max(
            1+max(map(lambda patch: max(patch.cells, key=lambda c: c[0])[0], self.patches)),
            self.min_cols
        )

    def getRows(self):
        return max(
            1+max(map(lambda patch: max(patch.cells, key=lambda c: c[1])[1], self.patches)),
            self.min_rows
        )



