
import qiskit.aqua.operators as qk
from qiskit.aqua.operators import H,I,CX

import pauli_rotations_to_lattice_surgery as ls

import webgui.lattice_view
from fractions import Fraction


def circuit_add_op_to_qubit(circ : qk.CircuitOp, op: qk.PrimitiveOp, idx: int) -> qk.CircuitOp:
    new_op = (qk.I ^ idx ) ^ op ^ (qk.I ^ (circ.num_qubits - idx - 1))
    return new_op @ circ


if __name__ == "__main__":

    print(qk.X @ qk.Y @ qk.Z)
    print(qk.Zero)
    print((qk.H @ qk.Zero).eval())
    print("============")
    a_circ = (((H ^ 5) @ ((CX ^ 2) ^ I) @ (I ^ (CX ^ 2))) ** 2)
    print(type(a_circ))
    print(a_circ.eval(qk.Zero^5))

    print("Compile single pauli ops")

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

    sim_circ = qk.Zero^c.qubit_num

    for slice_num, slice in enumerate(comp.composer.getSlices()):

        # Handle single qubit ops
        for qubit_idx, cell in enumerate(comp.iterate_over_qubit_patches()):
            patch = slice.getPatchOfCell(cell)
            if isinstance(patch.state, ls.ActiveState):
                activity = patch.state.activity
                if activity.activity_type == ls.ActivityType.Unitary:
                    if activity.op == ls.PauliOperator.X:
                        sim_circ = circuit_add_op_to_qubit(sim_circ, qk.X, qubit_idx)


    # Do a multi-body measuremt
    # Part 3 of the operator flow tutorial + N&C measurement observable

    # Create an observable of the desired form
    op :  qk.primitive_ops.pauli_op.PauliOp = qk.X^qk.Z
    observable=qk.StateFn(op).adjoint()

    print("=== Observable ===")
    print(observable @ (qk.Zero^qk.Plus))

    print(sim_circ.eval())