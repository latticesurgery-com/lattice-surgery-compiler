from typing import *
from patches import *
from lattice_surgery_computation_composer import *



class SinglePatchMeasurement:
    def __init__(self, cell_of_patch: Union[Tuple[int,int],uuid.UUID], op: PauliOperator):
        self.cell_of_patch = cell_of_patch
        self.op = op

    def get_cell(self, lsc : LatticeSurgeryComputation):
        if isinstance(self.cell_of_patch,uuid.UUID):
            maybe_patch = lsc.composer.lattice().getPatchByUuid(self.cell_of_patch)
            if maybe_patch is None:
                raise Exception("Failed to find patch")
            return maybe_patch.getRepresentative()
        return self.cell_of_patch

class MultiBodyMeasurement:
    def __init__(self, patch_pauli_operator_map: Dict[Tuple[int, int], PauliOperator]):
        self.patch_pauli_operator_map = patch_pauli_operator_map
        self.ancilla_uuid = None
        self.ancilla_pauli_op = None

    def add_ancilla(self,ancilla_uuid:uuid.UUID, ancilla_pauli_op:PauliOperator):
        self.ancilla_uuid = ancilla_uuid
        self.ancilla_pauli_op = ancilla_pauli_op


def circuit_to_patch_measurement(self, lsc: LatticeSurgeryComputation, m: Measurement) \
        -> Union[SinglePatchMeasurement,MultiBodyMeasurement]:
    ret : Dict[Tuple[int, int], patches.PauliOperator] = dict()
    for qubit_idx in range(m.qubit_num):
        if m.get_op(qubit_idx)!=PauliOperator.I:
            ret[lsc.get_cell_for_qubit_idx(qubit_idx)] = m.get_op(qubit_idx)

    if len(ret) == 1:
        return SinglePatchMeasurement(next(iter(ret)),ret[next(iter(ret))])
    return  MultiBodyMeasurement(ret)


class AncillaQubitPatchInitialization:
    def __init__(self, patch_state: QubitState, patch_uuid : Optional[uuid.UUID] = None):
        self.patch_state = patch_state
        self.patch_uuid = patch_uuid


class IndividualPauliOperators:
    def __init__(self,patch_pauli_operator_map: Dict[Tuple[int, int], PauliOperator] ):
        self.patch_pauli_operator_map = patch_pauli_operator_map
