import numpy as np 
from rotation import Rotation, Gate
from fractions import Fraction

class Circuit(object):
    """
    Class for representing quantum circuit.

    """

    def __init__(self, no_of_qubit: int, name: str = '') -> None:
        """
        Generating a circuit

        Args:
            no_of_qubit (int): Number of qubits in the circuit
            name (str, optional): Circuit's name (for display). Defaults to ''.
        """
        self.qubit_num = no_of_qubit
        self.rotations = list()
        self.name = name 


    def __str__(self) -> str:
        return 'Circuit {}: {} qubit(s), {} rotation(s)'.format(self.name, self.qubit_num, len(self))


    def __repr__(self) -> str:
        return str(self)


    def  __len__(self) -> int:
        return len(self.rotations)


    def copy(self) -> Circuit:
        new_circuit = Circuit(self.qubit_num, self.name)
        new_circuit.rotations = [r.copy() for r in self.rotations]


    def add_rotation(self, rotation: Rotation, index: int = len(self) - 1) -> None:
        """
        Add a rotation to the circuit

        Args:
            rotation (Rotation): Targeted rotation
            index (int, optional): Index location. Default: End of the circuit
        """
        self.rotations.insert(index, rotation)


    def add_single_gate(self, qubit: int, gate_type: int, rotation_amount: Fraction, index: int = len(self) - 1) -> None:
        """
        Add a single gate (I, X, Z, Y) to the circuit.

        Args:
            qubit (int): Targeted qubit
            gate_type (int): Gate type (0 = I, 1 = X, 2 = Z, 3 = Y)
            index (int, optional): Index location. Default: end of the circuit
        """
        
        new_rotation = Rotation(self.qubit_num, rotation_amount)
        new_rotation.change_gate(qubit, gate_type)

        self.add_rotation(new_rotation, index)


    def apply_transformation(self) -> None:
        """
        Apply Litinski's Transformation

        """
        # TODO: Write the algorithm 
        pass

    
    