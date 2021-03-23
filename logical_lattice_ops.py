from typing import *
from rotation import *
import uuid
from collections import deque
from qubit_state import *
from circuit import *


# TODO give a uuid to all patches

"""Patches are now identified by uuids"""


class LogicalLatticeOperation(EvaluationConditionManager):

    def get_operating_patches(self) -> List[uuid.UUID]:
        raise NotImplemented()



class SinglePatchMeasurement(LogicalLatticeOperation,HasPauliEigenvalueOutcome):
    def __init__(self, qubit_uuid: uuid.UUID, op: PauliOperator):
        self.qubit_uuid = qubit_uuid
        self.op = op

    def get_operating_patches(self) -> List[uuid.UUID]:
        return [self.qubit_uuid]


class MultiBodyMeasurement(LogicalLatticeOperation,HasPauliEigenvalueOutcome):
    def __init__(self, patch_pauli_operator_map: Dict[uuid.UUID, PauliOperator]):
        self.patch_pauli_operator_map = patch_pauli_operator_map

    def get_operating_patches(self) -> List[uuid.UUID]:
        return list(self.patch_pauli_operator_map.keys())


class AncillaQubitPatchInitialization(LogicalLatticeOperation):
    def __init__(self, qubit_state: QubitState, qubit_uuid : uuid.UUID):
        self.qubit_state = qubit_state
        self.qubit_uuid = qubit_uuid

    def get_operating_patches(self) -> List[uuid.UUID]:
        return [self.qubit_uuid]


class LogicalPauli(LogicalLatticeOperation):
    def __init__(self,qubit_uuid: uuid.UUID, pauli_matrix: PauliOperator):
        self.qubit_uuid = qubit_uuid
        self.pauli_matrix = pauli_matrix

    def get_operating_patches(self) -> List[uuid.UUID]:
        return [self.qubit_uuid]


class MagicStateRequest(LogicalLatticeOperation):
    def __init__(self, qubit_uuid: uuid.UUID,):
        self.qubit_uuid = qubit_uuid

    def get_operating_patches(self) -> List[uuid.UUID]:
        return [self.qubit_uuid]




class LogicalLatticeComputation:
    
    def __init__(self, circuit: Circuit):
        self.circuit = circuit
        self.logical_qubit_uuid_map = dict([(j,uuid.uuid4()) for j in range(circuit.qubit_num)])
        self.ops : List[LogicalLatticeOperation] = []

        self._load_circuit()


    def _load_circuit(self):

        def to_lattice_operation(op: PauliProductOperation) -> Union[LogicalLatticeOperation, Rotation]:
            if isinstance(op, Rotation): return op
            if isinstance(op, Measurement):
                patches_measurement =  self.circuit_to_patch_measurement(op)
                patches_measurement.set_condition(op.get_condition())
                return patches_measurement
            raise Exception("Unsupported PauliProductOperation " + repr(op))

        operations_queue: Deque[Union[Rotation, LogicalLatticeOperation]] \
            = deque(map(to_lattice_operation, self.circuit.ops))

        while len(operations_queue) > 0:
            current_op = operations_queue.popleft()
            if isinstance(current_op, Rotation):
                rotations_composer = RotationsComposer(self)
                operations_queue.extendleft(reversed(rotations_composer.expand_rotation(current_op)))
            else:
                self.ops.append(current_op)

    def circuit_to_patch_measurement(self,m: Measurement) -> Union[SinglePatchMeasurement, MultiBodyMeasurement]:

        ret: Dict[uuid.UUID, PauliOperator] = dict()
        for qubit_idx in range(m.qubit_num):
            if m.get_op(qubit_idx) != PauliOperator.I:
                ret[self.logical_qubit_uuid_map[qubit_idx]] = m.get_op(qubit_idx)

        if len(ret) == 1:
            return SinglePatchMeasurement(next(iter(ret)), ret[next(iter(ret))])
        return MultiBodyMeasurement(ret)


    def num_logical_qubits(self) -> int:
        return len(self.logical_qubit_uuid_map)

    def count_magic_states(self) -> int:
        c=0
        for op in self.ops:
            if isinstance(op,MagicStateRequest):
                c += 1
        return c


class RotationsComposer:

    def __init__(self, computation: LogicalLatticeComputation):
        self.computation = computation

    def expand_rotation(self, r: Rotation) -> List[LogicalLatticeOperation]:
        if r.rotation_amount == Fraction(1, 2):
            return self.pi_over_two(r.get_ops_map(), r.get_condition())
        elif r.rotation_amount == Fraction(1, 4):
            return self.add_pi_over_four(r.get_ops_map(), False, r.get_condition())
        elif r.rotation_amount == Fraction(-1, 4):
            return self.add_pi_over_four(r.get_ops_map(), True, r.get_condition())
        elif r.rotation_amount == Fraction(1, 8):
            return self.add_pi_over_eight(r.get_ops_map(), False, r.get_condition())
        elif r.rotation_amount == Fraction(-1, 8):
            return self.add_pi_over_eight(r.get_ops_map(), True, r.get_condition())
        else:
            raise Exception("Unsupported pauli rotation angle pi*%d/%d"
                            % (r.rotation_amount.numerator, r.rotation_amount.denominator))

    def pi_over_two(self, ops_map :  Dict[int, PauliOperator], condition:Optional[EvaluationCondition]) -> List[LogicalLatticeOperation]:

        paulis = []
        for qubit_id, op in ops_map.items():
            logical_pauli = LogicalPauli(self.computation.logical_qubit_uuid_map[qubit_id],op)
            logical_pauli.set_condition(condition)
            paulis.append(logical_pauli)
        return paulis

    def add_pi_over_four(self, ops_map: Dict[int, PauliOperator],
                         invert_correction:bool,
                         condition:Optional[EvaluationCondition]) -> List[LogicalLatticeOperation]:
        """See Figure 11 of Litinski's GoSC
        """
        ancilla_uuid = uuid.uuid4()
        ancilla_initialization = AncillaQubitPatchInitialization(DefaultSymbolicStates.YPosEigenState, ancilla_uuid)

        multi_body_measurement = MultiBodyMeasurement({})
        multi_body_measurement.set_condition(condition)
        multi_body_measurement.patch_pauli_operator_map[ancilla_uuid] = PauliOperator.Z

        ancilla_measurement = SinglePatchMeasurement(ancilla_uuid, PauliOperator.X)

        corrective_rotation = Rotation(self.logical_qubit_num(), Fraction(1, 2))
        corrective_rotation.set_condition(PiOverFourCorrectionCondition(multi_body_measurement,
                                                                        ancilla_measurement,
                                                                        invert_correction))
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

    def add_pi_over_eight(self, ops_map :  Dict[int, PauliOperator],
                          invert_correction:bool,
                          condition:Optional[EvaluationCondition]) -> List[LogicalLatticeOperation]:
        """Returns the correction terms. See Figure 11 of Litinski's GoSC"""
        magic_state_uuid = uuid.uuid4()

        multi_body_measurement = MultiBodyMeasurement({})
        multi_body_measurement.set_condition(condition)
        multi_body_measurement.patch_pauli_operator_map[magic_state_uuid] = PauliOperator.Z

        first_corrective_rotation = Rotation(self.logical_qubit_num(), Fraction(1,4))
        first_corrective_rotation.set_condition(PiOverEightCorrectionConditionPiOverFour(multi_body_measurement,
                                                                                         invert_correction))

        ancilla_measurement = SinglePatchMeasurement(magic_state_uuid, PauliOperator.X)

        second_corrective_rotation = Rotation(self.logical_qubit_num(), Fraction(1,2))
        second_corrective_rotation.set_condition(PiOverEightCorrectionConditionPiOverTwo(ancilla_measurement))

        for qubit_idx, op in ops_map.items():
            cell = self.computation.logical_qubit_uuid_map[qubit_idx]
            multi_body_measurement.patch_pauli_operator_map[cell]=op
            first_corrective_rotation.change_single_op(qubit_idx, op)
            second_corrective_rotation.change_single_op(qubit_idx, op)

        return [MagicStateRequest(magic_state_uuid),
                multi_body_measurement,
                first_corrective_rotation,
                ancilla_measurement,
                second_corrective_rotation]


class PiOverFourCorrectionCondition(EvaluationCondition):
    def __init__(self,multi_body_measurement : MultiBodyMeasurement,ancilla_measurement:SinglePatchMeasurement, invert: bool):
        self.multi_body_measurement = multi_body_measurement
        self.ancilla_measurement = ancilla_measurement
        self.invert = invert

    def does_evaluate(self):
        if not self.multi_body_measurement.does_evaluate():
            return False

        out = self.multi_body_measurement.get_outcome()*self.ancilla_measurement.get_outcome() == -1
        if self.invert:
            out = not out
        return out


class PiOverEightCorrectionConditionPiOverFour(EvaluationCondition):
    def __init__(self,multi_body_measurement : MultiBodyMeasurement, invert : bool):
        self.multi_body_measurement = multi_body_measurement
        self.invert = invert

    def does_evaluate(self):
        if not self.multi_body_measurement.does_evaluate():
            return False

        out = self.multi_body_measurement.get_outcome() == -1
        if self.invert:
            out = not out
        return out

class PiOverEightCorrectionConditionPiOverTwo(EvaluationCondition):
    def __init__(self, ancilla_measurement: SinglePatchMeasurement):
        self.ancilla_measurement = ancilla_measurement

    def does_evaluate(self):
        if not self.ancilla_measurement.does_evaluate():
            return False

        return self.ancilla_measurement.get_outcome() == -1