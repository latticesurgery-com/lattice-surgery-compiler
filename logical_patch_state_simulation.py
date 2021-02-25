from patches import *

import qiskit.aqua.operators as qk

from typing import *
import math


def circuit_add_op_to_qubit(circ : qk.CircuitOp, op: qk.PrimitiveOp, idx: int) -> qk.CircuitOp:
    """"Take a local operator (applied to a single qubit) and apply it to the given circuit."""
    new_op = op
    if idx > 0:
        new_op = (qk.I ^ idx ) ^ new_op
    if circ.num_qubits-idx-1 > 0:
        new_op = new_op ^ (qk.I ^ (circ.num_qubits - idx - 1))
    return new_op @ circ

class ProjectiveMeasurement:

        @staticmethod
        def borns_rule(projector: qk.PrimitiveOp, state: qk.OperatorBase) -> float:
            # https://qiskit.org/documentation/tutorials/operators/01_operator_flow.html#listop
            compute_states = lambda s: s.to_matrix_op().eval()

            return qk.StateFn(projector).adjoint().eval(compute_states(state))

        @staticmethod
        def compute_outcome(projector: qk.PrimitiveOp, state: qk.OperatorBase) -> Tuple[qk.OperatorBase, float]:
            prob = ProjectiveMeasurement.borns_rule(projector, state)
            assert prob.imag < 10 ** (-8)
            prob = prob.real
            state = (projector @ state) / math.sqrt(prob)
            return state, prob

        @staticmethod
        def get_projectors_from_pauli_observable(pauli_observable: qk.OperatorBase) -> Tuple[
            qk.PrimitiveOp, qk.PrimitiveOp]:
            eye = qk.I ^ pauli_observable.num_qubits
            return (eye + pauli_observable) / 2, (eye - pauli_observable) / 2

        @staticmethod
        def measure_projectors(projs: List[qk.PrimitiveOp], state: qk.OperatorBase) \
                -> List[Tuple[qk.OperatorBase, float]]:
            return [ProjectiveMeasurement.compute_outcome(proj, state) for proj in projs]

        @staticmethod
        def measure_pauli_product(pauli_observable: qk.OperatorBase, state: qk.OperatorBase) \
                -> List[Tuple[qk.OperatorBase, float]]:
            p1, p2 = ProjectiveMeasurement.get_projectors_from_pauli_observable(pauli_observable)
            return ProjectiveMeasurement.measure_projectors([p1, p2], state)


class PatchToQubitMapper:
    def __init__(self, slices: List[Lattice]):
        self.patch_location_to_logical_idx: Dict[Union[Tuple[int, int], uuid.UUID], int] = dict()
        for slice in slices:
            self.__add_patches_from_slice(slice)

    def get_idx(self, patch: Union[Tuple[int, int], uuid.UUID]) -> int:
        return self.patch_location_to_logical_idx[patch]

    def qubit_num(self):
        return len(self.patch_location_to_logical_idx)

    def __add_patches_from_slice(self, lattice: Lattice):
        for p in PatchToQubitMapper.__get_operating_patches(lattice.logical_ops):
            if self.patch_location_to_logical_idx.get(p) is None:
                self.patch_location_to_logical_idx[p] = self.qubit_num()

    @staticmethod
    def __get_operating_patches(logical_ops: List[LogicalLatticeOperation]) -> List[Union[Tuple[int, int], uuid.UUID]]:
        patch_set = set()
        for op in logical_ops:
            patch_set = patch_set.union(op.get_operating_patches())
        return list(patch_set)


def simulate_slices(slices: List[Lattice]) -> List[List[qk.DictStateFn]]:
    """Returns a list of computation states"""
    mapper = PatchToQubitMapper(slices)
    logical_state = qk.Zero ^ mapper.qubit_num()
    per_slice_intermediate_logical_states: List[List[qk.OperatorBase]] = [[logical_state]]

    for slice_num, slice in enumerate(slices):
        per_slice_intermediate_logical_states.append([])

        for current_op in slice.logical_ops:
            if isinstance(current_op, SinglePatchMeasurement):
                measure_idx = mapper.get_idx(current_op.cell_of_patch)
                local_observable = lattice_surgery_op_to_quiskit_op(current_op.op)
                global_observable = (qk.I ^ measure_idx) ^ local_observable ^ (
                            qk.I ^ (mapper.qubit_num() - measure_idx - 1))
                logical_state = ProjectiveMeasurement.measure_pauli_product(global_observable, logical_state)
            # elif isinstance(current_op, AncillaQubitPatchInitialization):
            # TODO init ahead of time

            elif isinstance(current_op, IndividualPauliOperators):
                for patch, op in current_op.patch_pauli_operator_map.items():
                    logical_state = circuit_add_op_to_qubit(logical_state, lattice_surgery_op_to_quiskit_op(op),
                                                            mapper.get_idx(patch))
                    logical_state = logical_state.eval()  # Convert to DictStateFn
            # elif isinstance(current_op, MultiBodyMeasurement):

            per_slice_intermediate_logical_states[-1].append(logical_state)

    return per_slice_intermediate_logical_states
