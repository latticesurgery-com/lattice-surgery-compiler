from typing import List

import pytest

from lsqecc.gates.compress_rotation_approximations import partition_gate_sequence


class TestGateCompression:
    @pytest.mark.parametrize(
        "gate_string, partitioned_gates",
        [
            ("SSSXHSTHTHSTHTH", ["SSS", "X", "HSTH", "T", "HSTH", "T", "H"]),
            ("SHSSXH", ["S", "H", "SS", "X", "H"]),
            ("SHSSHX", ["S", "HSSH", "X"]),
            ("HSSTTSHSX", ["HSSTTSH", "S", "X"]),
            ("STXH", ["ST", "X", "H"]),
            ("HSTX", ["H", "ST", "X"]),
            ("XHST", ["X", "H", "ST"]),
        ],
    )
    def test_partition_gate_sequence(self, gate_string: str, partitioned_gates: List[str]):
        func_output = partition_gate_sequence(gate_string)
        assert len(partitioned_gates) == len(func_output)
        assert func_output == partitioned_gates
