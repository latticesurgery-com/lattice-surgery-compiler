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

import uuid
from collections import deque
from fractions import Fraction
from typing import Deque, Dict, List, Optional, Sequence, Union

import lsqecc.simulation.conditional_operation_control as coc
import lsqecc.simulation.qubit_state as qs
from lsqecc.pauli_rotations import (
    Measurement,
    PauliOpCircuit,
    PauliOperator,
    PauliProductOperation,
    PauliRotation,
)

# TODO give a uuid to all patches

# Patches are now identified by uuids


class LogicalLatticeOperation(coc.ConditionalOperation):
    def get_operating_patches(self) -> List[uuid.UUID]:
        raise NotImplementedError


class SinglePatchMeasurement(LogicalLatticeOperation, coc.HasPauliEigenvalueOutcome):
    def __init__(
        self, qubit_uuid: uuid.UUID, op: PauliOperator, isNegative: Optional[bool] = False
    ):
        self.qubit_uuid = qubit_uuid
        self.op = op
        self.isNegative = isNegative

    def get_operating_patches(self) -> List[uuid.UUID]:
        return [self.qubit_uuid]


class MultiBodyMeasurement(LogicalLatticeOperation, coc.HasPauliEigenvalueOutcome):
    def __init__(
        self, patch_pauli_operator_map: Dict[uuid.UUID, PauliOperator], isNegative: bool = False
    ):
        self.patch_pauli_operator_map = patch_pauli_operator_map
        self.isNegative = isNegative

    def get_operating_patches(self) -> List[uuid.UUID]:
        return list(self.patch_pauli_operator_map.keys())


class AncillaQubitPatchInitialization(LogicalLatticeOperation):
    def __init__(self, qubit_state: qs.QubitState, qubit_uuid: uuid.UUID):
        self.qubit_state = qubit_state
        self.qubit_uuid = qubit_uuid

    def get_operating_patches(self) -> List[uuid.UUID]:
        return [self.qubit_uuid]


class LogicalPauli(LogicalLatticeOperation):
    def __init__(self, qubit_uuid: uuid.UUID, pauli_matrix: PauliOperator):
        self.qubit_uuid = qubit_uuid
        self.pauli_matrix = pauli_matrix

    def get_operating_patches(self) -> List[uuid.UUID]:
        return [self.qubit_uuid]


class MagicStateRequest(LogicalLatticeOperation):
    def __init__(self, qubit_uuid: uuid.UUID):
        self.qubit_uuid = qubit_uuid

    def get_operating_patches(self) -> List[uuid.UUID]:
        return [self.qubit_uuid]


class LogicalLatticeComputation:
    def __init__(self, circuit: PauliOpCircuit):
        self.circuit = circuit
        self.logical_qubit_uuid_map: Dict[int, uuid.UUID] = dict(
            [(j, uuid.uuid4()) for j in range(circuit.qubit_num)]
        )
        self.ops: List[LogicalLatticeOperation] = []

        self._load_circuit()

    def _load_circuit(self):
        def to_lattice_operation(
            op: PauliProductOperation,
        ) -> Union[LogicalLatticeOperation, PauliRotation]:
            if isinstance(op, PauliRotation):
                return op
            if isinstance(op, Measurement):
                return self.circuit_to_patch_measurement(op)
            raise Exception("Unsupported PauliProductOperation " + repr(op))

        operations_queue: Deque[Union[PauliRotation, LogicalLatticeOperation]] = deque(
            map(to_lattice_operation, self.circuit.ops)
        )

        while len(operations_queue) > 0:
            current_op = operations_queue.popleft()
            if isinstance(current_op, PauliRotation):
                rotations_composer = RotationsComposer(self)
                operations_queue.extendleft(
                    reversed(rotations_composer.expand_rotation(current_op))
                )
            else:
                self.ops.append(current_op)

    def circuit_to_patch_measurement(
        self, m: PauliProductOperation
    ) -> Union[SinglePatchMeasurement, MultiBodyMeasurement]:
        if not isinstance(m, Measurement):
            raise TypeError("Make sure the passed argument is of type Measurement")

        ret: Dict[uuid.UUID, PauliOperator] = dict()
        for qubit_idx in range(m.qubit_num):
            if m.get_op(qubit_idx) != PauliOperator.I:
                ret[self.logical_qubit_uuid_map[qubit_idx]] = m.get_op(qubit_idx)

        if len(ret) == 1:
            return SinglePatchMeasurement(next(iter(ret)), ret[next(iter(ret))], m.isNegative)
        return MultiBodyMeasurement(ret, m.isNegative)

    def num_logical_qubits(self) -> int:
        return len(self.logical_qubit_uuid_map)

    def count_magic_states(self) -> int:
        c = 0
        for op in self.ops:
            if isinstance(op, MagicStateRequest):
                c += 1
        return c


class RotationsComposer:
    def __init__(self, computation: LogicalLatticeComputation):
        self.computation = computation

    def expand_rotation(
        self, r: PauliRotation
    ) -> Sequence[Union[LogicalLatticeOperation, PauliProductOperation]]:
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
            raise Exception(
                "Unsupported pauli rotation angle pi*%d/%d"
                % (r.rotation_amount.numerator, r.rotation_amount.denominator)
            )

    def pi_over_two(
        self, ops_map: Dict[int, PauliOperator], condition: Optional[coc.EvaluationCondition]
    ) -> Sequence[LogicalLatticeOperation]:
        paulis = []
        for qubit_id, op in ops_map.items():
            logical_pauli = LogicalPauli(self.computation.logical_qubit_uuid_map[qubit_id], op)
            logical_pauli.set_condition(condition)
            paulis.append(logical_pauli)
        return paulis

    def add_pi_over_four(
        self,
        ops_map: Dict[int, PauliOperator],
        invert_correction: bool,
        condition: Optional[coc.EvaluationCondition],
    ) -> Sequence[Union[LogicalLatticeOperation, PauliProductOperation]]:
        """See Figure 11 of Litinski's GoSC"""
        ancilla_uuid = uuid.uuid4()
        ancilla_initialization = AncillaQubitPatchInitialization(
            qs.DefaultSymbolicStates.YPosEigenState, ancilla_uuid
        )

        multi_body_measurement = MultiBodyMeasurement({})
        multi_body_measurement.set_condition(condition)
        multi_body_measurement.patch_pauli_operator_map[ancilla_uuid] = PauliOperator.Z

        ancilla_measurement = SinglePatchMeasurement(ancilla_uuid, PauliOperator.X)

        corrective_rotation = PauliRotation(self.logical_qubit_num(), Fraction(1, 2))
        corrective_rotation.set_condition(
            PiOverFourCorrectionCondition(
                multi_body_measurement, ancilla_measurement, invert_correction
            )
        )
        for qubit_idx, op in ops_map.items():
            patch = self.computation.logical_qubit_uuid_map[qubit_idx]
            multi_body_measurement.patch_pauli_operator_map[patch] = op
            corrective_rotation.change_single_op(qubit_idx, op)

        return [
            ancilla_initialization,
            multi_body_measurement,
            ancilla_measurement,
            corrective_rotation,
        ]

    def logical_qubit_num(self):
        return len(self.computation.logical_qubit_uuid_map)

    def add_pi_over_eight(
        self,
        ops_map: Dict[int, PauliOperator],
        invert_correction: bool,
        condition: Optional[coc.EvaluationCondition],
    ) -> Sequence[Union[LogicalLatticeOperation, PauliProductOperation]]:
        """Returns the correction terms. See Figure 11 of Litinski's GoSC"""
        magic_state_uuid = uuid.uuid4()

        multi_body_measurement = MultiBodyMeasurement({})
        multi_body_measurement.set_condition(condition)
        multi_body_measurement.patch_pauli_operator_map[magic_state_uuid] = PauliOperator.Z

        first_corrective_rotation = PauliRotation(self.logical_qubit_num(), Fraction(1, 4))
        first_corrective_rotation.set_condition(
            PiOverEightCorrectionConditionPiOverFour(multi_body_measurement, invert_correction)
        )

        ancilla_measurement = SinglePatchMeasurement(magic_state_uuid, PauliOperator.X)

        second_corrective_rotation = PauliRotation(self.logical_qubit_num(), Fraction(1, 2))
        second_corrective_rotation.set_condition(
            PiOverEightCorrectionConditionPiOverTwo(ancilla_measurement)
        )

        for qubit_idx, op in ops_map.items():
            cell = self.computation.logical_qubit_uuid_map[qubit_idx]
            multi_body_measurement.patch_pauli_operator_map[cell] = op
            first_corrective_rotation.change_single_op(qubit_idx, op)
            second_corrective_rotation.change_single_op(qubit_idx, op)

        return [
            MagicStateRequest(magic_state_uuid),
            multi_body_measurement,
            first_corrective_rotation,
            ancilla_measurement,
            second_corrective_rotation,
        ]


class PiOverFourCorrectionCondition(coc.EvaluationCondition):
    def __init__(
        self,
        multi_body_measurement: MultiBodyMeasurement,
        ancilla_measurement: SinglePatchMeasurement,
        invert: bool,
    ):
        self.multi_body_measurement = multi_body_measurement
        self.ancilla_measurement = ancilla_measurement
        self.invert = invert

    def does_evaluate(self):
        if not self.multi_body_measurement.does_evaluate():
            return False

        if (
            self.multi_body_measurement.get_outcome() is None
            or self.ancilla_measurement.get_outcome() is None
        ):
            return True  # Always evaluate an op when no simulation is present

        out = (
            self.multi_body_measurement.get_outcome() * self.ancilla_measurement.get_outcome() == -1
        )
        if self.invert:
            out = not out
        return out


class PiOverEightCorrectionConditionPiOverFour(coc.EvaluationCondition):
    def __init__(self, multi_body_measurement: MultiBodyMeasurement, invert: bool):
        self.multi_body_measurement = multi_body_measurement
        self.invert = invert

    def does_evaluate(self):
        if not self.multi_body_measurement.does_evaluate():
            return False

        if self.multi_body_measurement.get_outcome() is None:
            return True  # Always evaluate an op when no simulation is present

        out = self.multi_body_measurement.get_outcome() == -1
        if self.invert:
            out = not out
        return out


class PiOverEightCorrectionConditionPiOverTwo(coc.EvaluationCondition):
    def __init__(self, ancilla_measurement: SinglePatchMeasurement):
        self.ancilla_measurement = ancilla_measurement

    def does_evaluate(self):
        if not self.ancilla_measurement.does_evaluate():
            return False

        if self.ancilla_measurement.get_outcome() is None:
            return True  # Always evaluate an op when no simulation is present

        return self.ancilla_measurement.get_outcome() == -1
