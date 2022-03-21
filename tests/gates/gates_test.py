from fractions import Fraction

import pytest

from lsqecc.gates import approximate, gates


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
