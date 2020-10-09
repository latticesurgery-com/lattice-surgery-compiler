from enum import Enum
from typing import Dict,Union,Optional,List,Tuple

import patches

class PauliMatrix(Enum):
    X = [[0,  1],
         [1,  0]]
    Y = [[0, -1j],
         [1j, 0]]
    Z = [[1,  0],
         [0, -1]]




class LatticeLayoutInitializer:


    def singleSquarePatch(cell: Tuple[int,int]):
        return patches.Patch(patches.PatchType.Qubit, patches.InitializeableState.Zero, [cell],[
            patches.Edge(patches.EdgeType.Solid,  cell, patches.Orientation.Top),
            patches.Edge(patches.EdgeType.Solid,  cell, patches.Orientation.Bottom),
            patches.Edge(patches.EdgeType.Dashed, cell, patches.Orientation.Left),
            patches.Edge(patches.EdgeType.Dashed, cell, patches.Orientation.Right)
        ])

    def simpleLayout(num_logical_qubits: int) -> patches.Lattice: # a linear array of one spaced square patches with a distillery on one side
        # TODO distillery
        return patches.Lattice([
            LatticeLayoutInitializer.singleSquarePatch((j*2,0)) for j in range(num_logical_qubits)
        ],2,0)





class TopologicalAssemblyComposer:
    def __init__(self, number_of_qubit_patches:int):
        self.qubit_patch_slices : List[patches.Lattice] = [] #initialize lattice here

    def initQubit(self, patch_idx:int, state: patches.InitializeableState): # Only initialization of |0> and |+> is predictable
        self.qubit_patch_slices.append(self.qubit_patch_slices[-1])

    def measureSinglePatch(self, patch_idx:int, basisMatrix:PauliMatrix):
        if basisMatrix not in [PauliMatrix.X,PauliMatrix.Z]:
            raise Exception("can't measure with basis matrix "+basisMatrix)
        self.qubit_patches[patch_idx] = None

    def measureMultiPatch(self, patch_operator_map: Dict[int,PauliMatrix]):
        pass




    def rotateSquarePatch(self,patch_idx: int):
        # assumes: The patch is square, there is room to rotate it
        # TODO make multiple rotations possible at the same time
       pass

