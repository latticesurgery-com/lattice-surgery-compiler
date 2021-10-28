from fractions import Fraction
from lsqecc.pauli_rotations import PauliRotation, PauliRotationCircuit, PauliOperator
from lsqecc.logical_lattice_ops import dependency_graph as dg

I = PauliOperator.I
X = PauliOperator.X
Z = PauliOperator.Z
Y = PauliOperator.Y

# Example from #71 as the base test case
c = PauliRotationCircuit(2)
c.add_pauli_block(PauliRotation.from_list([X, X],Fraction(1,8)))
c.add_pauli_block(PauliRotation.from_list([Z, Z],Fraction(1,4)))
c.add_pauli_block(PauliRotation.from_list([X, Z],Fraction(-1,4)))
c.add_pauli_block(PauliRotation.from_list([I, X],Fraction(-1,4)))
c.add_pauli_block(PauliRotation.from_list([Z, I],Fraction(-1,4)))
c.add_pauli_block(PauliRotation.from_list([I, Z],Fraction(-1,4)))

print(c.render_ascii())
a = dg.DependencyGraph.from_circuit_by_commutation(c)

print("Returned terminal nodes:")
print(a.terminal_node)
print()
print("Printing Graph:")
graph = a.generate_adjacency_list()
for i in graph:
    print('{}: {}'.format(i, graph[i]))