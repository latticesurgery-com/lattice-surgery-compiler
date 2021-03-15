import lattice_surgery_computation_composer as ls
import logical_patch_state_simulation as lssim


import webgui.lattice_view
from fractions import Fraction




if __name__ == "__main__":

    c = ls.Circuit(2)
    ls_I = ls.PauliOperator.I
    ls_X = ls.PauliOperator.X
    ls_Y = ls.PauliOperator.Y
    ls_Z = ls.PauliOperator.Z




    c.add_pauli_block(ls.Rotation.from_list([ls_I, ls_X], Fraction(1, 2)))
    c.add_pauli_block(ls.Rotation.from_list([ls_I, ls_X], Fraction(1, 2)))
    c.add_pauli_block(ls.Rotation.from_list([ls_Z, ls_Z], Fraction(1, 4)))
    print(c.render_ascii())

    logical_circuit = ls.LogicalLatticeComputation(c)
    comp = ls.LatticeSurgeryComputation.make_computation_with_simulation(logical_circuit,ls.LayoutType.SimplePreDistilledStates)
    webgui.lattice_view.render_to_file(comp.composer.getSlices(), "../index.html")

    print(" ===== Slice states: =====")

    for slice in comp.composer.getSlices():
        print(slice.logical_state)
