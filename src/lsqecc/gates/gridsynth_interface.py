import subprocess
from fractions import Fraction
from typing import Dict, Optional, Tuple

from lsqecc.gates.pi_over_2_to_the_n_rz_gate_approximations import (
    PRECISION,
    get_pi_over_2_to_the_n_rz_gate_neg,
    get_pi_over_2_to_the_n_rz_gate_pos,
)
from lsqecc.utils import is_power_of_two

_DEFAULT_GRIDSYNTH_EXECUTABLE = "/home/varunseshadri/.cabal/bin/gridsynth"


def to_standard_interval(f: Fraction) -> Fraction:
    return Fraction(f.numerator % 2 * f.denominator, f.denominator)


class _GridSynthCachedInterface:

    # save (log10(precision), pi_fraction) : gridsynth sequence
    cached_calls: Dict[Tuple[int, Fraction], str] = {}

    def __init__(self, gridsynth_executable: Optional[str] = _DEFAULT_GRIDSYNTH_EXECUTABLE):
        self.gridsynth_executable = gridsynth_executable
        self._populate_with_cache()

    def call_gridsynth(self, precision: int, pi_fraction: Fraction) -> str:
        if self.gridsynth_executable is None:
            raise Exception("Gridsynth not available")

        pi_fraction = to_standard_interval(pi_fraction)

        phase_gate_angle = f"{pi_fraction.numerator}*pi/{pi_fraction.denominator}"

        command = f"{self.gridsynth_executable} {phase_gate_angle} -d {precision}"
        command_output = subprocess.check_output(command, shell=True).decode("utf-8")
        command_output = command_output[:-1]  # Drop the trailing newline

        sequence = command_output.replace("W", "")  # drop the global phase information
        sequence = sequence[::-1]  # reverse to go from operator to circuit form

        # Gridsynth's decomposition for these case is very long
        if pi_fraction == Fraction(1, 2):
            sequence = "T"
        elif pi_fraction == Fraction(-1, 2):
            sequence = "SSST"

        return sequence

    def get_approximation(self, precision: int, pi_fraction: Fraction) -> str:
        if not is_power_of_two(pi_fraction.denominator):
            raise Exception("Denominator must be power of two")

        existing_value = self.cached_calls.get((precision, pi_fraction))
        if existing_value is not None:
            return existing_value
        else:
            v = self.call_gridsynth(precision, pi_fraction)
            self.cached_calls[(precision, pi_fraction)] = v
            return v

    def _populate_with_cache(self):
        for denominator_exponent, approx_str in enumerate(get_pi_over_2_to_the_n_rz_gate_pos):
            self.cached_calls[(PRECISION, Fraction(1, 2**denominator_exponent))] = approx_str
        for denominator_exponent, approx_str in enumerate(get_pi_over_2_to_the_n_rz_gate_neg):
            self.cached_calls[(PRECISION, Fraction(-1, 2**denominator_exponent))] = approx_str


class GridsynthInterface:
    _instance = _GridSynthCachedInterface(_DEFAULT_GRIDSYNTH_EXECUTABLE)

    @staticmethod
    def get_approximation(precision: int, pi_fraction: Fraction) -> str:
        return GridsynthInterface._instance.get_approximation(precision, pi_fraction)
