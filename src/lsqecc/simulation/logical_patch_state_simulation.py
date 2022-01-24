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
from collections import deque
from typing import Dict, Iterable, List, Optional, Tuple, TypeVar, cast

import qiskit.opflow as qkop

import lsqecc.logical_lattice_ops.logical_lattice_ops as llops
from lsqecc.pauli_rotations import PauliOperator
from lsqecc.simulation.lazy_tensor_op import LazyTensorOp

from .qubit_state import DefaultSymbolicStates, SymbolicState


class ConvertersToQiskit:
    @staticmethod
    def pauli_op(op: PauliOperator) -> Optional[qkop.OperatorBase]:
        known_map: Dict[PauliOperator, qkop.OperatorBase] = {
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


def circuit_apply_op_to_qubit(
    circ: qkop.OperatorBase, op: qkop.OperatorBase, idx: int
) -> qkop.CircuitOp:
    """Take a local operator (applied to a single qubit) and apply it to the given circuit."""
    identity_padded_op = op
    # TODO check that this actually has to be reversed
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
    def borns_rule(projector: qkop.OperatorBase, state: qkop.OperatorBase) -> float:
        # https://qiskit.org/documentation/tutorials/operators/01_operator_flow.html#listop
        def compute_states(s):
            return s.to_matrix_op().eval()

        return cast(float, qkop.StateFn(projector).adjoint().eval(compute_states(state)))

    @staticmethod
    def compute_outcome_state(
        projector: qkop.OperatorBase, state_before_measurement: qkop.OperatorBase
    ) -> Tuple[qkop.DictStateFn, float]:
        prob = ProjectiveMeasurement.borns_rule(projector, state_before_measurement)
        assert prob.imag < 10 ** (-8)
        prob = prob.real
        # Projective measurement by applying the projector. According to Neilsen and Chuang 2.104
        state_after_measurement = (projector @ state_before_measurement).eval() / (
            math.sqrt(prob) if prob > 0 else 1
        )
        return (
            state_after_measurement
            if isinstance(state_after_measurement, qkop.DictStateFn)
            else state_after_measurement.eval().to_dict_fn(),
            prob,
        )

    @staticmethod
    def get_projectors_from_pauli_observable(
        pauli_observable: qkop.OperatorBase,
    ) -> Tuple[qkop.OperatorBase, qkop.OperatorBase]:
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
            numerical_out_state, prob = ProjectiveMeasurement.compute_outcome_state(proj, state)
            if isinstance(numerical_out_state, qkop.VectorStateFn) or isinstance(
                numerical_out_state, qkop.SparseVectorStateFn
            ):
                numerical_out_state = numerical_out_state.to_dict_fn()
            if not isinstance(numerical_out_state, qkop.DictStateFn):
                raise Exception(
                    "Composed ops do not eval to single state, but to " + str(numerical_out_state)
                )
            if prob > 10 ** (-8):
                out.append(
                    (
                        ProjectiveMeasurement.BinaryMeasurementOutcome(numerical_out_state, eigenv),
                        prob,
                    )
                )
        return out


T = TypeVar("T")


def proportional_choice(assoc_data_prob: List[Tuple[T, float]]) -> T:
    """Used to sample measurement outcomes"""
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

    def swap_patches(self, idx1: int, idx2: int):
        uuid1 = self.get_uuid(idx1)
        uuid2 = self.get_uuid(idx2)
        self.patch_location_to_logical_idx[uuid1] = idx2
        self.patch_location_to_logical_idx[uuid2] = idx1

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
        # Add the patches used logical qubits
        patch_list = list(logical_computation.logical_qubit_uuid_map.values())

        # Add the ancilla patches
        for op in logical_computation.ops:
            for new_patch in op.get_operating_patches():
                if new_patch not in patch_list:
                    patch_list.append(new_patch)

        return patch_list


class PatchSimulator:
    def __init__(self, logical_computation: llops.LogicalLatticeComputation):
        # TODO decouple the simulation frm the logical computation. It should be possible to do it
        # because the logical computation is only used to construct the mapper and the initial
        # states.

        self.logical_computation = logical_computation
        self.mapper = PatchToQubitMapper(logical_computation)
        self.logical_state: LazyTensorOp[qkop.StateFn] = self._make_initial_logical_state()

    def _make_initial_logical_state(self) -> LazyTensorOp[qkop.StateFn]:
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
        return LazyTensorOp(all_init_states)

    def apply_logical_operation(self, logical_op: llops.LogicalLatticeOperation):
        """Update the logical state"""

        if not logical_op.does_evaluate():
            raise Exception(
                "apply_logical_operation called with non evaluating operation :" + repr(logical_op)
            )

        if isinstance(logical_op, llops.SinglePatchMeasurement):
            measure_idx = self.mapper.get_idx(logical_op.qubit_uuid)
            operand_idx, idx_within_operand = self.logical_state.get_idxs_of_qubit(measure_idx)
            operand = self.logical_state.ops[operand_idx]

            local_observable = ConvertersToQiskit.pauli_op(logical_op.op)
            observable_global_to_operand = circuit_apply_op_to_qubit(
                qkop.I ^ operand.num_qubits, local_observable, idx_within_operand
            )

            distribution = ProjectiveMeasurement.pauli_product_measurement_distribution(
                observable_global_to_operand, operand
            )
            outcome: ProjectiveMeasurement.BinaryMeasurementOutcome = proportional_choice(
                distribution
            )
            self.logical_state.ops[operand_idx] = outcome.resulting_state
            logical_op.set_outcome(outcome.corresponding_eigenvalue)

            if idx_within_operand == operand.num_qubits - 1:
                self.logical_state.separate_last_qubit_of_operand(operand_idx)
                # TODO use .permute + reindexing to detach any qubit, not just the last
        elif isinstance(logical_op, llops.LogicalPauli):
            op_idx = self.mapper.get_idx(logical_op.qubit_uuid)
            operand_idx, idx_within_operand = self.logical_state.get_idxs_of_qubit(op_idx)
            operand = self.logical_state.ops[operand_idx]

            symbolic_state = circuit_apply_op_to_qubit(
                operand,
                ConvertersToQiskit.pauli_op(logical_op.pauli_matrix),
                idx_within_operand,
            )
            self.logical_state.ops[operand_idx] = cast(qkop.StateFn, symbolic_state.eval())

        elif isinstance(logical_op, llops.MultiBodyMeasurement):
            # Prepare the state by moving all involved operands to the front
            self.align_state_with_pauli_op_to_first_operand(logical_op)
            size_of_first_operand = self.logical_state.ops[0].num_qubits

            # Move
            global_observable = qkop.I ^ size_of_first_operand
            for patch_uuid in logical_op.get_operating_patches():
                qubit_idx = self.mapper.get_idx(patch_uuid)
                assert qubit_idx < size_of_first_operand
                global_observable = circuit_apply_op_to_qubit(
                    global_observable,
                    ConvertersToQiskit.pauli_op(logical_op.patch_pauli_operator_map[patch_uuid]),
                    qubit_idx,
                )

            distribution = list(
                ProjectiveMeasurement.pauli_product_measurement_distribution(
                    global_observable, self.logical_state.ops[0]
                )
            )
            outcome = proportional_choice(distribution)
            self.logical_state.ops[0] = outcome.resulting_state
            logical_op.set_outcome(outcome.corresponding_eigenvalue)

            # TODO use .permute + reindexing to separate qubits not measured

    def bring_active_operands_to_front(self, logical_op: llops.MultiBodyMeasurement) -> int:
        """Returns the number of involved operators, that are now at the front"""

        involved_qubit_idxs: List[int] = [
            self.mapper.patch_location_to_logical_idx[patch_uuid]
            for patch_uuid in logical_op.get_operating_patches()
        ]

        involved_operand_idxs: List[int] = list(
            set(
                [
                    self.logical_state.get_idxs_of_qubit(qubit_idx)[0]
                    for qubit_idx in involved_qubit_idxs
                ]
            )
        )
        involved_operand_idxs.sort()

        swap_target_counter = 0
        operands_to_swap = deque(involved_operand_idxs)
        while len(operands_to_swap):
            front_of_queue = operands_to_swap.popleft()
            self.logical_state.swap_operands(swap_target_counter, front_of_queue)
            self.mapper.swap_patches(swap_target_counter, front_of_queue)
            swap_target_counter += 1

        return len(involved_operand_idxs)

    def align_state_with_pauli_op_to_first_operand(self, logical_op: llops.MultiBodyMeasurement):
        n_operands = self.bring_active_operands_to_front(logical_op)
        self.logical_state.merge_the_first_n_operands(n_operands - 1)
