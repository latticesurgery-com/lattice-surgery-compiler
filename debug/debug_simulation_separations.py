from lattice_surgery_computation_composer import *
from logical_patch_state_simulation import qk
from webgui import lattice_view
from debug.util import *

if __name__ == "__main__":
    c = PauliOpCircuit(4)
    I = PauliOperator.I
    X = PauliOperator.X
    Y = PauliOperator.Y
    Z = PauliOperator.Z

    c.add_pauli_block(PauliRotation.from_list([X, I, I, I], Fraction(1, 2)))
    c.add_pauli_block(PauliRotation.from_list([I, X, I, I], Fraction(1, 2)))
    c.add_pauli_block(PauliRotation.from_list([I, I, X, I], Fraction(1, 2)))
    c.add_pauli_block(PauliRotation.from_list([I, I, I, X], Fraction(1, 2)))


    print(c.render_ascii())

    logical_comp = LogicalLatticeComputation(c)
    sim = PatchSimulator(logical_comp)

    for op in logical_comp.ops:
        print("Bf:",sim.logical_state)
        print("Op:",op)
        sim.apply_logical_operation(op)
        print("Af:", sim.logical_state)
        print("Seps:",nice_print_dict_of_dict_states(StateSeparator.get_separable_qubits(sim.logical_state)))
