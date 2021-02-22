import qiskit as qk
import pauli_rotations_to_lattice_surgery as ls
from fractions import Fraction
import webgui.lattice_view

import qiskit.extensions.simulator #access snapshot
import qiskit.circuit.measure #access measure
import qiskit.extensions.simulator


"""
*_*_*_*_*_*_*_*_* Found that this doesn't work *_*_*_*_*_*_*_*_*
    It's very hard to implement multi-body measurement with 
                   simulators like qiskits'.
"""


if __name__ == "__main__":


    c = ls.Circuit(2)
    I = ls.PauliOperator.I
    X = ls.PauliOperator.X
    Y = ls.PauliOperator.Y
    Z = ls.PauliOperator.Z

    c.add_pauli_block(ls.Rotation.from_list([I,X], Fraction(1, 2)))
    c.add_pauli_block(ls.Rotation.from_list([X,I], Fraction(1, 2)))
    print(c.render_ascii())


    comp = ls.pauli_rotation_to_lattice_surgery_computation(c)
    webgui.lattice_view.render_to_file(comp.composer.getSlices(), "../index.html")


    sim_circ = qk.QuantumCircuit(qk.QuantumRegister(c.qubit_num))

    for slice_num, slice in enumerate(comp.composer.getSlices()):

        # Handle single qubit ops
        for qubit_idx, cell in enumerate(comp.iterate_over_qubit_patches()):
            patch = slice.getPatchOfCell(cell)
            if isinstance(patch.state, ls.ActiveState):
                activity = patch.state.activity
                if activity.activity_type == ls.ActivityType.Unitary:
                    if activity.op == ls.PauliOperator.X:
                        sim_circ.x(qubit_idx)

        sim_circ.snapshot("slice-"+str(slice_num))

    #sim_circ.measure()

    print(sim_circ.draw('text'))

    result = qk.execute(sim_circ, qk.Aer.get_backend('statevector_simulator')).result()
    print(result.get_snapshot('slice-1'))
    print(result.get_snapshot('slice-2'))


