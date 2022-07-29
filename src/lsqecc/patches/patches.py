# Copyright (C) 2020-2021 - George Watkins and Alex Nguyen
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
# USA

from __future__ import annotations

import itertools
import uuid
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from lsqecc.pauli_rotations import PauliOperator

if TYPE_CHECKING:
    from lsqecc.logical_lattice_ops.logical_lattice_ops import LogicalLatticeOperation
    from lsqecc.simulation.qubit_state import QubitState


class Orientation(Enum):
    Top = "Top"
    Bottom = "Bottom"
    Left = "Left"
    Right = "Right"

    @staticmethod
    def get_graph_edge(edge: Edge) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        col, row = edge.cell
        return (
            {
                Orientation.Top: ((col, row), (col, row - 1)),
                Orientation.Bottom: ((col, row), (col, row + 1)),
                Orientation.Left: ((col, row), (col - 1, row)),
                Orientation.Right: ((col, row), (col + 1, row)),
            }
        ).get(edge.orientation)


class EdgeType(Enum):
    Solid = "Solid"
    SolidStiched = "SolidStiched"
    Dashed = "Dashed"
    DashedStiched = "DashedStiched"
    AncillaJoin = "AncillaJoin"

    def stitched_type(self):
        if self == EdgeType.Solid:
            return EdgeType.SolidStiched
        if self == EdgeType.Dashed:
            return EdgeType.DashedStiched
        return self

    def unstitched_type(self):
        if self == EdgeType.SolidStiched:
            return EdgeType.Solid
        if self == EdgeType.DashedStiched:
            return EdgeType.Dashed
        return self


PAULI_OPERATOR_TO_EDGE_MAP: Dict[PauliOperator, EdgeType] = {
    PauliOperator.X: EdgeType.Dashed,
    PauliOperator.Z: EdgeType.Solid,
}


class PatchType(Enum):
    Qubit = "Qubit"
    DistillationQubit = "DistillationQubit"
    Ancilla = "Ancilla"


class Edge:
    """Class for representing an Edge (of a Patch) on a 2D Lattice."""

    def __init__(self, edge_type: EdgeType, cell: Tuple[int, int], orientation: Orientation):
        self.cell = cell
        self.orientation = orientation
        self.border_type = edge_type

    def getNeighbouringCell(self) -> Optional[Tuple[int, int]]:
        col, row = self.cell
        return (
            {
                Orientation.Top: (col, row - 1),
                Orientation.Bottom: (col, row + 1),
                Orientation.Left: (col - 1, row),
                Orientation.Right: (col + 1, row),
            }
        ).get(self.orientation)

    def isStiched(self):
        return self.border_type in [EdgeType.SolidStiched, EdgeType.DashedStiched]


class CoordType(Enum):
    Col = 0
    Row = 1


class Patch:
    def __init__(
        self,
        patch_type: PatchType,
        state: Optional[QubitState],
        cells: List[Tuple[int, int]],
        edges: List[Edge],
        qubit_uuid: Optional[uuid.UUID] = None,
    ):
        self.patch_type = patch_type
        self.cells = cells
        self.edges = edges
        self.state = state
        self.patch_uuid = qubit_uuid
        # TODO sanity check

    def getRepresentative(self) -> Tuple[int, int]:
        return self.cells[0]

    def borders(self, to_cell: Tuple[int, int]) -> List[Edge]:
        """Get all the borders betwen self and to_cell"""
        edges_between = list()
        for from_cell in self.cells:
            for edge in self.edges:
                if edge.cell == from_cell and edge.orientation == get_border_orientation(
                    from_cell, to_cell
                ):
                    edges_between.append(edge)
        return edges_between

    def getCoordList(self, coord_type: CoordType) -> List[int]:
        return list(map(lambda cell: cell[coord_type.value], self.cells))

    def set_uuid(self, patch_uuid: uuid.UUID):
        self.patch_uuid = patch_uuid


class Lattice:
    def __init__(self, patches: List[Patch], min_rows: int, min_cols: int):
        self.patches = patches
        self.min_rows = min_rows
        self.min_cols = min_cols
        self.logical_ops: List[LogicalLatticeOperation] = []

    def getMaxCoord(self, coord_type: CoordType) -> int:
        all_coords = list(
            itertools.chain.from_iterable(
                map(lambda patch: patch.getCoordList(coord_type), self.patches)
            )
        )
        lower_bound = self.min_rows if coord_type == CoordType.Row else self.min_cols

        max_coords = max(all_coords) if len(all_coords) else 0
        return max(1 + max_coords, lower_bound)

    def getCols(self):
        return self.getMaxCoord(CoordType.Col)

    def getRows(self):
        return self.getMaxCoord(CoordType.Row)

    def clear(self):
        self.patches = []

    def getPatchOfCell(self, target: Tuple[int, int]) -> Optional[Patch]:
        for patch in self.patches:
            for cell in patch.cells:
                if cell == target:
                    return patch
        return None

    def cellIsFree(self, target: Tuple[int, int]):
        return self.getPatchOfCell(target) is None

    def getPatchRepresentative(self, cell: Tuple[int, int]):
        maybe_patch = self.getPatchOfCell(cell)
        return maybe_patch.cells[0] if maybe_patch is not None else cell

    def patchTypeOfCell(self, cell: Tuple[int, int]) -> Optional[PatchType]:
        maybe_patch = self.getPatchOfCell(cell)
        return maybe_patch.patch_type if maybe_patch is not None else None

    def getPatchByUuid(self, patch_uuid: uuid.UUID) -> Optional[Patch]:
        for p in self.patches:
            if p.patch_uuid is not None and p.patch_uuid == patch_uuid:
                return p
        return None


def get_border_orientation(subject: Tuple[int, int], neighbour: Tuple[int, int]):
    return (
        {
            (0, -1): Orientation.Top,
            (0, +1): Orientation.Bottom,
            (-1, 0): Orientation.Left,
            (+1, 0): Orientation.Right,
        }
    )[(neighbour[0] - subject[0], neighbour[1] - subject[1])]
