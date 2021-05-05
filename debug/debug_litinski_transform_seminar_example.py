from circuit import *
from rotation import *

I = PauliOperator.I 
X = PauliOperator.X 
Z = PauliOperator.Z 
Y = PauliOperator.Y  

c = PauliCircuit(4)

c.add_pauli_block(Rotation.from_list([Z, I, I, I],Fraction(1,8)))
c.add_pauli_block(Rotation.from_list([I, X, Z, I],Fraction(1,4)))
c.add_pauli_block(Rotation.from_list([I, I, I, X],Fraction(-1,4)))

c.add_pauli_block(Rotation.from_list([X, I, I, I],Fraction(-1,4)))
c.add_pauli_block(Rotation.from_list([I, X, I, I],Fraction(-1,4)))
c.add_pauli_block(Rotation.from_list([I, I, Z, I],Fraction(-1,4)))
c.add_pauli_block(Rotation.from_list([I, I, I, Z],Fraction(1,8)))

c.add_pauli_block(Rotation.from_list([X, Z, I, I],Fraction(1,4)))
c.add_pauli_block(Rotation.from_list([I, I, X, I],Fraction(1,4)))

c.add_pauli_block(Rotation.from_list([X, I, I, I],Fraction(-1,4)))
c.add_pauli_block(Rotation.from_list([I, I, Z, I],Fraction(1,8)))

c.add_pauli_block(Rotation.from_list([X, I, I, Z],Fraction(1,4)))

c.add_pauli_block(Rotation.from_list([Z, I, I, I],Fraction(1,8)))

c.add_pauli_block(Rotation.from_list([X, I, I, I],Fraction(-1,4)))
c.add_pauli_block(Rotation.from_list([I, X, I, I],Fraction(1,4)))
c.add_pauli_block(Rotation.from_list([I, I, X, I],Fraction(1,4)))
c.add_pauli_block(Rotation.from_list([I, I, I, X],Fraction(1,4)))

c.add_pauli_block(Measurement.from_list([Z, I, I, I]))
c.add_pauli_block(Measurement.from_list([I, Z, I, I]))
c.add_pauli_block(Measurement.from_list([I, I, Z, I]))
c.add_pauli_block(Measurement.from_list([I, I, I, Z]))

print("BEFORE:")
print(c.render_ascii())
c.apply_transformation()
print("AFTER:")
print(c.render_ascii())