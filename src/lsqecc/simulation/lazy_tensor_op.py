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


from typing import Generic, List, Tuple, TypeVar

import qiskit.opflow as qkop

from lsqecc.simulation.logical_patch_state_simulation import tensor_list


class LazyTensorOpsNotMatchingException(Exception):
    pass


R = TypeVar("R", bound=qkop.OperatorBase)
S = TypeVar("S", bound=qkop.OperatorBase)
T = TypeVar("T", bound=qkop.OperatorBase)


class LazyTensorOp(Generic[T]):
    """Store operators such as `I otimes CNOT otimes I otimes I otimes X` as list of the tensor
    operands. Has methods to apply operators so that the tensor structure is preserved"""

    def __init__(self, ops: List[T]):
        self.ops = ops

    def apply_matching_tensors(self, other: "LazyTensorOp[S]", eval=True) -> "LazyTensorOp[R]":
        for i, op in enumerate(self.ops):
            if op.num_qubits != other.ops[i].num_qubits:
                raise LazyTensorOpsNotMatchingException(
                    "Items in LazyTensortOp must be matching."
                    + f"Got:\n {repr(op)}\n and\n {repr(other.ops[i])}"
                )

        res = [other.ops[i] @ self.ops[i] for i in range(len(self.ops))]
        if eval:
            res = [op.eval() for op in res]

        return LazyTensorOp(res)

    def apply_more_granular_lazy_tensor(
        self, other: "LazyTensorOp[S]", eval=True
    ) -> "LazyTensorOp[R]":
        """Apply an operator expressed as a tensor product such that each applied operators applies
        exactly to the elements in the tensor product in this object"""
        other_op_idx_counter = 0
        other_as_matching_tensor: List[S] = []

        # Group the the more granular tensors so they match the ops in self
        for op in self.ops:
            qubits_from_other_for_current_application = 0
            ops_from_other_for_current_application: List[S] = []
            while qubits_from_other_for_current_application < op.num_qubits:
                ops_from_other_for_current_application.append(other.ops[other_op_idx_counter])
                qubits_from_other_for_current_application += other.ops[
                    other_op_idx_counter
                ].num_qubits
                other_op_idx_counter += 1
            other_as_matching_tensor.append(tensor_list(ops_from_other_for_current_application))

        return self.apply_matching_tensors(LazyTensorOp(other_as_matching_tensor), eval=eval)

    def get_idxs_of_qubit(self, qubit_idx: int) -> Tuple[int, int]:
        """Returns index_of_tensor_operand, index_within_tensor_operand"""
        block_sizes = list(map(lambda op: op.num_qubits, self.ops))
        sums = [0]
        for block_size in block_sizes:
            sums.append(sums[-1] + block_size)
        print(sums)
        for i in range(len(sums) - 1):  # skip the last sum because it would be the (n+1)-th block
            if qubit_idx < sums[i + 1]:
                return i, qubit_idx - sums[i]
        raise IndexError(f"Requesting qubit index: {qubit_idx} out of range: {sums[-1]}")

    def disentangle_separable_qubit(self, idx: int):
        pass  # TODO

    def are_possibly_entangled(self):
        pass  # TODO

    def get_state(self):
        pass  # TODO
