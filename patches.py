from typing import *
from enum import Enum
from rotation import *


class QubitState:

    def __init__(self):
        self.is_active = False

    def ket_repr(self):
        raise Exception("Method not implemented")

    def compose_operator(self, op: PauliOperator):
        return self # Do nothing


class SymbolicState(QubitState):
    def __init__(self, name : str):
        self.name = name

    def ket_repr(self):
        return self.name


class InitializeableState(Enum):
    Zero = SymbolicState('|0>')
    Plus = SymbolicState('|+>')
    UnknownState = SymbolicState('|?>')
    Magic = SymbolicState('|m>') # magic state (|0>+e^(pi*i/4)|1>)/sqrt(2)

    def ket_repr(self):
        return self.value

    def compose_operator(self, op: PauliOperator):
        return InitializeableState.UnknownState



class ExplicitPatchQubitState(QubitState):
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


    def get_graph_edge(edge)-> Optional[Tuple[int,int]]:
        col,row = edge.cell
        return ({
            Orientation.Top:    ((col,row),(col,row-1)),
            Orientation.Bottom: ((col,row),(col,row+1)),
            Orientation.Left:   ((col,row),(col-1,row)),
            Orientation.Right:  ((col,row),(col+1,row))
        }).get(edge.orientation)


class EdgeType(Enum):
    Solid = "Solid"
    SolidStiched = "SolidStiched"
    Dashed = "Dashed"
    DashedStiched = "DashedStiched"
    AncillaJoin = "AncillaJoin"

    def stitched_type(self):
        if self == EdgeType.Solid: return EdgeType.SolidStiched
        if self == EdgeType.Dashed: return EdgeType.DashedStiched
        return self

    def unstitched_type(self):
        if self == EdgeType.SolidStiched: return EdgeType.Solid
        if self == EdgeType.DashedStiched: return EdgeType.Dashed
        return self


PAULI_OPERATOR_TO_EDGE_MAP : Dict[PauliOperator, EdgeType] = {
    PauliOperator.X: EdgeType.Dashed,
    PauliOperator.Z: EdgeType.Solid
}


class PatchType(Enum):
    Qubit = "Qubit"
    DistillationQubit = "DistillationQubit"
    Ancilla = "Ancilla"


class Edge:
    def __init__(self, edge_type: EdgeType, cell: Tuple[int, int], orientation: List[Orientation]):
        self.cell = cell
        self.orientation = orientation
        self.border_type = edge_type

    def getNeighbouringCell(self) -> Optional[Tuple[int,int]]:
        col, row = self.cell
        return ({
                Orientation.Top:    (col, row - 1),
                Orientation.Bottom: (col, row + 1),
                Orientation.Left:   (col - 1, row),
                Orientation.Right:  (col + 1, row)
            }).get(self.orientation)

    def isStiched(self):
        return self.border_type in [EdgeType.SolidStiched, EdgeType.DashedStiched]

class Patch:
    def __init__(self,
                 patch_type: PatchType,
                 state: Union[None, QubitState],
                 cells: List[Tuple[int,int]],
                 edges: List[Edge]):
        self.patch_type = patch_type
        self.cells = cells
        self.edges = edges
        self.state = state

        # TODO sanity check

    def getRepresentative(self)->Tuple[int,int]:
        return self.cells[0]


    def borders(self, to_cell: Tuple[int,int]) -> List[Edge]:
        """Get all the borders betwen self and to_cell"""
        edges_between = list()
        for from_cell in self.cells:
            for edge in self.edges:
                if edge.cell == from_cell and edge.orientation == get_border_orientation(from_cell,to_cell):
                    edges_between.append(edge)
        return edges_between



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

    def clear(self):
        self.patches = []

    def getPatchOfCell(self, target : Tuple[int,int]) -> Optional[Patch]:
        for patch in self.patches:
            for cell in patch.cells:
                if cell == target:
                    return patch
        return None

    def cellIsFree(self, target : Tuple[int,int]):
        return self.getPatchOfCell(target) is None

    def getPatchRepresentative(self, cell: Tuple[int,int]):
        maybe_patch = self.getPatchOfCell(cell)
        return maybe_patch.cells[0] if maybe_patch is not None else cell

    def patchTypeOfCell(self, cell: Tuple[int,int]) -> Optional[PatchType]:
        maybe_patch = self.getPatchOfCell(cell)
        return maybe_patch.patch_type if maybe_patch is not None else None


def get_border_orientation(subject: Tuple[int,int], neighbour: Tuple[int,int]):
    return ({
        ( 0, -1): Orientation.Top    ,
        ( 0, +1): Orientation.Bottom ,
        (-1, 0 ): Orientation.Left   ,
        (+1, 0 ): Orientation.Right
    })[(neighbour[0]-subject[0], neighbour[1]-subject[1])]


