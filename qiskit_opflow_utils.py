import qiskit.aqua.operators as qk
import qiskit.quantum_info as qkinfo
import qiskit.exceptions as qkexcept
import numpy.linalg

from typing import *


class StateSeparator:

    @staticmethod
    def trace_dict_state(state: qk.DictStateFn, trace_over: List[int]) -> qk.DictStateFn:
        """Assumes state is separable as a DictStateFn can only represent pure states"""
        input_statevector = qkinfo.Statevector(state.to_matrix())
        traced_statevector = qkinfo.partial_trace(input_statevector, trace_over).to_statevector()
        return qk.DictStateFn(traced_statevector.to_dict())

    @staticmethod
    def trace_to_density_op(state: qk.DictStateFn, trace_over: List[int]) -> qkinfo.DensityMatrix:
        input_statevector = qkinfo.Statevector(state.to_matrix())
        return qkinfo.partial_trace(input_statevector, trace_over)

    @staticmethod
    def separate(qnum:int, dict_state : qk.DictStateFn) -> Optional[qk.DictStateFn]:
        """The closer to zero the closer to being separable"""

        # Qubits are indexed left to right in the dict state so we need to swap
        remaing_qubits = list(range(dict_state.num_qubits))
        remaing_qubits.remove(qnum)

        selected_qubit_maybe_mixed_state = StateSeparator.trace_to_density_op(dict_state, remaing_qubits)

        try:
            selected_qubit_pure_state = selected_qubit_maybe_mixed_state.to_statevector(rtol=10**(-10))
            return qk.DictStateFn(selected_qubit_pure_state.to_dict())

        except qkexcept.QiskitError as e:
            if e.message != 'Density matrix is not a pure state':  raise e
            return None


    @staticmethod
    def get_separable_qubits(dict_state : qk.DictStateFn) -> Dict[int,qk.DictStateFn]:
        out = {}
        for i in range(dict_state.num_qubits):
            maybe_state = StateSeparator.separate(i, dict_state)
            if maybe_state is not None:
                out[i] = maybe_state
        return out