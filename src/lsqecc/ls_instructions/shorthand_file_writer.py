from typing import TextIO

import lsqecc.simulation.qubit_state as qs
from lsqecc.ls_instructions import ls_instructions as lsi


class ShorthandFileWriter:
    def __init__(self, output_file: TextIO):
        self.output_file = output_file

    def write_instruction(self, instruction: lsi.LSInstruction):
        if isinstance(instruction, lsi.DeclareLogicalQubitPatches):
            self.output_file.write(repr(instruction))
        elif isinstance(instruction, lsi.Init):
            self.output_file.write("0 ")
            self.output_file.write(str(instruction.patch_id))
            self.output_file.write(" ")
            self.output_file.write(ShorthandFileWriter.shorthand_state(instruction.state))
        elif isinstance(instruction, lsi.MeasureSinglePatch):
            self.output_file.write("1 ")
            self.output_file.write(str(instruction.patch_id))
            self.output_file.write(" ")
            self.output_file.write(str(instruction.op))
        elif isinstance(instruction, lsi.MultiBodyMeasure):
            self.output_file.write("2 ")
            self.output_file.write(
                ",".join(
                    str(patch_id) + ":" + str(op)
                    for patch_id, op in instruction.patch_pauli_map.items()
                )
            )
        elif isinstance(instruction, lsi.RequestMagicState):
            self.output_file.write("3 ")
            self.output_file.write(str(instruction.patch_id))
        elif isinstance(instruction, lsi.LogicalPauli):
            self.output_file.write("4 ")
            self.output_file.write(str(instruction.patch_id))
            self.output_file.write(" ")
            self.output_file.write(str(instruction.op))
        elif isinstance(instruction, lsi.HGate):
            self.output_file.write("5 ")
            self.output_file.write(str(instruction.patch_id))
        elif isinstance(instruction, lsi.SGate):
            self.output_file.write("6 ")
            self.output_file.write(str(instruction.patch_id))
        elif isinstance(instruction, lsi.RequestYState):
            self.output_file.write("7 ")
            self.output_file.write(str(instruction.patch_id))
        else:
            raise NotImplementedError(f"No shorthand for instruction: {instruction}")
        self.output_file.write("\n")

    @staticmethod
    def shorthand_state(symbolic_state: qs.QubitState) -> str:
        if symbolic_state == qs.DefaultSymbolicStates.Zero:
            return "0"
        if symbolic_state == qs.DefaultSymbolicStates.Plus:
            return "+"
        return symbolic_state.ket_repr()
