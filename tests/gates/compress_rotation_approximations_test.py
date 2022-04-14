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
            ("SHSSXHSHSSXH", ["S", "H", "SS", "X", "HSH", "SS", "X", "H"]),
            ("H", ["H"]),
            ("S", ["S"]),
            ("HS", ["H", "S"]),
            ("SH", ["S", "H"]),
            ("HSH", ["HSH"]),
            ("SHS", ["S", "H", "S"]),
            ("HSHS", ["HSH", "S"]),
            ("SHSH", ["S", "HSH"]),
            ("HSHSH", ["HSH", "S", "H"]),
            ("SHSHS", ["S", "HSH", "S"]),
            ("HSHSHS", ["HSH", "S", "H", "S"]),
            ("SHSHSH", ["S", "HSH", "S", "H"]),
            ("SSSXHSTHTHSTHTH", ["SSS", "X", "HSTH", "T", "HSTH", "T", "H"]),
            ("HSTHSSHSTHT", ["HSTH", "SS", "HSTH", "T"]),
            ("HSTHSSHSTH", ["HSTH", "SS", "HSTH"]),
            ("STHSSHSTHTH", ["ST", "HSSH", "ST", "HTH"]),
            ("XHSTHST", ["X", "HSTH", "ST"]),
            ("HXHSTHST", ["H", "X", "HSTH", "ST"]),
        ],
    )
    def test_partition_gate_sequence(self, gate_string: str, partitioned_gates: List[str]):
        func_output = partition_gate_sequence(gate_string)
        assert len(partitioned_gates) == len(func_output)
        assert func_output == partitioned_gates
