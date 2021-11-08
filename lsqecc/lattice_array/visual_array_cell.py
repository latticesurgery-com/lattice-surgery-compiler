# Copyright (C) 2020 - George Watkins and Alex Nguyen
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
