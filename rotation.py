import numpy as np
from fractions import Fraction

class Gate(object):
    """
    Class for representing Quantum Gate inside a rotation block. 

    """
    def __init__(self, gate_type: int, qubit: int) -> None:
        """
        Generate a Gate

        Args:
            gate_type (int): 0 = I, 1 = X, 2 = Y, 3 = Z
            qubit (int): Qubit mapped to gate
        """
        self.gate_type = gate_type
        self.qubit = qubit
        
    def __str__(self) -> str:
        option = {
            0: "I",
            1: "X",
            2: "Y",
            3: "Z",
        }
        
        return '{}({})'.format(option[self.gate_type], self.qubit)
        
    def __repr__(self) -> str:
        return str(self)        

    def copy(self):
        return Gate(self.gate_type, self.qubit)

class Rotation(object):
    """
    Class for representing a Pauli Rotation Block 

    """
    def __init__(self, no_of_qubit: int, rotation_amount: Fraction) -> None:
        """
        Creating a Pauli Rotation Block. All gates inside are initialized to Identity. 
        A Pauli Rotation Block MUST span all qubits on the circuit. 

        Args:
            no_of_qubit (int): Number of qubits on the circuit
            rotation_amount (Fraction): Rotation amount (e.g. 1/4, 1/8)
        """

        self.qubit_num = no_of_qubit
        self.rotation_amount = rotation_amount
        self.gate_list = [Gate(0, i) for i in range(no_of_qubit)]
    
    
    def __str__(self):
        return '{}: {}'.format(self.rotation_amount, self.gate_list) 
        
    
    def __repr__(self):
        return str(self)    
    
    
    def copy(self):
        new_rotation = Rotation(self.qubit_num, self.rotation_amount)
        self.gate_list = [g.copy() for g in self.gate_list]
        return new_rotation

    
    def change_gate(self, qubit: int, target_gate: int) -> None:
        """
        Modify a Gate in the Pauli Rotation Block

        Args:
            qubit (int): Targeted qubit
            target_gate (int): New gate type (0 = I, 1 = X, 2 = Z, 3 = Y)
        """
        self.gate_list[qubit] = target_gate

    
    def return_gate(self, qubit: int) -> Gate:
        """
        Return the current gate of qubit i. 

        Args:
            qubit (int): Targeted qubit

        Returns:
            Gate: Gate of targeted qubit.
        """
        return self.gate_list[qubit]

    
        
class Measurement(object):
    """
    Representing a Pauli Product Measurement Block

    """
    def __init__(self, no_of_qubit: int, isNegative: bool = False) -> None:
        """
        Generate a Pauli Product Measurement Block. All gates inside are initialized to Identity.
        A Pauli Product Measurement Block MUST span all qubits in the circuit

        Args:
            no_of_qubit (int): Number of qubits in the circuit
            isNegative (bool, optional): Set to negative. Defaults to False.
        """
        self.qubit_num = no_of_qubit
        self.isNegative = isNegative
        self.gate_list = [Gate(0, i) for i in range(no_of_qubit)]
        
    def __str__(self):
        return '{}M: {}'.format('-' if self.isNegative else '', self.gate_list) 
        
    
    def __repr__(self):
        return str(self)    
    
    
    def copy(self):
        new_rotation = Rotation(self.qubit_num, self.isNegative)
        self.gate_list = [g.copy() for g in self.gate_list]
        return new_rotation

    
    def change_gate(self, qubit: int, target_gate: int) -> None:
        """
        Modify a Gate in the Pauli Rotation Block

        Args:
            qubit (int): Targeted qubit
            target_gate (int): New gate type (0 = I, 1 = X, 2 = Z, 3 = Y)
        """
        self.gate_list[qubit] = target_gate

    
    def return_gate(self, qubit: int) -> Gate:
        """
        Return the current gate of qubit i. 

        Args:
            qubit (int): Targeted qubit

        Returns:
            Gate: Gate of targeted qubit.
        """
        return self.gate_list[qubit]