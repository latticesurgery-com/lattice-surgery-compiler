from circuit import *
from lattice_surgery_computation_composer import *
from typing import *
from patches import *
from collections import deque
from fractions import Fraction
from logical_lattice_ops import *



def circuit_to_patch_measurement( lsc: LatticeSurgeryComputation, m: Measurement) \
        -> Union[SinglePatchMeasurement,MultiBodyMeasurement]:
    ret : Dict[Tuple[int, int], PauliOperator] = dict()
    for qubit_idx in range(m.qubit_num):
        if m.get_op(qubit_idx)!=PauliOperator.I:
            ret[lsc.get_cell_for_qubit_idx(qubit_idx)] = m.get_op(qubit_idx)

    if len(ret) == 1:
        return SinglePatchMeasurement(next(iter(ret)),ret[next(iter(ret))])
    return  MultiBodyMeasurement(ret)


def to_lattice_operation(op:PauliProductOperation) -> LogicalLatticeOperation:
    if isinstance(op, Rotation): return op
    if isinstance(op, Measurement): return circuit_to_patch_measurement(op)
    raise Exception("Unsupported PauliProductOperation "+repr(op))



def pauli_rotation_to_logical_lattice_operations(circuit : Circuit) -> List[LogicalLatticeOperation]:

    operations_queue : Deque[Union[Rotation,LogicalLatticeOperation]] \
        = deque(map(to_lattice_operation, circuit.get_operations()))

    logical_ops : List[LogicalLatticeOperation] = list()

    while len(operations_queue)>0:
        current_op = operations_queue.popleft()

        rotations_composer = RotationsToLatticeSurgeryComputationHelpers(lsc)

        if isinstance(current_op,Rotation):
            # Rotations need to be broken down further
            operations_queue.extendleft(reversed(rotations_composer.expand_rotation(current_op)))
        else:
            # Other operations translate directly to lattice lattice surgery
            logical_ops.append(current_op)

    return logical_ops




def pauli_rotation_to_lattice_surgery_computation(circuit : Circuit) -> LatticeSurgeryComputation:
    lsc = LatticeSurgeryComputationPreparedMagicStates(circuit.qubit_num,
                                                       circuit.count_rotations_by(Fraction(1, 8)))

    logical_ops = pauli_rotation_to_logical_lattice_operations(circuit)
    lsc.add_logical_lattice_operations(logical_ops)

    return lsc


class RotationsToLatticeSurgeryComputationHelpers:

    def __init__(self, computation :LatticeSurgeryComputation):
        self.computation = computation

    def expand_rotation(self, r: Rotation) -> List[LogicalLatticeOperation]:
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

    def pi_over_two(self, ops_map :  Dict[int, PauliOperator]) -> [LogicalLatticeOperation]:
        paulis = IndividualPauliOperators(dict())
        for qubit_id, op in ops_map.items():
            cell = self.computation.get_cell_for_qubit_idx(qubit_id)
            paulis.patch_pauli_operator_map[cell] = op
        return [paulis]

    def add_pi_over_four(self, ops_map: Dict[int, PauliOperator], invert_correction:bool) -> List[LogicalLatticeOperation]:
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

    def add_pi_over_eight(self, ops_map :  Dict[int, PauliOperator], invert_correction:bool) -> List[LogicalLatticeOperation]:
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

