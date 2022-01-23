import uuid
from fractions import Fraction

import pytest

import lsqecc.simulation.qubit_state as qs
from lsqecc.logical_lattice_ops.logical_lattice_ops import (
    AncillaQubitPatchInitialization,
    LogicalLatticeComputation,
    LogicalLatticeOperation,
    LogicalPauli,
    MagicStateRequest,
    MultiBodyMeasurement,
    SinglePatchMeasurement,
)
from lsqecc.pauli_rotations import Measurement, PauliOperator, segmented_qasm_parser
from lsqecc.pauli_rotations.circuit import PauliOpCircuit
from lsqecc.pauli_rotations.rotation import PauliRotation

I = PauliOperator.I  # noqa: E741
X = PauliOperator.X
Y = PauliOperator.Y
Z = PauliOperator.Z


class TestLogicalLatticeOperation:
    def test_get_operating_patches(self):
        op = LogicalLatticeOperation()
        with pytest.raises(NotImplementedError):
            op.get_operating_patches()


class TestSinglePatchMeasurement:
    def test_get_operating_patches(self):
        m = Measurement.from_list([X])
        qubit_id = uuid.uuid4()
        patch_op = SinglePatchMeasurement(qubit_id, m.get_op(0))
        assert patch_op.get_operating_patches() == [qubit_id]


class TestMultiBodyMeasurement:
    def test_get_operating_patches(self):
        multi_measurement = Measurement.from_list([X, Z, X, Z])
        patch_operator_map = dict([(uuid.uuid4(), op) for op in multi_measurement.ops_list])
        multi_body_patch_op = MultiBodyMeasurement(patch_operator_map)
        assert multi_body_patch_op.get_operating_patches() == list(patch_operator_map.keys())


class TestAncillaQubitPatchInitialization:
    def test_get_operating_patches(self):
        ancilla_uuid = uuid.uuid4()
        state = qs.DefaultSymbolicStates.YPosEigenState
        ancilla_patch = AncillaQubitPatchInitialization(state, ancilla_uuid)
        assert ancilla_patch.get_operating_patches() == [ancilla_uuid]


class TestLogicalPauli:
    def test_get_operating_patches(self):
        qubit_id = uuid.uuid4()
        matrix = X
        logical_pauli = LogicalPauli(qubit_id, matrix)
        assert logical_pauli.get_operating_patches() == [qubit_id]


class TestMagicStateRequest:
    def test_get_operating_patches(self):
        qubit_id = uuid.uuid4()
        magic_state = MagicStateRequest(qubit_id)
        assert magic_state.get_operating_patches() == [qubit_id]


def generate_tests_num_logical_qubits():
    c1 = PauliOpCircuit(2)
    c1.add_pauli_block(PauliRotation.from_list([X, Z], Fraction(1, 4)))
    c1.add_pauli_block(PauliRotation.from_list([Z, X], Fraction(1, 8)))

    c2 = PauliOpCircuit(4)
    c2.add_pauli_block(PauliRotation.from_list([X, I, X, Z], Fraction(1, 2)))
    c2.add_pauli_block(Measurement.from_list([Z, Z, I, Z]))

    c3 = PauliOpCircuit(1)
    c3.add_pauli_block(PauliRotation.from_list([X], Fraction(-1, 4)))
    c3.add_pauli_block(Measurement.from_list([Z]))
    return [(c1, 2), (c2, 4), (c3, 1)]


def generate_tests_count_magic_states():
    with open("assets/demo_circuits/nontrivial_state.qasm") as input_file:
        c1 = segmented_qasm_parser.parse_str(input_file.read())

    with open("assets/demo_circuits/bell_pair.qasm") as input_file:
        c2 = segmented_qasm_parser.parse_str(input_file.read())

    return [(c1, 1), (c2, 0)]


def generate_tests_circuit_to_single_patch_measurement():
    m1 = Measurement.from_list([X], isNegative=False)
    m2 = Measurement.from_list([I, Z], isNegative=False)

    c1 = PauliOpCircuit(1)
    c1.add_pauli_block(m1)

    c2 = PauliOpCircuit(2)
    c2.add_pauli_block(m2)

    return [(c1, m1), (c2, m2)]


def generate_tests_circuit_to_multi_body_measurements():
    m1 = Measurement.from_list([Z, X], isNegative=True)
    m2 = Measurement.from_list([Z, I, I, Z], isNegative=False)

    c1 = PauliOpCircuit(2)
    c1.add_pauli_block(m1)

    c2 = PauliOpCircuit(4)
    c2.add_pauli_block(m2)

    return [(c1, m1), (c2, m2)]


class TestLogicalLatticeComputation:
    @pytest.mark.parametrize("input, expected", generate_tests_num_logical_qubits())
    def test_num_logical_qubits(self, input, expected):
        logical_computation = LogicalLatticeComputation(input)
        assert logical_computation.num_logical_qubits() == expected

    @pytest.mark.parametrize("input, expected", generate_tests_count_magic_states())
    def test_count_magic_states(self, input, expected):
        logical_computation = LogicalLatticeComputation(input)
        assert logical_computation.count_magic_states() == expected

    @pytest.mark.parametrize(
        "circuit, measurement", generate_tests_circuit_to_single_patch_measurement()
    )
    def test_circuit_to_single_patch_measurement(
        self, circuit: PauliOpCircuit, measurement: Measurement
    ):
        logical_comp = LogicalLatticeComputation(circuit)
        patch_measurement = logical_comp.circuit_to_patch_measurement(logical_comp.circuit.ops[0])

        assert isinstance(patch_measurement, SinglePatchMeasurement)
        assert [patch_measurement.op] == list(measurement.get_ops_map().values())

    @pytest.mark.parametrize(
        "circuit, measurement", generate_tests_circuit_to_multi_body_measurements()
    )
    def test_circuit_to_multi_body_measurement(
        self, circuit: PauliOpCircuit, measurement: Measurement
    ):
        logical_comp = LogicalLatticeComputation(circuit)
        patch_measurement = logical_comp.circuit_to_patch_measurement(logical_comp.circuit.ops[0])
        assert isinstance(patch_measurement, MultiBodyMeasurement)
        assert list(patch_measurement.patch_pauli_operator_map.values()) == list(
            measurement.get_ops_map().values()
        )

    def test_circuit_to_patch_measurement_type_error(self):
        circuit = PauliOpCircuit(1)
        circuit.add_pauli_block(PauliRotation.from_list([X], Fraction(1, 4)))
        logical_comp = LogicalLatticeComputation(circuit)
        with pytest.raises(TypeError):
            logical_comp.circuit_to_patch_measurement(logical_comp.circuit.ops[0])

    def test__load_circuit(self):
        # TODO: Determine example circuits, dependent on RotationsComposer
        pass
