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
            self.composer = LatticeSurgeryComputationComposer(PatchInitializer.simpleLayout(argv[0]))
            self.composer.newTimeSlice()
        else:
            raise Exception("Unsupported layout type:"+repr(layout_type))

    def timestep(self):
        class LatticeSurgeryComputationSliceContextManager:
            def __init__(self, root_composer: LatticeSurgeryComputationComposer):
                self.root_composer = root_composer

            def __enter__(self):
                return self.root_composer

            def __exit__(self, exception_type, val, traceback):
                self.root_composer.newTimeSlice()
                self.root_composer.clearAncilla()

                return False  # re reaises the exception

        return LatticeSurgeryComputationSliceContextManager(self.composer)



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
            PatchInitializer.singleSquarePatch((j * 2, 0)) for j in range(num_logical_qubits)
        ] + PatchInitializer.simpleRightFacingDistillery((2 * num_logical_qubits, 0))
                               , 2, 0)






class LatticeSurgeryComputationComposer:
    def __init__(self, initial_layout: patches.Lattice):
        self.qubit_patch_slices : List[patches.Lattice] = [initial_layout] #initialize lattice here

    def lattice(self):
        return self.qubit_patch_slices[-1]

    def addPatch(self, patch: patches.Patch):
        self.lattice().patches.append(patch)

    def measurePatch(self, cell_of_patch: Tuple[int, int], basis_matrix: patches.PauliMatrix):
        if basis_matrix not in [patches.PauliMatrix.X, patches.PauliMatrix.Z]:
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

    def measureMultiPatch(self, patch_pauli_operator_map: Dict[Tuple[int, int], patches.PauliMatrix]):
        # TODO refactor this method

        # Break down Y measurements into an simultaneous X and Y measurement, as specified by Litnski's Game of
        # Surface codes in Fig.2.

        def replace_operator(operator_map,old,new) -> Dict[Tuple[int, int], patches.PauliMatrix]:
            new_operator_map = {}
            for cell, operator in operator_map.items():
                if operator == old:
                    new_operator_map[cell] = new
                else:
                    new_operator_map[cell] = operator
            return new_operator_map

        ancilla_patch_routing.compute_ancilla_cells(self.qubit_patch_slices[-1], patch_pauli_operator_map)

        # TODO fix removal of y operators
        # if 1: return "FIX BELOW using compute_ancilla_cells directly on the lattice"
        # # Try first without replacing the operator and then with replacing the operator
        # ancilla_cells = compute_ancilla_cells(
        #     self.qubit_patch_slices[-1],
        #     replace_operator(patch_pauli_operator_map,patches.PauliMatrix.Y,patches.PauliMatrix.Z)
        # )
        # ancilla_cells.extend(compute_ancilla_cells(
        #     self.qubit_patch_slices[-1],
        #     replace_operator(patch_pauli_operator_map,patches.PauliMatrix.Y,patches.PauliMatrix.X)
        # ))
        #
        # if len(ancilla_cells) > 0:
        #     ancilla_cells = list(set(ancilla_cells)) # Eliminate duplicates
        #     self.qubit_patch_slices[-1].patches.append(patches.Patch(patches.PatchType.Ancilla, None, ancilla_cells,[] ))
        # else:
        #     print("WARNING: no ancilla patch generated for measurement:")
        #     print(patch_pauli_operator_map)






    def clearAncilla(self):
        for j, patch in enumerate(self.qubit_patch_slices[-1].patches):
            for i, edge in enumerate(patch.edges):
                if edge.isStiched():
                    edge.border_type = edge.border_type.unstitched_type()
                    # After measurement we are not ready to track state yet
                    self.lattice().getPatchOfCell(edge.cell).state = None

        self.qubit_patch_slices[-1].patches = list(filter(
            lambda patch: patch.patch_type != patches.PatchType.Ancilla, self.qubit_patch_slices[-1].patches))

    def clearLattice(self):
        self.qubit_patch_slices[-1].clear()

    def rotateSquarePatch(self, patch_idx: int):
        # assumes: The patch is square, there is room to rotate it
        # TODO make multiple rotations possible at the same time
       pass



    def getSlices(self) -> List[patches.Lattice]:
        return self.qubit_patch_slices


