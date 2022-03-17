from cProfile import label
from lsqecc.gates.compress_rotation_approximations import partition_gate_sequence
from lsqecc.pauli_rotations.rotation import CachedRotationApproximations
from lsqecc.gates.pi_over_2_to_the_n_rz_gate_approximations import get_pi_over_2_to_the_n_rz_gate
import numpy as np
import matplotlib.pyplot as plt

# test_sequence_1 = "SSSXHSTHTHSTHTH"
# test_sequence_2 = "SHSSXH"
# test_sequence_3 = "HSSTTSHSH"
# test_sequence = CachedRotationApproximations.get_pi_over_2_to_the_n_rz_gate(3)
# sequences = partition_gate_sequence(test_sequence)
# print(f"The number of gates without compression in Gate Frame is {len(test_sequence)} ")
# print(
#     f"Number of gates without compressiopn in Pauli Frame is {len(test_sequence) + 2*test_sequence.count('H')}"
# )
# print(f"The number of partitions (Compressed list of gates) is {len(sequences)}")

# for seq in sequences:
#     print(f"{seq}")

# Most common ones are HTH and HSTH
gate_counts = np.zeros((len(get_pi_over_2_to_the_n_rz_gate[3:]), 3))
for index, gate_sequence in enumerate(get_pi_over_2_to_the_n_rz_gate[3:]):
    compressed_sequence = partition_gate_sequence(gate_sequence)
    gate_counts[index, 0] = len(gate_sequence)
    gate_counts[index, 1] = len(gate_sequence) + 2 * gate_sequence.count("H")
    gate_counts[index, 2] = len(compressed_sequence)

compression_ratio_mean = np.mean(np.divide(gate_counts[:, 1], gate_counts[:, 2]))

plt.figure(figsize=(16, 9))
plt.plot(
    np.arange(0, len(get_pi_over_2_to_the_n_rz_gate[3:])),
    gate_counts[:, 0],
    label="Uncompressed Gate Count: Gate Frame",
)
plt.plot(
    np.arange(0, len(get_pi_over_2_to_the_n_rz_gate[3:])),
    gate_counts[:, 1],
    label="Uncompressed Gate Count: Pauli Frame",
)
plt.plot(
    np.arange(0, len(get_pi_over_2_to_the_n_rz_gate[3:])),
    gate_counts[:, 2],
    label="Compressed Gate Count: Pauli Frame",
)
plt.xlabel("Rotation amount (in powers of 2)")
plt.ylabel("Gate Count")
plt.title(
    f"Compression of gates in Pauli Frame | Mean Compression Ratio = ={compression_ratio_mean}"
)
plt.legend()
plt.savefig("assets/compression.png")
