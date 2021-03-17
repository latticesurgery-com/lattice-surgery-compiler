from lattice_surgery_computation_composer import *
from webgui import lattice_view
from debug.util import *
import qiskit.quantum_info as qkinfo

if __name__ == "__main__":

    phased_state = (qk.Zero ^ qk.Zero ^ (qk.H @ qk.One).eval() ^ qk.Zero)
    print("Input state:")
    print(phased_state)
    input_statevector = qkinfo.Statevector(phased_state.to_matrix())
    print("Statevector:")
    print( input_statevector)
    #print("DensityMatrix:", qkinfo.DensityMatrix(input_statevector))
    print("Density op, traced:")
    print( qkinfo.partial_trace(input_statevector, [0,2,3]))

    print("separate qubit 1")
    print(StateSeparator.trace_to_density_op(phased_state, [0,2,3]))
    print(StateSeparator.separate(1, phased_state))
