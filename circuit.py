import numpy as np 
from rotation import PauliProductOperation, Rotation, Measurement, PauliOperator
from fractions import Fraction
from utils import decompose_pi_fraction
import pyzx as zx
from typing import *


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
        self.qubit_num:     int = no_of_qubit
        self.ops:           List[PauliProductOperation] = list()
        self.name:          str = name 


    def __str__(self) -> str:
        return 'Circuit {}: {} qubit(s), {} rotation(s)'.format(self.name, self.qubit_num, len(self))


    def __repr__(self) -> str:
        return str(self)


    def  __len__(self) -> int:
        return len(self.ops)


    def copy(self) -> 'Circuit':
        new_circuit = Circuit(self.qubit_num, self.name)
        new_circuit.ops = [r.copy() for r in self.ops]


    def add_pauli_block(self, new_block: PauliProductOperation, index: int = None) -> None:
        """
        Add a rotation to the circuit

        Args:
            rotation (Rotation): Targeted rotation
            index (int, optional): Index location. Default: End of the circuit
        """

        if new_block.qubit_num != self.qubit_num:
            raise Exception("Amount of qubits do not match.")

        if index is None:
            index = len(self)
            
        # print(rotation)
        self.ops.insert(index, new_block)


    def add_single_operator(self, qubit: int, operator_type: PauliOperator, rotation_amount: Fraction, index: int = None) -> None:
        """
        Add a single Pauli operator (I, X, Z, Y) to the circuit.

        Args:
            qubit (int): Targeted qubit
            operator_type (PauliOperator): Operator type (I, X, Y, Z)
            index (int, optional): Index location. Default: end of the circuit
        """

        if index is None:
            index = len(self)

        new_rotation = Rotation(self.qubit_num, rotation_amount)
        new_rotation.change_single_op(qubit, operator_type)

        self.add_pauli_block(new_rotation, index)


    def apply_transformation(self) -> None:
        """
        Apply Litinski's Transformation

        """

        # Moving pi/4 to the end of the circuit done. 
        # TODO: Implement merging pi/4 to measurements. 

        quarter_rotation = list()

        # Build a stack of pi/4 rotations

        for i in range(len(self)):
            if isinstance(self.ops[i], Rotation) and self.ops[i].rotation_amount in {Fraction(1,4), Fraction(-1,4)}:
                quarter_rotation.append(i)
        
        while quarter_rotation:
            index = quarter_rotation.pop()
            while index < len(self) - 1:

                # if isinstance(self.ops[index + 1], Measurement):
                #     break
                
                self.commute_pi_over_four_rotation(index)
                index += 1


    def commute_pi_over_four_rotation(self, index: int) -> None:
        """
        Commute a rotation block pass its neighbor block.

        Args:
            index (int): Index of the targeted block in the current circuit. 

        """
        next_block = index + 1

        if next_block >= len(self.ops):
            raise Exception("No operation to commute past")

        if not cast(Rotation,self.ops[index]).rotation_amount in {Fraction(1,4),Fraction(-1,4)}:
            raise Exception("First operand must be +-pi/4 Pauli rotation")

        # Need to calculate iPP' when PP' = -P'P (anti-commute)
        if not self.are_commuting(index, next_block):
            product_of_coefficients = 1
            
            for i in range(self.qubit_num):
                new_op = PauliOperator.multiply_operators(self.ops[index].get_op(i), self.ops[next_block].get_op(i))
                
                self.ops[next_block].change_single_op(i, new_op[1])
                product_of_coefficients *= new_op[0]

            # Flip the phase if product of coefficients is negative
            # Product of coefficients will always be either i or -i (see issues #28 for proof)
            product_of_coefficients /= 1j
            if isinstance(self.ops[next_block], Measurement):
                if product_of_coefficients.real < 0:
                    self.ops[next_block].isNegative = not self.ops[next_block].isNegative

            else:
                self.ops[next_block].rotation_amount *= -1 if product_of_coefficients.real < 0 else 1 

        temp = self.ops[index]
        self.ops[index] = self.ops[next_block]
        self.ops[next_block] = temp
        # print(self.render_ascii())
        

    def are_commuting(self, block1: int, block2: int) -> bool:
        """
        Check if 2 Pauli Product blocks in the circuit (identified by indices) commute or anti-commute.

        Returns:
            bool: True if they commute, False if they anti-commute
        """
        ret_val = 1 

        # Use the fact that:
        # P*Q = (P_1 otimes ... otimes P_n)*(Q_1 otimes ... otimes Q_n)
        #     = (P_1*Q_1 otimes ... otimes P_n*Q_n)
        #
        # Since P_j's and Q_j's are Pauli product blocks, there are coefficients c_j=+-1,
        # such that P_j*Q_j = c_j * Q_j*P_j.
        #
        # Then, since the multiplication by a scalar can be taken out of a tensor product:
        # Q*P = (c_1*Q_1*P_1 otimes...otimes c_n*Q_n*P_n)
        #     = (c_1*...*c_n)*P*Q
        #
        # The loop below computes (c_1*...*c_n) in ret_val
        
        for i in range(self.qubit_num):
            ret_val *= 1 if PauliOperator.are_commuting(self.ops[block1].get_op(i), self.ops[block2].get_op(i)) else -1

        return (ret_val > 0) 
    

    @staticmethod
    def load_from_pyzx(circuit) -> 'Circuit':
        """
        Generate circuit from PyZX Circuit

        Returns:
            circuit: PyZX Circuit
        """
        
        X = PauliOperator.X
        Z = PauliOperator.Z

        basic_circ = circuit.to_basic_gates()
        ret_circ = Circuit(basic_circ.qubits, circuit.name)

        gate_missed = 0

        for gate in basic_circ.gates:
            # print("Original Gate:", gate)
            
            if isinstance(gate, zx.circuit.ZPhase):
                pauli_rot = decompose_pi_fraction(gate.phase / 2)
                for rotation in pauli_rot:
                    if rotation != Fraction(1,1):
                        ret_circ.add_single_operator(gate.target, Z, rotation)


            elif isinstance(gate, zx.circuit.XPhase):
                pauli_rot = decompose_pi_fraction(gate.phase / 2)
                for rotation in pauli_rot:
                    if rotation != Fraction(1,1):
                        ret_circ.add_single_operator(gate.target, X, rotation)


            elif isinstance(gate, zx.circuit.HAD):
                ret_circ.add_single_operator(gate.target, X, Fraction(1,4))
                ret_circ.add_single_operator(gate.target, Z, Fraction(1,4))
                ret_circ.add_single_operator(gate.target, X, Fraction(1,4))


            elif isinstance(gate, zx.circuit.CNOT):
                temp = Rotation(ret_circ.qubit_num, Fraction(1,4))
                temp.change_single_op(gate.control, Z)
                temp.change_single_op(gate.target, X)
                ret_circ.add_pauli_block(temp)

                ret_circ.add_single_operator(gate.control, Z, Fraction(-1,4))
                ret_circ.add_single_operator(gate.target, X, Fraction(-1,4))


            elif isinstance(gate, zx.circuit.CZ):
                temp = Rotation(ret_circ.qubit_num, Fraction(1,4))
                temp.change_single_op(gate.control, Z)
                temp.change_single_op(gate.target, Z)
                ret_circ.add_pauli_block(temp)

                ret_circ.add_single_operator(gate.control, Z, Fraction(-1,4))
                ret_circ.add_single_operator(gate.target, Z, Fraction(-1,4))


            else: 
                gate_missed += 1
                print("Failed to convert gate:", gate)
        
        print("Conversion completed")
        print("Gate Missed: ", gate_missed)
        return ret_circ

   
    @staticmethod
    def load_from_file(fname: str) -> 'Circuit':
        """
        Generate circuit from file. Supported formats are QASM, QC and Quipper ASCII (per PyZX)
        """

        pyzx_circ = zx.Circuit.load(fname)
        ret_circ = Circuit.load_from_pyzx(pyzx_circ)

        return ret_circ


    def count_rotations_by(self, rotation_amount : Fraction) -> int:
        return len(list(filter(lambda r: isinstance(r, Rotation) and r.rotation_amount==rotation_amount, self.ops)))

   
    def render_ascii(self) -> str:
        """
        Return circuit diagram in text format 
        """

        cols : List[List[str]] = []

        first_col = list(map(lambda n: 'q'+str(n),range(self.qubit_num))) + ["pi*"]
        max_len = max(map(len,first_col))
        # Space padding
        first_col = list(map(lambda s: ' '*(max_len-len(s))+s,first_col))
        cols.append(first_col)

        for op in self.ops:
            if isinstance(op, Rotation):
                operator_str = " " if op.rotation_amount.numerator > 0 else ""
                operator_str += str(op.rotation_amount.numerator) + "/" + str(op.rotation_amount.denominator)
            elif isinstance(op, Measurement):
                operator_str = ' -M ' if op.isNegative else '  M '


            qubit_line_separator = '-'*(len(operator_str)-2)

            cols.append([qubit_line_separator]*(self.qubit_num) + [" "])
            cols.append(list(map(lambda op: "|"+op.value+"|", op.ops_list)) + [operator_str])

        out = ""
        for row_n in range(self.qubit_num+1):
            out += "".join(map(lambda col: col[row_n],cols)) + "\n"
        return out