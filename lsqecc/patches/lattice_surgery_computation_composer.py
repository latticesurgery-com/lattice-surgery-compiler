import copy
import enum
import uuid
from typing import Dict, List, Optional, Tuple, cast

import lsqecc.logical_lattice_ops.logical_lattice_ops as llops
import lsqecc.patches.patches as patches
import lsqecc.simulation.logical_patch_state_simulation as lps
import lsqecc.simulation.qiskit_opflow_utils as qo_utils
import lsqecc.simulation.qubit_state as qs

from . import ancilla_region_routing as ancilla_region_routing


class LayoutType(enum.Enum):
    SimplePreDistilledStates = "Simple"


class LayoutInitializer:
    def get_layout(self) -> patches.Lattice:
        raise NotImplementedError

    def map_qubit_to_cell(self, qubit_n: int):
        raise NotImplementedError

    @staticmethod
    def singleSquarePatch(
        cell: Tuple[int, int],
        patch_type: patches.PatchType = patches.PatchType.Qubit,
        patch_state: qs.QubitState = qs.DefaultSymbolicStates.Zero,
    ):
        return patches.Patch(
            patch_type,
            patch_state,
            [cell],
            [
                patches.Edge(patches.EdgeType.Dashed, cell, patches.Orientation.Top),
                patches.Edge(patches.EdgeType.Dashed, cell, patches.Orientation.Bottom),
                patches.Edge(patches.EdgeType.Solid, cell, patches.Orientation.Left),
                patches.Edge(patches.EdgeType.Solid, cell, patches.Orientation.Right),
            ],
        )

    @staticmethod
    def rotatedSingleSquarePatch(
        cell: Tuple[int, int],
        patch_type: patches.PatchType = patches.PatchType.Qubit,
        patch_state: qs.QubitState = qs.DefaultSymbolicStates.Zero,
    ):
        return patches.Patch(
            patch_type,
            patch_state,
            [cell],
            [
                patches.Edge(patches.EdgeType.Solid, cell, patches.Orientation.Top),
                patches.Edge(patches.EdgeType.Solid, cell, patches.Orientation.Bottom),
                patches.Edge(patches.EdgeType.Dashed, cell, patches.Orientation.Left),
                patches.Edge(patches.EdgeType.Dashed, cell, patches.Orientation.Right),
            ],
        )

    @staticmethod
    def simpleRightFacingDistillery(top_left_corner: Tuple[int, int]) -> List[patches.Patch]:
        # Requires
        x, y = top_left_corner
        return [
            LayoutInitializer.singleSquarePatch(
                (x + 2, y), patches.PatchType.DistillationQubit, qs.DefaultSymbolicStates.Magic
            ),
            LayoutInitializer.singleSquarePatch(
                (x + 3, y), patches.PatchType.DistillationQubit, qs.DefaultSymbolicStates.Magic
            ),
            LayoutInitializer.singleSquarePatch(
                (x + 4, y + 1), patches.PatchType.DistillationQubit, qs.DefaultSymbolicStates.Plus
            ),
            LayoutInitializer.singleSquarePatch(
                (x + 3, y + 2), patches.PatchType.DistillationQubit, qs.DefaultSymbolicStates.Magic
            ),
            LayoutInitializer.singleSquarePatch(
                (x + 2, y + 2), patches.PatchType.DistillationQubit, qs.DefaultSymbolicStates.Magic
            ),
            patches.Patch(
                patches.PatchType.DistillationQubit,
                qs.DefaultSymbolicStates.Zero,
                [(x, y), (x, y + 1)],
                [
                    patches.Edge(patches.EdgeType.Solid, (x, y), patches.Orientation.Top),
                    patches.Edge(patches.EdgeType.Solid, (x, y), patches.Orientation.Left),
                    patches.Edge(patches.EdgeType.Dashed, (x, y), patches.Orientation.Right),
                    patches.Edge(patches.EdgeType.Dashed, (x, y + 1), patches.Orientation.Left),
                    patches.Edge(patches.EdgeType.Dashed, (x, y + 1), patches.Orientation.Bottom),
                    patches.Edge(patches.EdgeType.Solid, (x, y + 1), patches.Orientation.Right),
                ],
            ),
            patches.Patch(
                patches.PatchType.DistillationQubit,
                qs.DefaultSymbolicStates.Magic,
                [(x + 1, y), (x + 1, y + 1)],
                [
                    patches.Edge(patches.EdgeType.Dashed, (x + 1, y), patches.Orientation.Top),
                    patches.Edge(patches.EdgeType.Solid, (x + 1, y), patches.Orientation.Left),
                    patches.Edge(patches.EdgeType.Dashed, (x + 1, y), patches.Orientation.Right),
                    patches.Edge(patches.EdgeType.Solid, (x + 1, y + 1), patches.Orientation.Left),
                    patches.Edge(
                        patches.EdgeType.Dashed, (x + 1, y + 1), patches.Orientation.Bottom
                    ),
                    patches.Edge(patches.EdgeType.Solid, (x + 1, y + 1), patches.Orientation.Right),
                ],
            ),
        ]


class SimplePreDistilledStatesLayoutInitializer(LayoutInitializer):
    """a linear array of one spaced square patches with a linear array of magic states"""

    def __init__(self, num_logical_qubits: int):
        """a linear array of one spaced square patches with a distillery on one side"""
        # TODO distillery
        self.lattice = patches.Lattice(
            [
                LayoutInitializer.singleSquarePatch(self.map_qubit_to_cell(j))
                for j in range(num_logical_qubits)
            ],
            2,
            0,
        )

    def map_qubit_to_cell(self, qubit_n: int):
        return (qubit_n * 2, 0)

    def get_layout(self) -> patches.Lattice:
        return self.lattice

    def addRightDistillery(self):
        self.lattice.patches.append(
            LayoutInitializer.simpleRightFacingDistillery((self.lattice.getCols(), 0))
        )


class LatticeSurgeryComputation:
    def __init__(
        self, logical_computation: llops.LogicalLatticeComputation, layout_type: LayoutType
    ):
        """
        Layout arguments:
            - Simple: n_logical_qubits: int
        """
        self.logical_computation = logical_computation

        if layout_type != LayoutType.SimplePreDistilledStates:
            raise NotImplementedError("Layout Type not supported: " + layout_type.value)

        self.num_qubits = logical_computation.num_logical_qubits()

        self._initialize_layout(SimplePreDistilledStatesLayoutInitializer(self.num_qubits))

        self.ancilla_locations = [(j, 2) for j in range(self.num_qubits)]
        self.composer.lattice().min_cols = 2 * self.num_qubits
        self.composer.lattice().min_rows = 3

        self._init_simple_magic_state_array(self.logical_computation.count_magic_states())

    @staticmethod
    def make_computation_with_simulation(
        logical_computation: llops.LogicalLatticeComputation, layout_type: LayoutType
    ):
        comp = LatticeSurgeryComputation(logical_computation, layout_type)
        sim = lps.PatchSimulator(logical_computation)

        with comp.timestep() as blank_slice:
            cast(object, blank_slice)  # no-op

        for logical_op in comp.logical_computation.ops:
            if logical_op.does_evaluate():
                with comp.timestep() as slice:
                    slice.addLogicalOperation(logical_op)
                    sim.apply_logical_operation(logical_op)
                    slice.set_separable_states(sim)

        # Display the sates in the final slice
        comp.composer.set_separable_states(sim)

        return comp

    def _initialize_layout(self, initializer: LayoutInitializer):
        self.composer = LatticeSurgeryComputationComposer(self, initializer.get_layout())

        self.logical_qubits: List[Tuple[int, int]] = []
        for j, quuid in self.logical_computation.logical_qubit_uuid_map.items():
            cell = initializer.map_qubit_to_cell(j)
            self.logical_qubits.append(cell)
            self.composer.lattice().getPatchOfCell(cell).set_uuid(quuid)

    def _init_simple_magic_state_array(
        self, num_magic_states: int
    ):  # TODO move this to layout initializer
        start_magic_state_array = self.composer.lattice().getCols()
        self.magic_state_queue: List[Tuple[int, int]] = []
        for j in range(start_magic_state_array, start_magic_state_array + num_magic_states):
            magic_state_pos = (j + 1, 0)
            self.composer.lattice().patches.append(
                LayoutInitializer.rotatedSingleSquarePatch(
                    magic_state_pos,
                    patches.PatchType.DistillationQubit,
                    qs.DefaultSymbolicStates.Magic,
                )
            )
            self.magic_state_queue.append(magic_state_pos)

        self.composer.lattice().min_cols = self.composer.lattice().getCols()

    def is_ancilla_location(self, cell: Tuple[int, int]) -> bool:
        return cell in self.ancilla_locations

    def timestep(self):
        class LatticeSurgeryComputationSliceContextManager:
            def __init__(self, root_composer: LatticeSurgeryComputationComposer):
                self.root_composer = root_composer

            def __enter__(self):
                return self.root_composer

            def __exit__(self, exception_type, val, traceback):
                self.root_composer.newTimeSlice()
                self.root_composer.clearAncilla()
                self.root_composer.clearActiveStates()

                return False  # re reaises the exception

        return LatticeSurgeryComputationSliceContextManager(self.composer)

    def find_cell_by_qubit_uuid(self, qubit_uuid: uuid.UUID) -> Tuple[int, int]:
        return self.composer.lattice().getPatchByUuid(qubit_uuid).getRepresentative()

    def bind_magic_state(self, patch_uuid: uuid.UUID) -> Optional[patches.Patch]:
        if len(self.magic_state_queue) == 0:
            return None
        cell = self.magic_state_queue[0]
        del self.magic_state_queue[0]

        patch = self.composer.lattice().getPatchOfCell(cell)
        if patch is None:
            raise RuntimeError("Invalid cell in magic state queue " + str(cell))
        patch.set_uuid(patch_uuid)
        return patch


class LatticeSurgeryComputationComposer:
    def __init__(self, computation: LatticeSurgeryComputation, initial_layout: patches.Lattice):
        self.computation = computation
        self.qubit_patch_slices: List[patches.Lattice] = [initial_layout]  # initialize lattice here

    def lattice(self):
        return self.qubit_patch_slices[-1]

    def addPatch(self, patch: patches.Patch):
        self.lattice().patches.append(patch)

    def addSquareAncilla(
        self, patch_state: qs.QubitState, patch_uuid: Optional[uuid.UUID] = None
    ) -> Optional[Tuple[int, int]]:
        cell = self.getAncillaLocation()
        if cell is None:
            return None
        new_patch = LayoutInitializer.singleSquarePatch(cell, patches.PatchType.Qubit, patch_state)
        new_patch.set_uuid(patch_uuid)
        self.addPatch(new_patch)
        return cell

    def getAncillaLocation(self) -> Optional[Tuple[int, int]]:
        for ancilla in self.computation.ancilla_locations:
            if self.lattice().getPatchOfCell(ancilla) is None:
                return ancilla
        return None

    def measurePatch(self, cell_of_patch: Tuple[int, int], basis_matrix: patches.PauliOperator):
        if basis_matrix not in [patches.PauliOperator.X, patches.PauliOperator.Z]:
            raise Exception("Can't measure with basis matrix " + basis_matrix.value + " yet")
        for patch in self.qubit_patch_slices[-1].patches:
            if patch.getRepresentative() == cell_of_patch:
                assert patch.state is not None
                patch.state = patch.state.apply_measurement(basis_matrix)

    def newTimeSlice(self):
        self.qubit_patch_slices.append(copy.deepcopy(self.lattice()))
        self.qubit_patch_slices[-1].logical_ops = []

    def multiBodyMeasurePatches(
        self, cell_pauli_operator_map: Dict[Tuple[int, int], patches.PauliOperator]
    ):
        """Corresponds to a lattice surgery merge followed by a split."""

        for v in cell_pauli_operator_map.values():
            if v not in {patches.PauliOperator.X, patches.PauliOperator.Z}:
                raise Exception(
                    "Only X and Y operators are supported in multibody mesurement, got " + repr(v)
                )

        ancilla_region_routing.compute_ancilla_region_cells(
            self.qubit_patch_slices[-1], cell_pauli_operator_map
        )

    def applyPauliOperator(self, cell_of_patch: Tuple[int, int], operator: patches.PauliOperator):

        for patch in self.lattice().patches:
            if patch.getRepresentative() == cell_of_patch and patch.state is not None:
                patch.state = patch.state.compose_operator(operator)

    def clearAncilla(self):
        for j, patch in enumerate(self.qubit_patch_slices[-1].patches):
            for i, edge in enumerate(patch.edges):
                if edge.isStiched():
                    edge.border_type = edge.border_type.unstitched_type()
                    # After measurement we are not ready to track state yet
                    self.lattice().getPatchOfCell(
                        edge.cell
                    ).state = qs.DefaultSymbolicStates.UnknownState

        def is_not_ancilla(patch):
            return patch.patch_type != patches.PatchType.Ancilla

        self.qubit_patch_slices[-1].patches = list(filter(is_not_ancilla, self.lattice().patches))

    def clearActiveStates(self):
        # Make measured patches disappear
        def patch_stays(patch: patches.Patch) -> bool:
            if (
                patch.state is not None
                and isinstance(patch.state, qs.ActiveState)
                and patch.state.activity.activity_type == qs.ActivityType.Measurement
                and self.computation.is_ancilla_location(patch.getRepresentative())
            ):
                return False
            return True

        self.lattice().patches = list(filter(patch_stays, self.lattice().patches))

        # Clear other activity
        for patch in self.lattice().patches:
            if patch.state is not None and isinstance(patch.state, qs.ActiveState):
                patch.state = patch.state.next

    def clearLattice(self):
        self.qubit_patch_slices[-1].clear()

    def rotateSquarePatch(self, patch_idx: int):
        # assumes: The patch is square, there is room to rotate it
        # TODO make multiple rotations possible at the same time
        pass

    # TODO maybe slices should belong to the computation
    def getSlices(self) -> List[patches.Lattice]:
        return self.qubit_patch_slices

    def get_patch_representative(self, quuid: uuid.UUID) -> Tuple[int, int]:
        return self.get_patch(quuid).getRepresentative()

    def get_patch(self, quuid: uuid.UUID) -> patches.Patch:
        p = self.lattice().getPatchByUuid(quuid)
        assert p is not None
        return p

    def addLogicalOperation(self, current_op: llops.LogicalLatticeOperation):
        self.lattice().logical_ops.append(current_op)

        if isinstance(current_op, llops.SinglePatchMeasurement):
            self.measurePatch(self.get_patch_representative(current_op.qubit_uuid), current_op.op)

        elif isinstance(current_op, llops.AncillaQubitPatchInitialization):
            maybe_cell_location = self.addSquareAncilla(
                current_op.qubit_state, current_op.qubit_uuid
            )
            if maybe_cell_location is None:
                raise Exception("Could not allocate ancilla")

        elif isinstance(current_op, llops.LogicalPauli):
            self.applyPauliOperator(
                self.get_patch_representative(current_op.qubit_uuid), current_op.pauli_matrix
            )

        elif isinstance(current_op, llops.MultiBodyMeasurement):
            patch_pauli_operator_map = dict(
                [
                    (self.get_patch_representative(uuid), op)
                    for uuid, op in current_op.patch_pauli_operator_map.items()
                ]
            )
            self.multiBodyMeasurePatches(patch_pauli_operator_map)

        elif isinstance(current_op, llops.MagicStateRequest):
            cell = self.computation.bind_magic_state(current_op.qubit_uuid)
            if cell is None:
                raise Exception("No magic state available")

        else:
            raise Exception("Unsupported operation %s" % repr(current_op))

    def set_separable_states(self, sim: lps.PatchSimulator):
        separable_states = qo_utils.StateSeparator.get_separable_qubits(sim.logical_state)
        for patch in self.lattice().patches:
            if patch.patch_uuid is not None:
                idx = sim.mapper.get_idx(patch.patch_uuid)
                if separable_states.get(idx) is not None:
                    alpha, beta = separable_states[idx].to_matrix()
                    if isinstance(patch.state, qs.ActiveState):
                        patch.state.next = qs.DefaultSymbolicStates.from_amplitudes(alpha, beta)
                    else:
                        patch.state = qs.DefaultSymbolicStates.from_amplitudes(alpha, beta)
                else:
                    patch.state = qs.EntangledState()
