import copy
from lsqecc.pauli_rotations import Circuit
from typing import List, TypeVar

T = TypeVar('T')


class DependencyGraph:
    class Node:
        def __init__(self, op: T):
            self.op = op
            self.parents: List['DependencyGraph.Node'] = list()
            self.children: List['DependencyGraph.Node'] = list()

        def __str__(self) -> str:
            return '({}: Parent: {}, Children: {})'.format(self.op, [a.op for a in self.parents],
                                                           [b.op for b in self.children])

        def __repr__(self) -> str:
            return str(self)

        def __eq__(self, other) -> bool:
            if isinstance(other, DependencyGraph.Node):
                return self.op == other.op
            else:
                return False

    def __init__(self):
        self.terminal_node = list()

    @staticmethod
    def from_circuit_by_commutation(circuit: Circuit) -> 'DependencyGraph':
        """
        Build a dependency tree from a Pauli rotation circuit based on commutation.

        """

        # This because new dependency is added between non-commuting operations
        def func(arg1, arg2):
            return not Circuit.are_commuting(arg1, arg2)

        return DependencyGraph.from_list(circuit.ops, func)

    @staticmethod
    def from_list(input_list: list(), comparing_function) -> 'DependencyGraph':
        """
        Build a DependencyGraph from a list.

        Args:
            input_list: list used to generate the graph
            comparing_function: function used for deciding dependency
             in the graph. New dependency is added when it returns True.

        """

        ret_graph = DependencyGraph()
        frontier = list()
        current = len(input_list)
        while current > 0:
            current -= 1
            new_node = DependencyGraph.Node(input_list[current])
            is_added = False  # Check to avoid adding a node twice or momre

            # First node
            if current == len(input_list) - 1:
                ret_graph.terminal_node.append(new_node)
                frontier.append(new_node)
                continue

            for node in copy.copy(frontier):
                # comparing_function() returns True: add new dependency
                if comparing_function(node.op, new_node.op):
                    new_node.parents.append(node)
                    node.children.append(new_node)
                    frontier.pop(frontier.index(node))
                    if not is_added:
                        frontier.append(new_node)
                    is_added = True
                    continue

                # Else: traverse the graph backwards, add new dependencies if
                # found nodes to which comparing_function() return True to.
                queue = list()
                visited = set()
                queue += node.parents
                # 'Reversed' BFS to avoid traversing deeper than necessary
                while queue:
                    s = queue.pop(0)
                    if comparing_function(s.op, new_node.op):
                        new_node.parents.append(s)
                        s.children.append(new_node)
                        is_added = True
                        continue

                    for parent in s.parents:
                        if parent.op not in visited:
                            visited.add(parent.op)
                            queue.append(parent)

            if not is_added:
                ret_graph.terminal_node.append(new_node)
                frontier.append(new_node)

        return ret_graph

    def generate_adjacency_list(self):
        # Currently used to print out the tree, but might come useful in the future :wink:
        graph = dict()
        visited = set()
        queue = list()
        queue += self.terminal_node

        while queue:
            curr = queue.pop(0)
            if curr.op not in graph:
                graph[curr.op] = list()
            graph[curr.op] += [i.op for i in curr.children]

            for child in curr.children:
                if child.op not in visited:
                    queue.append(child)
                    visited.add(child.op)

        return graph

    def generate_edge_list(self):
        adjacency_list = self.generate_adjacency_list()
        return_list = list()
        for node in adjacency_list:
            for child in adjacency_list[node]:
                return_list.append((node, child))

        return return_list
