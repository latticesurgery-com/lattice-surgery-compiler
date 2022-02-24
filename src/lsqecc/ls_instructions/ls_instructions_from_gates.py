import itertools
from typing import Sequence

import lsqecc.simulation.qubit_state as qs
from lsqecc.gates import gates
from lsqecc.gates.gates_circuit import GatesCircuit
from lsqecc.ls_instructions import ls_instructions
from lsqecc.pauli_rotations import PauliOperator


class LSInstructionsFromGatesGenerator:
    """
    Convert a sequence of gates to LSInstructions
    """

    def __init__(self, start_ancilla_qubit_counter=0):
        self.ancilla_qubit_counter = start_ancilla_qubit_counter

    def get_new_ancilla(self):
        self.ancilla_qubit_counter += 1
        return self.ancilla_qubit_counter

    def gen_instructions(self, gate: gates.Gate) -> Sequence[ls_instructions.LSInstruction]:
        if isinstance(gate, gates.X):
            return [ls_instructions.LogicalPauli(gate.target_qubit, PauliOperator.X)]
        elif isinstance(gate, gates.Z):
            return [ls_instructions.LogicalPauli(gate.target_qubit, PauliOperator.Z)]
        elif isinstance(gate, gates.S):
            return [ls_instructions.SGate(gate.target_qubit)]
        elif isinstance(gate, gates.T):
            ancilla = self.get_new_ancilla()
            return [
                ls_instructions.RequestMagicState(ancilla),
                ls_instructions.MultiBodyMeasure(
                    {gate.target_qubit: PauliOperator.Z, ancilla: PauliOperator.X}
                ),
                ls_instructions.MeasureSinglePatch(ancilla, PauliOperator.Z),
                ls_instructions.SGate(gate.target_qubit),
                ls_instructions.LogicalPauli(gate.target_qubit),
            ]
        elif isinstance(gate, gates.H):
            return [ls_instructions.HGate(gate.target_qubit)]
        elif isinstance(gate, gates.CNOT):
            ancilla = self.get_new_ancilla()
            return [
                ls_instructions.Init(patch_id=ancilla, state=qs.DefaultSymbolicStates.Plus),
                ls_instructions.MultiBodyMeasure(
                    {gate.control_qubit: PauliOperator.Z, ancilla: PauliOperator.Z}
                ),
                ls_instructions.MultiBodyMeasure(
                    {gate.target_qubit: PauliOperator.X, ancilla: PauliOperator.X}
                ),
                ls_instructions.MeasureSinglePatch(ancilla, PauliOperator.Z),
            ]
        else:
            raise Exception(f"Gate {gate} is not Clifford+T")

    @staticmethod
    def text_from_gates_circuit(circuit: GatesCircuit) -> str:
        generator = LSInstructionsFromGatesGenerator()
        instructions = itertools.chain.from_iterable(map(generator.gen_instructions, circuit.gates))
        return "\n".join(map(repr, instructions))
