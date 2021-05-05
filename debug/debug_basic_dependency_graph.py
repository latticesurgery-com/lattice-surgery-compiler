from circuit import *
from rotation import *
from dependency_graph import *

I = PauliOperator.I 
X = PauliOperator.X 
Z = PauliOperator.Z 
Y = PauliOperator.Y  

# Example from #71 as the base test case
c = PauliCircuit(2)
c.add_pauli_block(Rotation.from_list([X, X],Fraction(1,8)))
c.add_pauli_block(Rotation.from_list([Z, Z],Fraction(1,4)))
c.add_pauli_block(Rotation.from_list([X, Z],Fraction(-1,4)))
c.add_pauli_block(Rotation.from_list([I, X],Fraction(-1,4)))
c.add_pauli_block(Rotation.from_list([Z, I],Fraction(-1,4)))
c.add_pauli_block(Rotation.from_list([I, Z],Fraction(-1,4)))

print(c.render_ascii())
a = DependencyGraph.from_circuit_by_commutation(c)

print("Returned terminal nodes:")
print(a.terminal_node)
print()
print("Printing Graph:")
graph = a.generate_adjacency_list()
for i in graph:
    print('{}: {}'.format(i, graph[i]))