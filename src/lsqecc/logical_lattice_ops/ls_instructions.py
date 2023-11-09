
import lsqecc.logical_lattice_ops.logical_lattice_ops as llops

def to_instruction(lattice_op:llops.LogicalLatticeOperation):
    if isinstance(lattice_op, llops.MagicStateRequest):
        return f"RequestMagicState {lattice_op.qubit_uuid}"
    elif isinstance(lattice_op, llops.AncillaQubitPatchInitialization):
        return f"RequestYState {lattice_op.qubit_uuid}"
    elif isinstance(lattice_op, llops.MultiBodyMeasurement):
        operators =  ",".join([f"{patch_id}:{operator}"
                               for patch_id, operator in lattice_op.patch_pauli_operator_map.items()])
        return f"MultiBodyMeasure {operators}"
    elif isinstance(lattice_op, llops.SinglePatchMeasurement):
        return f"MeasureSinglePatch {lattice_op.qubit_uuid}"
    else:
        assert isinstance(lattice_op, llops.LogicalPauli)
        return f"Pauli {lattice_op.qubit_uuid}"



def from_logical_lattice_ops(computation: llops.LogicalLatticeComputation):
    return "\n".join(map(to_instruction, computation.ops))+"\n"


