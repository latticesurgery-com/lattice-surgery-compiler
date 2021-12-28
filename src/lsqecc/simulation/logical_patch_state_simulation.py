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

import math
import random
import uuid
from typing import Dict, Iterable, List, Optional, Set, Tuple, TypeVar

import qiskit.opflow as qkop

import lsqecc.logical_lattice_ops.logical_lattice_ops as llops
from lsqecc.pauli_rotations import PauliOperator

from .qubit_state import DefaultSymbolicStates, SymbolicState


class ConvertersToQiskit:
    @staticmethod
    def pauli_op(op: PauliOperator) -> Optional[qkop.PrimitiveOp]:
        known_map: Dict[PauliOperator, qkop.PrimitiveOp] = {
            PauliOperator.I: qkop.I,
            PauliOperator.X: qkop.X,
            PauliOperator.Y: qkop.Y,
            PauliOperator.Z: qkop.Z,
        }
        return known_map[op]

    @staticmethod
    def symbolic_state(s: SymbolicState) -> qkop.StateFn:
        zero_ampl, one_ampl = DefaultSymbolicStates.get_amplitudes(s)
        return zero_ampl * qkop.Zero + one_ampl * qkop.One


def circuit_add_op_to_qubit(
    circ: qkop.OperatorBase, op: qkop.PrimitiveOp, idx: int
) -> qkop.CircuitOp:
    """Take a local operator (applied to a single qubit) and apply it to the given circuit."""
    identity_padded_op = op
    if circ.num_qubits - idx - 1 > 0:
        identity_padded_op = (qkop.I ^ (circ.num_qubits - idx - 1)) ^ identity_padded_op
    if idx > 0:
        identity_padded_op = identity_padded_op ^ (qkop.I ^ idx)
    return identity_padded_op @ circ


class ProjectiveMeasurement:
    class BinaryMeasurementOutcome:
        def __init__(self, resulting_state: qkop.DictStateFn, corresponding_eigenvalue: int):
            assert corresponding_eigenvalue in {-1, 1}
            self.resulting_state = resulting_state
            self.corresponding_eigenvalue = corresponding_eigenvalue

    @staticmethod
    def borns_rule(projector: qkop.PrimitiveOp, state: qkop.OperatorBase) -> float:
        # https://qiskit.org/documentation/tutorials/operators/01_operator_flow.html#listop
        def compute_states(s):
            return s.to_matrix_op().eval()

        return qkop.StateFn(projector).adjoint().eval(compute_states(state))

    @staticmethod
    def compute_outcome_state(
        projector: qkop.PrimitiveOp, state: qkop.OperatorBase
    ) -> Tuple[qkop.OperatorBase, float]:
        prob = ProjectiveMeasurement.borns_rule(projector, state)
        assert prob.imag < 10 ** (-8)
        prob = prob.real
        state = (projector @ state) / math.sqrt(prob) if prob != 0 else (projector @ state)
        return state, prob

    @staticmethod
    def get_projectors_from_pauli_observable(
        pauli_observable: qkop.OperatorBase,
    ) -> Tuple[qkop.PrimitiveOp, qkop.PrimitiveOp]:
        eye = qkop.I ^ pauli_observable.num_qubits
        return (eye + pauli_observable) / 2, (eye - pauli_observable) / 2

    @staticmethod
    def pauli_product_measurement_distribution(
        pauli_observable: qkop.OperatorBase, state: qkop.OperatorBase
    ) -> List[Tuple[BinaryMeasurementOutcome, float]]:
        p_plus, p_minus = ProjectiveMeasurement.get_projectors_from_pauli_observable(
            pauli_observable
        )

        out = []
        for proj, eigenv in [[p_plus, +1], [p_minus, -1]]:
            out_state, prob = ProjectiveMeasurement.compute_outcome_state(proj, state)
            numerical_out_state = out_state.eval()
            if not isinstance(numerical_out_state, qkop.DictStateFn):
                raise Exception(
                    "Composed ops do not eval to single state, but to " + str(numerical_out_state)
                )
            out.append(
                (ProjectiveMeasurement.BinaryMeasurementOutcome(numerical_out_state, eigenv), prob)
            )
        return out


T = TypeVar("T")


def proportional_choice(assoc_data_prob: List[Tuple[T, float]]) -> T:
    return random.choices(
        [val for val, prob in assoc_data_prob], weights=[prob for val, prob in assoc_data_prob], k=1
    )[0]


class PatchToQubitMapper:
    def __init__(self, logical_computation: llops.LogicalLatticeComputation):
        self.patch_location_to_logical_idx: Dict[uuid.UUID, int] = dict()
        for p in PatchToQubitMapper._get_all_operating_patches(logical_computation):
            if self.patch_location_to_logical_idx.get(p) is None:
                self.patch_location_to_logical_idx[p] = self.max_num_patches()

    def get_idx(self, patch: uuid.UUID) -> int:
        return self.patch_location_to_logical_idx[patch]

    def max_num_patches(self) -> int:
        return len(self.patch_location_to_logical_idx)

    def get_uuid(self, target_idx: int) -> uuid.UUID:
        for quiid, idx in self.patch_location_to_logical_idx.items():
            if idx == target_idx:
                return quiid
        raise Exception(f"Patch with idx {target_idx} not found")

    def enumerate_patches_by_index(self) -> Iterable[Tuple[int, uuid.UUID]]:
        for idx in range(self.max_num_patches()):
            yield (idx, self.get_uuid(idx))

    @staticmethod
    def _get_all_operating_patches(
        logical_computation: llops.LogicalLatticeComputation,
    ) -> List[uuid.UUID]:
        patch_set: Set[uuid.UUID] = set()
        patch_set.update(logical_computation.logical_qubit_uuid_map.values())

        for op in logical_computation.ops:
            patch_set = patch_set.union(op.get_operating_patches())

        return list(patch_set)


def tensor_list(input_list):
    t = input_list[0]
    for s in input_list[1:]:
        t = t ^ s
    return t


class PatchSimulator:
    def __init__(self, logical_computation: llops.LogicalLatticeComputation):
        self.logical_computation = logical_computation
        self.mapper = PatchToQubitMapper(logical_computation)
        self.logical_state: qkop.DictStateFn = self._make_initial_logical_state()

    def _make_initial_logical_state(self) -> qkop.DictStateFn:
        """Every patch, when initialized, is considered a new logical qubit.
        So all patch initializations and magic state requests are handled ahead of time"""
        initial_ancilla_states: Dict[uuid.UUID, SymbolicState] = dict()

        def add_initial_ancilla_state(quuid, symbolic_state):
            if initial_ancilla_states.get(quuid) is not None:
                raise Exception("Initializing patch " + str(quuid) + " twice")
            initial_ancilla_states[quuid] = symbolic_state

        def get_init_state(quuid: uuid.UUID) -> qkop.StateFn:
            return ConvertersToQiskit.symbolic_state(
                initial_ancilla_states.get(quuid, DefaultSymbolicStates.Zero)
            )

        for op in self.logical_computation.ops:
            if isinstance(op, llops.AncillaQubitPatchInitialization):
                add_initial_ancilla_state(op.qubit_uuid, op.qubit_state)
            elif isinstance(op, llops.MagicStateRequest):
                add_initial_ancilla_state(op.qubit_uuid, DefaultSymbolicStates.Magic)

        all_init_states = [
            get_init_state(quuid) for idx, quuid in self.mapper.enumerate_patches_by_index()
        ]
        return tensor_list(all_init_states)

    def apply_logical_operation(self, logical_op: llops.LogicalLatticeOperation):
        """Update the logical state"""

        if not logical_op.does_evaluate():
            raise Exception(
                "apply_logical_operation called with non evaluating operation :" + repr(logical_op)
            )

        if isinstance(logical_op, llops.SinglePatchMeasurement):
            measure_idx = self.mapper.get_idx(logical_op.qubit_uuid)
            local_observable = ConvertersToQiskit.pauli_op(logical_op.op)
            global_observable = (
                (qkop.I ^ measure_idx)
                ^ local_observable
                ^ (qkop.I ^ (self.mapper.max_num_patches() - measure_idx - 1))
            )
            distribution = ProjectiveMeasurement.pauli_product_measurement_distribution(
                global_observable, self.logical_state
            )
            outcome: ProjectiveMeasurement.BinaryMeasurementOutcome = proportional_choice(
                distribution
            )
            self.logical_state = outcome.resulting_state
            logical_op.set_outcome(outcome.corresponding_eigenvalue)

        elif isinstance(logical_op, llops.LogicalPauli):
            symbolic_state = circuit_add_op_to_qubit(
                self.logical_state,
                ConvertersToQiskit.pauli_op(logical_op.pauli_matrix),
                self.mapper.get_idx(logical_op.qubit_uuid),
            )
            self.logical_state = symbolic_state.eval()  # Convert to DictStateFn

        elif isinstance(logical_op, llops.MultiBodyMeasurement):
            pauli_op_list: List[qkop.PrimitiveOp] = []

            for j, quuid in self.mapper.enumerate_patches_by_index():
                pauli_op_list.append(
                    logical_op.patch_pauli_operator_map.get(quuid, PauliOperator.I)
                )
            global_observable = tensor_list(list(map(ConvertersToQiskit.pauli_op, pauli_op_list)))
            distribution = list(
                ProjectiveMeasurement.pauli_product_measurement_distribution(
                    global_observable, self.logical_state
                )
            )
            outcome = proportional_choice(distribution)
            self.logical_state = outcome.resulting_state
            logical_op.set_outcome(outcome.corresponding_eigenvalue)
