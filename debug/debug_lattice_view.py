
import patches
import lattice_view
from lattice_surgery_computation_composer import TopologicalAssemblyComposer,LatticeLayoutInitializer


# Example
# Construct the device layout
tac = TopologicalAssemblyComposer(
    LatticeLayoutInitializer.simpleLayout(5))

tac.measureMultiPatch({
    (0,0):patches.PauliMatrix.X,
    (4,0):patches.PauliMatrix.Z,
    (6,0):patches.PauliMatrix.X
})

tac.newTimeSlice()
tac.clearAncilla()


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

lattice_view.to_file(tac.getSlices(),"index.html")