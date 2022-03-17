from lsqecc.pauli_rotations.rotation import PauliRotation, PauliOperator
from fractions import Fraction

Z = PauliOperator.Z
uncompressed_list = PauliRotation.from_list([Z], Fraction(1, 16)).to_basic_form_decomposition(
    compress_rotations=False
)
print(len(uncompressed_list))
compressed_list = PauliRotation.from_list([Z], Fraction(1, 16)).to_basic_form_decomposition(
    compress_rotations=True
)
print(len(compressed_list))
