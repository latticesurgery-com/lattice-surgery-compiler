from lattice_surgery_computation_composer import *
from webgui import lattice_view

if __name__ == "__main__":
    c = Circuit(4)
    I = PauliOperator.I
    X = PauliOperator.X
    Y = PauliOperator.Y
    Z = PauliOperator.Z

    c.add_pauli_block(Rotation.from_list([I, X, I, Z], Fraction(1, 2)))
    c.add_pauli_block(Rotation.from_list([X, I, Z, I], Fraction(1, 4)))
    # c.add_pauli_block(Rotation.from_list([I, X, I, Z], Fraction(1, 8)))
    # c.add_pauli_block(Rotation.from_list([X, I, Z, I], Fraction(-1, 8)))


    print(c.render_ascii())

    logical_comp = LogicalLatticeComputation(c)
    lsc = LatticeSurgeryComputation.make_computation_with_simulation(logical_comp, LayoutType.SimplePreDistilledStates)
    lattice_view.render_to_file(lsc.composer.getSlices(), "index.html", template="/home/george/courses/CMPT415_498/code/lattice-surgery-compiler/webgui/templates/lattice_view.mak")
