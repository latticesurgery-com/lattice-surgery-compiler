


from typing import List, Optional, Tuple

import qiskit.visualization as qkvis
from qiskit import circuit as qkcirc

import lsqecc.lattice_array.visual_array_cell as vac
import lsqecc.logical_lattice_ops.logical_lattice_ops as llops
import lsqecc.patches.lattice_surgery_computation_composer as lscc
import lsqecc.pauli_rotations.segmented_qasm_parser as segmented_qasm_parser
from  lsqecc.pauli_rotations import PauliOpCircuit, PauliRotation, Measurement, PauliOperator
import lsqecc.simulation.logical_patch_state_simulation as lssim
from lsqecc.lattice_array import sparse_lattice_to_array
from lsqecc.resource_estimation.resource_estimator import estimate_resources

from fractions import Fraction

import cprofile_pretty_printer

GUISlice = List[List[Optional[vac.VisualArrayCell]]]  # 2D array of cells


X=PauliOperator.X
Z=PauliOperator.Z

if __name__=="__main__":
    c = PauliOpCircuit.from_list([
        PauliRotation.from_list([Z],Fraction(1,4)),
        PauliRotation.from_list([X],Fraction(1,4)),
        PauliRotation.from_list([Z],Fraction(1,4)),
        PauliRotation.from_list([X],Fraction(1,4)),
        PauliRotation.from_list([Z],Fraction(1,8)),
    ])

    logical_computation = llops.LogicalLatticeComputation(c)
    print("Made logical computation")

    print("Making slices:")
    lsc = lscc.LatticeSurgeryComputation.make_computation(
        logical_computation, lscc.LayoutType.SimplePreDistilledStates, simulation_type=lssim.SimulatorType.NOOP
    )