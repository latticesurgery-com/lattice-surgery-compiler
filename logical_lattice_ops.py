from typing import *
from rotation import *
import uuid
from collections import deque
from qubit_state import *
from circuit import *


# TODO give a uuid to all patches

"""Patches are now identified by uuids"""

class LogicalLatticeOperation:
    def get_operating_patches(self) -> List[uuid.UUID]:
        raise NotImplemented()




class SinglePatchMeasurement(LogicalLatticeOperation):
    def __init__(self, cell_of_patch: uuid.UUID, op: PauliOperator):
        self.cell_of_patch = cell_of_patch
        self.op = op

    def get_operating_patches(self) -> List[uuid.UUID]:
        return [self.cell_of_patch]


class MultiBodyMeasurement(LogicalLatticeOperation):
    def __init__(self, patch_pauli_operator_map: Dict[uuid.UUID, PauliOperator]):
        self.patch_pauli_operator_map = patch_pauli_operator_map

    def get_operating_patches(self) -> List[uuid.UUID]:
        return list(self.patch_pauli_operator_map.keys())


class AncillaQubitPatchInitialization(LogicalLatticeOperation):
    def __init__(self, patch_state: QubitState, patch_uuid : uuid.UUID):
        self.patch_state = patch_state
        self.patch_uuid = patch_uuid

    def get_operating_patches(self) -> List[uuid.UUID]:
        return [self.patch_uuid]


class LogicalPauli(LogicalLatticeOperation):
    def __init__(self,patch: uuid.UUID, op:PauliOperator ):
        self.patch = patch
        self.op = op

    def get_operating_patches(self) -> List[uuid.UUID]:
        return [self.patch]





class LogicalLatticeComputation:
    
    def __init__(self, circuit: Circuit):
        self.circuit = circuit
        self.logical_qubit_uuid_map = dict([(j,uuid.uuid4()) for j in range(circuit.qubit_num)])
        self.ancilla_states : List[uuid.UUID] = []
        self.magic_states : List[uuid.UUID] = []
        self.ops : List[LogicalLatticeOperation] = []

        self._load_circuit()


    def _load_circuit(self):

        def to_lattice_operation(op: PauliProductOperation) -> Union[LogicalLatticeOperation, Rotation]:
            if isinstance(op, Rotation): return op
            if isinstance(op, Measurement): return self.circuit_to_patch_measurement(op)
            raise Exception("Unsupported PauliProductOperation " + repr(op))

        operations_queue: Deque[Union[Rotation, LogicalLatticeOperation]] \
            = deque(map(to_lattice_operation, self.circuit.get_operations()))

        while len(operations_queue) > 0:
            current_op = operations_queue.popleft()
            if isinstance(current_op, Rotation):
                rotations_composer = RotationsComposer(self)
                operations_queue.extendleft(reversed(rotations_composer.expand_rotation(current_op)))
            else:
                self.ops.append(current_op)

    def request_magic_state(self) -> uuid.UUID:
        self.magic_states.append(uuid.uuid4())
        return self.magic_states[-1]

    def allocate_ancilla_state(self) -> uuid.UUID:
        self.ancilla_states.append(uuid.uuid4())
        return self.ancilla_states[-1]

    def circuit_to_patch_measurement(self,m: Measurement) -> Union[SinglePatchMeasurement, MultiBodyMeasurement]:

        ret: Dict[uuid.UUID, PauliOperator] = dict()
        for qubit_idx in range(m.qubit_num):
            if m.get_op(qubit_idx) != PauliOperator.I:
                ret[self.logical_qubit_uuid_map[qubit_idx]] = m.get_op(qubit_idx)

        if len(ret) == 1:
            return SinglePatchMeasurement(next(iter(ret)), ret[next(iter(ret))])
        return MultiBodyMeasurement(ret)



class RotationsComposer:

    def __init__(self, computation: LogicalLatticeComputation):
        self.computation = computation

    def expand_rotation(self, r: Rotation) -> List[LogicalLatticeOperation]:
        if r.rotation_amount == Fraction(1, 2):
            return self.pi_over_two(r.get_ops_map())
        elif r.rotation_amount == Fraction(1, 4):
            return self.add_pi_over_four(r.get_ops_map(), False)
        elif r.rotation_amount == Fraction(-1, 4):
            return self.add_pi_over_four(r.get_ops_map(), True)
        elif r.rotation_amount == Fraction(1, 8):
            return self.add_pi_over_eight(r.get_ops_map(), False)
        elif r.rotation_amount == Fraction(-1, 8):
            return self.add_pi_over_eight(r.get_ops_map(), True)
        else:
            raise Exception("Unsupported pauli rotation angle pi*%d/%d"
                            % (r.rotation_amount.numerator, r.rotation_amount.denominator))

    def pi_over_two(self, ops_map :  Dict[int, PauliOperator]) -> List[LogicalLatticeOperation]:
        paulis = []
        for qubit_id, op in ops_map.items():
            paulis.append(LogicalPauli(self.computation.logical_qubit_uuid_map[qubit_id],op))
        return paulis

    def add_pi_over_four(self, ops_map: Dict[int, PauliOperator], invert_correction:bool) -> List[LogicalLatticeOperation]:
        """See Figure 11 of Litinski's GoSC
        """
        ancilla_uuid = self.computation.allocate_ancilla_state()
        ancilla_initialization = AncillaQubitPatchInitialization(SymbolicState("|Y>"), ancilla_uuid)

        multi_body_measurement = MultiBodyMeasurement({})
        multi_body_measurement.patch_pauli_operator_map[ancilla_uuid] = PauliOperator.Z

        ancilla_measurement = SinglePatchMeasurement(ancilla_uuid, PauliOperator.X)

        corrective_rotation = Rotation(self.logical_qubit_num(), Fraction(1, 2))
        for qubit_idx, op in ops_map.items():
            patch = self.computation.logical_qubit_uuid_map[qubit_idx]
            multi_body_measurement.patch_pauli_operator_map[patch] = op
            corrective_rotation.change_single_op(qubit_idx, op)

        return [ancilla_initialization,
                multi_body_measurement,
                ancilla_measurement,
                corrective_rotation]

    def logical_qubit_num(self):
        return len(self.computation.logical_qubit_uuid_map)

    def add_pi_over_eight(self, ops_map :  Dict[int, PauliOperator], invert_correction:bool) -> List[LogicalLatticeOperation]:
        """Returns the correction terms. See Figure 11 of Litinski's GoSC"""
        magic_state_uuid = self.computation.request_magic_state()

        multi_body_measurement = MultiBodyMeasurement({})
        multi_body_measurement.patch_pauli_operator_map[magic_state_uuid] = PauliOperator.Z

        first_corrective_rotation = Rotation(self.logical_qubit_num(), Fraction(1,4))
        second_corrective_rotation = Rotation(self.logical_qubit_num(), Fraction(1,2))

        for qubit_idx, op in ops_map.items():
            cell = self.computation.logical_qubit_uuid_map[qubit_idx]
            multi_body_measurement.patch_pauli_operator_map[cell]=op
            first_corrective_rotation.change_single_op(qubit_idx, op)
            second_corrective_rotation.change_single_op(qubit_idx, op)

        return [multi_body_measurement,
                first_corrective_rotation,
                SinglePatchMeasurement(magic_state_uuid, PauliOperator.X),
                second_corrective_rotation]

