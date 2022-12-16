import itertools
from dataclasses import dataclass, field
from typing import Optional, Sequence

import lsqecc.gates.parse
from lsqecc.gates import gates  # noqa: F401


@dataclass
class GatesCircuit:
    """Circuit as a sequence of gates. Each gates carries information about its wires."""

    gates: Sequence["gates.Gate"] = field(default_factory=lambda: [])  # noqa: F811
    num_qubits: Optional[int] = None

    def to_clifford_plus_t(self, compress_rotations: bool = False) -> "GatesCircuit":
        return GatesCircuit(
            list(
                itertools.chain.from_iterable(
                    [gate.to_clifford_plus_t(compress_rotations) for gate in self.gates]
                )
            ),
            num_qubits=self.num_qubits,
        )

    @staticmethod
    def from_qasm(qasm: str) -> "GatesCircuit":
        num_qubits = lsqecc.gates.parse.get_num_qubits(qasm)
        return GatesCircuit(lsqecc.gates.parse.parse_gates_circuit(qasm), num_qubits=num_qubits)
