
import patches
import lattice_view
from lattice_surgery_computation_composer import LatticeSurgeryComputationComposer,PatchInitializer

# Example
# Construct the device layout
tac = LatticeSurgeryComputationComposer(
    PatchInitializer.simpleLayout(5))

tac.newTimeSlice()

tac.addPatch(PatchInitializer.singleSquarePatch((4,2),patches.PatchType.Qubit, patches.InitializeableState.Plus))

tac.newTimeSlice()

tac.addPatch(PatchInitializer.singleSquarePatch((3,2),patches.PatchType.Qubit, patches.InitializeableState.Plus))

tac.newTimeSlice()

tac.measureMultiPatch({
    (3,2):patches.PauliMatrix.X,
    (4,2):patches.PauliMatrix.X
})

tac.newTimeSlice()

tac.clearAncilla()
tac.lattice().getPatchOfCell((3,2)).state = None
tac.lattice().getPatchOfCell((4,2)).state = None

tac.newTimeSlice()
tac.measurePatch((4,2),patches.PauliMatrix.X)

tac.newTimeSlice()
tac.measurePatch((3,2),patches.PauliMatrix.X)

tac.newTimeSlice()

tac.measureMultiPatch({
    (0,0):patches.PauliMatrix.X,
    (4,0):patches.PauliMatrix.Z,
    (6,0):patches.PauliMatrix.X
})

tac.newTimeSlice()
tac.clearAncilla()
tac.lattice().getPatchOfCell((0,0)).state = None
tac.lattice().getPatchOfCell((4,0)).state = None
tac.lattice().getPatchOfCell((6,0)).state = None

tac.newTimeSlice()


tac.measureMultiPatch({
    (0,0):patches.PauliMatrix.X,
    (10,0):patches.PauliMatrix.X
})

tac.newTimeSlice()
tac.clearAncilla()

tac.measureMultiPatch({
    (0,0):patches.PauliMatrix.X,
    (4,0):patches.PauliMatrix.Z,
})

tac.measureMultiPatch({
    (8,0):patches.PauliMatrix.X,
    (11,0):patches.PauliMatrix.X,
})


tac.newTimeSlice()
tac.clearAncilla()


tac.measureMultiPatch({
    (10,0):patches.PauliMatrix.Z,
    (8,0):patches.PauliMatrix.X,
})

tac.measureMultiPatch({
    (10,0):patches.PauliMatrix.X,
    (11,0):patches.PauliMatrix.Z,
})

tac.newTimeSlice()
tac.clearAncilla()

tac.measureMultiPatch({
    (4,0):patches.PauliMatrix.X,
    (6,0):patches.PauliMatrix.Z,
})

tac.measureMultiPatch({
    (0,0):patches.PauliMatrix.X,
    (10,0):patches.PauliMatrix.Z,
})

tac.measureMultiPatch({
    (11,0):patches.PauliMatrix.X,
    (12,0):patches.PauliMatrix.X
})

lattice_view.to_file(tac.getSlices(),"index.html")