from django.shortcuts import render

import os, sys, uuid, shutil
from typing import *

import patches, circuit
from pauli_rotations_to_lattice_surgery import pauli_rotation_to_lattice_surgery_computation

from .sparse_lattice_to_array import sparse_lattice_to_array
from qubit_state import *



def upload_circuit(request):
    context = {}
    return render(request,"lattice_main/upload_circuit.html",context)

def view_compiled(request):
    """ url shortcut name: lattice_main-latticeview """
    # Save the file to a tmp dir so that pyzx can read it
    print("post-request",request.FILES['circuit'].name)

    file_ext = request.FILES['circuit'].name.split('.')[-1]
    circuit_tmp_save_location = os.path.join('/tmp','%s.%s'%(uuid.uuid4(),file_ext))
    intput_circuit_file = request.FILES['circuit']
    intput_circuit_file.seek(0)
    with open(circuit_tmp_save_location, 'wb') as output_file:
        shutil.copyfileobj(intput_circuit_file, output_file)

    input_circuit = circuit.Circuit.load_from_file(circuit_tmp_save_location)
    print(input_circuit.render_ascii())
    os.unlink(circuit_tmp_save_location)

    # TODO refactor the process of getting slices into circuit
    lsc = pauli_rotation_to_lattice_surgery_computation(input_circuit)
    slices = lsc.composer.getSlices()
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