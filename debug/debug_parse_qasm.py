import lattice_surgery_computation_composer as ls

from qiskit import circuit as qkcirc
import qiskit.visualization as qkvis
from webgui import lattice_view


import segmented_qasm_parser





class CondtitionOnMeasurement(ls.EvaluationCondition):
    def __init__(self,reference_measurement : ls.Measurement, required_value : int):
        self.reference_measurement = reference_measurement
        self.required_value = required_value

    def does_evaluate(self):
        return self.reference_measurement.get_outcome()==self.required_value


EXAMPLE_FILE="../assets/demo_circuits/bell_pair.qasm"




if __name__ == "__main__":
    compilation_text = ""

    I = ls.PauliOperator.I
    X = ls.PauliOperator.X
    Y = ls.PauliOperator.Y
    Z = ls.PauliOperator.Z

    c = qkcirc.QuantumCircuit.from_qasm_file(EXAMPLE_FILE)
    print(qkvis.circuit_drawer(c).single_string())


    c = segmented_qasm_parser.parse(EXAMPLE_FILE)
    print(c.render_ascii())




