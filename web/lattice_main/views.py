from django.shortcuts import render

import os, sys, uuid, shutil
from typing import *

import patches, circuit
import lattice_surgery_computation_composer as lscc

#from pauli_rotations_to_lattice_surgery import pauli_rotation_to_lattice_surgery_computation

from .sparse_lattice_to_array import sparse_lattice_to_array
from qubit_state import *



def upload_circuit(request):
    path_to_assests = "../assets/"
    circuits = os.listdir(path_to_assests)
    print(circuits)
    context = {"circuits":circuits}
    return render(request,"lattice_main/upload_circuit.html",context)

def view_compiled(request):
    """ url shortcut name: lattice_main-latticeview """
    
    # print(request.POST)

    if "localcircuit" in request.POST: # then select dropdown was used and therefore we have a local copy of the circuit in /assets/
        filename = request.POST['circuit']
        file_ext = filename.split('.')[-1]
        input_circuit_file = open(f"../assets/{filename}", "rb")
    else:
        file_ext = request.FILES['circuit'].name.split('.')[-1]
        # Save the file to a tmp dir so that pyzx can read it
        input_circuit_file = request.FILES['circuit']
    
    tmp_abs_path = os.path.abspath("./lattice_main/tmp/")
    circuit_tmp_save_location = os.path.join(tmp_abs_path,'%s.%s'%(uuid.uuid4(),file_ext))
    input_circuit_file.seek(0)
    with open(circuit_tmp_save_location, 'wb') as output_file:
        shutil.copyfileobj(input_circuit_file, output_file)

    input_circuit = circuit.Circuit.load_from_file(circuit_tmp_save_location)
    print(input_circuit.render_ascii())
    os.unlink(circuit_tmp_save_location)

    # TODO refactor the process of getting slices into circuit
    logical_circuit = lscc.LogicalLatticeComputation(input_circuit)
    if "localcircuit" in request.POST:
        input_circuit_file.close() # close file
    layout_type = lscc.LayoutType.SimplePreDistilledStates
    lattice_comp = lscc.LatticeSurgeryComputation.make_computation_with_simulation(logical_circuit, layout_type)
    
    slices = lattice_comp.composer.getSlices()
    mapped_slices = list(map(sparse_lattice_to_array, slices))
    context = {
        'slices': mapped_slices,
        'patches': patches
    }
    return render(request,"lattice_main/lattice_view.html",context)

# def render_to_file(request,slices, output_file_name): # (slices : List[patches.Lattice], output_file_name : str) -> str
#     slices = list(map(sparse_lattice_to_array, slices))
#     styles_map = styles_map
#     patches = patches
#     context = {
#         "slices":slices,
#         "styles_map":styles_map,
#         "patches":patches
#     }
#     template = Template(filename='templates/lattice_view.mak')
#     with open(output_file_name, 'w') as f:
#         f.write(template.render(
#             slices=list(map(sparse_lattice_to_array, slices)),
#             styles_map=styles_map,
#             patches=patches
#         ))