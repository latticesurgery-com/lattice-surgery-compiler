import uuid

import pytest

import lsqecc.simulation.qubit_state as qs
from lsqecc.logical_lattice_ops.logical_lattice_ops import (
    AncillaQubitPatchInitialization,
    LogicalLatticeOperation,
    LogicalPauli,
    MagicStateRequest,
    MultiBodyMeasurement,
    SinglePatchMeasurement,
)
from lsqecc.pauli_rotations import Measurement, PauliOperator

I = PauliOperator.I  # noqa: E741
X = PauliOperator.X
Y = PauliOperator.Y
Z = PauliOperator.Z


class TestLogicalLatticeOperation:
    def test_get_operating_patches(self):
        op = LogicalLatticeOperation()
        with pytest.raises(NotImplementedError):
            op.get_operating_patches()


class TestSinglePatchMeasurement:
    def test_get_operating_patches(self):
        m = Measurement.from_list([X])
        qubit_id = uuid.uuid4()
        patch_op = SinglePatchMeasurement(qubit_id, m.get_op(0))
        assert patch_op.get_operating_patches() == [qubit_id]


class TestMultiBodyMeasurement:
    def test_get_operating_patches(self):
        multi_measurement = Measurement.from_list([X, Z, X, Z])
        patch_operator_map = dict([(uuid.uuid4(), op) for op in multi_measurement.ops_list])
        multi_body_patch_op = MultiBodyMeasurement(patch_operator_map)
        assert multi_body_patch_op.get_operating_patches() == list(patch_operator_map.keys())


class TestAncillaQubitPatchInitialization:
    def test_get_operating_patches(self):
        ancilla_uuid = uuid.uuid4()
        state = qs.DefaultSymbolicStates.YPosEigenState
        ancilla_patch = AncillaQubitPatchInitialization(state, ancilla_uuid)
        assert ancilla_patch.get_operating_patches() == [ancilla_uuid]


class TestLogicalPauli:
    def test_get_operating_patches(self):
        qubit_id = uuid.uuid4()
        matrix = X
        logical_pauli = LogicalPauli(qubit_id, matrix)
        assert logical_pauli.get_operating_patches() == [qubit_id]


class TestMagicStateRequest:
    def test_get_operating_patches(self):
        qubit_id = uuid.uuid4()
        magic_state = MagicStateRequest(qubit_id)
        assert magic_state.get_operating_patches() == [qubit_id]
