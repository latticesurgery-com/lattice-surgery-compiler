
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
        (3,2):patches.PauliOperator.X,
        (4,2):patches.PauliOperator.X
    })

with lsc.timestep() as slice:
    pass

with lsc.timestep() as slice:
    slice.measurePatch((4,2), patches.PauliOperator.X)

with lsc.timestep() as slice:
    slice.measurePatch((3,2), patches.PauliOperator.X)

with lsc.timestep() as slice:

    slice.measureMultiPatch({
        (0,0):patches.PauliOperator.X,
        (4,0):patches.PauliOperator.Z,
        (6,0):patches.PauliOperator.X
    })

with lsc.timestep() as slice:
    pass

with lsc.timestep() as slice:


    slice.measureMultiPatch({
        (0,0):patches.PauliOperator.X,
        (10,0):patches.PauliOperator.X
    })

with lsc.timestep() as slice:

    slice.measureMultiPatch({
        (0,0):patches.PauliOperator.X,
        (4,0):patches.PauliOperator.Z,
    })

    slice.measureMultiPatch({
        (8,0):patches.PauliOperator.X,
        (11,0):patches.PauliOperator.X,
    })

with lsc.timestep() as slice:

    slice.measureMultiPatch({
        (10,0):patches.PauliOperator.Z,
        (8,0):patches.PauliOperator.X,
    })

    slice.measureMultiPatch({
        (10,0):patches.PauliOperator.X,
        (11,0):patches.PauliOperator.Z,
    })

with lsc.timestep() as slice:

    slice.measureMultiPatch({
        (4,0):patches.PauliOperator.X,
        (6,0):patches.PauliOperator.Z,
    })

    slice.measureMultiPatch({
        (0,0):patches.PauliOperator.X,
        (10,0):patches.PauliOperator.Z,
    })

    slice.measureMultiPatch({
        (11,0):patches.PauliOperator.X,
        (12,0):patches.PauliOperator.X
    })

lattice_view.to_file(lsc.composer.getSlices(),"index.html")