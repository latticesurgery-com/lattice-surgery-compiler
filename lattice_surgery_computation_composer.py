import patches
import ancilla_patch_routing

from typing import *
import copy
import enum

import uuid

class QubitLayoutTypes:
    Simple = "Simple"



class LatticeSurgeryComputation:

    def __init__(self, num_qubits: int):
        """
        Layout arguments:
            - Simple: n_logical_qubits: int
        """
        self.num_qubits = num_qubits
        self.composer = LatticeSurgeryComputationComposer(self, PatchInitializer.simpleLayout(self.num_qubits))
        self.qubit_idx_to_cell_mapping = dict([(j, PatchInitializer.simpleMapQubitToCell(j)) for j in range(self.num_qubits)])

        self.ancilla_locations = [(j,2) for j in range(self.num_qubits)]
        self.magic_state_queue = [(j + self.num_qubits,2) for j in range(self.num_qubits)]


        self.composer.lattice().min_cols = 2*self.num_qubits
        self.composer.lattice().min_rows = 3


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

    def get_cell_for_qubit_idx(self, qubit_idx: int) -> Tuple[int,int]:
        return self.qubit_idx_to_cell_mapping[qubit_idx]

    def grab_magic_state(self, patch_uuid : uuid.UUID)->Optional[patches.Patch]:
        for cell in self.magic_state_queue:
            p = self.composer.lattice().getPatchOfCell(cell)
            if p.patch_uuid is None:
                p.patch_uuid = patch_uuid
                return p
        return None


class LatticeSurgeryComputationPreparedMagicStates(LatticeSurgeryComputation):
    def __init__(self, num_qubits : int, num_magic_states : int):
        super().__init__(num_qubits)
        self.magic_state_queue = []
        start_magic_state_array = self.composer.lattice().getCols()
        for j in range(start_magic_state_array, start_magic_state_array+num_magic_states):
            magic_state_pos = (j,0)
            self.composer.lattice().patches.append(PatchInitializer.singleSquarePatch(
                magic_state_pos,
                patches.PatchType.DistillationQubit,
                patches.InitializeableState.Magic))
            self.magic_state_queue.append(magic_state_pos)
        self.composer.lattice().min_cols += num_magic_states



class PatchInitializer:

    def singleSquarePatch(cell:Tuple[int,int],
                          patch_type:patches.PatchType = patches.PatchType.Qubit,
                          patch_state:patches.SymbolicState = patches.InitializeableState.Zero ):
        return patches.Patch(patch_type, patch_state, [cell],[
            patches.Edge(patches.EdgeType.Dashed,  cell, patches.Orientation.Top),
            patches.Edge(patches.EdgeType.Dashed,  cell, patches.Orientation.Bottom),
            patches.Edge(patches.EdgeType.Solid,  cell, patches.Orientation.Left),
            patches.Edge(patches.EdgeType.Solid,  cell, patches.Orientation.Right)
        ])

    def simpleRightFacingDistillery(top_left_corner: Tuple[int,int]) -> List[patches.Patch]:
        # Requires
        x,y = top_left_corner
        return [
            PatchInitializer.singleSquarePatch((x + 2, y), patches.PatchType.DistillationQubit, patches.InitializeableState.Magic),
            PatchInitializer.singleSquarePatch((x + 3, y), patches.PatchType.DistillationQubit, patches.InitializeableState.Magic),
            PatchInitializer.singleSquarePatch((x + 4, y + 1), patches.PatchType.DistillationQubit, patches.InitializeableState.Plus),
            PatchInitializer.singleSquarePatch((x + 3, y + 2), patches.PatchType.DistillationQubit, patches.InitializeableState.Magic),
            PatchInitializer.singleSquarePatch((x + 2, y + 2), patches.PatchType.DistillationQubit, patches.InitializeableState.Magic),
            patches.Patch(patches.PatchType.DistillationQubit, patches.InitializeableState.Zero, [(x, y), (x, y+1)],
                          [
                              patches.Edge(patches.EdgeType.Solid, (x, y), patches.Orientation.Top),
                              patches.Edge(patches.EdgeType.Solid, (x, y), patches.Orientation.Left),
                              patches.Edge(patches.EdgeType.Dashed,(x, y), patches.Orientation.Right),
                              patches.Edge(patches.EdgeType.Dashed,(x, y+1), patches.Orientation.Left),
                              patches.Edge(patches.EdgeType.Dashed,(x, y+1), patches.Orientation.Bottom),
                              patches.Edge(patches.EdgeType.Solid, (x, y+1), patches.Orientation.Right),
                          ]),
            patches.Patch(patches.PatchType.DistillationQubit, patches.InitializeableState.Magic, [(x+1, y), (x+1, y+1)],
                          [
                              patches.Edge(patches.EdgeType.Dashed,  (x+1, y), patches.Orientation.Top),
                              patches.Edge(patches.EdgeType.Solid,  (x+1, y), patches.Orientation.Left),
                              patches.Edge(patches.EdgeType.Dashed, (x+1, y), patches.Orientation.Right),
                              patches.Edge(patches.EdgeType.Solid, (x+1, y+1), patches.Orientation.Left),
                              patches.Edge(patches.EdgeType.Dashed, (x+1, y+1), patches.Orientation.Bottom),
                              patches.Edge(patches.EdgeType.Solid,  (x+1, y+1), patches.Orientation.Right),
                          ]),
        ]



    @staticmethod
    def simpleLayout(num_logical_qubits: int) -> patches.Lattice:
        """a linear array of one spaced square patches with a distillery on one side"""
        # TODO distillery
        return patches.Lattice([
            PatchInitializer.singleSquarePatch(PatchInitializer.simpleMapQubitToCell(j)) for j in range(num_logical_qubits)
        ], 2, 0)


    @staticmethod
    def addRightDistillery(lattice: patches.Lattice):
        lattice.patches.append(
            PatchInitializer.simpleRightFacingDistillery((lattice.getCols(), 0)))

    @staticmethod
    def simpleLayoutWithPreparedMagicStates(num_logical_qubits: int, num_magic_states):
        """a linear array of one spaced square patches with a linear array of magic states"""
        pass


    def simpleMapQubitToCell(qubit_n: int):
        return (qubit_n * 2, 0)





class LatticeSurgeryComputationComposer:
    def __init__(self, computation: LatticeSurgeryComputation, initial_layout: patches.Lattice):
        self.computation = computation
        self.qubit_patch_slices : List[patches.Lattice] = [initial_layout] #initialize lattice here

    def lattice(self):
        return self.qubit_patch_slices[-1]

    def addPatch(self, patch: patches.Patch):
        self.lattice().patches.append(patch)

    def addSquareAncilla(self, patch_state: patches.SymbolicState, patch_uuid: Optional[uuid.UUID] = None) \
            -> Optional[Tuple[int,int]]:
        cell = self.getAncillaLocation()
        if cell is None: return None
        new_patch = PatchInitializer.singleSquarePatch(cell, patches.PatchType.Qubit, patch_state)
        new_patch.patch_uuid = patch_uuid
        self.addPatch(new_patch)
        return cell

    def getAncillaLocation(self) -> Optional[Tuple[int,int]]:
        for ancilla in self.computation.ancilla_locations:
            if self.lattice().getPatchOfCell(ancilla) is None:
                return ancilla
        return None

    def findMagicState(self) -> Optional[Tuple[int,int]]:
        for magic_cell in self.computation.magic_state_queue:
            if self.lattice().getPatchOfCell(magic_cell) is not None:
                return magic_cell
        return None

    def measurePatch(self, cell_of_patch: Tuple[int, int], basis_matrix: patches.PauliOperator):
        if basis_matrix not in [patches.PauliOperator.X, patches.PauliOperator.Z]:
            raise Exception("Can't measure with basis matrix "+basis_matrix.value+" yet")
        for patch in self.qubit_patch_slices[-1].patches:
            if patch.getRepresentative() == cell_of_patch:
                patch.state = patch.state.apply_measurement(basis_matrix)

    def newTimeSlice(self):
        self.qubit_patch_slices.append(copy.deepcopy(self.lattice()))

    def multiBodyMeasurePatches(self, patch_pauli_operator_map: Dict[Tuple[int, int], patches.PauliOperator]):
        """
        Corresponds to a lattice surgery merge followed by a split.
        """
        for v in patch_pauli_operator_map.values():
            if v not in {patches.PauliOperator.X,patches.PauliOperator.Z}:
                raise Exception("Only X and Y operators are supported in multibody mesurement, got "+repr(v))

        ancilla_patch_routing.compute_ancilla_cells(self.qubit_patch_slices[-1], patch_pauli_operator_map)


    def applyPauliProductOperator(self,
                                  cell_of_patch : Tuple[int,int],
                                  operator: patches.PauliOperator,
                                  conditional:bool = False):

        for patch in self.lattice().patches:
            if patch.getRepresentative() == cell_of_patch and patch.state is not None:
                patch.state = patch.state.compose_operator(operator)


    def clearAncilla(self):
        for j, patch in enumerate(self.qubit_patch_slices[-1].patches):
            for i, edge in enumerate(patch.edges):
                if edge.isStiched():
                    edge.border_type = edge.border_type.unstitched_type()
                    # After measurement we are not ready to track state yet
                    self.lattice().getPatchOfCell(edge.cell).state = patches.InitializeableState.UnknownState


        is_not_ancilla  =lambda patch: patch.patch_type != patches.PatchType.Ancilla
        self.qubit_patch_slices[-1].patches = list(filter(is_not_ancilla, self.lattice().patches))

    def clearActiveStates(self):
        # Make measured patches disappear
        def patch_stays(patch : patches.Patch) -> bool:
            if patch.state is not None and isinstance(patch.state,patches.ActiveState) and patch.state.disappears():
                return False
            return True

        self.lattice().patches = list(filter(patch_stays,self.lattice().patches))

        # Clear other activity
        for patch in self.lattice().patches:
            if patch.state is not None and isinstance(patch.state,patches.ActiveState):
                patch.state = patch.state.next


    def clearLattice(self):
        self.qubit_patch_slices[-1].clear()

    def rotateSquarePatch(self, patch_idx: int):
        # assumes: The patch is square, there is room to rotate it
        # TODO make multiple rotations possible at the same time
       pass



    def getSlices(self) -> List[patches.Lattice]:
        return self.qubit_patch_slices


