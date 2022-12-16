import itertools
from typing import Sequence
from typing.io import IO

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

    @staticmethod
    def get_declaration_instruction(qubit_ids: list[int]) -> ls_instructions.LSInstruction:
        return ls_instructions.DeclareLogicalQubitPatches(patch_ids=qubit_ids)

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
        elif isinstance(gate, gates.SingleQubitMeasurement):
            return [ls_instructions.MeasureSinglePatch(patch_id=gate.target_qubit, op=gate.basis)]
        else:
            raise Exception(f"Gate {gate} is not Clifford+T")

    @staticmethod
    def text_from_gates_circuit(circuit: GatesCircuit) -> str:
        generator = LSInstructionsFromGatesGenerator()
        instructions = itertools.chain.from_iterable(map(generator.gen_instructions, circuit.gates))
        return "\n".join(map(repr, instructions))

    @staticmethod
    def write_instruction(circuit: GatesCircuit, f: IO):
        if circuit.num_qubits is None:
            raise Exception("num_qubits required to write ls instrtuctions")
        print(
            repr(
                ls_instructions.DeclareLogicalQubitPatches(
                    patch_ids=list(range(circuit.num_qubits))
                )
            ),
            file=f,
        )

        generator = LSInstructionsFromGatesGenerator(circuit.num_qubits)
        for gate in circuit.gates:
            for instr in generator.gen_instructions(gate):
                print(repr(instr), file=f)
