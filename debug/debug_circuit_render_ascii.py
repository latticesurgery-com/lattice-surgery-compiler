from circuit import *
from rotation import *


output = """\
 q0--|I|--|I|--|I|--|I|---|I|---|I|--|I|--|I|
 q1--|Z|--|Z|--|Z|--|Z|---|Z|---|Z|--|Z|--|Z|
 q2--|Y|--|Y|--|Y|--|Y|---|Y|---|Y|--|Y|--|Y|
 q3--|Z|--|Z|--|Z|--|Z|---|Z|---|Z|--|Z|--|Z|
pi*  1/2  1/4  1/8 -1/8  1/16 -1/16   M   -M 
"""

if __name__ == "__main__":
    c = Circuit(4)

    I = PauliOperator.I
    X = PauliOperator.Z
    Y = PauliOperator.Y
    Z = PauliOperator.Z

    c.add_pauli_block(Rotation.from_list([I,X,Y,Z],Fraction(1,2)))
    c.add_pauli_block(Rotation.from_list([I,X,Y,Z],Fraction(1,4)))
    c.add_pauli_block(Rotation.from_list([I,X,Y,Z],Fraction(1,8)))
    c.add_pauli_block(Rotation.from_list([I,X,Y,Z],Fraction(-1,8)))
    c.add_pauli_block(Rotation.from_list([I,X,Y,Z],Fraction(1,16)))
    c.add_pauli_block(Rotation.from_list([I,X,Y,Z],Fraction(-1,16)))
    c.add_pauli_block(Measurement.from_list([I,X,Y,Z]))
    c.add_pauli_block(Measurement.from_list([I,X,Y,Z],True))


    print(c.render_ascii())

    assert (c.render_ascii()==output)