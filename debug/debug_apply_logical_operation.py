from lsqecc.patches import lattice_surgery_computation_composer as lscc 
from lsqecc.logical_lattice_ops import logical_lattice_ops as llops
from lsqecc.pauli_rotations import PauliRotationCircuit, PauliOperator, PauliRotation
from fractions import Fraction
# from webgui import lattice_view

if __name__ == "__main__":
    c = PauliRotationCircuit(4)
    I = PauliOperator.I
    X = PauliOperator.X
    Y = PauliOperator.Y
    Z = PauliOperator.Z

    c.add_pauli_block(PauliRotation.from_list([X, I, I, I], Fraction(1, 2)))
    c.add_pauli_block(PauliRotation.from_list([I, X, I, I], Fraction(1, 2)))
    c.add_pauli_block(PauliRotation.from_list([I, I, X, I], Fraction(1, 2)))
    c.add_pauli_block(PauliRotation.from_list([I, I, I, X], Fraction(1, 2)))


    print(c.render_ascii())

    logical_comp = llops.LogicalLatticeComputation(c)
    lsc = lscc.LatticeSurgeryComputation.make_computation_with_simulation(logical_comp, lscc.LayoutType.SimplePreDistilledStates)
    # lattice_view.render_to_file(lsc.composer.getSlices(), "index.html", template="/home/george/courses/CMPT415_498/code/lattice-surgery-compiler/webgui/templates/lattice_view.mak")
