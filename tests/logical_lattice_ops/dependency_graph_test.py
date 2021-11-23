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

import pytest

from lsqecc.logical_lattice_ops.dependency_graph import DependencyGraph


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

    def test_generate_adjacency_list(self):
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
        assert graph.generate_adjacency_list() == {
            "test1": ["test3"],
            "test2": ["test3", "test4"],
            "test3": ["test5"],
            "test4": ["test5"],
            "test5": [],
        }
