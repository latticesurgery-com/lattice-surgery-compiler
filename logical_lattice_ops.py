from typing import *
from rotation import *
import uuid
from qubit_state import *

class SinglePatchMeasurement:
    def __init__(self, cell_of_patch: Union[Tuple[int,int],uuid.UUID], op: PauliOperator):
        self.cell_of_patch = cell_of_patch
        self.op = op

class MultiBodyMeasurement:
    def __init__(self, patch_pauli_operator_map: Dict[Tuple[int, int], PauliOperator]):
        self.patch_pauli_operator_map = patch_pauli_operator_map
        self.ancilla_uuid = None
        self.ancilla_pauli_op = None

    def add_ancilla(self,ancilla_uuid:uuid.UUID, ancilla_pauli_op:PauliOperator):
        self.ancilla_uuid = ancilla_uuid
        self.ancilla_pauli_op = ancilla_pauli_op



class AncillaQubitPatchInitialization:
    def __init__(self, patch_state: QubitState, patch_uuid : Optional[uuid.UUID] = None):
        self.patch_state = patch_state
        self.patch_uuid = patch_uuid


class IndividualPauliOperators:
    def __init__(self,patch_pauli_operator_map: Dict[Tuple[int, int], PauliOperator] ):
        self.patch_pauli_operator_map = patch_pauli_operator_map



LogicalLatticeOperation = Union[SinglePatchMeasurement,
                                MultiBodyMeasurement,
                                AncillaQubitPatchInitialization,
                                IndividualPauliOperators]