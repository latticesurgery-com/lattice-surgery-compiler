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

import numpy as np
import qiskit.opflow as qkop

import lsqecc.simulation.qiskit_opflow_utils as qkutil


class LazyTensorOpsNotMatchingException(Exception):
    pass


R = TypeVar("R", bound=qkop.OperatorBase)
S = TypeVar("S", bound=qkop.OperatorBase)
T = TypeVar("T", bound=qkop.OperatorBase)


class LazyTensorOp(Generic[T]):
    """Lazily evaluated tensor products.
    Store operators such as `I otimes CNOT otimes I otimes I otimes X` as list of the tensor
    operands. Has methods to apply operators so that the tensor structure is preserved."""

    def __init__(self, ops: List[T]):
        self.ops = ops[:]  # TODO rename to operands

    def apply_matching_tensors(self, lhs: "LazyTensorOp[S]", eval=True) -> "LazyTensorOp[R]":
        """Left applies the list of matching tensors to the current object"""
        for i, op in enumerate(self.ops):
            if op.num_qubits != lhs.ops[i].num_qubits:
                raise LazyTensorOpsNotMatchingException(
                    "Items in LazyTensortOp must be matching."
                    + f"Got:\n {repr(op)}\n and\n {repr(lhs.ops[i])}"
                )

        res = [lhs.ops[i] @ self.ops[i] for i in range(len(self.ops))]
        if eval:
            res = [op.eval() for op in res]

        return LazyTensorOp(res)

    def apply_more_granular_lazy_tensor(
        self, lhs: "LazyTensorOp[S]", eval=True
    ) -> "LazyTensorOp[R]":
        """Left pply an operator expressed as a tensor product such that each applied operators
        applies exactly to the elements in the tensor product in this object"""
        other_op_idx_counter = 0
        other_as_matching_tensor: List[S] = []

        # Group the the more granular tensors so they match the ops in self
        for op in self.ops:
            qubits_from_other_for_current_application = 0
            ops_from_other_for_current_application: List[S] = []
            while qubits_from_other_for_current_application < op.num_qubits:
                ops_from_other_for_current_application.append(lhs.ops[other_op_idx_counter])
                qubits_from_other_for_current_application += lhs.ops[
                    other_op_idx_counter
                ].num_qubits
                other_op_idx_counter += 1
            other_as_matching_tensor.append(tensor_list(ops_from_other_for_current_application))

        return self.apply_matching_tensors(LazyTensorOp(other_as_matching_tensor), eval=eval)

    def get_operand_sizes(self) -> List[int]:
        return list(map(lambda op: op.num_qubits, self.ops))

    def get_idx_of_first_qubit_for_each_operand(self) -> List[int]:
        first_idxs = [0]
        for block_size in self.get_operand_sizes()[:-1]:  # skip the last
            first_idxs.append(first_idxs[-1] + block_size)
        return first_idxs

    def get_idxs_of_qubit(self, qubit_idx: int) -> Tuple[int, int]:
        """Returns index_of_operand, index_within_operand"""
        operand_boundaries = self.get_idx_of_first_qubit_for_each_operand() + [
            self.get_num_qubits()
        ]
        for i in range(
            len(operand_boundaries) - 1
        ):  # skip the last sum because it would be the (n+1)-th block
            if qubit_idx < operand_boundaries[i + 1]:
                return i, qubit_idx - operand_boundaries[i]
        raise IndexError(
            f"Requesting qubit index: {qubit_idx} out of range: {operand_boundaries[-1]}"
        )

    def get_idx_of_first_qubit_in_operand(self, operand_idx: int):
        return self.get_idx_of_first_qubit_for_each_operand()[operand_idx]

    def swap_operands(self, operand_idx1: int, operand_idx2: int) -> None:
        self.ops[operand_idx2], self.ops[operand_idx1] = (
            self.ops[operand_idx1],
            self.ops[operand_idx2],
        )

    def merge_operand_with_the_next(self, target_operand_idx: int) -> None:
        if target_operand_idx >= len(self.ops) - 1:
            raise IndexError()

        new_ops = [op for i, op in enumerate(self.ops) if i != target_operand_idx + 1]
        new_ops[target_operand_idx] = (
            self.ops[target_operand_idx] ^ self.ops[target_operand_idx + 1]
        )
        self.ops = new_ops

    def merge_the_first_n_operands(self, n: int) -> None:
        for i in range(n):
            self.merge_operand_with_the_next(0)

    def separate_last_qubit_of_operand(self, operand_idx: int) -> bool:
        """Returns true if the qubit was not entangled and hence the operation possible"""
        operand = self.ops[operand_idx]
        assert isinstance(operand, qkop.DictStateFn)
        if operand.num_qubits == 1:
            return True

        maybe_new_operand_from_qubit = qkutil.StateSeparator.separate(
            operand.num_qubits - 1, operand
        )
        if maybe_new_operand_from_qubit is None:
            return False
        self.ops[operand_idx] = qkutil.StateSeparator.trace_dict_state(
            operand, [operand.num_qubits - 1]
        )
        self.ops.insert(operand_idx + 1, maybe_new_operand_from_qubit)
        return True

    def remove_operand(self, operand_idx: int) -> None:
        if self.ops[operand_idx].num_qubits == 1:
            self.ops.pop(operand_idx)
        else:
            raise Exception(f"Cannot remove non separable qubit at operand {operand_idx}: {self.ops[operand_idx]}")

    def are_possibly_entangled(self):
        pass  # TODO

    def get_state(self):
        pass  # TODO

    def matches(self, other: "LazyTensorOp[S]"):
        """Returns true iff the other tensor has matching operand number and sizes"""
        if len(self.ops) != len(other.ops):
            return False
        return all([op1.num_qubits == op2.num_qubits for op1, op2 in zip(self.ops, other.ops)])

    def matching_approx_eq_matrix(self, other: "LazyTensorOp[S]", atol: float = 10 ** (-8)) -> bool:
        # TODO check is matrix
        assert self.matches(other)
        return all(
            [
                np.allclose(op1.to_matrix(), op2.to_matrix(), atol=atol)
                for op1, op2 in zip(self.ops, other.ops)
            ]
        )

    def matching_approx_eq_vector(self, other: "LazyTensorOp[S]", atol: float = 10 ** (-8)) -> bool:
        # TODO check is vector
        if not self.matches(other):
            raise LazyTensorOpsNotMatchingException()
        return all(
            [
                np.allclose(qkutil.to_vector(op1), qkutil.to_vector(op2), atol=atol)
                for op1, op2 in zip(self.ops, other.ops)
            ]
        )

    def get_num_qubits(self):
        return sum(map(lambda x: x.num_qubits, self.ops))

    def __repr__(self):
        return f"<LazyTensorOps ops.len={len(self.ops)} ops={self.ops}>"


def tensor_list(input_list):
    t = input_list[0]
    for s in input_list[1:]:
        t = t ^ s
    return t
