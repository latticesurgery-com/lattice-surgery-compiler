
import patches
import lattice_view
from lattice_surgery_computation_composer import LatticeSurgeryComputation,PatchInitializer,LayoutTypes

# Example
# Construct the device layout

lsc = LatticeSurgeryComputation(LayoutTypes.Simple,5);


with lsc.timestep() as slice:
    slice.addPatch(PatchInitializer.singleSquarePatch((4,2),patches.PatchType.Qubit, patches.InitializeableState.Plus))


with lsc.timestep() as slice:

    slice.addPatch(PatchInitializer.singleSquarePatch((3,2),patches.PatchType.Qubit, patches.InitializeableState.Plus))

with lsc.timestep() as slice:

    slice.measureMultiPatch({
        (3,2):patches.PauliMatrix.X,
        (4,2):patches.PauliMatrix.X
    })

with lsc.timestep() as slice:
    pass

with lsc.timestep() as slice:
    slice.measurePatch((4,2),patches.PauliMatrix.X)

with lsc.timestep() as slice:
    slice.measurePatch((3,2),patches.PauliMatrix.X)

with lsc.timestep() as slice:

    slice.measureMultiPatch({
        (0,0):patches.PauliMatrix.X,
        (4,0):patches.PauliMatrix.Z,
        (6,0):patches.PauliMatrix.X
    })

with lsc.timestep() as slice:
    pass

with lsc.timestep() as slice:


    slice.measureMultiPatch({
        (0,0):patches.PauliMatrix.X,
        (10,0):patches.PauliMatrix.X
    })

with lsc.timestep() as slice:

    slice.measureMultiPatch({
        (0,0):patches.PauliMatrix.X,
        (4,0):patches.PauliMatrix.Z,
    })

    slice.measureMultiPatch({
        (8,0):patches.PauliMatrix.X,
        (11,0):patches.PauliMatrix.X,
    })

with lsc.timestep() as slice:

    slice.measureMultiPatch({
        (10,0):patches.PauliMatrix.Z,
        (8,0):patches.PauliMatrix.X,
    })

    slice.measureMultiPatch({
        (10,0):patches.PauliMatrix.X,
        (11,0):patches.PauliMatrix.Z,
    })

with lsc.timestep() as slice:

    slice.measureMultiPatch({
        (4,0):patches.PauliMatrix.X,
        (6,0):patches.PauliMatrix.Z,
    })

    slice.measureMultiPatch({
        (0,0):patches.PauliMatrix.X,
        (10,0):patches.PauliMatrix.Z,
    })

    slice.measureMultiPatch({
        (11,0):patches.PauliMatrix.X,
        (12,0):patches.PauliMatrix.X
    })

lattice_view.to_file(lsc.composer.getSlices(),"index.html")