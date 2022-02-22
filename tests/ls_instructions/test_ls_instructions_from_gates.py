import pytest

from lsqecc.gates.gates_circuit import GatesCircuit
from lsqecc.ls_instructions.ls_instructions_from_gates import (
    LSInstructionsFromGatesGenerator,
)

QFT_CIRCUIT = """OPENQASM 2.0;
include "qelib1.inc";
qreg q0[4];
h q0[3];
barrier q0[0],q0[1],q0[2],q0[3];
crz(pi/2) q0[2],q0[3];
h q0[2];
barrier q0[0],q0[1],q0[2],q0[3];
crz(pi/4) q0[1],q0[3];
crz(pi/2) q0[1],q0[2];
h q0[1];
barrier q0[0],q0[1],q0[2],q0[3];
crz(pi/8) q0[0],q0[3];
crz(pi/4) q0[0],q0[2];
crz(pi/2) q0[0],q0[1];
h q0[0];
barrier q0[0],q0[1],q0[2],q0[3];
"""


class TestLSInstructionsFromGatesGenerator:
    def test_text_from_gates_circuit(self, snapshot):
        instructions: str = LSInstructionsFromGatesGenerator.text_from_gates_circuit(
            GatesCircuit.from_qasm(QFT_CIRCUIT).to_clifford_plus_t()
        )
        snapshot.assert_match(instructions, "circuit.txt")

    def test_text_from_gates_circuit_fail_non_clifford_plus_t(self):
        circuit = GatesCircuit.from_qasm(QFT_CIRCUIT)
        with pytest.raises(Exception):
            LSInstructionsFromGatesGenerator.text_from_gates_circuit(circuit)
