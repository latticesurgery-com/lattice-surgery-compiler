from __future__ import annotations

from ast import literal_eval as make_tuple
from typing import TYPE_CHECKING, Dict, List, Tuple

import igraph
import lsqecc.patches.patches as patches

if TYPE_CHECKING:
    from lsqecc.pauli_rotations import PauliOperator


class AncillaRegionRoutingException(Exception):
    pass


# TODO reference to paper explaining this part of the algorithm


def get_pauli_op_listing(
    cell: Tuple[int, int],
    lattice: patches.Lattice,
    patch_pauli_operator_map: Dict[Tuple[int, int], PauliOperator],
):
    def get_patch_of_cell_from_patch(cell: Tuple[int, int]):
        patch = lattice.getPatchOfCell(cell)
        assert patch is not None
        return patch

    # TODO check overlapping with representative and document
    l = list(
        filter(
            lambda cell: cell in patch_pauli_operator_map, get_patch_of_cell_from_patch(cell).cells
        )
    )

    if len(l) == 0:
        return None
    r = lattice.getPatchRepresentative(cell)
    if l[0] != r:
        raise Exception(
            "Non patch repr cell associated with operator: " + str(l[0]) + ". Repr is " + str(r)
        )
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
            for neighbour_col, neighbour_row in [
                (col, row + 1),
                (col, row - 1),
                (col + 1, row),
                (col - 1, row),
            ]:
                if (
                    neighbour_col in range(ncols)
                    and neighbour_row in range(nrows)
                    and lattice.cellIsFree((col, row))
                    and lattice.cellIsFree((neighbour_col, neighbour_row))
                ):
                    g.add_edges([(str((col, row)), str((neighbour_col, neighbour_row)))])

    return g


def add_directed_edges(
    ancilla_search_graph: igraph.Graph,
    lattice: patches.Lattice,
    patch_pauli_operator_map: Dict[Tuple[int, int], PauliOperator],
    source_patch_vertex: str,
    tagret_patch_vertex: List[str],
):
    for j, patch in enumerate(lattice.patches):
        patch_representative = str(patch.getRepresentative())

        # Skip inactive patches
        if (
            patch_representative != source_patch_vertex
            and patch_representative not in tagret_patch_vertex
        ):
            continue

        # Add the directed edges
        # TODO add Y support
        requested_edge_type = patches.PAULI_OPERATOR_TO_EDGE_MAP[
            patch_pauli_operator_map[patch.getRepresentative()]
        ]
        for edge in patch.edges:
            in_patch_neighbour = str(edge.cell)
            free_lattice_neighbour = str(edge.getNeighbouringCell())

            if (
                edge.border_type == requested_edge_type
                and free_lattice_neighbour in ancilla_search_graph.vs["name"]
            ):
                # Add the corresponding directed edge
                if patch.getRepresentative() == source_patch_vertex:
                    ancilla_search_graph.add_edge(patch_representative, in_patch_neighbour)
                    ancilla_search_graph.add_edge(in_patch_neighbour, free_lattice_neighbour)
                else:
                    ancilla_search_graph.add_edge(free_lattice_neighbour, in_patch_neighbour)
                    ancilla_search_graph.add_edge(in_patch_neighbour, patch_representative)


def add_ancilla_region_to_lattice_from_paths(
    lattice: patches.Lattice, paths: List[List[Tuple[int, int]]]  # Lists of cells
) -> None:
    for path in paths:

        # Shrink the path to the last cells that belong to a qubit patch
        if lattice.getPatchRepresentative(path[0]) == lattice.getPatchRepresentative(path[1]):
            path = path[1:]
        if lattice.getPatchRepresentative(path[-1]) == lattice.getPatchRepresentative(path[-2]):
            path = path[:-1]

        source_patch = lattice.getPatchOfCell(path[0])
        assert source_patch is not None
        for edge in source_patch.edges:
            if edge.getNeighbouringCell() == path[1]:
                edge.border_type = edge.border_type.stitched_type()

        target_patch = lattice.getPatchOfCell(path[-1])
        assert target_patch is not None
        for edge in target_patch.edges:
            if edge.getNeighbouringCell() == path[-2]:
                edge.border_type = edge.border_type.stitched_type()

        if len(path) > 2:
            for prev_cell, curr_cell, next_cell in zip(path[:-2], path[1:-1], path[2:]):
                if lattice.cellIsFree(curr_cell):
                    lattice.patches.append(
                        patches.Patch(patches.PatchType.Ancilla, None, [curr_cell], [])
                    )

                curr_patch = lattice.getPatchOfCell(curr_cell)
                assert curr_patch is not None
                if curr_patch.patch_type == patches.PatchType.Ancilla:
                    curr_patch.edges.append(
                        patches.Edge(
                            patches.EdgeType.AncillaJoin,
                            curr_cell,
                            patches.get_border_orientation(curr_cell, next_cell),
                        )
                    )
                    curr_patch = lattice.getPatchOfCell(curr_cell)
                    assert curr_patch is not None
                    curr_patch.edges.append(
                        patches.Edge(
                            patches.EdgeType.AncillaJoin,
                            curr_cell,
                            patches.get_border_orientation(curr_cell, prev_cell),
                        )
                    )


def compute_ancilla_region_cells(
    lattice: patches.Lattice, patch_pauli_operator_map: Dict[Tuple[int, int], PauliOperator]
) -> None:
    """Compute which cells of the lattice are occupied by the ancilla region to perform the multibody measurement
    specified by the dict of operators.
    """

    assert all(
        map(
            lambda cell: lattice.getPatchRepresentative(cell) == cell,
            patch_pauli_operator_map.keys(),
        )
    )

    # Join all neighbouring free cells with bi directional edges along the lattice
    g = make_graph_of_free_cells(lattice)

    active_qubits = list(map(str, patch_pauli_operator_map.keys()))

    # For path finding purposes separate take one qubit to be the source and the others to be the targets
    source_qubit: str = active_qubits[0]
    target_qubits: List[str] = active_qubits[1:]

    # Connect the active patches each with a single directed edge along the border of the desired operator
    add_directed_edges(g, lattice, patch_pauli_operator_map, source_qubit, target_qubits)

    # Now find the paths that join al the patches through the desired operators
    shortest_paths_raw = g.get_shortest_paths(
        source_qubit, target_qubits, mode="all", output="vpath"
    )
    shortest_paths = [
        [make_tuple(g.vs[v_idx]["name"]) for v_idx in path] for path in shortest_paths_raw
    ]

    if len(shortest_paths) < 1 or len(shortest_paths) == 1 and len(shortest_paths[0]) == 0:
        raise AncillaRegionRoutingException

    add_ancilla_region_to_lattice_from_paths(lattice, shortest_paths)
