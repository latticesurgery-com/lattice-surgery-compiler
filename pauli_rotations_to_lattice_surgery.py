from circuit import *
from lattice_surgery_computation_composer import *
from typing import *
from patches import *
from collections import deque
from fractions import Fraction




class SinglePatchMeasurement:
    def __init__(self, cell_of_patch: Union[Tuple[int,int],uuid.UUID], op: PauliOperator):
        self.cell_of_patch = cell_of_patch
        self.op = op

    def get_cell(self, lsc : LatticeSurgeryComputation):
        if isinstance(self.cell_of_patch,uuid.UUID):
            maybe_patch = lsc.composer.lattice().getPatchByUuid(self.cell_of_patch)
            if maybe_patch is None:
                raise Exception("Failed to find patch")
            return maybe_patch.getRepresentative()
        return self.cell_of_patch

class MultiBodyMeasurement:
    def __init__(self, patch_pauli_operator_map: Dict[Tuple[int, int], PauliOperator]):
        self.patch_pauli_operator_map = patch_pauli_operator_map
        self.ancilla_uuid = None
        self.ancilla_pauli_op = None

    def add_ancilla(self,ancilla_uuid:uuid.UUID, ancilla_pauli_op:PauliOperator):
        self.ancilla_uuid = ancilla_uuid
        self.ancilla_pauli_op = ancilla_pauli_op


def circuit_to_patch_measurement(self, lsc: LatticeSurgeryComputation, m: Measurement) \
        -> Union[SinglePatchMeasurement,MultiBodyMeasurement]:
    ret : Dict[Tuple[int, int], patches.PauliOperator] = dict()
    for qubit_idx in range(m.qubit_num):
        if m.get_op(qubit_idx)!=PauliOperator.I:
            ret[lsc.get_cell_for_qubit_idx(qubit_idx)] = m.get_op(qubit_idx)

    if len(ret) == 1:
        return SinglePatchMeasurement(next(iter(ret)),ret[next(iter(ret))])
    return  MultiBodyMeasurement(ret)


class AncillaQubitPatchInitialization:
    def __init__(self, patch_state: QubitState, patch_uuid : Optional[uuid.UUID] = None):
        self.patch_state = patch_state
        self.patch_uuid = patch_uuid


class IndividualPauliOperators:
    def __init__(self,patch_pauli_operator_map: Dict[Tuple[int, int], PauliOperator] ):
        self.patch_pauli_operator_map = patch_pauli_operator_map


LatticeOperation = Union[Rotation,
                         SinglePatchMeasurement,
                         MultiBodyMeasurement,
                         AncillaQubitPatchInitialization,
                         IndividualPauliOperators]


def to_lattice_operation(op:PauliProductOperation) -> LatticeOperation:
    if isinstance(op, Rotation): return op
    if isinstance(op, Measurement): return circuit_to_patch_measurement(op)
    raise Exception("Unsupported PauliProductOperation "+repr(op))


def is_composite(op:LatticeOperation) -> bool:
    """Decide if op needs to decomposed further or it has a direct translation to a lattice operation"""
    return isinstance(op,Rotation)

def pauli_rotation_to_lattice_surgery_computation(circuit : Circuit) -> LatticeSurgeryComputation:

    lsc = LatticeSurgeryComputationPreparedMagicStates(circuit.qubit_num, circuit.count_rotations_by(Fraction(1,8)))
    with lsc.timestep() as blank_slice: pass

    operations_queue : Deque[LatticeOperation] = deque(map(to_lattice_operation,circuit.get_operations()))

    while len(operations_queue)>0:
        current_op = operations_queue.popleft()

        rotations_composer = RotationsToLatticeSurgeryComputationHelpers(lsc)

        if isinstance(current_op,Rotation):
            # Rotations need to be broken down further
            operations_queue.extendleft(reversed(rotations_composer.expand_rotation(current_op)))
        else:
            # Other operations translate directly to lattice lattice suregery
            assert not is_composite(current_op)
            with lsc.timestep() as slice:
                if isinstance(current_op, SinglePatchMeasurement):
                    slice.measurePatch(current_op.get_cell(lsc), current_op.op)

                elif isinstance(current_op, AncillaQubitPatchInitialization):
                    maybe_cell_location = slice.addSquareAncilla(current_op.patch_state, current_op.patch_uuid)
                    if maybe_cell_location is None: raise Exception("Could not allocate ancilla")

                elif isinstance(current_op, IndividualPauliOperators):
                    for cell,op, in current_op.patch_pauli_operator_map.items():
                        slice.applyPauliProductOperator(cell,op)

                elif isinstance(current_op, MultiBodyMeasurement):
                    patch_pauli_operator_map = current_op.patch_pauli_operator_map # .copy()
                    if current_op.ancilla_pauli_op is not None:
                        cell = slice.lattice().getPatchByUuid(current_op.ancilla_uuid).getRepresentative()
                        patch_pauli_operator_map[cell] = current_op.ancilla_pauli_op
                    slice.multiBodyMeasurePatches(patch_pauli_operator_map)

                else:
                    raise Exception("Unsupported operation %s" % repr(current_op))
    return lsc


class RotationsToLatticeSurgeryComputationHelpers:

    def __init__(self, computation :LatticeSurgeryComputation):
        self.computation = computation

    def expand_rotation(self, r: Rotation) -> List[LatticeOperation]:
        if r.rotation_amount == Fraction(1, 2):
            return self.pi_over_two(r.get_ops_map())
        elif r.rotation_amount == Fraction(1, 4):
            return self.add_pi_over_four(r.get_ops_map(), False)
        elif r.rotation_amount == Fraction(-1, 4):
            return self.add_pi_over_four(r.get_ops_map(), True)
        elif r.rotation_amount == Fraction(1, 8):
            return self.add_pi_over_eight(r.get_ops_map(), False)
        elif r.rotation_amount == Fraction(-1, 8):
            return self.add_pi_over_eight(r.get_ops_map(), True)
        else:
            raise Exception("Unsupported pauli rotation angle pi*%d/%d"
                            % (r.rotation_amount.numerator, r.rotation_amount.denominator))

    def pi_over_two(self, ops_map :  Dict[int, PauliOperator]) -> [LatticeOperation]:
        paulis = IndividualPauliOperators(dict())
        for qubit_id, op in ops_map.items():
            cell = self.computation.get_cell_for_qubit_idx(qubit_id)
            paulis.patch_pauli_operator_map[cell] = op
        return [paulis]

    def add_pi_over_four(self, ops_map: Dict[int, PauliOperator], invert_correction:bool) -> List[LatticeOperation]:
        """See Figure 11 of Litinski's GoSC
        """
        ancilla_uuid = uuid.uuid4()
        ancilla_initialization = AncillaQubitPatchInitialization(SymbolicState("|Y>"), ancilla_uuid)

        multi_body_measurement = MultiBodyMeasurement({})
        multi_body_measurement.add_ancilla(ancilla_uuid,PauliOperator.Z)

        ancilla_measurement = SinglePatchMeasurement(ancilla_uuid, PauliOperator.X)

        corrective_rotation = Rotation(self.computation.num_qubits, Fraction(1,2))
        for qubit_idx, op in ops_map.items():
            cell = self.computation.get_cell_for_qubit_idx(qubit_idx)
            multi_body_measurement.patch_pauli_operator_map[cell] = op
            corrective_rotation.change_single_op(qubit_idx, op)

        return [ancilla_initialization,
                multi_body_measurement,
                ancilla_measurement,
                corrective_rotation]

    def add_pi_over_eight(self, ops_map :  Dict[int, PauliOperator], invert_correction:bool) -> List[LatticeOperation]:
        """Returns the correction terms. See Figure 11 of Litinski's GoSC"""

        magic_state_uuid = uuid.uuid4()
        magic_state_patch = self.computation.grab_magic_state(magic_state_uuid)
        if magic_state_patch is None: raise Exception("Could not find Magic State for pi/8 rotation")

        multi_body_measurement = MultiBodyMeasurement({})
        multi_body_measurement.add_ancilla(magic_state_uuid,PauliOperator.Z)

        first_corrective_rotation = Rotation(self.computation.num_qubits, Fraction(1,4))
        second_corrective_rotation = Rotation(self.computation.num_qubits, Fraction(1,2))

        for qubit_idx, op in ops_map.items():
            cell = self.computation.get_cell_for_qubit_idx(qubit_idx)
            multi_body_measurement.patch_pauli_operator_map[cell]=op
            first_corrective_rotation.change_single_op(qubit_idx, op)
            second_corrective_rotation.change_single_op(qubit_idx, op)

        return [multi_body_measurement,
                first_corrective_rotation,
                SinglePatchMeasurement(magic_state_uuid, PauliOperator.X),
                second_corrective_rotation]

