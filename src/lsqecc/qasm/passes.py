from typing import List

import numpy as np
from qiskit import QuantumCircuit
from qiskit.converters import circuit_to_dag, dag_to_circuit
from qiskit.transpiler import TransformationPass

from lsqecc.gates.parse import IGNORED_INSTRUCTIONS


class ForceReplaceWithDefinitionPass(TransformationPass):
    def __init__(self, gate_names: List[str]):
        super().__init__()
        self.to_force_decompose = gate_names

    def run(self, dag):
        for node in dag.op_nodes():
            if node.op.name in self.to_force_decompose:
                dag.substitute_node_with_dag(node, circuit_to_dag(node.op.definition))
        return dag


class GenericUnitaryToSpecificGate(TransformationPass):
    def run(self, dag):
        for node in dag.op_nodes():
            if node.op.name == "u1":
                angle = node.op.params[0]
                replacement = QuantumCircuit(1)
                if angle == np.pi / 4:
                    replacement.t(0)
                elif angle == -np.pi / 4:
                    replacement.tdg(0)
                else:
                    replacement.rz(angle, 0)
                dag.substitute_node_with_dag(node, circuit_to_dag(replacement))
            if node.op.name == "u2":
                if node.op.params[0] in {0, -2 * np.pi} and node.op.params[1] == np.pi:
                    replacement = QuantumCircuit(1)
                    replacement.h(0)
                    dag.substitute_node_with_dag(node, circuit_to_dag(replacement))
        return dag


class PhasesToRZPass(TransformationPass):
    def run(self, dag):
        for node in dag.op_nodes():
            if node.op.name == "p":
                angle = node.op.params[0]
                replacement = QuantumCircuit(1)
                replacement.rz(angle, 0)
                dag.substitute_node_with_dag(node, circuit_to_dag(replacement))
            if node.op.name == "t":
                replacement = QuantumCircuit(1)
                replacement.rz(np.pi / 4, 0)
                dag.substitute_node_with_dag(node, circuit_to_dag(replacement))
            if node.op.name == "tdg":
                replacement = QuantumCircuit(1)
                replacement.rz(-np.pi / 4, 0)
                dag.substitute_node_with_dag(node, circuit_to_dag(replacement))

        return dag


def drop_circuit_boilerplate(qasm: str) -> str:
    return "\n".join(
        [line for line in qasm.split("\n") if not any(key in line for key in IGNORED_INSTRUCTIONS)]
    )


def collect_circuit_boilerplate(qasm: str) -> str:
    return "\n".join(
        [line for line in qasm.split("\n") if any(key in line for key in IGNORED_INSTRUCTIONS)]
    )


def layer_to_qasm(layer) -> str:
    return dag_to_circuit(layer["graph"]).qasm()


def to_qasm_by_layer(circuit: QuantumCircuit) -> str:
    first_layer = next(circuit_to_dag(circuit).layers())
    qasm = collect_circuit_boilerplate(layer_to_qasm(first_layer)) + "\n"

    layers = circuit_to_dag(circuit).layers()
    for layer in layers:
        qasm += drop_circuit_boilerplate(layer_to_qasm(layer)) + "\n"

    return qasm
