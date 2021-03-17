from lattice_surgery_computation_composer import *
from webgui import lattice_view
from debug.util import *

if __name__ == "__main__":
    c = Circuit(4)
    I = PauliOperator.I
    X = PauliOperator.X
    Y = PauliOperator.Y
    Z = PauliOperator.Z

    c.add_pauli_block(Rotation.from_list([X, I, I, I], Fraction(1, 2)))
    c.add_pauli_block(Rotation.from_list([Z, I, I, I], Fraction(1, 2)))


    print(c.render_ascii())

    logical_comp = LogicalLatticeComputation(c)

    lsc = LatticeSurgeryComputation.make_computation_with_simulation(logical_comp, LayoutType.SimplePreDistilledStates)
    lattice_view.render_to_file(lsc.composer.getSlices(), "index.html", template="/home/george/courses/CMPT415_498/code/lattice-surgery-compiler/webgui/templates/lattice_view.mak")
