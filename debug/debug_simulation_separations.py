from lattice_surgery_computation_composer import *
from logical_patch_state_simulation import qk
from webgui import lattice_view

if __name__ == "__main__":
    c = Circuit(4)
    I = PauliOperator.I
    X = PauliOperator.X
    Y = PauliOperator.Y
    Z = PauliOperator.Z

    c.add_pauli_block(Rotation.from_list([X, I, I, I], Fraction(1, 2)))
    c.add_pauli_block(Rotation.from_list([I, X, I, I], Fraction(1, 2)))
    c.add_pauli_block(Rotation.from_list([I, I, X, I], Fraction(1, 2)))
    c.add_pauli_block(Rotation.from_list([I, I, I, X], Fraction(1, 2)))


    print(c.render_ascii())

    logical_comp = LogicalLatticeComputation(c)
    sim = PatchSimulator(logical_comp)

    def nice_print_dict_of_dict_states(ds):
        out = "{"
        for k,v in ds.items():
            out += "\n\t" + str(k) + " : "
            out +=        str(v.primitive) + " ,"
        return out + "}"


    for op in logical_comp.ops:
        print("Bf:",sim.logical_state)
        print("Op:",op)
        sim.apply_logical_operation(op)
        print("Af:", sim.logical_state)
        print("Seps:",nice_print_dict_of_dict_states(StateSeparator.get_separable_qubits(sim.logical_state)))

    lsc = LatticeSurgeryComputation.make_computation_with_simulation(logical_comp, LayoutType.SimplePreDistilledStates)
    lattice_view.render_to_file(lsc.composer.getSlices(), "index.html", template="/home/george/courses/CMPT415_498/code/lattice-surgery-compiler/webgui/templates/lattice_view.mak")
