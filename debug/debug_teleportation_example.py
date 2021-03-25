import circuit
import lattice_surgery_computation_composer as ls
import logical_lattice_ops
import sparse_lattice_to_array
from visual_array_cell import *

from qiskit import circuit as qkcirc
import qiskit.visualization as qkvis
from webgui import lattice_view



class CondtitionOnMeasurement(ls.EvaluationCondition):
    def __init__(self,reference_measurement : ls.Measurement, required_value : int):
        self.reference_measurement = reference_measurement
        self.required_value = required_value

    def does_evaluate(self):
        return self.reference_measurement.get_outcome()==self.required_value

if __name__ == "__main__":
    compilation_text = ""

    I = ls.PauliOperator.I
    X = ls.PauliOperator.X
    Y = ls.PauliOperator.Y
    Z = ls.PauliOperator.Z

    # Construct in parallel a quiskit circuit to print and an equivalent pauli circuit to execute
    # The construtction of the pauli rotation circuit get's kick started with gates from the other circuit,
    # so it is initialized below

    crz = qkcirc.ClassicalRegister(1)
    crx = qkcirc.ClassicalRegister(1)
    qreg = qkcirc.QuantumRegister(3)
    qiskit_circ = qkcirc.QuantumCircuit(qreg, crx, crz)


    # Entangle a Bell pair. 1 is Alice's 2 is Bob's
    qiskit_circ.h(1)
    qiskit_circ.cx(1, 2)
    qiskit_circ.barrier()

    # Create a non trivial state in q0, the one Alice wants to send to Bob.
    qiskit_circ.h(0)
    qiskit_circ.t(0)
    qiskit_circ.h(0)
    qiskit_circ.barrier()

    # Alice's  part of the teleportation
    qiskit_circ.cx(0, 1)
    qiskit_circ.h(0)
    qiskit_circ.barrier()


    print(qiskit_circ.qasm())
    # Here is where the circuit of pauli rotations is initialized
    input_circuit = ls.Circuit.load_from_quasm_string(qiskit_circ.qasm())

    # measure q[0] -> c[0];
    qiskit_circ.measure(0, crz)
    m1 = ls.Measurement.from_list([X, I, I])
    input_circuit.add_pauli_block(m1)

    # measure q[1] -> c[1];
    qiskit_circ.measure(1, crx)
    m2 = logical_lattice_ops.Measurement.from_list([I, X, I])
    input_circuit.add_pauli_block(m2)

    compilation_text += "State preparation Circuit\n"
    compilation_text += qkvis.circuit_drawer(qiskit_circ).single_string()

    compilation_text += "State preparation Circuit Litinski\n"
    first_non_bell_preparation_rotation = 6
    input_circuit.apply_transformation(first_non_bell_preparation_rotation)
    compilation_text += input_circuit.render_ascii()

    # Bob's recovery of the state with the help of the classical bits

    qiskit_circ.x(2).c_if(crx, 1)
    ls_cx = ls.Rotation.from_list([I, I, X], ls.Fraction(1,2))
    ls_cx.set_condition(CondtitionOnMeasurement(m1,1))
    input_circuit.add_pauli_block(ls_cx)

    qiskit_circ.z(2).c_if(crz, 1)
    ls_cz = ls.Rotation.from_list([I, I, Z], ls.Fraction(1,2))
    ls_cz.set_condition(CondtitionOnMeasurement(m2, 1))
    input_circuit.add_pauli_block(ls_cz)

    # q[2] now holds the non trivial state Alice wanted to transfer

    compilation_text += "Input Circuit:\n"

    compilation_text += qkvis.circuit_drawer(qiskit_circ).single_string()

    compilation_text += "\nCircuit as Pauli rotations:\n"
    compilation_text += input_circuit.render_ascii()

    print(compilation_text)

    logical_computation = logical_lattice_ops.LogicalLatticeComputation(input_circuit)
    lsc = ls.LatticeSurgeryComputation.make_computation_with_simulation(logical_computation, ls.LayoutType.SimplePreDistilledStates)

    lattice_view.render_to_file(lsc.composer.getSlices(), "index.html", template="/home/george/courses/CMPT415_498/code/lattice-surgery-compiler/webgui/templates/lattice_view.mak")





