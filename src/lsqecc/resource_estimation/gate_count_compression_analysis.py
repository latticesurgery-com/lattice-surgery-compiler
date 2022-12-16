import matplotlib.pyplot as plt
import numpy as np

from lsqecc.gates.compress_rotation_approximations import partition_gate_sequence
from lsqecc.gates.pi_over_2_to_the_n_rz_gate_approximations import (
    get_pi_over_2_to_the_n_rz_gate_pos,
)

gate_counts_Z = np.zeros((len(get_pi_over_2_to_the_n_rz_gate_pos[3:]), 3))
for index, gate_sequence in enumerate(get_pi_over_2_to_the_n_rz_gate_pos[3:]):
    compressed_sequence = partition_gate_sequence(gate_sequence)
    gate_counts_Z[index, 0] = len(gate_sequence)
    gate_counts_Z[index, 1] = len(gate_sequence) + 2 * gate_sequence.count("H")
    gate_counts_Z[index, 2] = len(compressed_sequence)

gate_counts_X = np.zeros((len(get_pi_over_2_to_the_n_rz_gate_pos[3:]), 3))
for index, gate_sequence in enumerate(get_pi_over_2_to_the_n_rz_gate_pos[3:]):
    compressed_sequence = partition_gate_sequence("H" + gate_sequence + "H")
    gate_counts_X[index, 0] = len(gate_sequence)
    gate_counts_X[index, 1] = len(gate_sequence) + 2 * gate_sequence.count("H") + 6
    gate_counts_X[index, 2] = len(compressed_sequence)


compression_ratio_mean_Z = np.mean(np.divide(gate_counts_Z[:, 1], gate_counts_Z[:, 2]))
compression_ratio_mean_X = np.mean(np.divide(gate_counts_X[:, 1], gate_counts_X[:, 2]))


plt.figure(figsize=(16, 9))
plt.plot(
    np.arange(0, len(get_pi_over_2_to_the_n_rz_gate_pos[3:])),
    gate_counts_Z[:, 0],
    label="Uncompressed Gate Count: Gate Frame",
)
plt.plot(
    np.arange(0, len(get_pi_over_2_to_the_n_rz_gate_pos[3:])),
    gate_counts_Z[:, 1],
    label="Uncompressed Gate Count: Pauli Frame",
)
plt.plot(
    np.arange(0, len(get_pi_over_2_to_the_n_rz_gate_pos[3:])),
    gate_counts_Z[:, 2],
    label="Compressed Gate Count: Pauli Frame",
)
plt.xlabel("Rotation amount (in powers of 2)")
plt.ylabel("Gate Count")
plt.title(
    "Compression of Z Rotation gates in Pauli Frame \n"
    + f" Mean Compression Ratio = ={compression_ratio_mean_Z}"
)
plt.legend()
# plt.savefig("assets/compression_Z_rotations.png")

plt.figure(figsize=(16, 9))
plt.plot(
    np.arange(0, len(get_pi_over_2_to_the_n_rz_gate_pos[3:])),
    gate_counts_X[:, 0],
    label="Uncompressed Gate Count: Gate Frame",
)
plt.plot(
    np.arange(0, len(get_pi_over_2_to_the_n_rz_gate_pos[3:])),
    gate_counts_X[:, 1],
    label="Uncompressed Gate Count: Pauli Frame",
)
plt.plot(
    np.arange(0, len(get_pi_over_2_to_the_n_rz_gate_pos[3:])),
    gate_counts_X[:, 2],
    label="Compressed Gate Count: Pauli Frame",
)
plt.xlabel("Rotation amount (in powers of 2)")
plt.ylabel("Gate Count")
plt.title(
    "Compression of X Rotation gates in Pauli Frame \n"
    + f"Mean Compression Ratio = ={compression_ratio_mean_X}"
)
plt.legend()
# plt.savefig("assets/compression_X_rotations.png")
