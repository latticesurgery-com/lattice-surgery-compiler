
import patches
from webgui import lattice_view
from lattice_surgery_computation_composer import LatticeSurgeryComputation,LayoutInitializer,LayoutTypes

# Example
# Construct the device layout

lsc = LatticeSurgeryComputation(LayoutTypes.Simple,5);


with lsc.timestep() as slice:
    slice.addPatch(LayoutInitializer.singleSquarePatch((4, 2), patches.PatchType.Qubit, patches.DefalutSymbolicStates.Plus))


with lsc.timestep() as slice:

    slice.addPatch(LayoutInitializer.singleSquarePatch((3, 2), patches.PatchType.Qubit, patches.DefalutSymbolicStates.Plus))

with lsc.timestep() as slice:

    slice.multiBodyMeasurePatches({
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

    slice.multiBodyMeasurePatches({
        (0,0):patches.PauliOperator.X,
        (4,0):patches.PauliOperator.Z,
        (6,0):patches.PauliOperator.X
    })

with lsc.timestep() as slice:
    pass

with lsc.timestep() as slice:


    slice.multiBodyMeasurePatches({
        (0,0):patches.PauliOperator.X,
        (10,0):patches.PauliOperator.X
    })

with lsc.timestep() as slice:

    slice.multiBodyMeasurePatches({
        (0,0):patches.PauliOperator.X,
        (4,0):patches.PauliOperator.Z,
    })

    slice.multiBodyMeasurePatches({
        (8,0):patches.PauliOperator.X,
        (11,0):patches.PauliOperator.X,
    })

with lsc.timestep() as slice:

    slice.multiBodyMeasurePatches({
        (10,0):patches.PauliOperator.Z,
        (8,0):patches.PauliOperator.X,
    })

    slice.multiBodyMeasurePatches({
        (10,0):patches.PauliOperator.X,
        (11,0):patches.PauliOperator.Z,
    })

with lsc.timestep() as slice:

    slice.multiBodyMeasurePatches({
        (4,0):patches.PauliOperator.X,
        (6,0):patches.PauliOperator.Z,
    })

    slice.multiBodyMeasurePatches({
        (0,0):patches.PauliOperator.X,
        (10,0):patches.PauliOperator.Z,
    })

    slice.multiBodyMeasurePatches({
        (11,0):patches.PauliOperator.X,
        (12,0):patches.PauliOperator.X
    })

lattice_view.render_to_file(lsc.composer.getSlices(), "index.html")