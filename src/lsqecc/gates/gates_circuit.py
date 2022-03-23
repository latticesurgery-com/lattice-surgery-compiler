import itertools
from dataclasses import dataclass, field
from typing import Sequence

import lsqecc.gates.parse
from lsqecc.gates import gates  # noqa: F401


@dataclass
class GatesCircuit:
    """Circuit as a sequence of gates. Each gates carries information about its wires."""

    gates: Sequence["gates.Gate"] = field(default_factory=lambda: [])  # noqa: F811

    def to_clifford_plus_t(self, compress_rotations: bool = False) -> "GatesCircuit":
        return GatesCircuit(
            list(
                itertools.chain.from_iterable(
                    [gate.to_clifford_plus_t(compress_rotations) for gate in self.gates]
                )
            )
        )

    @staticmethod
    def from_qasm(qasm: str) -> "GatesCircuit":
        return GatesCircuit(lsqecc.gates.parse.parse_gates_circuit(qasm))
