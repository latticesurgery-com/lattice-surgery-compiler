import pauli_rotations_to_lattice_surgery as ls
from logical_patch_state_simulation import *


import webgui.lattice_view
from fractions import Fraction




if __name__ == "__main__":

    c = ls.Circuit(2)
    ls_I = ls.PauliOperator.I
    ls_X = ls.PauliOperator.X
    ls_Y = ls.PauliOperator.Y
    ls_Z = ls.PauliOperator.Z




    c.add_pauli_block(ls.Rotation.from_list([ls_I, ls_X], Fraction(1, 2)))
    c.add_pauli_block(ls.Rotation.from_list([ls_X, ls_I], Fraction(1, 2)))
    print(c.render_ascii())

    comp = ls.pauli_rotation_to_lattice_surgery_computation(c)
    webgui.lattice_view.render_to_file(comp.composer.getSlices(), "../index.html")

    print(" ===== Slice states: =====")

    sim_states = simulate_slices(comp.composer.getSlices())
    for sim_state in sim_states:
        print(sim_state)



#    # Do a multi-body measuremt
#    # Part 3 of the operator flow tutorial + N&C measurement observable
#
#    # Create an observable of the desired form
#    observable = qk.X^qk.Z
#
#    print( sim_circ.to_matrix_op().eval())
#    print( observable)
#    projector = ProjectiveMeasurement.get_projectors_from_pauli_observable(observable)[0]
#    print( projector )
#    #print( qk.StateFn(projector).adjoint().eval(sim_circ.to_matrix_op().eval()))
#    print( ProjectiveMeasurement.measure_pauli_product(observable, sim_circ.eval()) )
#    print( ProjectiveMeasurement.measure_pauli_product(observable, sim_circ.eval())[0][0].eval())