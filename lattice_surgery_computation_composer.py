import patches
import ancilla_patch_routing

from typing import *
import copy




class LatticeLayoutInitializer:

    def singleSquarePatch(cell: Tuple[int,int], patch_type=patches.PatchType.Qubit, patch_state=patches.InitializeableState.Zero ):
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
            LatticeLayoutInitializer.singleSquarePatch((x+2,y), patches.PatchType.DistillationQubit, patches.InitializeableState.Magic),
            LatticeLayoutInitializer.singleSquarePatch((x+3,y), patches.PatchType.DistillationQubit, patches.InitializeableState.Magic),
            LatticeLayoutInitializer.singleSquarePatch((x+4,y+1), patches.PatchType.DistillationQubit, patches.InitializeableState.Plus),
            LatticeLayoutInitializer.singleSquarePatch((x+3,y+2), patches.PatchType.DistillationQubit, patches.InitializeableState.Magic),
            LatticeLayoutInitializer.singleSquarePatch((x+2,y+2), patches.PatchType.DistillationQubit, patches.InitializeableState.Magic),
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
            LatticeLayoutInitializer.singleSquarePatch((j*2,0)) for j in range(num_logical_qubits)
        ] + LatticeLayoutInitializer.simpleRightFacingDistillery((2*num_logical_qubits,0))
        ,2,0)






class TopologicalAssemblyComposer:
    def __init__(self, initial_layout: patches.Lattice):
        self.qubit_patch_slices : List[patches.Lattice] = [initial_layout] #initialize lattice here

    def initQubit(self, patch_idx:int, state: patches.InitializeableState): # Only initialization of |0> and |+> is predictable
        self.qubit_patch_slices.append(self.qubit_patch_slices[-1])

    def measureSinglePatch(self, patch_idx:int, basisMatrix: patches.PauliMatrix):
        if basisMatrix not in [patches.PauliMatrix.X, patches.PauliMatrix.Z]:
            raise Exception("can't measure with basis matrix "+basisMatrix+" yet")
        self.qubit_patches[patch_idx] = None

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
                self.qubit_patch_slices[-1].patches[j].edges[i].border_type = edge.border_type.unstitched_type()

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

