"""
Lattice Surgery instructions before routing. These classes encode a language of operations that a
router can use to generate a 3D-Assembly of lattice surgery instructions over a certain layout.

Specification: https://github.com/latticesurgery-com/lattice-surgery-compiler/issues/246
"""

from dataclasses import dataclass, field
from typing import Dict, List

import lsqecc.simulation.qubit_state as qs
from lsqecc.pauli_rotations import PauliOperator

PatchId = int


class LSInstruction:
    def get_args(self) -> List[str]:
        raise NotImplementedError


@dataclass
class DeclareLogicalQubitPatches(LSInstruction):
    patch_ids: List[PatchId] = field(default_factory=lambda: [])

    def __repr__(self):
        return f"{type(self).__name__} {','.join(map(repr,self.patch_ids))}"


@dataclass
class Init(LSInstruction):
    patch_id: PatchId = -1
    state: qs.QubitState = qs.DefaultSymbolicStates.Zero

    def __repr__(self):
        return f"{type(self).__name__} {self.patch_id} {self.state.ket_repr()}"


@dataclass
class RequestMagicState(LSInstruction):
    patch_id: PatchId = -1

    def __repr__(self):
        return f"{type(self).__name__}  {self.patch_id}"


@dataclass
class RequestYState(LSInstruction):
    patch_id: PatchId = -1

    def __repr__(self):
        return f"{type(self).__name__}  {self.patch_id}"


@dataclass
class MultiBodyMeasure(LSInstruction):
    patch_pauli_map: Dict[PatchId, PauliOperator] = field(default_factory=lambda: {})

    def __repr__(self):
        return (
            type(self).__name__
            + " "
            + ",".join(f"{patch_id}:{op}" for patch_id, op in self.patch_pauli_map.items())
        )


@dataclass
class MeasureSinglePatch(LSInstruction):
    patch_id: PatchId = -1
    op: PauliOperator = PauliOperator.Z

    def __repr__(self):
        return f"{type(self).__name__} {self.patch_id} {self.op}"


@dataclass
class LogicalPauli(LSInstruction):
    patch_id: PatchId = -1
    op: PauliOperator = PauliOperator.X

    def __repr__(self):
        return f"{type(self).__name__} {self.patch_id} {self.op}"


@dataclass
class SGate(LSInstruction):
    patch_id: PatchId = -1

    def __repr__(self):
        return f"{type(self).__name__} {self.patch_id}"


@dataclass
class HGate(LSInstruction):
    patch_id: PatchId = -1

    def __repr__(self):
        return f"{type(self).__name__} {self.patch_id}"
