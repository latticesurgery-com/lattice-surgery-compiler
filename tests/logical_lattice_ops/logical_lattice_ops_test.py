from unittest.mock import patch
import pytest
from lsqecc.pauli_rotations import PauliOpCircuit, PauliRotation, Measurement, PauliOperator

from lsqecc.logical_lattice_ops.logical_lattice_ops import (
    LogicalLatticeOperation,
    SinglePatchMeasurement,
)
import pytest
import uuid

I = PauliOperator.I
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
