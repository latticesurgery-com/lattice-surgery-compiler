import patches
import ancilla_patch_routing

from typing import *
import copy
import enum

class LayoutTypes:
    Simple = "Simple"



class LatticeSurgeryComputation:

    def __init__(self,layout_type: LayoutTypes, *argv):
        """
        Layout arguments:
            - Simple: n_logical_qubits: int
        """
        if layout_type == LayoutTypes.Simple:
            self.num_qubits = argv[0]
            self.composer = LatticeSurgeryComputationComposer(PatchInitializer.simpleLayout(self.num_qubits ))
            self.qubit_idx_to_cell_mapping = dict([(j, PatchInitializer.simpleMapQubitToCell(j)) for j in range(self.num_qubits)])
            self.ancilla_locations = [(2,j) for j in range(self.num_qubits)]
            self.magic_state_queue = [(2,j+self.num_qubits) for j in range(self.num_qubits)]
        else:
            raise Exception("Unsupported layout type:"+repr(layout_type))

        self.composer.newTimeSlice()

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

    def get_cell_for_qubit_idx(self, qubit_idx: int):
        return self.qubit_idx_to_cell_mapping[qubit_idx]


class PatchInitializer:

    def singleSquarePatch(cell:Tuple[int,int],
                          patch_type:patches.PatchType = patches.PatchType.Qubit,
                          patch_state:patches.InitializeableState = patches.InitializeableState.Zero ):
        return patches.Patch(patch_type, patch_state, [cell],[
            patches.Edge(patches.EdgeType.Solid,  cell, patches.Orientation.Top),
            patches.Edge(patches.EdgeType.Solid,  cell, patches.Orientation.Bottom),
            patches.Edge(patches.EdgeType.Dashed, cell, patches.Orientation.Left),
            patches.Edge(patches.EdgeType.Dashed, cell, patches.Orientation.Right)
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



    def simpleLayout(num_logical_qubits: int) -> patches.Lattice: # a linear array of one spaced square patches with a distillery on one side
        # TODO distillery
        return patches.Lattice([
            PatchInitializer.singleSquarePatch(PatchInitializer.simpleMapQubitToCell(j)) for j in range(num_logical_qubits)
        ] + PatchInitializer.simpleRightFacingDistillery((2 * num_logical_qubits, 0))
                               , 2, 0)

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

    def addSquareAncilla(self, patch_state: patches.InitializeableState) -> Optional[Tuple[int,int]]:
        cell = self.getAncillaLocation()
        if cell is None: return None
        self.addPatch(PatchInitializer.singleSquarePatch(patches.PatchType.Qubit,patch_state))
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
            raise Exception("Can't measure with basis matrix "+basis_matrix+" yet")
        index_to_remove = None
        for i,patch in enumerate(self.qubit_patch_slices[-1].patches):
            if patch.getRepresentative() == cell_of_patch:
                index_to_remove = i
                break
        if index_to_remove is not None:
            del self.qubit_patch_slices[-1].patches[index_to_remove]
        else:
            raise Exception("No patch to measure at " + cell_of_patch + "")

    def newTimeSlice(self):
        self.qubit_patch_slices.append(copy.deepcopy(self.qubit_patch_slices[-1]))

    def measureMultiPatch(self, patch_pauli_operator_map: Dict[Tuple[int, int], patches.PauliOperator]):
        # TODO refactor this method

        # Break down Y measurements into an simultaneous X and Y measurement, as specified by Litnski's Game of
        # Surface codes in Fig.2.

        def replace_operator(operator_map,old,new) -> Dict[Tuple[int, int], patches.PauliOperator]:
            new_operator_map = {}
            for cell, operator in operator_map.items():
                if operator == old:
                    new_operator_map[cell] = new
                else:
                    new_operator_map[cell] = operator
            return new_operator_map

        ancilla_patch_routing.compute_ancilla_cells(self.qubit_patch_slices[-1], patch_pauli_operator_map)


    def applyPauliProductOperator(self,
                                  cell_of_patch : Tuple[int,int],
                                  operator: patches.PauliOperator,
                                  conditional:bool = False):

        for patch in self.lattice().patches:
            if patch.getRepresentative() == cell_of_patch and patch.state is not None:
                patch.state = patches.NonTrivialState()
                patch.state.is_active = True


    def clearAncilla(self):
        for j, patch in enumerate(self.qubit_patch_slices[-1].patches):
            for i, edge in enumerate(patch.edges):
                if edge.isStiched():
                    edge.border_type = edge.border_type.unstitched_type()
                    # After measurement we are not ready to track state yet
                    self.lattice().getPatchOfCell(edge.cell).state = None

        self.qubit_patch_slices[-1].patches = list(filter(
            lambda patch: patch.patch_type != patches.PatchType.Ancilla, self.qubit_patch_slices[-1].patches))

    def clearActiveStates(self):
        for patch in self.lattice():
            if patch.state is not None:
                patch.state.is_active = False


    def clearLattice(self):
        self.qubit_patch_slices[-1].clear()

    def rotateSquarePatch(self, patch_idx: int):
        # assumes: The patch is square, there is room to rotate it
        # TODO make multiple rotations possible at the same time
       pass



    def getSlices(self) -> List[patches.Lattice]:
        return self.qubit_patch_slices


