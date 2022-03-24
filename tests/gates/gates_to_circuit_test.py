from lsqecc.gates.gates_circuit import GatesCircuit

# Tests all QFT gates, by starting with a 3 qubit QFT an moving the the gate that needs
# approximations to a separate case.

EXAMPLE_CIRCUIT_NO_APPROX_NEEDED = """OPENQASM 2.0;
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
crz(pi/4) q0[0],q0[2];
crz(pi/2) q0[0],q0[1];
h q0[0];
barrier q0[0],q0[1],q0[2],q0[3];
"""

EXAMPLE_CIRCUIT_NEEDING_APPROX = """OPENQASM 2.0;
include "qelib1.inc";
qreg q0[4];
crz(pi/8) q0[0],q0[3];
"""


class TestGateToCircuit:
    def test_to_clifford_plus_t(self, snapshot):
        snapshot.assert_match(
            repr(
                GatesCircuit.from_qasm(EXAMPLE_CIRCUIT_NO_APPROX_NEEDED).to_clifford_plus_t(
                    compress_rotations=False
                )
            ),
            "circuit_no_approx.txt",
        )

        snapshot.assert_match(
            repr(
                GatesCircuit.from_qasm(EXAMPLE_CIRCUIT_NEEDING_APPROX).to_clifford_plus_t(
                    compress_rotations=False
                )
            ),
            "circuit_with_approx.txt",
        )

    def test_to_clifford_plus_t_with_compression(self, snapshot):
        snapshot.assert_match(
            repr(
                GatesCircuit.from_qasm(EXAMPLE_CIRCUIT_NO_APPROX_NEEDED).to_clifford_plus_t(
                    compress_rotations=True
                )
            ),
            "circuit_no_approx.txt",
        )

        snapshot.assert_match(
            repr(
                GatesCircuit.from_qasm(EXAMPLE_CIRCUIT_NEEDING_APPROX).to_clifford_plus_t(
                    compress_rotations=True
                )
            ),
            "circuit_with_approx.txt",
        )
