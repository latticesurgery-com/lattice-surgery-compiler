import numpy as np
from enum import Enum 
from fractions import Fraction


class PauliOperator(Enum):
    """
    Representation of a Pauli operator inside of a rotation block 

    """

    I = "I"
    X = "X"
    Y = "Y"
    Z = "Z"

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return str(self)

        

class Rotation(object):
    """
    Class for representing a Pauli Product Rotation Block 

    """
    def __init__(self, no_of_qubit: int, rotation_amount: Fraction) -> None:
        """
        Creating a Pauli Product Rotation Block. All operators are set to I (Identity). 
        A Pauli Product Rotation Block MUST span all qubits on the circuit. 

        Args:
            no_of_qubit (int): Number of qubits on the circuit
            rotation_amount (Fraction): Rotation amount (e.g. 1/4, 1/8). Implicitly multiplied by pi.
        """

        self.qubit_num = no_of_qubit
        self.rotation_amount = rotation_amount
        self.ops_list = [PauliOperator("I") for i in range(no_of_qubit)]
    
    
    def __str__(self):
        return '{}: {}'.format(self.rotation_amount, self.ops_list) 
        
    
    def __repr__(self):
        return str(self)    
    
    
    def copy(self):
        new_rotation = Rotation(self.qubit_num, self.rotation_amount)
        self.ops_list = [g.copy() for g in self.ops_list]
        return new_rotation

    
    def change_single_op(self, qubit: int, new_op: str) -> None:
        """
        Modify a Pauli Operator in the Pauli Rotation Block

        Args:
            qubit (int): Targeted qubit
            new_op (int): New operator type (I, X, Z, Y)
        """
        self.ops_list[qubit] = PauliOperator(new_op)

    
    def return_operator(self, qubit: int) -> PauliOperator:
        """
        Return the current operator of qubit i. 

        Args:
            qubit (int): Targeted qubit

        Returns:
            PauliOperator: Pauli operator of targeted qubit.
        """
        return self.ops_list[qubit]

    
        
class Measurement(object):
    """
    Representing a Pauli Product Measurement Block

    """
    def __init__(self, no_of_qubit: int, isNegative: bool = False) -> None:
        """
        Generate a Pauli Product Measurement Block. All operators are set to I (Identity). 
        A Pauli Product Measurement Block MUST span all qubits in the circuit

        Args:
            no_of_qubit (int): Number of qubits in the circuit
            isNegative (bool, optional): Set to negative. Defaults to False.
        """
        self.qubit_num = no_of_qubit
        self.isNegative = isNegative
        self.ops_list = [PauliOperator("I") for i in range(no_of_qubit)]
        
    def __str__(self):
        return '{}M: {}'.format('-' if self.isNegative else '', self.ops_list) 
        
    
    def __repr__(self):
        return str(self)    
    
    
    def copy(self):
        new_rotation = Rotation(self.qubit_num, self.isNegative)
        self.ops_list = [g.copy() for g in self.ops_list]
        return new_rotation

    
    def change_single_op(self, qubit: int, new_op: str) -> None:
        """
        Modify a Pauli Operator in the Pauli Rotation Block

        Args:
            qubit (int): Targeted qubit
            new_op (int): New operator type (I, X, Z, Y)
        """
        self.ops_list[qubit] = PauliOperator(new_op)

    
    def return_operator(self, qubit: int) -> PauliOperator:
        """
        Return the current operator of qubit i. 

        Args:
            qubit (int): Targeted qubit

        Returns:
            PauliOperator: Pauli operator of targeted qubit.
        """
        return self.ops_list[qubit]