from enum import Enum
from functools import reduce
from typing import Dict,Union,Optional,List,Tuple
import copy
from ast import literal_eval as make_tuple

import igraph

import patches




class LatticeLayoutInitializer:


    def singleSquarePatch(cell: Tuple[int,int], patch_type=patches.PatchType.Qubit, patch_state=patches.InitializeableState.Zero ):
        return patches.Patch(patch_type, patch_state, [cell],[
            patches.Edge(patches.EdgeType.Solid,  cell, patches.Orientation.Top),
            patches.Edge(patches.EdgeType.Solid,  cell, patches.Orientation.Bottom),
            patches.Edge(patches.EdgeType.Dashed, cell, patches.Orientation.Left),
            patches.Edge(patches.EdgeType.Dashed, cell, patches.Orientation.Right)
        ])

    def simpleRightFacingDistillery(top_left_corner: Tuple[int,int]) -> List[patches.Patch]:
        # Requires
        x,y = top_left_corner
        return [
            LatticeLayoutInitializer.singleSquarePatch((x+2,y), patches.PatchType.DistillationQubit, patches.InitializeableState.Magic),
            LatticeLayoutInitializer.singleSquarePatch((x+3,y), patches.PatchType.DistillationQubit, patches.InitializeableState.Magic),
            LatticeLayoutInitializer.singleSquarePatch((x+4,y+1), patches.PatchType.DistillationQubit, patches.InitializeableState.Plus),
            LatticeLayoutInitializer.singleSquarePatch((x+3,y+2), patches.PatchType.DistillationQubit, patches.InitializeableState.Magic),
            LatticeLayoutInitializer.singleSquarePatch((x+2,y+2), patches.PatchType.DistillationQubit, patches.InitializeableState.Magic),
            patches.Patch(patches.PatchType.DistillationQubit, patches.InitializeableState.Zero, [(x, y), (x, y+1)],
                          [
                              patches.Edge(patches.EdgeType.Solid, (x, y), patches.Orientation.Top),
                              patches.Edge(patches.EdgeType.Solid, (x, y), patches.Orientation.Left),
                              patches.Edge(patches.EdgeType.Dashed,(x, y), patches.Orientation.Right),
                              patches.Edge(patches.EdgeType.Dashed,(x, y+1), patches.Orientation.Left),
                              patches.Edge(patches.EdgeType.Dashed,(x, y+1), patches.Orientation.Bottom),
                              patches.Edge(patches.EdgeType.Solid, (x, y+1), patches.Orientation.Right),
                          ]),
            patches.Patch(patches.PatchType.DistillationQubit, patches.InitializeableState.Magic, [(x+1, y), (x+1, y+1)],
                          [
                              patches.Edge(patches.EdgeType.Dashed,  (x+1, y), patches.Orientation.Top),
                              patches.Edge(patches.EdgeType.Solid,  (x+1, y), patches.Orientation.Left),
                              patches.Edge(patches.EdgeType.Dashed, (x+1, y), patches.Orientation.Right),
                              patches.Edge(patches.EdgeType.Solid, (x+1, y+1), patches.Orientation.Left),
                              patches.Edge(patches.EdgeType.Dashed, (x+1, y+1), patches.Orientation.Bottom),
                              patches.Edge(patches.EdgeType.Solid,  (x+1, y+1), patches.Orientation.Right),
                          ]),
        ]



    def simpleLayout(num_logical_qubits: int) -> patches.Lattice: # a linear array of one spaced square patches with a distillery on one side
        # TODO distillery
        return patches.Lattice([
            LatticeLayoutInitializer.singleSquarePatch((j*2,0)) for j in range(num_logical_qubits)
        ] + LatticeLayoutInitializer.simpleRightFacingDistillery((2*num_logical_qubits,0))
        ,2,0)






class TopologicalAssemblyComposer:
    def __init__(self, initial_layout: patches.Lattice):
        self.qubit_patch_slices : List[patches.Lattice] = [initial_layout] #initialize lattice here

    def initQubit(self, patch_idx:int, state: patches.InitializeableState): # Only initialization of |0> and |+> is predictable
        self.qubit_patch_slices.append(self.qubit_patch_slices[-1])

    def measureSinglePatch(self, patch_idx:int, basisMatrix: patches.PauliMatrix):
        if basisMatrix not in [patches.PauliMatrix.X,patches.PauliMatrix.Z]:
            raise Exception("can't measure with basis matrix "+basisMatrix)
        self.qubit_patches[patch_idx] = None

    def measureMultiPatch(self, patch_operator_map: Dict[Tuple[int,int], patches.PauliMatrix]):
        # TODO graph search for optimal routing
        new_layer : patches.Lattice = copy.deepcopy(self.qubit_patch_slices[-1])

        # Mark edges that need stitching
        stitched_graph_edges:List[Tuple[Tuple[str],Tuple[str]]] = []
        active_qubit_cells:List[str] = []
        for j, patch in enumerate(new_layer.patches):
            for i, edge in enumerate(patch.edges):
                if edge.cell in patch_operator_map:
                    requested_edge_type = patches.operator_to_edge_map[patch_operator_map[edge.cell]]

                    active_qubit_cells.append(str(edge.cell)) if str(edge.cell) not in active_qubit_cells else None

                    if requested_edge_type == edge.border_type:
                        stitched_graph_edges.append(tuple(map(str,patches.Orientation.get_graph_edge(edge))))


        # Compute the ancilla patches

        g = igraph.Graph()
        for row in range(new_layer.getRows()):
            for col in range(new_layer.getCols()):
                g.add_vertex(str((col,row)))

        for row in range(new_layer.getRows()):
            for col in range(new_layer.getCols()):
                for neighbour_col,neighbour_row in [(col,row+1),(col,row-1),(col+1,row),(col-1,row)]:
                    if neighbour_col in range(new_layer.getCols()) and neighbour_row in range(new_layer.getRows()):
                        g.add_edges([(str((col,row)),str((neighbour_col,neighbour_row)))])

        for patch in new_layer.patches:
            if patch.patch_type in [patches.PatchType.Qubit,patches.PatchType.DistillationQubit]:
                for cell in patch.cells:
                    g.delete_vertices([str(cell)])

        g.add_vertices(active_qubit_cells)


        # Now we add the corresponding to the active cell borders. To avoid finding paths that cross a patch
        # we give a direction to the edges going in and out the active patches.

        g.to_directed(mutual=True) # Exisiting egses are bidirectional

        # Filter out the edges that are not connected to patches in the graph
        def edge_in_graph(e):
            v1, v2 = e
            return str(v1) in g.vs.get_attribute_values("name") and str(v2) in g.vs.get_attribute_values("name")
        good_edges = filter(edge_in_graph, stitched_graph_edges)

        # Edges from the first patch are outward, the rest inward
        outward_cells = new_layer.getPatchOfCell(list(patch_operator_map.keys())[0]).cells
        for v1, v2 in good_edges:
            if v1 in outward_cells:
                g.add_edge(v1, v2)
            else:
                g.add_edge(v2, v1)


        shortest_paths = g.get_shortest_paths(active_qubit_cells[0],active_qubit_cells[1:],mode='all',output='vpath')
        shortest_paths_union = [ g.vs[v_idx]["name"] for v_idx in reduce(lambda a,b:a+b, shortest_paths)]

        def is_edge_on_path(egde : patches.Edge):
            v1, v2 = patches.Orientation.get_graph_edge(edge)
            for j in range(len(shortest_paths_union)-1):
                if {str(v1),str(v2)} == {shortest_paths_union[j], shortest_paths_union[j + 1]}:
                    return True
            return False

        # Mark the active edges
        for j, patch in enumerate(new_layer.patches):
            for i, edge in enumerate(patch.edges):
                if edge.cell in patch_operator_map and is_edge_on_path(edge):
                    new_layer.patches[j].edges[i].border_type = edge.border_type.stitched_type()

        ancilla_cells = [make_tuple(v) for v in shortest_paths_union if v not in active_qubit_cells]
        new_layer.patches.append(patches.Patch(patches.PatchType.Ancilla, None, ancilla_cells,[] ))

        self.qubit_patch_slices.append(new_layer)





    def rotateSquarePatch(self, patch_idx: int):
        # assumes: The patch is square, there is room to rotate it
        # TODO make multiple rotations possible at the same time
       pass



    def getSlices(self) -> List[patches.Lattice]:
        return self.qubit_patch_slices