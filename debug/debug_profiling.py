import os
from typing import List, Optional, Tuple

import cProfile, pstats, io

import qiskit.visualization as qkvis
from lsqecc.lattice_array import sparse_lattice_to_array
from qiskit import circuit as qkcirc

import lsqecc.logical_lattice_ops.logical_lattice_ops as llops
import lsqecc.patches.lattice_surgery_computation_composer as lscc
import lsqecc.pauli_rotations.segmented_qasm_parser as segmented_qasm_parser
import lsqecc.simulation.logical_patch_state_simulation as lssim

SAMPLE_CIRCUIT= """
OPENQASM 2.0;
include "qelib1.inc";

qreg q[2];

h q[0];
t q[0];
h q[0];
cx q[0],q[1];

h q[0];
t q[0];
h q[0];
cx q[0],q[1];

h q[0];
t q[0];
h q[0];
cx q[0],q[1];
"""

PROFILE_LINES_TO_PRINT=20

import lsqecc.pipeline.lattice_surgery_compilation_pipeline as lscp

if __name__ == "__main__":
    res = lscp.compile_str_with_profile(SAMPLE_CIRCUIT,simulation_type=lscp.lssim.SimulatorType.LAZY_TENSOR,apply_litinski_transform=False)
    print(res.profiling_text)


