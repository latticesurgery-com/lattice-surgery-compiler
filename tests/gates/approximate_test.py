from fractions import Fraction

import pytest

from lsqecc.gates import gates
from lsqecc.gates.approximate import approximate_rz


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
        repr(approximate_rz(gates.RZ(target_qubit=1, phase=phase))),
        "gates.txt",
    )
