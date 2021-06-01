from conditional_operation_control import *
from rotation import Rotation, PauliOperator
from fractions import Fraction

class TransversalOp():
    pass 


class Hadamard(TransversalOp):
    def __init__(self, target):
        self.qubit: int = target

    def to_pauli_rotation(self, qubit_count):
        rotation1 = Rotation(qubit_count, Fraction(1,4))
        rotation1.change_single_op(self.qubit, PauliOperator.X)

        rotation2 = Rotation(qubit_count, Fraction(1,4))
        rotation2.change_single_op(self.qubit, PauliOperator.Z)

        rotation3 = Rotation(qubit_count, Fraction(1,4))
        rotation3.change_single_op(self.qubit, PauliOperator.X)

        return rotation1, rotation2, rotation3
        

class TransversalX(TransversalOp):
    def __init__(self, target):
        self.qubit: int = target

    def to_pauli_rotation(self, qubit_count):
        ret_rotation = Rotation(qubit_count, Fraction(1,2))
        ret_rotation.change_single_op(self.qubit, PauliOperator.X)
        return ret_rotation


class TransversalY(TransversalOp):
    def __init__(self, target):
        self.qubit: int = target

    
    def to_pauli_rotation(self, qubit_count):
        ret_rotation = Rotation(qubit_count, Fraction(1,2))
        ret_rotation.change_single_op(self.qubit, PauliOperator.Z)
        return ret_rotation