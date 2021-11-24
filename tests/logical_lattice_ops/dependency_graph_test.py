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

from fractions import Fraction

import pytest

from lsqecc.logical_lattice_ops.dependency_graph import DependencyGraph
from lsqecc.pauli_rotations import PauliOpCircuit, PauliOperator, PauliRotation


class TestNode:
    """Tests for DependencyGraph.Node"""

    def test_init(self):
        node = DependencyGraph.Node("test")
        assert node.op == "test"
        assert node.parents == []
        assert node.children == []

    @pytest.mark.parametrize(
        "op, parents, children",
        [
            ("test", [], []),
            ("test", [1, 2, 3], []),
            ("test", [], [1, 2, 3]),
            ("test", [1, 2, 3], [3, 4, 5]),
        ],
    )
    def test_str(self, op, parents, children):
        node = DependencyGraph.Node(op)
        node.parents += [DependencyGraph.Node(p) for p in parents]
        node.children += [DependencyGraph.Node(c) for c in children]
        assert str(node) == f"({op}: Parent: {parents}, Children: {children})"

    def test_eq(self):
        node1 = DependencyGraph.Node("test")
        node2 = DependencyGraph.Node("test")
        assert node1 == node2

    def test_ne(self):
        node1 = DependencyGraph.Node("test")
        node2 = DependencyGraph.Node("test2")
        assert node1 != node2

    def test_add_child(self):
        node = DependencyGraph.Node("test")
        child = DependencyGraph.Node("child")
        node.add_child(child)
        assert node.children == [DependencyGraph.Node("child")]
        assert child.parents == [DependencyGraph.Node("test")]

    def test_add_parent(self):
        node = DependencyGraph.Node("test")
        parent = DependencyGraph.Node("parent")
        node.add_parent(parent)
        assert node.parents == [DependencyGraph.Node("parent")]
        assert parent.children == [DependencyGraph.Node("test")]


class TestDependencyGraph:
    """Tests for DependencyGraph"""

    def test_init(self):
        graph = DependencyGraph()
        assert graph.terminal_node == []

    def test_generate_adjacency_list_empty(self):
        graph = DependencyGraph()
        assert graph.generate_adjacency_list() == {}

    def test_generate_adjacency_list_one_node(self):
        graph = DependencyGraph()
        graph.terminal_node.append(DependencyGraph.Node("test"))
        assert graph.generate_adjacency_list() == {"test": []}

    @pytest.fixture
    def sample_graph(self):
        graph = DependencyGraph()
        node1 = DependencyGraph.Node("test1")
        node2 = DependencyGraph.Node("test2")
        node3 = DependencyGraph.Node("test3")
        node4 = DependencyGraph.Node("test4")
        node5 = DependencyGraph.Node("test5")
        graph.terminal_node += [node1, node2]
        node1.add_child(node3)
        node2.add_child(node3)
        node2.add_child(node4)
        node3.add_child(node5)
        node4.add_child(node5)
        return graph

    def test_generate_adjacency_list(self, sample_graph):
        assert sample_graph.generate_adjacency_list() == {
            "test1": ["test3"],
            "test2": ["test3", "test4"],
            "test3": ["test5"],
            "test4": ["test5"],
            "test5": [],
        }

    def test_generate_edge_list(self, sample_graph):
        assert sample_graph.generate_edge_list() == [
            ("test1", "test3"),
            ("test2", "test3"),
            ("test2", "test4"),
            ("test3", "test5"),
            ("test4", "test5"),
        ]

    @pytest.fixture
    def sample_circuit(self):
        """Sample PauliOpCircuit based on #71"""
        pauli_list = [
            ([PauliOperator.X, PauliOperator.X], Fraction(1, 8)),
            ([PauliOperator.Z, PauliOperator.Z], Fraction(1, 4)),
            ([PauliOperator.X, PauliOperator.Z], Fraction(-1, 4)),
            ([PauliOperator.I, PauliOperator.X], Fraction(-1, 4)),
            ([PauliOperator.Z, PauliOperator.I], Fraction(-1, 4)),
            ([PauliOperator.I, PauliOperator.Z], Fraction(-1, 4)),
        ]
        c = PauliOpCircuit(2)

        for block in pauli_list:
            c.add_pauli_block(PauliRotation.from_list(*block))
        return c

    def test_from_circuit_by_commutation(self, sample_circuit):
        """Testing DAG genration from PauliOpCircuit, example from #71"""
        graph = DependencyGraph.from_circuit_by_commutation(sample_circuit)

        node5 = graph.terminal_node[0]
        node4 = graph.terminal_node[1]
        node3 = node5.children[0]
        node2 = node4.children[0]
        node1 = node2.children[0]
        node0 = node2.children[1]

        assert node0.op == sample_circuit.ops[0]
        assert node1.op == sample_circuit.ops[1]
        assert node3.op == sample_circuit.ops[3]
        assert node2.op == sample_circuit.ops[2]
        assert node4.op == sample_circuit.ops[4]
        assert node5.op == sample_circuit.ops[5]
