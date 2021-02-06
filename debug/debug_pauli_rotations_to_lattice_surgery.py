from pauli_rotations_to_lattice_surgery import *
import lattice_view

if __name__ == "__main__":
    c = Circuit(1)
    I = PauliOperator.I
    X = PauliOperator.X
    Y = PauliOperator.Y
    Z = PauliOperator.Z



    c.add_pauli_block(Rotation.from_list([X],Fraction(1,8)))


    print(c.render_ascii())


    lsc = pauli_rotation_to_lattice_surgery_computation(c)
    lattice_view.to_file(lsc.composer.getSlices(), "rotations.html")