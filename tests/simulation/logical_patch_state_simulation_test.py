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
from typing import Tuple

import pytest
import qiskit.opflow as qkop

from lsqecc.simulation.logical_patch_state_simulation import (
    ProjectiveMeasurement,
    circuit_add_op_to_qubit,
)
from lsqecc.simulation.qiskit_opflow_utils import to_vector
from tests.simulation.numpy_matrix_assertions import assert_eq_numpy_vectors


@pytest.mark.parametrize(
    "circuit, op, idx, desired_state",
    [
        (qkop.Zero, qkop.X, 0, qkop.One),
        (qkop.Zero ^ qkop.Zero, qkop.X, 0, qkop.Zero ^ qkop.One),
        (qkop.Zero ^ qkop.Zero, qkop.X, 1, qkop.One ^ qkop.Zero),
        (qkop.Zero ^ qkop.Zero ^ qkop.Zero, qkop.X, 0, qkop.Zero ^ qkop.Zero ^ qkop.One),
        (qkop.Zero ^ qkop.Zero ^ qkop.Zero, qkop.X, 1, qkop.Zero ^ qkop.One ^ qkop.Zero),
        (qkop.Zero ^ qkop.Zero ^ qkop.Zero, qkop.X, 2, qkop.One ^ qkop.Zero ^ qkop.Zero),
    ],
)
def test_circuit_add_op_to_qubit(
    circuit: qkop.OperatorBase, op, idx, desired_state: qkop.OperatorBase
):
    circuit_with_op_applied = circuit_add_op_to_qubit(circuit, op, idx)
    assert_eq_numpy_vectors(
        to_vector(circuit_with_op_applied.eval()), to_vector(desired_state.eval())
    )


class TestProjectiveMeasurement:
    @pytest.mark.parametrize(
        "projector, state, probability",
        [
            ((qkop.I + qkop.Z) / 2, qkop.Zero, 1),
            ((qkop.I - qkop.Z) / 2, qkop.Zero, 0),
            ((qkop.I + qkop.Z) / 2, qkop.Plus, 0.5),
            ((qkop.I - qkop.Z) / 2, qkop.Plus, 0.5),
            ((qkop.I + qkop.X) / 2, qkop.Plus, 1),
            ((qkop.I - qkop.X) / 2, qkop.Plus, 0),
            ((qkop.I + qkop.X) / 2, qkop.Zero, 0.5),
            ((qkop.I - qkop.X) / 2, qkop.Zero, 0.5),
        ],
    )
    def test_borns_rule(self, projector: qkop.OperatorBase, state: qkop.OperatorBase, probability):
        assert ProjectiveMeasurement.borns_rule(projector, state) == pytest.approx(probability)

    @pytest.mark.parametrize(
        "projector, initial_state, desired_state_after_measurement, desired_probability",
        [
            ((qkop.I + qkop.Z) / 2, qkop.Zero, qkop.Zero, 1),
            ((qkop.I + qkop.Z) / 2, qkop.Plus, qkop.Zero, 0.5),
            ((qkop.I - qkop.Z) / 2, qkop.Plus, qkop.One, 0.5),
            ((qkop.I + qkop.X) / 2, qkop.Plus, qkop.Plus, 1),
            ((qkop.I + qkop.X) / 2, qkop.Zero, qkop.Plus, 0.5),
            ((qkop.I - qkop.X) / 2, qkop.Zero, qkop.Minus, 0.5),
        ],
    )
    def test_compute_outcome_state(
        self,
        projector: qkop.OperatorBase,
        initial_state: qkop.OperatorBase,
        desired_state_after_measurement: qkop.OperatorBase,
        desired_probability,
    ):
        actual_state, actual_probability = ProjectiveMeasurement.compute_outcome_state(
            projector, initial_state
        )
        assert actual_probability == pytest.approx(desired_probability)
        assert_eq_numpy_vectors(
            to_vector(desired_state_after_measurement.eval()), to_vector(actual_state)
        )

    @pytest.mark.parametrize(
        "pauli_observable, desired_projectors",
        [
            (qkop.X, ((qkop.I + qkop.X) / 2, (qkop.I - qkop.X) / 2)),
            (
                qkop.I ^ qkop.X,
                (
                    ((qkop.I ^ qkop.I) + (qkop.I ^ qkop.X)) / 2,
                    ((qkop.I ^ qkop.I) - (qkop.I ^ qkop.X)) / 2,
                ),
            ),
            (
                qkop.Z ^ qkop.X,
                (
                    ((qkop.I ^ qkop.I) + (qkop.Z ^ qkop.X)) / 2,
                    ((qkop.I ^ qkop.I) - (qkop.Z ^ qkop.X)) / 2,
                ),
            ),
        ],
    )
    def test_get_projectors_from_pauli_observable(
        self,
        pauli_observable: qkop.OperatorBase,
        desired_projectors: Tuple[qkop.OperatorBase, qkop.OperatorBase],
    ):
        p_0, p_1 = ProjectiveMeasurement.get_projectors_from_pauli_observable(pauli_observable)
        assert_eq_numpy_vectors(to_vector(desired_projectors[0]), to_vector(p_0))
        assert_eq_numpy_vectors(to_vector(desired_projectors[1]), to_vector(p_1))
