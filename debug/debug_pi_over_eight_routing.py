from lattice_surgery_computation_composer import *
from webgui import lattice_view
from debug.util import *

if __name__ == "__main__":
    c = PauliOpCircuit(4)
    I = PauliOperator.I
    X = PauliOperator.X
    Y = PauliOperator.Y
    Z = PauliOperator.Z

    c.add_pauli_block(PauliRotation.from_list(    [I, X, I, I], Fraction(1, 8)))
    c.add_pauli_block(PauliRotation.from_list(    [I, I, Z, X], Fraction(1, 8)))

    print(c.render_ascii())

    logical_comp = LogicalLatticeComputation(c)

    lsc = LatticeSurgeryComputation.make_computation_with_simulation(logical_comp, LayoutType.SimplePreDistilledStates)
    lattice_view.render_to_file(lsc.composer.getSlices(), "index.html", template="/home/george/courses/CMPT415_498/code/lattice-surgery-compiler/webgui/templates/lattice_view.mak")
