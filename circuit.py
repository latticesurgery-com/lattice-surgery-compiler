import numpy as np 
from rotation import Rotation, Measurement, PauliOperator
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


    def copy(self) -> 'Circuit':
        new_circuit = Circuit(self.qubit_num, self.name)
        new_circuit.rotations = [r.copy() for r in self.rotations]


    def add_rotation(self, rotation: Rotation, index: int = None) -> None:
        """
        Add a rotation to the circuit

        Args:
            rotation (Rotation): Targeted rotation
            index (int, optional): Index location. Default: End of the circuit
        """

        if index is None:
            index = len(self)
            
        # print(rotation)
        self.rotations.insert(index, rotation)


    def add_single_operator(self, qubit: int, operator_type: str, rotation_amount: Fraction, index: int = None) -> None:
        """
        Add a single Pauli operator (I, X, Z, Y) to the circuit.

        Args:
            qubit (int): Targeted qubit
            operator_type (str): Operator type ("I", "X", "Y", "Z")
            index (int, optional): Index location. Default: end of the circuit
        """
        
        if index is None:
            index = len(self)

        new_rotation = Rotation(self.qubit_num, rotation_amount)
        new_rotation.change_single_op(qubit, operator_type)

        self.add_rotation(new_rotation, index)


    def apply_transformation(self) -> None:
        """
        Apply Litinski's Transformation

        """
        # TODO: Write the algorithm 

        quarter_rotation = list()

        # Build a stack of pi/4 rotations

        for i in range(len(self.circuit)):
            if isinstance(self.circuit[i], Rotation) and self.circuit[i].rotation_amount in {Fraction(1,4), Fraction(-1,4)}:
                quarter_rotation.append(i)
        
        while quarter_rotation:
            index = quarter_rotation.pop()
            while index < len(self.circuit) - 1:

                if isinstance(self.circuit[index + 1], Rotation):
                    self.merge_measurement(index)
                    break
                
                self.swap_rotation(index)
                index += 1

        pass
    
    def swap_rotation(self, index: int) -> None:
        pass

    def is_commuting(self, gate1: int, gate2: int) -> None:
        pass
    
    def merge_measurement(self, index: int) -> None:
        """
        Merge a pi/4 rotation with it's neighbor measurement 

        Args:
            index (int): index of targeted rotation
        """
        pass

    @staticmethod
    def load_from_pyzx(circuit) -> 'Circuit':
        """
        Generate circuit from PyZX Circuit

        Returns:
            circuit: PyZX Circuit
        """
        import pyzx as zx

        basic_circ = circuit.to_basic_gates()
        ret_circ = Circuit(basic_circ.qubits, circuit.name)

        gate_missed = 0

        for gate in basic_circ.gates:
            # print("Original Gate:", gate)
            
            if isinstance(gate, zx.circuit.ZPhase):
                pauli_rot = gate.phase / 2
                ret_circ.add_single_operator(gate.target, "Z", pauli_rot)


            elif isinstance(gate, zx.circuit.XPhase):
                pauli_rot = gate.phase / 2
                ret_circ.add_single_operator(gate.target, "X", pauli_rot)
                
            elif isinstance(gate, zx.circuit.HAD):
                ret_circ.add_single_operator(gate.target, "X", Fraction(1,4))
                ret_circ.add_single_operator(gate.target, "Z", Fraction(1,4))
                ret_circ.add_single_operator(gate.target, "X", Fraction(1,4))

            elif isinstance(gate, zx.circuit.CNOT):
                temp = Rotation(ret_circ.qubit_num, Fraction(1,4))
                temp.change_single_op(gate.control, "Z")
                temp.change_single_op(gate.target, "X")
                ret_circ.add_rotation(temp)

                ret_circ.add_single_operator(gate.control, "Z", Fraction(-1,4))
                ret_circ.add_single_operator(gate.target, "X", Fraction(-1,4))


            elif isinstance(gate, zx.circuit.CZ):
                temp = Rotation(ret_circ.qubit_num, Fraction(1,4))
                temp.change_single_op(gate.control, "Z")
                temp.change_single_op(gate.target, "Z")
                ret_circ.add_rotation(temp)

                ret_circ.add_single_operator(gate.control, "Z", Fraction(-1,4))
                ret_circ.add_single_operator(gate.target, "Z", Fraction(-1,4))
            else: 
                gate_missed += 1
                print("Failed to convert gate:", gate)
        
        print("Conversion completed")
        print("Gate Missed: ", gate_missed)
        return ret_circ
    