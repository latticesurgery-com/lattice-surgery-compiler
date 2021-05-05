from lattice_surgery_computation_composer import *
from logical_patch_state_simulation import qk
from webgui import lattice_view
from debug.util import *

if __name__ == "__main__":
    c = PauliCircuit(4)
    I = PauliOperator.I
    X = PauliOperator.X
    Y = PauliOperator.Y
    Z = PauliOperator.Z

    c.add_pauli_block(Rotation.from_list([X, Z, I, I], Fraction(1, 4)))
    c.add_pauli_block(Rotation.from_list([I, I, X, X], Fraction(1, 4)))
    c.add_pauli_block(Rotation.from_list([I, I, Z, I], Fraction(1, 8)))
    c.add_pauli_block(Rotation.from_list([I, X, I, I], Fraction(1, 8)))

    print("Starting circuit:")
    print(c.render_ascii())

    c.apply_transformation(remove_y_operators=False)
    print("Removed stabilizer rotations:")
    print(c.render_ascii())

    print("Removed y operators:")
    c.remove_y_operators_from_circuit()
    print(c.render_ascii())
