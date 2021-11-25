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

from abc import ABC, abstractmethod
from enum import Enum
from fractions import Fraction
from typing import Dict, List, Tuple

import lsqecc.simulation.conditional_operation_control as coc
from lsqecc.utils import phase_frac_to_latex


class PauliOperator(Enum):
    """
    Representation of a Pauli operator inside of a rotation block
    """

    I = "I"  # noqa: E741
    X = "X"
    Y = "Y"
    Z = "Z"

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def are_commuting(a: "PauliOperator", b: "PauliOperator") -> bool:
        """Returns True if a and b are commute and False if anti-commute."""
        if not isinstance(a, PauliOperator) or not isinstance(b, PauliOperator):
            raise TypeError("Only supports PauliOperator")

        if (a, b) in _PauliOperator_anticommute_tbl:
            return False

        else:
            return True

    @staticmethod
    def multiply_operators(a: "PauliOperator", b: "PauliOperator"):
        """Given 2 Pauli operators A and B, return the nearest Pauli operator as the product of A
        and B and the coefficient required for such product.

        Returns:
            tuple: (coefficient, resultant Pauli operator). Coefficient is either 1, -i or i.
        """

        if not isinstance(a, PauliOperator) or not isinstance(b, PauliOperator):
            raise TypeError("Only supports PauliOperator")

        if (a, b) in _PauliOperator_anticommute_tbl:
            return _PauliOperator_anticommute_tbl[(a, b)]

        if a == b:
            return (1, PauliOperator.I)

        if a == PauliOperator.I or b == PauliOperator.I:
            return (1, b if a == PauliOperator.I else a)


_PauliOperator_anticommute_tbl: Dict[
    Tuple["PauliOperator", "PauliOperator"], Tuple[complex, "PauliOperator"]
] = {
    (PauliOperator.Z, PauliOperator.X): (1j, PauliOperator.Y),
    (PauliOperator.X, PauliOperator.Z): (-1j, PauliOperator.Y),
    (PauliOperator.Y, PauliOperator.Z): (1j, PauliOperator.X),
    (PauliOperator.Z, PauliOperator.Y): (-1j, PauliOperator.X),
    (PauliOperator.X, PauliOperator.Y): (1j, PauliOperator.Z),
    (PauliOperator.Y, PauliOperator.X): (-1j, PauliOperator.Z),
}


class PauliProductOperation(ABC):
    def __init__(self, no_of_qubit: int):
        self.qubit_num: int = no_of_qubit
        self.ops_list: List[PauliOperator] = [PauliOperator("I") for i in range(no_of_qubit)]

    @abstractmethod
    def __str__(self) -> str:
        pass

    def __repr__(self) -> str:
        return str(self)

    @abstractmethod
    def __eq__(self, other):
        pass

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    @abstractmethod
    def to_latex(self) -> str:
        return_str = f"({self.ops_list[0]}"
        if self.qubit_num > 1:
            for i in range(1, len(self.ops_list)):
                return_str += r" \otimes" + " " + str(self.ops_list[i])
        return_str += ")"
        return return_str

    def change_single_op(self, qubit: int, new_op: PauliOperator) -> None:
        """Modify a Pauli Operator

        Args:
            qubit (int): Targeted qubit
            new_op (PauliOperator): New operator type (I, X, Z, Y)
        """

        if not isinstance(new_op, PauliOperator):
            raise TypeError("Cannot add type", type(new_op), "to circuit")

        self.ops_list[qubit] = new_op

    def get_op(self, qubit: int) -> PauliOperator:
        """Return the current operator of qubit i.

        Args:
            qubit (int): Targeted qubit

        Returns:
            PauliOperator: Pauli operator of targeted qubit.
        """
        return self.ops_list[qubit]

    def get_ops_map(self) -> Dict[int, PauliOperator]:
        """ "
        Return a map of qubit_n -> operator
        """
        return dict(
            [
                (qn, self.ops_list[qn])
                for qn in range(self.qubit_num)
                if self.ops_list[qn] != PauliOperator.I
            ]
        )


class PauliRotation(PauliProductOperation, coc.ConditionalOperation):
    """Class for representing a Pauli Product Rotation Block."""

    def __init__(self, no_of_qubit: int, rotation_amount: Fraction) -> None:
        """Creating a Pauli Product Rotation Block. All operators are set to I (Identity).
        A Pauli Product Rotation Block MUST span all qubits on the circuit.

        Args:
            no_of_qubit (int): Number of qubits on the circuit
            rotation_amount (Fraction): Rotation amount (e.g. 1/4, 1/8). Implicitly multiplied
                by pi.
        """
        super().__init__(no_of_qubit)
        self.rotation_amount: Fraction = rotation_amount

    def __str__(self) -> str:
        return f"{self.rotation_amount}: {self.ops_list}"

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, PauliRotation)
            and self.rotation_amount == other.rotation_amount
            and self.ops_list == other.ops_list
        )

    def __hash__(self) -> int:
        return hash(hash(self.rotation_amount) + hash(tuple(self.ops_list)))

    def to_latex(self) -> str:
        return f"{super().to_latex()}_{{{phase_frac_to_latex(self.rotation_amount)}}}"

    @staticmethod
    def from_list(pauli_ops: List[PauliOperator], rotation: Fraction) -> "PauliRotation":
        if not pauli_ops:
            raise ValueError("Cannot create PauliRotation from empty list")

        r = PauliRotation(len(pauli_ops), rotation)
        for i, op in enumerate(pauli_ops):
            r.change_single_op(i, op)
        return r


class Measurement(PauliProductOperation, coc.ConditionalOperation):
    """Representing a Pauli Product Measurement Block"""

    def __init__(self, no_of_qubit: int, isNegative: bool = False) -> None:
        """Generate a Pauli Product Measurement Block. All operators are set to I (Identity).
        A Pauli Product Measurement Block MUST span all qubits in the circuit

        Args:
            no_of_qubit (int): Number of qubits in the circuit
            isNegative (bool, optional): Set to negative. Defaults to False.
        """
        super().__init__(no_of_qubit)
        self.isNegative: bool = isNegative

    def __str__(self) -> str:
        sign = "-" if self.isNegative else ""
        return f"{sign}M: {self.ops_list}"

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, Measurement)
            and self.isNegative == other.isNegative
            and self.ops_list == other.ops_list
        )

    def __hash__(self) -> int:
        return hash(hash(self.isNegative) + hash(tuple(self.ops_list)))

    def to_latex(self) -> str:
        return_str = super().to_latex()
        return_str += "_{-M}" if self.isNegative else "_M"
        return return_str

    @staticmethod
    def from_list(pauli_ops: List[PauliOperator], isNegative: bool = False) -> "Measurement":
        if not pauli_ops:
            raise ValueError("Cannot create PauliRotation from empty list")

        m = Measurement(len(pauli_ops), isNegative)
        for i, op in enumerate(pauli_ops):
            m.change_single_op(i, op)

        return m
