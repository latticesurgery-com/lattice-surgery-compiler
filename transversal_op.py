from conditional_operation_control import *

class TransversalOp():
    pass 


class Hadamard(TransversalOp):
    def __init__(self, target):
        self.qubit: int = target

class CNOT(TransversalOp):
    def __init__(self, control, target):
        self.control: int = control
        self.target: int = target