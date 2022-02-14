
from lsqecc.pauli_rotations.circuit import *

from app_oriented_benchmarks_adapted import qft_benchmark


if __name__ == "__main__":
    qasm = qft_benchmark.qft_gate(4).qasm()
    print(qasm)
    print(PauliOpCircuit._manual_parse_from_reversible_qasm(qasm))

