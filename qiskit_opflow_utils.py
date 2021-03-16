import qiskit.aqua.operators as qk
import qiskit.quantum_info as qkinfo
import qiskit.exceptions as qkexcept
import numpy.linalg

from typing import *


class StateSeparator:
    """Namespace for functions that deal with separating states."""
    
    @staticmethod
    def trace_dict_state(state: qk.DictStateFn, trace_over: List[int]) -> qk.DictStateFn:
        """
        Take a state comprised on n qubits and get the trace of the system over the subsystems
        specified by a list of indices.
        
        Assumes state is separable as a DictStateFn can only represent pure states.
        """
        input_statevector = qkinfo.Statevector(state.to_matrix())
        traced_statevector = qkinfo.partial_trace(input_statevector, trace_over).to_statevector()
        return qk.DictStateFn(traced_statevector.to_dict())

    @staticmethod
    def trace_to_density_op(state: qk.DictStateFn, trace_over: List[int]) -> qkinfo.DensityMatrix:
        """
        Take a state comprised on n qubits and get the trace of the system over the subsystems
        specified by a list of indices.
        
        Makes no assumption about the separability of the traced subsystems and gives a density
        matrix as a result.
        """
        input_statevector = qkinfo.Statevector(state.to_matrix())
        return qkinfo.partial_trace(input_statevector, trace_over)

    @staticmethod
    def separate(qnum:int, dict_state : qk.DictStateFn) -> Optional[qk.DictStateFn]:
        """
        When a qubit is not entangled (up to a small tolerance) with the rest of the register,
        trace over the rest of the system, giving the qubits' pure state.

        If the selected qubit is entangled return None.
        """

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
        """
        For each qubit, numerically detect if it's seprabale or not. If it is, add to
        the result dict, indexed by subsystem, the state traced over the remaining qubits.

        I.e. if a qubit is not entangled with the rest, its state shows up in the result. 
        """
        out = {}
        for i in range(dict_state.num_qubits):
            maybe_state = StateSeparator.separate(i, dict_state)
            if maybe_state is not None:
                out[dict_state.num_qubits-i-1] = maybe_state
        return out
