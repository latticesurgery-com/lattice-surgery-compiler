from typing import TextIO, cast

import pytest

import lsqecc.simulation.qubit_state as qs
from lsqecc.ls_instructions import ls_instructions as lsi
from lsqecc.ls_instructions.shorthand_file_writer import ShorthandFileWriter
from lsqecc.pauli_rotations import PauliOperator


class MockFile:
    def __init__(self):
        self.content = ""

    def write(self, s: str):
        self.content += s


@pytest.mark.parametrize(
    "instruction, expected_output",
    [
        (lsi.DeclareLogicalQubitPatches([0, 1, 2, 100]), "DeclareLogicalQubitPatches 0,1,2,100"),
        (lsi.Init(patch_id=101, state=qs.DefaultSymbolicStates.Zero), "0 101 0"),
        (lsi.Init(patch_id=102, state=qs.DefaultSymbolicStates.Plus), "0 102 +"),
        (lsi.Init(patch_id=102, state=qs.DefaultSymbolicStates.UnknownState), "0 102 |?>"),
        (lsi.MeasureSinglePatch(patch_id=103, op=PauliOperator.X), "1 103 X"),
        (lsi.MeasureSinglePatch(patch_id=104, op=PauliOperator.Z), "1 104 Z"),
        (
            lsi.MultiBodyMeasure(patch_pauli_map={105: PauliOperator.X, 106: PauliOperator.Z}),
            "2 105:X,106:Z",
        ),
        (
            lsi.MultiBodyMeasure(
                patch_pauli_map={107: PauliOperator.X, 108: PauliOperator.Z, 109: PauliOperator.Z}
            ),
            "2 107:X,108:Z,109:Z",
        ),
        (lsi.RequestMagicState(patch_id=110), "3 110"),
        (lsi.LogicalPauli(patch_id=111, op=PauliOperator.X), "4 111 X"),
        (lsi.LogicalPauli(patch_id=112, op=PauliOperator.Z), "4 112 Z"),
        (lsi.HGate(patch_id=113), "5 113"),
        (lsi.SGate(patch_id=114), "6 114"),
        (lsi.RequestYState(patch_id=115), "7 115"),
    ],
)
def test_write_instruction(instruction, expected_output):
    mock_file = MockFile()
    writer = ShorthandFileWriter(cast(TextIO, mock_file))
    writer.write_instruction(instruction)
    assert mock_file.content == expected_output + "\n"
