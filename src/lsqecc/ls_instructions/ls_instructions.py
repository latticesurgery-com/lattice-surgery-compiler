from dataclasses import dataclass, field
from typing import Dict

import lsqecc.simulation.qubit_state as qs
from lsqecc.pauli_rotations import PauliOperator

PatchId = int


class LSInstruction:
    pass


class DeclareLogicalQubitPatches(LSInstruction):
    patch_ids: PatchId = field(default_factory=lambda: [])

@dataclass
class Init(LSInstruction):
    patch_id: PatchId = -1
    state: qs.QubitState = qs.DefaultSymbolicStates.Zero

@dataclass
class RequestMagicState(LSInstruction):
    patch_id: PatchId = -1

@dataclass
class RequestYState(LSInstruction):
    patch_id: PatchId = -1

@dataclass
class MultiBodyMeasure(LSInstruction):
    patch_pauli_map : Dict[PatchId,PauliOperator] = field(default_factory=lambda: {})

@dataclass
class MeasureSinglePatch(LSInstruction):
    patch_id: PatchId = -1
    op : PauliOperator = PauliOperator.Z

@dataclass
class LogicalPauli(LSInstruction):
    patch_id: PatchId = -1
    op : PauliOperator = PauliOperator.X

@dataclass
class SGate(LSInstruction):
    patch_id: PatchId = -1

@dataclass
class HGate(LSInstruction):
    patc_id: PatchId = -1

