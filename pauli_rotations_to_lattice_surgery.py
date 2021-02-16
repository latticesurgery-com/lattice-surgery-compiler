from circuit import *
from lattice_surgery_computation_composer import *
from typing import *
from patches import *
from collections import deque
from fractions import Fraction

class SinglePatchMeasurement:
    def __init__(self, cell_of_patch: Tuple[int,int], op: PauliOperator):
        self.cell_of_patch = cell_of_patch
        self.op = op


def pauli_rotation_to_lattice_surgery_computation(circuit : Circuit) -> LatticeSurgeryComputation:

    lsc = LatticeSurgeryComputationPreparedMagicStates(circuit.qubit_num, circuit.count_rotations_by(Fraction(1,8)))
    with lsc.timestep() as blank_slice: pass

    rotations_queue : Deque[Union[Rotation,SinglePatchMeasurement]] = deque(circuit.get_operations())

    while len(rotations_queue)>0:
        with lsc.timestep() as slice: #TODO be more clever about making slices to allow concurrent operations
            current_op = rotations_queue.popleft()

            rotations_composer = RotationsToLatticeSurgeryComputationHelpers(lsc, slice)

            if isinstance(current_op,SinglePatchMeasurement):
                slice.measurePatch(current_op.cell_of_patch, current_op.op)

            elif isinstance(current_op,Rotation):
                if current_op.rotation_amount == Fraction(1,2):
                    rotations_composer.pi_over_two(current_op.get_ops_map())
                elif current_op.rotation_amount == Fraction(1,4):
                    corrections = rotations_composer.add_pi_over_four(current_op.get_ops_map())
                    rotations_queue.extendleft(corrections)
                elif current_op.rotation_amount == Fraction(-1,4):
                    corrections = rotations_composer.add_pi_over_four(current_op.get_ops_map())
                    corrections = invert_correction_apply_condition(corrections)
                    rotations_queue.extendleft(corrections)
                elif current_op.rotation_amount == Fraction(1,8):
                    corrections = rotations_composer.add_pi_over_eight(current_op.get_ops_map())
                    rotations_queue.extendleft(corrections)
                elif current_op.rotation_amount == Fraction(-1,8):
                    corrections = rotations_composer.add_pi_over_eight(current_op.get_ops_map())
                    corrections = invert_correction_apply_condition(corrections)
                    rotations_queue.extendleft(corrections)
                else:
                    raise Exception("Unsupported pauli rotation angle")
            else:
                assert False


    return lsc


class RotationsToLatticeSurgeryComputationHelpers:

    def __init__(self, computation :LatticeSurgeryComputation, slice : LatticeSurgeryComputationComposer):
        self.computation = computation
        self.slice = slice

    def pi_over_two(self, ops_map :  Dict[int, PauliOperator]) -> None:
        for qubit_id, op in ops_map.items():
            patch = self.computation.get_cell_for_qubit_idx(qubit_id)
            self.slice.applyPauliProductOperator(patch, op)

    def add_pi_over_four(self, ops_map :  Dict[int, PauliOperator]) -> List[Union[Rotation,SinglePatchMeasurement]]:
        """Returns the correction terms. See Figure 11 of Litinski's GoSC"""

        pauli_op_map: Dict[Tuple[int, int], patches.PauliOperator] = dict()

        # First we need to initialize an ancilla 0 state
        zero_ancilla = self.slice.addSquareAncilla(SymbolicState("|Y>"))
        if zero_ancilla is None: raise Exception("Could not allocate ancilla Zero State for pi/4 rotation")

        pauli_op_map[zero_ancilla] = PauliOperator.Z

        corrective_rotation = Rotation(self.computation.num_qubits, Fraction(1,2))

        for qubit_idx, op in ops_map.items():
            patch = self.computation.get_cell_for_qubit_idx(qubit_idx)
            pauli_op_map[patch] = op
            corrective_rotation.change_single_op(qubit_idx, op)


        self.slice.multiBodyMeasurePatches(pauli_op_map)

        return [SinglePatchMeasurement(zero_ancilla,PauliOperator.X),corrective_rotation]

    def add_pi_over_eight(self, ops_map :  Dict[int, PauliOperator]) -> List[Union[Rotation,SinglePatchMeasurement]]:
        """Returns the correction terms. See Figure 11 of Litinski's GoSC"""

        pauli_op_map: Dict[Tuple[int, int], patches.PauliOperator] = dict()

        magic_state_cell = self.slice.findMagicState()
        if magic_state_cell is None: raise Exception("Could not find Magic State for pi/8 rotation")

        pauli_op_map[magic_state_cell] = PauliOperator.Z

        first_corrective_rotation = Rotation(self.computation.num_qubits, Fraction(1,4))
        second_corrective_rotation = Rotation(self.computation.num_qubits, Fraction(1,2))

        for qubit_idx, op in ops_map.items():
            patch = self.computation.get_cell_for_qubit_idx(qubit_idx)
            pauli_op_map[patch] = op
            first_corrective_rotation.change_single_op(qubit_idx, op)
            second_corrective_rotation.change_single_op(qubit_idx, op)


        self.slice.multiBodyMeasurePatches(pauli_op_map)

        return [first_corrective_rotation, SinglePatchMeasurement(magic_state_cell, PauliOperator.X), second_corrective_rotation]


def invert_correction_apply_condition(corrections:List[Union[Rotation,SinglePatchMeasurement]])\
    -> List[Union[Rotation,SinglePatchMeasurement]]:
    # TODO
    return corrections

