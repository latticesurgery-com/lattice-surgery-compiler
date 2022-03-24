from lsqecc.gates.compress_rotation_approximations import partition_gate_sequence
from lsqecc.pauli_rotations.rotation import CachedRotationApproximations
from lsqecc.gates.pi_over_2_to_the_n_rz_gate_approximations import get_pi_over_2_to_the_n_rz_gate
import numpy as np
import matplotlib.pyplot as plt

# test_sequence_1 = "SSSXHSTHTHSTHTH"
# test_sequence_2 = "SHSSXH"
# test_sequence_3 = "HSSTTSHSH"
test_sequence = CachedRotationApproximations.get_pi_over_2_to_the_n_rz_gate(2)
sequences_Z = partition_gate_sequence(test_sequence)
# sequences_X = partition_gate_sequence("H" + test_sequence + "H")

print(partition_gate_sequence("H"))
print(partition_gate_sequence("S"))
print(partition_gate_sequence("HS"))
print(partition_gate_sequence("SH"))
print(partition_gate_sequence("HSH"))
print(partition_gate_sequence("SHS"))
print(partition_gate_sequence("HSHS"))
print(partition_gate_sequence("SHSH"))
print(partition_gate_sequence("HSHSH"))
print(partition_gate_sequence("SHSHS"))
print(partition_gate_sequence("HSHSHS"))
print(partition_gate_sequence("SHSHSH"))
print(partition_gate_sequence("SSSXHSTHTHSTHTH"))
print(partition_gate_sequence("HSTHSSHSTHT"))
print(partition_gate_sequence("HSTHSSHSTH"))
print(partition_gate_sequence("STHSSHSTHTH"))
# print("The gate for a Z rotation are:\n")
# # print(f"The number of gates without compression in Gate Frame of is {len(test_sequence)} ")
# # print(
# #     f"Number of gates without compressiopn in Pauli Frame is {len(test_sequence) + 2*test_sequence.count('H')}"
# # )
# # print(f"The number of partitions (Compressed list of gates) is {len(sequences_Z)}")

# # print("The gate for a X rotation are:\n")
# # print(f"The number of gates without compression in Gate Frame of is {len(test_sequence)+2} ")
# # print(
# #     f"Number of gates without compressiopn in Pauli Frame is {len(test_sequence) + 2*test_sequence.count('H') + 6}"
# # )
# # print(f"The number of partitions (Compressed list of gates) is {len(sequences_X)}")


# for seq in sequences:
#     print(f"{seq}")

# Most common ones are HTH and HSTH
