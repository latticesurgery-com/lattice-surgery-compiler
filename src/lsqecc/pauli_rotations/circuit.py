# Copyright (C) 2020-2021 - George Watkins and Alex Nguyen
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
# USA

import copy
from fractions import Fraction
from typing import List, cast

import pyzx as zx

from lsqecc.utils import phase_frac_to_latex

from .rotation import Measurement, PauliOperator, PauliProductOperation, PauliRotation


class PauliOpCircuit(object):
    """Class for representing quantum circuit."""

    def __init__(self, no_of_qubit: int, name: str = "") -> None:
        """Generating a circuit

        Args:
            no_of_qubit (int): Number of qubits in the circuit
            name (str, optional): Circuit's name (for display). Defaults to ''.
        """
        self.qubit_num: int = no_of_qubit
        self.ops: List[PauliProductOperation] = list()
        self.name: str = name

    def __str__(self) -> str:
        return f"PauliOpCircuit {self.name}: {self.qubit_num} qubit(s), {len(self)} block(s)"

    def __repr__(self) -> str:
        return str(self)

    def __len__(self) -> int:
        return len(self.ops)

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, PauliOpCircuit)
            and self.qubit_num == other.qubit_num
            and self.ops == other.ops
        )

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def copy(self) -> "PauliOpCircuit":
        return copy.deepcopy(self)

    def add_pauli_block(self, new_block: PauliProductOperation, index: int = None) -> None:
        """Add a rotation to the circuit

        Args:
            rotation (PauliRotation): Targeted rotation
            index (int, optional): Index location. Default: End of the circuit
        """

        if new_block.qubit_num != self.qubit_num:
            raise Exception("Amount of qubits do not match.")

        if index is None:
            index = len(self)

        self.ops.insert(index, new_block)

    def add_single_operator(
        self,
        qubit: int,
        operator_type: PauliOperator,
        rotation_amount: Fraction,
        index: int = None,
    ) -> None:
        """Add a single Pauli operator rotation (X, Z, Y) to the circuit.

        Args:
            qubit (int): Targeted qubit
            operator_type (PauliOperator): Operator type (X, Y, Z)
            index (int, optional): Index location. Default: end of the circuit
        """

        if index is None:
            index = len(self)

        new_rotation = PauliRotation(self.qubit_num, rotation_amount)
        new_rotation.change_single_op(qubit, operator_type)

        self.add_pauli_block(new_rotation, index)

    def apply_transformation(self, start_index: int = 0) -> None:
        """Apply Litinski's Transformation"""

        quarter_rotation = list()
        circuit_has_measurements: bool = self.circuit_has_measurements()
        # Build a stack of pi/4 rotations

        for i in range(start_index, len(self)):
            if isinstance(self.ops[i], PauliRotation):
                if cast(PauliRotation, self.ops[i]).rotation_amount in {
                    Fraction(1, 4),
                    Fraction(-1, 4),
                }:
                    quarter_rotation.append(i)

        # Moving all pi/4 rotations towards the end of the circuit
        # and removing them afterwards
        while quarter_rotation:
            index = quarter_rotation.pop()
            while index + 1 < len(self):
                self.swap_adjacent_blocks(index)
                index += 1
            if circuit_has_measurements:
                self.ops.pop()

    def get_y_free_equivalent(self) -> "PauliOpCircuit":
        """Return a Y-operator-free copy of the current circuit."""
        y_free_circuit = PauliOpCircuit(self.qubit_num, self.name)

        for block in self.ops:
            y_free_circuit.ops.extend(block.get_y_free_equivalent())

        return y_free_circuit

    def get_basic_form(self) -> "PauliOpCircuit":
        """
        Returns a circuit where all pauli rotations are either by pi/2, pi/4 or pi/8
        """
        ret_circuit = PauliOpCircuit(self.qubit_num, self.name)
        for op in self.ops:
            if isinstance(op, Measurement):
                ret_circuit.add_pauli_block(op)
            else:
                assert isinstance(op, PauliRotation)
                for new_op in op.get_basic_form_decomposition():
                    ret_circuit.add_pauli_block(new_op)
        return ret_circuit

    def _swap_adjacent_commuting_blocks(self, index: int) -> None:
        """
        Move a pi over four rotation block past its' neighbor block when the blocks commute

        Args:
            index (int): Index of the targeted block in the current circuit
        """
        next_block = index + 1
        if not PauliOpCircuit.are_commuting(self.ops[index], self.ops[next_block]):
            raise Exception("The blocks to be swapped must commute!")

        temp = self.ops[index]
        self.ops[index] = self.ops[next_block]
        self.ops[next_block] = temp

    def _swap_adjacent_anticommuting_blocks(self, index: int) -> None:
        """
        Move a pi over four rotation block past its' neighbor block when the blocks anti-commute

        Args:
            index (int): Index of the targeted block in the current circuit

        """
        next_block = index + 1
        if PauliOpCircuit.are_commuting(self.ops[index], self.ops[next_block]):
            raise Exception("The blocks to be swapped must anti-commute!")

        product_of_coefficients = complex(1)

        for i in range(self.qubit_num):
            new_op = PauliOperator.multiply_operators(
                self.ops[index].get_op(i), self.ops[next_block].get_op(i)
            )

            self.ops[next_block].change_single_op(i, new_op[1])
            product_of_coefficients *= new_op[0]

        # Flip the phase if product of coefficients is negative
        # Product of coefficients will always be either i or -i (see issues #28 for proof)
        product_of_coefficients *= 1j
        if isinstance(self.ops[next_block], Measurement):
            if product_of_coefficients.real < 0:
                measurement = cast(Measurement, self.ops[next_block])
                measurement.isNegative = not measurement.isNegative

        else:
            cast(PauliRotation, self.ops[next_block]).rotation_amount *= (
                -1 if product_of_coefficients.real < 0 else 1
            )

        temp = self.ops[index]
        self.ops[index] = self.ops[next_block]
        self.ops[next_block] = temp

    def swap_adjacent_blocks(self, index: int) -> None:
        """
        Move a pi over four rotation block past its' neighbor block

        Args:
            index (int): Index of the targeted block in the current circuit
        """
        next_block = index + 1
        if next_block >= len(self.ops):
            raise Exception("No operation to commute past")

        if not cast(PauliRotation, self.ops[index]).rotation_amount in {
            Fraction(1, 4),
            Fraction(-1, 4),
        }:
            raise Exception("First operand must be +-pi/4 Pauli rotation")

        if not PauliOpCircuit.are_commuting(self.ops[index], self.ops[next_block]):
            self._swap_adjacent_anticommuting_blocks(index)
        else:
            self._swap_adjacent_commuting_blocks(index)

    def circuit_has_measurements(self) -> bool:
        """Check if circuit has any Measurement blocks.

        Returns:
            bool: True if measurements block are present, False if not present
        """

        for block in self.ops:
            if isinstance(block, Measurement):
                return True
        return False

    @staticmethod
    def are_commuting(block1: PauliProductOperation, block2: PauliProductOperation) -> bool:
        """Check if 2 Pauli Product blocks commute or anti-commute.

        Returns:
            bool: True if they commute, False if they anti-commute
        """
        if block1.qubit_num != block2.qubit_num:
            raise Exception("Blocks must have same number of qubits")

        ret_val = 1

        # Use the fact that:
        # P*Q = (P_1 otimes ... otimes P_n)*(Q_1 otimes ... otimes Q_n)
        #     = (P_1*Q_1 otimes ... otimes P_n*Q_n)
        #
        # Since P_j's and Q_j's are Pauli product blocks, there are
        # coefficients c_j=+-1, such that P_j*Q_j = c_j * Q_j*P_j.
        #
        # Then, since the multiplication by a scalar can be taken
        # out of a tensor product:
        #     Q*P = (c_1*Q_1*P_1 otimes...otimes c_n*Q_n*P_n)
        #     = (c_1*...*c_n)*P*Q
        #
        # The loop below computes (c_1*...*c_n) in ret_val

        for i in range(block1.qubit_num):
            ret_val *= 1 if PauliOperator.are_commuting(block1.get_op(i), block2.get_op(i)) else -1

        return ret_val > 0

    @staticmethod
    def load_from_pyzx(circuit: zx.Circuit) -> "PauliOpCircuit":
        """Generate circuit from PyZX Circuit

        Returns:
            circuit: PyZX Circuit
        """

        X = PauliOperator.X
        Z = PauliOperator.Z

        basic_circ = circuit.to_basic_gates()
        ret_circ = PauliOpCircuit(basic_circ.qubits, circuit.name)

        for gate in basic_circ.gates:
            # print("Original Gate:", gate)

            if isinstance(gate, zx.circuit.ZPhase):
                ret_circ.add_single_operator(gate.target, Z, gate.phase / 2)

            elif isinstance(gate, zx.circuit.XPhase):
                ret_circ.add_single_operator(gate.target, X, gate.phase / 2)

            elif isinstance(gate, zx.circuit.HAD):
                ret_circ.add_single_operator(gate.target, X, Fraction(1, 4))
                ret_circ.add_single_operator(gate.target, Z, Fraction(1, 4))
                ret_circ.add_single_operator(gate.target, X, Fraction(1, 4))

            elif isinstance(gate, zx.circuit.CNOT):
                temp = PauliRotation(ret_circ.qubit_num, Fraction(1, 4))
                temp.change_single_op(gate.control, Z)
                temp.change_single_op(gate.target, X)
                ret_circ.add_pauli_block(temp)

                ret_circ.add_single_operator(gate.control, Z, Fraction(-1, 4))
                ret_circ.add_single_operator(gate.target, X, Fraction(-1, 4))

            elif isinstance(gate, zx.circuit.CZ):
                temp = PauliRotation(ret_circ.qubit_num, Fraction(1, 4))
                temp.change_single_op(gate.control, Z)
                temp.change_single_op(gate.target, Z)
                ret_circ.add_pauli_block(temp)

                ret_circ.add_single_operator(gate.control, Z, Fraction(-1, 4))
                ret_circ.add_single_operator(gate.target, Z, Fraction(-1, 4))

            else:
                raise Exception(f"Failed to convert gate {gate}")

        return ret_circ

    @staticmethod
    def from_list(pauli_op_list: List[PauliProductOperation]):
        c = PauliOpCircuit(pauli_op_list[0].qubit_num)
        for op in pauli_op_list:
            assert c.qubit_num == op.qubit_num
            c.add_pauli_block(op)
        return c

    @staticmethod
    def load_reversible_from_qasm_string(qasm_string: str) -> "PauliOpCircuit":
        """Load a string as if it were a QASM circuit. Only supports reversible circuits."""

        pyzx_circ = zx.Circuit.from_qasm(qasm_string)
        ret_circ = PauliOpCircuit.load_from_pyzx(pyzx_circ)

        return ret_circ

    @staticmethod
    def join(lhs: "PauliOpCircuit", rhs: "PauliOpCircuit") -> "PauliOpCircuit":
        if lhs.qubit_num != rhs.qubit_num:
            raise Exception("The two circuits joined must have the same number of qubits!")
        c = lhs.copy()
        c.ops.extend(rhs.ops)
        return c

    def count_rotations_by(self, rotation_amount: Fraction) -> int:
        return len(
            list(
                filter(
                    lambda r: isinstance(r, PauliRotation) and r.rotation_amount == rotation_amount,
                    self.ops,
                )
            )
        )

    def render_latex(self) -> str:
        """Generate latex render output of the current circuit."""

        from mako.template import Template

        latex_template = Template(filename="assets/circuit_latex_render.mak")

        operator_list: List[str] = list()
        phase_list: List[str] = list()
        for operation in self.ops:
            for operator in operation.ops_list:
                operator_list += str(operator)

            # Latex format for phase label (I didnt want to do this in the template file)
            if isinstance(operation, PauliRotation):
                operator_str = "$" + phase_frac_to_latex(operation.rotation_amount) + "$"

            elif isinstance(operation, Measurement):
                operator_str = "-M" if operation.isNegative else "M"

            phase_list.append(operator_str)

        doc_params = dict(
            qubit_num=self.qubit_num,
            operator_list=operator_list,
            phase_list=phase_list,
        )

        return latex_template.render(**doc_params)

    def render_ascii(self) -> str:
        """Return circuit diagram in text format"""

        cols: List[List[str]] = []

        first_col = list(map(lambda n: "q" + str(n), range(self.qubit_num))) + ["pi*"]
        max_len = max(map(len, first_col))
        # Space padding
        first_col = list(map(lambda s: " " * (max_len - len(s)) + s, first_col))
        cols.append(first_col)

        for op in self.ops:
            if isinstance(op, PauliRotation):
                operator_str = " " if op.rotation_amount.numerator > 0 else ""
                operator_str += (
                    str(op.rotation_amount.numerator) + "/" + str(op.rotation_amount.denominator)
                )
            elif isinstance(op, Measurement):
                operator_str = " -M " if op.isNegative else "  M "

            qubit_line_separator = "-" * (len(operator_str) - 2)

            cols.append([qubit_line_separator] * (self.qubit_num) + [" "])
            cols.append(list(map(lambda op: "|" + op.value + "|", op.ops_list)) + [operator_str])

        out = ""
        for row_n in range(self.qubit_num + 1):
            out += "".join(map(lambda col: col[row_n], cols)) + "\n"
        return out
