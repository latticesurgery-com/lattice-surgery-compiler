import pytest
from lsqecc.logical_lattice_ops.logical_lattice_ops import LogicalLatticeOperation
import pytest


class TestLogicalLatticeOperation:
    def test_get_operating_patches(self):
        op = LogicalLatticeOperation()
        with pytest.raises(NotImplementedError):
            op.get_operating_patches()
