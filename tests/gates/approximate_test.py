import math
from fractions import Fraction

import pytest

from lsqecc.gates import gates
from lsqecc.gates.approximate import approximate_rz, from_gate_string
from lsqecc.gates.compress_rotation_approximations import partition_gate_sequence
from lsqecc.gates.pi_over_2_to_the_n_rz_gate_approximations import (
    get_pi_over_2_to_the_n_rz_gate,
)
from lsqecc.pauli_rotations.rotation import PauliOperator


@pytest.mark.parametrize(
    "phase",
    [
        # These 3 values check that we half the angle
        Fraction(1, 1),
        Fraction(1, 2),
        Fraction(1, 4),
        # Some bigger approximations that need gridsynth
        Fraction(1, 8),
        Fraction(1, 16),
        Fraction(1, 2**50),
        Fraction(1, 2**100),
        Fraction(1, 2**134),  # current max
    ],
)
def test_approximate_rz(phase: Fraction, snapshot):
    snapshot.assert_match(
        repr(approximate_rz(gates.RZ(target_qubit=1, phase=phase), compress_rotations=False)),
        "gates.txt",
    )


@pytest.mark.parametrize(
    "phase",
    [
        # These 3 values check that we half the angle
        Fraction(1, 1),
        Fraction(1, 2),
        Fraction(1, 4),
        # Some bigger approximations that need gridsynth
        Fraction(1, 8),
        Fraction(1, 16),
        Fraction(1, 2**50),
        Fraction(1, 2**100),
        Fraction(1, 2**134),  # current max
    ],
)
def test_approximate_rz_with_compression(phase: Fraction, snapshot):
    snapshot.assert_match(
        repr(approximate_rz(gates.RZ(target_qubit=1, phase=phase), compress_rotations=True)),
        "gates.txt",
    )


class TestRotationCompression:
    @pytest.mark.parametrize(
        "phase, expected_gate_sequence",
        [
            (Fraction(1, 1), [gates.S(target_qubit=1), gates.S(target_qubit=1)]),
            (Fraction(1, 2), [gates.S(target_qubit=1)]),
            (Fraction(1, 4), [gates.T(target_qubit=1)]),
        ],
    )
    def test_approximate_rz_no_compression_basic_angles(self, phase, expected_gate_sequence):
        compressed_gates = approximate_rz(
            gates.RZ(target_qubit=1, phase=phase), compress_rotations=False
        )
        partitions = get_pi_over_2_to_the_n_rz_gate[int(math.log2(phase.denominator))]

        assert len(compressed_gates) == len(partitions)
        assert compressed_gates == expected_gate_sequence

    @pytest.mark.parametrize(
        "phase, expected_gate_sequence",
        [
            (
                Fraction(1, 1),
                [gates.PauliRotations(target_qubit=1, phase=Fraction(1, 1), axis=PauliOperator.Z)],
            ),
            (Fraction(1, 2), [gates.S(target_qubit=1)]),
            (Fraction(1, 4), [gates.T(target_qubit=1)]),
        ],
    )
    def test_approximate_rz_with_compression_basic_angles(
        self, phase: Fraction, expected_gate_sequence
    ):
        compressed_gates = approximate_rz(
            gates.RZ(target_qubit=1, phase=phase), compress_rotations=True
        )
        partitions = partition_gate_sequence(
            get_pi_over_2_to_the_n_rz_gate[int(math.log2(phase.denominator))]
        )

        assert len(compressed_gates) == len(partitions)
        assert compressed_gates == expected_gate_sequence

    @pytest.mark.parametrize(
        "phase",
        [
            # These 3 values check that we half the angle
            Fraction(1, 1),
            Fraction(1, 2),
            Fraction(1, 4),
            # Some bigger approximations that need gridsynth
            Fraction(1, 8),
            Fraction(1, 16),
            Fraction(1, 2**50),
            Fraction(1, 2**100),
            Fraction(1, 2**134),  # current max
        ],
    )
    def test_approximate_rz_compression_non_snapshot(self, phase: Fraction):
        compressed_gates = approximate_rz(
            gates.RZ(target_qubit=1, phase=phase), compress_rotations=True
        )
        partitions = partition_gate_sequence(
            get_pi_over_2_to_the_n_rz_gate[int(math.log2(phase.denominator))]
        )

        assert len(compressed_gates) == len(partitions)

    @pytest.mark.parametrize(
        "gate_string, expected_gate",
        [
            (
                "HSSSH",
                gates.PauliRotations(target_qubit=1, phase=Fraction(3, 2), axis=PauliOperator.X),
            ),
            (
                "SSS",
                gates.PauliRotations(target_qubit=1, phase=Fraction(3, 2), axis=PauliOperator.Z),
            ),
            (
                "HTTTTH",
                gates.PauliRotations(target_qubit=1, phase=Fraction(1, 1), axis=PauliOperator.X),
            ),
            (
                "TTTT",
                gates.PauliRotations(target_qubit=1, phase=Fraction(1, 1), axis=PauliOperator.Z),
            ),
            (
                "HTSTSH",
                gates.PauliRotations(target_qubit=1, phase=Fraction(3, 2), axis=PauliOperator.X),
            ),
            (
                "STST",
                gates.PauliRotations(target_qubit=1, phase=Fraction(3, 2), axis=PauliOperator.Z),
            ),
        ],
    )
    def test_from_gate_string(self, gate_string: str, expected_gate: "gates.PauliRotations"):
        assert (
            from_gate_string(target_qubit=expected_gate.target_qubit, gate_string=gate_string)
            == expected_gate
        )
