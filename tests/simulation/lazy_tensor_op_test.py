# Copyright (C) 2020-2021 - George Watkins, Alex Nguyen, Varun Seshadri
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
from typing import List

import pytest
import qiskit.opflow as qkop

from lsqecc.simulation.lazy_tensor_op import (
    LazyTensorOp,
    LazyTensorOpsNotMatchingException,
)
from lsqecc.simulation.qiskit_opflow_utils import to_vector
from tests.simulation.numpy_matrix_assertions import (
    assert_eq_numpy_matrices,
    assert_eq_numpy_vectors,
)


class TestLazyTensorOp:
    @pytest.mark.parametrize(
        "rhs, lhs, expected",
        [
            ([qkop.Zero], [qkop.X], [qkop.One]),
            ([qkop.Plus], [qkop.Z], [qkop.Minus]),
            ([qkop.X], [qkop.Z], [1j * qkop.Y]),
            ([qkop.X, qkop.I ^ qkop.Z], [qkop.I, qkop.Y ^ qkop.I], [qkop.X, qkop.Y ^ qkop.Z]),
        ],
    )
    def test_apply_matching_tensors(
        self,
        rhs: List[qkop.OperatorBase],
        lhs: List[qkop.OperatorBase],
        expected: List[qkop.OperatorBase],
    ):
        result: LazyTensorOp[qkop.OperatorBase] = LazyTensorOp(rhs).apply_matching_tensors(
            LazyTensorOp(lhs)
        )
        assert len(result.ops) == len(expected)
        for i, op in enumerate(expected):
            if isinstance(result.ops[i], qkop.DictStateFn) or isinstance(
                result.ops[i], qkop.VectorStateFn
            ):
                assert_eq_numpy_vectors(to_vector(op), to_vector(result.ops[i]))
            else:
                assert_eq_numpy_matrices(op.to_matrix(), result.ops[i].to_matrix())

    @pytest.mark.parametrize(
        "rhs, lhs",
        [
            ([qkop.I], [qkop.I ^ 2]),
            ([qkop.I ^ 2], [qkop.I]),
            ([qkop.I, qkop.I ^ 2], [qkop.I, qkop.I]),
            ([qkop.I ^ 2, qkop.I], [qkop.I, qkop.I]),
        ],
    )
    def test_apply_matching_tensors_fail(
        self,
        rhs: List[qkop.OperatorBase],
        lhs: List[qkop.OperatorBase],
    ):
        with pytest.raises(LazyTensorOpsNotMatchingException):
            LazyTensorOp(rhs).apply_matching_tensors(LazyTensorOp(lhs))

    @pytest.mark.parametrize(
        "rhs, lhs, eval, result_type",
        [
            ([qkop.Zero], [qkop.X], True, qkop.DictStateFn),
            ([qkop.Zero], [qkop.X], False, qkop.ComposedOp),
            ([qkop.X], [qkop.X], True, qkop.MatrixOp),
            ([qkop.X], [qkop.X], False, qkop.PauliOp),
        ],
    )
    def test_apply_matching_tensors_eval(self, rhs, lhs, eval, result_type):
        assert isinstance(
            LazyTensorOp(rhs).apply_matching_tensors(LazyTensorOp(lhs), eval=eval).ops[0],
            result_type,
        )

    @pytest.mark.parametrize(
        "rhs, lhs, expected",
        [
            ([qkop.Zero], [qkop.X], [qkop.One]),
            ([qkop.Plus], [qkop.Z], [qkop.Minus]),
            ([qkop.X], [qkop.Z], [1j * qkop.Y]),
            ([qkop.X ^ qkop.I, qkop.Z], [qkop.X, qkop.Y, qkop.I], [qkop.I ^ qkop.Y, qkop.Z]),
            ([qkop.X, qkop.I ^ qkop.Z], [qkop.I, qkop.Y, qkop.I], [qkop.X, qkop.Y ^ qkop.Z]),
            (
                [qkop.I, qkop.Y ^ qkop.I, qkop.I ^ qkop.X, qkop.H],
                [qkop.Z, qkop.I ^ qkop.X, qkop.X ^ qkop.Z, qkop.I],
                [qkop.Z, qkop.Y ^ qkop.X, qkop.X ^ (qkop.Y * 1j), qkop.H],
            ),
            (
                [qkop.I ^ qkop.I ^ qkop.I ^ qkop.I ^ qkop.I],
                [qkop.I, qkop.I, qkop.X, qkop.I, qkop.I],
                [qkop.I ^ qkop.I ^ qkop.X ^ qkop.I ^ qkop.I],
            ),
            (
                [qkop.I, qkop.I ^ qkop.I ^ qkop.I ^ qkop.I],
                [qkop.I, qkop.I, qkop.X, qkop.I, qkop.I],
                [qkop.I, qkop.I ^ qkop.X ^ qkop.I ^ qkop.I],
            ),
            (
                [qkop.I ^ qkop.I, qkop.I ^ qkop.I ^ qkop.I ^ qkop.I, qkop.I],
                [qkop.X ^ qkop.H, qkop.I, qkop.Y, qkop.I ^ qkop.I, qkop.Z],
                [qkop.X ^ qkop.H, qkop.I ^ qkop.Y ^ qkop.I ^ qkop.I, qkop.Z],
            ),
        ],
    )
    def test_apply_more_granular_tensors(
        self,
        rhs: List[qkop.OperatorBase],
        lhs: List[qkop.OperatorBase],
        expected: List[qkop.OperatorBase],
    ):
        result: LazyTensorOp[qkop.OperatorBase] = LazyTensorOp(rhs).apply_more_granular_lazy_tensor(
            LazyTensorOp(lhs)
        )
        assert len(result.ops) == len(expected)
        for i, op in enumerate(expected):
            if isinstance(result.ops[i], qkop.DictStateFn) or isinstance(
                result.ops[i], qkop.VectorStateFn
            ):
                assert_eq_numpy_vectors(to_vector(op), to_vector(result.ops[i]))
            else:
                assert_eq_numpy_matrices(op.to_matrix(), result.ops[i].to_matrix())

    @pytest.mark.parametrize(
        "operators, "
        "qubit_idx, "
        "expected_index_of_tensor_operand, "
        "expected_index_within_tensor_operand ",
        [
            ([qkop.I], 0, 0, 0),
            ([qkop.I ^ qkop.I], 0, 0, 0),
            ([qkop.I ^ qkop.I], 1, 0, 1),
            ([qkop.I, qkop.I], 1, 1, 0),
            ([qkop.I ^ qkop.I, qkop.I], 1, 0, 1),
            ([qkop.I ^ qkop.I ^ qkop.I], 2, 0, 2),
            ([qkop.I ^ qkop.I, qkop.I], 2, 1, 0),
            ([qkop.I, qkop.I ^ qkop.I], 2, 1, 1),
            ([qkop.I, qkop.I, qkop.I], 2, 2, 0),
            ([qkop.I ^ qkop.I, qkop.I ^ qkop.I], 0, 0, 0),
            ([qkop.I ^ qkop.I, qkop.I ^ qkop.I], 1, 0, 1),
            ([qkop.I ^ qkop.I, qkop.I ^ qkop.I], 2, 1, 0),
            ([qkop.I ^ qkop.I, qkop.I ^ qkop.I], 3, 1, 1),
        ],
    )
    def test_get_idxs_of_qubit(
        self,
        operators: List[qkop.OperatorBase],
        qubit_idx: int,
        expected_index_of_tensor_operand: int,
        expected_index_within_tensor_operand: int,
    ):
        index_of_tensor_operand, index_within_tensor_operand = LazyTensorOp(
            operators
        ).get_idxs_of_qubit(qubit_idx)
        assert expected_index_of_tensor_operand == index_of_tensor_operand
        assert expected_index_within_tensor_operand == index_within_tensor_operand

    @pytest.mark.parametrize(
        "lhs, rhs, should_match",
        [
            ([qkop.Zero], [qkop.Zero], True),
            ([qkop.Zero], [qkop.One], True),
            ([qkop.Zero], [qkop.Zero ^ qkop.Zero], False),
            ([qkop.Zero, qkop.Zero], [qkop.Zero, qkop.Zero], True),
            ([qkop.Zero, qkop.Zero], [qkop.One, qkop.One], True),
            ([qkop.Zero, qkop.Zero], [qkop.Zero ^ qkop.Zero], False),
            ([qkop.Zero ^ qkop.Plus, qkop.Zero], [qkop.Zero ^ qkop.Zero, qkop.Minus], True),
            ([qkop.Zero, qkop.Zero ^ qkop.Plus], [qkop.Zero ^ qkop.Plus, qkop.Minus], False),
        ],
    )
    def test_matches(
        self, lhs: List[qkop.OperatorBase], rhs: List[qkop.OperatorBase], should_match: bool
    ):
        assert LazyTensorOp(lhs).matches(LazyTensorOp(rhs)) == should_match

    @pytest.mark.parametrize(
        "lhs, rhs, should_match",
        [
            ([qkop.Zero], [qkop.Zero], True),
            ([qkop.Zero], [qkop.One], False),
            ([qkop.Zero], [qkop.Zero ^ qkop.Zero], False),
            ([qkop.Zero, qkop.Zero], [qkop.Zero, qkop.Zero], True),
            ([qkop.Zero, qkop.Zero], [qkop.One, qkop.Zero], False),
            ([qkop.Zero, qkop.Zero], [qkop.Zero ^ qkop.Zero], False),
            ([qkop.Zero ^ qkop.Minus, qkop.Zero], [qkop.Zero ^ qkop.Minus, qkop.Zero], True),
            ([qkop.Zero ^ qkop.Minus, qkop.Zero], [qkop.Zero ^ qkop.Zero, qkop.Zero], False),
            ([qkop.Zero ^ qkop.Plus, qkop.Zero], [qkop.Zero ^ qkop.Zero, qkop.Minus], False),
        ],
    )
    def test_matching_approx_eq_vector(
        self, lhs: List[qkop.OperatorBase], rhs: List[qkop.OperatorBase], should_match: bool
    ):
        assert LazyTensorOp(lhs).matches(LazyTensorOp(rhs)) == should_match
