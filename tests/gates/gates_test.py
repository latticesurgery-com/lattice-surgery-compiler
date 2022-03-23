from fractions import Fraction

import pytest

from lsqecc.gates import approximate, gates
from lsqecc.pauli_rotations.rotation import PauliOperator


class TestRZ:
    @pytest.mark.parametrize(
        "rz_gate, decomposition",
        [
            (gates.RZ(target_qubit=0, phase=Fraction(1, 1)), [gates.Z(target_qubit=0)]),
            (gates.RZ(target_qubit=0, phase=Fraction(1, 2)), [gates.S(target_qubit=0)]),
            (gates.RZ(target_qubit=0, phase=Fraction(1, 4)), [gates.T(target_qubit=0)]),
            (
                gates.RZ(target_qubit=0, phase=Fraction(1, 16)),
                approximate.approximate_rz(gates.RZ(target_qubit=0, phase=Fraction(1, 16))),
            ),
        ],
    )
    def test_to_clifford_plus_t(self, rz_gate, decomposition):
        assert rz_gate.to_clifford_plus_t() == decomposition


class TestCRZ:
    def test_to_clifford_plus_t(self):  # ):
        crz_gate = gates.CRZ(control_qubit=0, target_qubit=1, phase=Fraction(1, 2))

        decomposition = []
        decomposition.extend(gates.RZ(target_qubit=0, phase=Fraction(1, 4)).to_clifford_plus_t())
        decomposition.extend(gates.RZ(target_qubit=1, phase=Fraction(1, 4)).to_clifford_plus_t())
        decomposition.append(gates.CNOT(control_qubit=0, target_qubit=1))
        decomposition.extend(gates.RZ(target_qubit=1, phase=Fraction(1, 4)).to_clifford_plus_t())
        decomposition.append(gates.CNOT(control_qubit=0, target_qubit=1))

        assert crz_gate.to_clifford_plus_t() == decomposition


class TestPauliRotations:
    @pytest.mark.parametrize(
        "rot_gate, decomposition",
        [
            (
                gates.PauliRotations(target_qubit=0, phase=Fraction(1, 1), axis=PauliOperator.Z),
                [gates.Z(target_qubit=0)],
            ),
            (
                gates.PauliRotations(target_qubit=0, phase=Fraction(1, 2), axis=PauliOperator.Z),
                [gates.S(target_qubit=0)],
            ),
            (
                gates.PauliRotations(target_qubit=0, phase=Fraction(1, 4), axis=PauliOperator.Z),
                [gates.T(target_qubit=0)],
            ),
            (
                gates.PauliRotations(target_qubit=0, phase=Fraction(1, 16), axis=PauliOperator.Z),
                approximate.approximate_rz(gates.RZ(target_qubit=0, phase=Fraction(1, 16))),
            ),
        ],
    )
    def test_to_clifford_plus_t_z_axis(self, rot_gate, decomposition):
        assert rot_gate.to_clifford_plus_t(compress_rotations=False) == decomposition

    @pytest.mark.parametrize(
        "rot_gate, decomposition",
        [
            (
                gates.PauliRotations(target_qubit=0, phase=Fraction(1, 1), axis=PauliOperator.X),
                [gates.X(target_qubit=0)],
            ),
            (
                gates.PauliRotations(target_qubit=0, phase=Fraction(1, 2), axis=PauliOperator.X),
                [gates.H(target_qubit=0), gates.S(target_qubit=0), gates.H(target_qubit=0)],
            ),
            (
                gates.PauliRotations(target_qubit=0, phase=Fraction(1, 4), axis=PauliOperator.X),
                [gates.H(target_qubit=0), gates.T(target_qubit=0), gates.H(target_qubit=0)],
            ),
            (
                gates.PauliRotations(target_qubit=0, phase=Fraction(1, 16), axis=PauliOperator.X),
                [gates.H(target_qubit=0)]
                + approximate.approximate_rz(gates.RZ(target_qubit=0, phase=Fraction(1, 16)))
                + [gates.H(target_qubit=0)],
            ),
        ],
    )
    def test_to_clifford_plus_t_x_axis(self, rot_gate, decomposition):
        assert rot_gate.to_clifford_plus_t(compress_rotations=False) == decomposition
