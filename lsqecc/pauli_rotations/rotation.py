from enum import Enum
from fractions import Fraction
from typing import Dict, List, Tuple

import lsqecc.simulation.conditional_operation_control as coc
from lsqecc.utils import phase_frac_to_latex


class PauliOperator(Enum):
    """
    Representation of a Pauli operator inside of a rotation block

    """

    _ignore_ = ["_anticommute_tbl"]
    _anticommute_tbl: Dict[
        Tuple["PauliOperator", "PauliOperator"], Tuple[complex, "PauliOperator"]
    ] = {}

    I = "I"
    X = "X"
    Y = "Y"
    Z = "Z"

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def are_commuting(a: "PauliOperator", b: "PauliOperator") -> bool:
        """
        Returns True if a and b are commute and False if anti-commute.

        """
        if not isinstance(a, PauliOperator) or not isinstance(b, PauliOperator):
            raise Exception("Only supports PauliOperator")

        if (a, b) in PauliOperator._anticommute_tbl:
            return False

        else:
            return True

    @staticmethod
    def multiply_operators(a: "PauliOperator", b: "PauliOperator"):
        """
        Given 2 Pauli operators A and B, return the nearest Pauli operator as the product of A and B and
        the coefficient required for such product.

        Returns:
            tuple: (coefficient, resultant Pauli operator). Coefficient is either 1, -i or i.
        """

        if not isinstance(a, PauliOperator) or not isinstance(b, PauliOperator):
            raise Exception("Only supports PauliOperator")

        if (a, b) in PauliOperator._anticommute_tbl:
            return PauliOperator._anticommute_tbl[(a, b)]

        if a == b:
            return (1, PauliOperator.I)

        if a == PauliOperator.I or b == PauliOperator.I:
            return (1, b if a == PauliOperator.I else a)


PauliOperator._anticommute_tbl = {
    (PauliOperator.Z, PauliOperator.X): (1j, PauliOperator.Y),
    (PauliOperator.X, PauliOperator.Z): (-1j, PauliOperator.Y),
    (PauliOperator.Z, PauliOperator.Y): (1j, PauliOperator.X),
    (PauliOperator.Y, PauliOperator.Z): (-1j, PauliOperator.X),
    (PauliOperator.Y, PauliOperator.X): (1j, PauliOperator.Z),
    (PauliOperator.X, PauliOperator.Y): (-1j, PauliOperator.Z),
}


class PauliProductOperation(coc.ConditionalOperation):
    qubit_num: int
    ops_list: List[PauliOperator]

    def __str__(self) -> str:
        pass

    def __repr__(self) -> str:
        return str(self)

    def to_latex(self) -> str:
        return_str = "(" + str(self.ops_list[0])
        if self.qubit_num > 1:
            for i in range(1, len(self.ops_list)):
                return_str += " \otimes" + " " + str(self.ops_list[i])
        return_str += ")"
        return return_str

    def change_single_op(self, qubit: int, new_op: PauliOperator) -> None:
        """
        Modify a Pauli Operator

        Args:
            qubit (int): Targeted qubit
            new_op (PauliOperator): New operator type (I, X, Z, Y)
        """

        if not isinstance(new_op, PauliOperator):
            raise TypeError("Cannot add type", type(new_op), "to circuit")

        self.ops_list[qubit] = new_op

    def get_op(self, qubit: int) -> PauliOperator:
        """
        Return the current operator of qubit i.

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


class PauliRotation(PauliProductOperation):
    """
    Class for representing a Pauli Product Rotation Block.

    """

    def __init__(self, no_of_qubit: int, rotation_amount: Fraction) -> None:
        """
        Creating a Pauli Product Rotation Block. All operators are set to I (Identity).
        A Pauli Product Rotation Block MUST span all qubits on the circuit.

        Args:
            no_of_qubit (int): Number of qubits on the circuit
            rotation_amount (Fraction): Rotation amount (e.g. 1/4, 1/8). Implicitly multiplied by pi.
        """

        self.qubit_num: int = no_of_qubit
        self.rotation_amount: Fraction = rotation_amount
        self.ops_list: List[PauliOperator] = [PauliOperator("I") for i in range(no_of_qubit)]

    def __str__(self) -> str:
        return "{}: {}".format(self.rotation_amount, self.ops_list)

    def to_latex(self) -> str:
        return_str = super().to_latex()
        return_str += "_" + phase_frac_to_latex(self.rotation_amount)

        return return_str

    @staticmethod
    def from_list(pauli_ops: List[PauliOperator], rotation: Fraction) -> "PauliRotation":
        r = PauliRotation(len(pauli_ops), rotation)
        for i, op in enumerate(pauli_ops):
            r.change_single_op(i, op)
        return r


class Measurement(PauliProductOperation):
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
        self.qubit_num: int = no_of_qubit
        self.isNegative: bool = isNegative
        self.ops_list: List[PauliOperator] = [PauliOperator("I") for i in range(no_of_qubit)]

    def __str__(self) -> str:
        return "{}M: {}".format("-" if self.isNegative else "", self.ops_list)

    def to_latex(self) -> str:
        return_str = super().to_latex()
        return_str += "_{-M}" if self.isNegative else "_M"
        return return_str

    @staticmethod
    def from_list(pauli_ops: List[PauliOperator], isNegative: bool = False) -> "Measurement":
        m = Measurement(len(pauli_ops), isNegative)

        for i, op in enumerate(pauli_ops):
            m.change_single_op(i, op)

        return m
