import lattice_surgery_computation_composer as ls

import qiskit.qasm
import qiskit.qasm.node
import qiskit.qasm.node.node

import functools
import re

from typing import *


__all__ = ['parse']

def parse(qasm_filename : str) -> ls.Circuit:
    """
    Read a QASM file (currently supports only OPENQASM 2.0) into a circuit.

    Supports all gates from the standard library also supported by PyZX, measurements and barriers.
    Barriers have the effect of breaking reversible sections to be passed to pyzx.
    """
    parser = _SegmentedQASMParser(qasm_filename)
    return parser.get_circuit()



class _SegmentedQASMParser:

    # Certain nodes constitute a single segment, others can be in the same one as long as they are
    # Reversible
    Segment = Union[List[qiskit.qasm.node.node.Node],
                    qiskit.qasm.node.If,
                    qiskit.qasm.node.Measure,
                    qiskit.qasm.node.Barrier]
    individual_segment_node_types = {'if','measure'}
    measurement_operator = ls.PauliOperator.Z

    def __init__(self, qasm_filename: str):
        ast = _QASMASTSegmenter.ast_from_file(qasm_filename)

        _SegmentedQASMParser.accept_format_version(ast)

        # TODO use these
        _SegmentedQASMParser.extract_top_lvl_node(ast, 'gate')
        _SegmentedQASMParser.extract_top_lvl_node(ast, 'creg')

        quantum_registers = _SegmentedQASMParser.extract_top_lvl_node(ast, 'qreg')
        if len(quantum_registers) != 1:
            raise Exception('Program must have exactly one quantum register')
        self.qreg = cast(qiskit.qasm.node.qreg.Qreg, quantum_registers[0])

        segments = _QASMASTSegmenter.ast_to_segments(ast)
        sub_circuits = map(self.segment_to_circuit, segments)
        self.circuit = functools.reduce(ls.Circuit.join, sub_circuits)


    def get_circuit(self) -> ls.Circuit:
        return self.circuit

    def segment_to_circuit(self, segment: Segment):
        if isinstance(segment, List):
            return self.reversible_segment_to_circuit(segment)
        elif isinstance(segment,qiskit.qasm.node.Measure):
            return self.measure_node_to_circuit(segment)
        elif isinstance(segment,qiskit.qasm.node.If):
            return self.if_node_to_circuit(segment)
        else:
            raise Exception('Unsupported QASM node type ' + segment.type)

    def reversible_segment_to_circuit(self, segment: List[qiskit.qasm.node.node.Node]) -> ls.Circuit:
        program_wrapper_node = qiskit.qasm.node.Program(segment)
        text_qasm_program_wrapper =\
            'OPENQASM 2.0;\n'+\
            'include "qelib1.inc";\n'+\
            self.qreg.qasm()+"\n"+\
            program_wrapper_node.qasm()

        return ls.Circuit.load_reversible_from_qasm_string(text_qasm_program_wrapper)

    def if_node_to_circuit(self, node: qiskit.qasm.node.if_.If):
        raise NotImplementedError # TODO

    def measure_node_to_circuit(self, measurement_node: qiskit.qasm.node.Measure)\
            -> ls.Circuit:
        c = ls.Circuit(self.num_qubits())

        op_list = [ls.PauliOperator.I] * self.num_qubits()
        measure_idx: int = _SegmentedQASMParser.extract_measurement_idx(measurement_node)
        op_list[measure_idx] = _SegmentedQASMParser.measurement_operator
        c.add_pauli_block(ls.Measurement.from_list(op_list))

        return c

    def num_qubits(self):
        return _SegmentedQASMParser.extract_qreg_size(self.qreg)

    @staticmethod
    def extract_top_lvl_node(program_node : qiskit.qasm.node.program.Program, node_type : str)\
            -> List[qiskit.qasm.node.node.Node]:
        condition = lambda n: n.type == node_type
        take =  [x for x in  program_node.children if condition(x)]
        leave = [x for x in  program_node.children if not condition(x)]
        program_node.children = leave
        return take

    @staticmethod
    def extract_qreg_size(qreg_node : qiskit.qasm.node.Qreg):
        idxd_id : qiskit.qasm.node.IndexedId = qreg_node.id
        return idxd_id.index

    @staticmethod
    def extract_measurement_idx(measurement_node : qiskit.qasm.node.Measure):
        idxd_id: qiskit.qasm.node.indexedid = measurement_node.children[0]
        return idxd_id.index

    @staticmethod
    def accept_format_version(program_node : qiskit.qasm.node.Program) -> None:
        if not isinstance(program_node.children[0], qiskit.qasm.node.Format) \
                or program_node.children[0].qasm() != 'OPENQASM 2.0;':
            raise Exception("First directive must be 'OPENQASM 2.0;'")
        del program_node.children[0]

class _QASMASTSegmenter:

    @staticmethod
    def ast_to_segments(program_node: qiskit.qasm.node.Program) \
            -> List['_SegmentedQASMParser.Segment']:
        gate_segments: List[_SegmentedQASMParser.Segment] = []
        segment_accumulate: List[qiskit.qasm.node.node.Node] = []

        for n in program_node.children:
            if n.type == 'barrier':
                gate_segments.append(segment_accumulate)
                segment_accumulate = []
            elif n.type in _SegmentedQASMParser.individual_segment_node_types:
                gate_segments.append(segment_accumulate)
                gate_segments.append(n)
                segment_accumulate = []
            elif isinstance(n,qiskit.qasm.node.CustomUnitary):
                segment_accumulate.append(n)
            else:
                print("Ignoring unexpected node of type: " + n.type)

        if segment_accumulate:
            gate_segments.append(segment_accumulate)

        return gate_segments

    @staticmethod
    def ast_from_file(filename: str) -> qiskit.qasm.node.program.Program:
        with open(filename) as input_file:
            data = input_file.read()
            if re.search(r'include\s+"qelib1\.inc"\s*;',data) is None:
                raise Exception("Standard library not includes, add 'include \"qelib1.inc\";' to fix")
            qiskit_qasm_file = qiskit.qasm.qasm.Qasm(data=data)
            return qiskit_qasm_file.parse()


