from typing import *
from circuit import *
import copy

class DependencyGraph: 

    class Node:
        def __init__(self, op: int):
            self.op = op 
            self.parents: List['DependencyGraph.Node'] = list()
            self.children: List['DependencyGraph.Node'] = list()
        
        def __str__(self) -> str:
            return '({}: Parent: {}, Children: {})'.format(self.op, [a.op for a in self.parents], [b.op for b in self.children]) 
    
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
    def from_circuit(circuit : Circuit) -> 'DependencyGraph':
        """
        Build a dependency tree from a Pauli circuit

        """
        ret_graph = DependencyGraph()
        frontier = list()
        current = len(circuit) 
        while current > 0: 
            current -= 1 
            new_node = DependencyGraph.Node(current)
            is_added = False    # Check to avoid adding a node twice or momre

            # First node
            if current == len(circuit) - 1:
                ret_graph.terminal_node.append(new_node)
                frontier.append(new_node)
                continue
            
            for node in copy.copy(frontier): 
                # Non-commuting case: add new dependency 
                if not circuit.are_commuting(node.op, new_node.op):
                    new_node.parents.append(node)
                    node.children.append(new_node)
                    frontier.pop(frontier.index(node))
                    if not is_added:
                        frontier.append(new_node)
                    is_added = True
                    continue
                
                # Commuting case: Traverse the graph backwards, add new dependencies if non-commuting nodes found
                queue = list()
                visited = set()
                queue += node.parents
                # 'Reversed' BFS to avoid traversing deeper than necessary
                while queue:
                    s = queue.pop(0)
                    if not circuit.are_commuting(s.op, new_node.op):
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
            curr = queue.pop()
            if curr.op not in graph:
                graph[curr.op] = list()
            graph[curr.op] += [i.op for i in curr.children]

            for child in curr.children:
                if child.op not in visited:
                    queue.append(child)
                    visited.add(child.op)

        return graph
    