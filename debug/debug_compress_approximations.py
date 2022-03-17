from lsqecc.gates.compress_rotation_approximations import partition_gate_sequence
from lsqecc.pauli_rotations.rotation import CachedRotationApproximations

test_sequence_1 = "SSSXHSTHTHSTHTH"
test_sequence_2 = "SHSSXH"
test_sequence = CachedRotationApproximations.get_pi_over_2_to_the_n_rz_gate(100)
sequences = partition_gate_sequence(test_sequence)
print(f"The number of partitions is {len(sequences)}")
print(f"The number of gates is{len(test_sequence)} ")
# for seq in sequences:
#     print(f"{seq}")

# Most common ones are HTH and HSTH
