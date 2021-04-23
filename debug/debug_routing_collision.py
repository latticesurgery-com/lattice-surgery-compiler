import lattice_surgery_computation_composer as ls
from fractions import Fraction

if __name__ == "__main__":

    I = ls.PauliOperator.I
    X = ls.PauliOperator.X
    Y = ls.PauliOperator.Y
    Z = ls.PauliOperator.Z

    c = ls.Circuit(4)
    c.add_pauli_block(ls.Rotation.from_list([X, I, I, I], Fraction(1, 2)))
    c.add_pauli_block(ls.Rotation.from_list([I, X, I, I], Fraction(1, 2)))
    c.add_pauli_block(ls.Rotation.from_list([I, I, X, I], Fraction(1, 2)))
    c.add_pauli_block(ls.Rotation.from_list([I, I, I, X], Fraction(1, 2)))
    c.add_pauli_block(ls.Rotation.from_list([Z, I, I, I], Fraction(1, 2)))

    print(c.render_ascii())

    logical_comp = ls.LogicalLatticeComputation(c)

    computation = ls.LatticeSurgeryComputation(logical_comp,ls.LayoutType.SimplePreDistilledStates)

    placed_measurements = 0
    try:
        with computation.timestep() as slice:
            slice.multiBodyMeasurePatches({(0,0):X,(4,0):X})
            placed_measurements += 1
            slice.multiBodyMeasurePatches({(2,0):X,(6,0):X})
            placed_measurements += 1
    except ls.AncillaRegionRoutingException:
        print("AncillaRegionRoutingException caught")
    else:
        assert False

    assert placed_measurements == 1