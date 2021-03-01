from typing import *
from rotation import *
import uuid
from qubit_state import *


# TODO give a uuid to all patches

class LogicalLatticeOperation:

    def get_operating_patches(self) -> List[Union[Tuple[int,int],uuid.UUID]]:
        raise NotImplemented()



class SinglePatchMeasurement(LogicalLatticeOperation):
    def __init__(self, cell_of_patch: Union[Tuple[int,int],uuid.UUID], op: PauliOperator):
        self.cell_of_patch = cell_of_patch
        self.op = op

    def get_operating_patches(self) -> List[Union[Tuple[int,int],uuid.UUID]]:
        return [self.cell_of_patch]


class MultiBodyMeasurement(LogicalLatticeOperation):
    def __init__(self, patch_pauli_operator_map: Dict[Tuple[int, int], PauliOperator]):
        self.patch_pauli_operator_map = patch_pauli_operator_map
        self.ancilla_uuid = None
        self.ancilla_pauli_op = None

    def add_ancilla(self,ancilla_uuid:uuid.UUID, ancilla_pauli_op:PauliOperator):
        self.ancilla_uuid = ancilla_uuid
        self.ancilla_pauli_op = ancilla_pauli_op

    def get_operating_patches(self) -> List[Union[Tuple[int,int],uuid.UUID]]:
        out = list(self.patch_pauli_operator_map.keys())
        out.append(self.ancilla_uuid)
        return out


class AncillaQubitPatchInitialization(LogicalLatticeOperation):
    def __init__(self, patch_state: QubitState, patch_uuid : Optional[uuid.UUID] = None):
        self.patch_state = patch_state
        self.patch_uuid = patch_uuid

    def get_operating_patches(self) -> List[Union[Tuple[int,int],uuid.UUID]]:
        return [self.patch_uuid]


class IndividualPauliOperators(LogicalLatticeOperation):
    def __init__(self,patch_pauli_operator_map: Dict[Tuple[int, int], PauliOperator] ):
        self.patch_pauli_operator_map = patch_pauli_operator_map

    def get_operating_patches(self) -> List[Union[Tuple[int,int],uuid.UUID]]:
        return list(self.patch_pauli_operator_map.keys())


