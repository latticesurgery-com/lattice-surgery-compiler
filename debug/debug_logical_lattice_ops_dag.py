from logical_lattice_ops import *

if __name__ == "__main__":
    I = PauliOperator.I
    X = PauliOperator.X
    Z = PauliOperator.Z
    Y = PauliOperator.Y

    c = Circuit(4)

    c.add_pauli_block(Rotation.from_list([Z, I, I, I], Fraction(1, 8)))
    c.add_pauli_block(Rotation.from_list([I, X, Z, I], Fraction(1, 4)))
    c.add_pauli_block(Rotation.from_list([I, I, I, X], Fraction(-1, 4)))



    dag = DependencyGraph.from_circuit_by_commutation(c)
    ParallelLogicalLatticeComputation(dag)