import patches

import igraph

from typing import *
from functools import reduce
from ast import literal_eval as make_tuple


# TODO reference to paper explaining this part of the algorithm

def get_pauli_op_listing(
        cell: Tuple[int ,int],
        lattice: patches.Lattice,
        patch_pauli_operator_map: Dict[Tuple[int, int], patches.PauliOperator]):

    # TODO check overlapping with representative and document
    l = list(filter(
        lambda cell: cell in patch_pauli_operator_map,
        lattice.getPatchOfCell(cell).cells))

    if len(l) == 0: return None
    r=lattice.getPatchRepresentative(cell)
    if l[0] != r:
        raise Exception(
            "Non patch repr cell associated with operator: " + str(l[0]) + ". Repr is " + str(r))
    return l[0] if len(l) > 0 else None



def make_graph_of_free_cells(lattice: patches.Lattice) -> igraph.Graph:
    """The vertex labels are the coordinates as a string.
        E.g. "(12,9)"
    """
    g = igraph.Graph(directed=True)
    for row in range(lattice.getRows()):
        for col in range(lattice.getCols()):
            g.add_vertex(str((col, row)))

    nrows = lattice.getRows()
    ncols = lattice.getCols()
    for row in range(nrows):
        for col in range(ncols):
            for neighbour_col, neighbour_row in [(col, row + 1), (col, row - 1), (col + 1, row), (col - 1, row)]:
                if neighbour_col in range(ncols) and neighbour_row in range(nrows) \
                        and lattice.cellIsFree((col, row)) and lattice.cellIsFree((neighbour_col, neighbour_row)):
                    g.add_edges([(str((col, row)), str((neighbour_col, neighbour_row)))])

    return g

def add_directed_edges(
        ancilla_search_graph: igraph.Graph,
        lattice: patches.Lattice,
        patch_pauli_operator_map: Dict[Tuple[int, int], patches.PauliOperator],
        source_patch_vertex: str,
        tagret_patch_vertex: str
    ):

    for j, patch in enumerate(lattice.patches):
        patch_representative = str(patch.getRepresentative())

        # Skip inactive patches
        if patch_representative != source_patch_vertex and patch_representative not in tagret_patch_vertex: continue

        # Add the directed edges
        requested_edge_type = patches.PAULI_OPERATOR_TO_EDGE_MAP[patch_pauli_operator_map[patch.getRepresentative()]]
        for edge in patch.edges:
            in_patch_neighbour = str(edge.cell)
            free_lattice_neighbour = str(edge.getNeighbouringCell())

            if edge.border_type == requested_edge_type and free_lattice_neighbour in ancilla_search_graph.vs["name"]:
                # Add the corresponding directed edge
                if patch.getRepresentative() == source_patch_vertex:
                    ancilla_search_graph.add_edge(patch_representative, in_patch_neighbour)
                    ancilla_search_graph.add_edge(in_patch_neighbour, free_lattice_neighbour)
                else:
                    ancilla_search_graph.add_edge(free_lattice_neighbour, in_patch_neighbour)
                    ancilla_search_graph.add_edge(in_patch_neighbour, patch_representative)



def add_ancilla_to_lattice_from_paths(
        lattice: patches,
        paths: List[List[Tuple[int ,int]]] # Lists of cells
) -> None:

    for path in paths:

        # Shrink the path to the last cells that belong to a qubit patch
        if lattice.getPatchRepresentative(path[0]) == lattice.getPatchRepresentative(path[1]):
            path = path[1:]
        if lattice.getPatchRepresentative(path[-1]) == lattice.getPatchRepresentative(path[-2]):
            path = path[:-1]

        source_patch = lattice.getPatchOfCell(path[0])
        for edge in source_patch.edges:
            if edge.getNeighbouringCell() == path[1]:
                edge.border_type = edge.border_type.stitched_type()

        target_patch = lattice.getPatchOfCell(path[-1])
        for edge in target_patch.edges:
            if edge.getNeighbouringCell() == path[-2]:
                edge.border_type = edge.border_type.stitched_type()

        if len(path)>2:
            for prev_cell, curr_cell, next_cell in zip(path[:-2],path[1:-1],path[2:]):
                if lattice.cellIsFree(curr_cell):
                    lattice.patches.append(patches.Patch(patches.PatchType.Ancilla, None, [curr_cell] ,[]))

                if lattice.getPatchOfCell(curr_cell).patch_type == patches.PatchType.Ancilla:
                    curr_patch = lattice.getPatchOfCell(curr_cell)
                    curr_patch.edges.append(
                        patches.Edge(
                            patches.EdgeType.AncillaJoin,
                            curr_cell,
                            patches.get_border_orientation(curr_cell,next_cell)
                        ))
                    curr_patch = lattice.getPatchOfCell(curr_cell)
                    curr_patch.edges.append(
                        patches.Edge(
                            patches.EdgeType.AncillaJoin,
                            curr_cell,
                            patches.get_border_orientation(curr_cell, prev_cell)
                        ))




def compute_ancilla_cells(
        lattice: patches.Lattice,
        patch_pauli_operator_map: Dict[Tuple[int, int], patches.PauliOperator]
) -> None:

    assert(all(map(lambda cell: lattice.getPatchRepresentative(cell) == cell, patch_pauli_operator_map.keys())))

    # Join all neighbouring free cells with bi directional edges along the lattice
    g = make_graph_of_free_cells(lattice)

    active_qubits = list(map(str, patch_pauli_operator_map.keys()))

    # For path finding purposes separate take one qubit to be the source and the others to be the targets
    source_qubit : str = active_qubits[0]
    target_qubits : str = active_qubits[1:]

    # Connect the active patches each with a single directed edge along the border of the desired operator
    add_directed_edges(
        g,
        lattice,
        patch_pauli_operator_map,
        source_qubit,
        target_qubits)

    # Now find the paths that join al the patches through the desired operators
    shortest_paths_raw = g.get_shortest_paths(source_qubit, target_qubits, mode='all', output='vpath')
    shortest_paths = [[make_tuple(g.vs[v_idx]["name"]) for v_idx in path] for path in shortest_paths_raw]

    #make_path_extremes_join_a_neigbouring_cell(lattice,shortest_paths,op)

    add_ancilla_to_lattice_from_paths(lattice, shortest_paths)


