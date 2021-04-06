from django.shortcuts import render,redirect
from django.template.loader import render_to_string

import os, sys, uuid, shutil, sys
from typing import *

import lattice_surgery_compilation_pipeline
import patches # TODO remove the dependency on this import


PATH_TO_DEMO_CIRCUITS="../assets/demo_circuits"

def upload_circuit(request):
    demo_circuits = [circuit for circuit in os.listdir(PATH_TO_DEMO_CIRCUITS) if ".qasm" in circuit]
    #print(demo_circuits)
    context = {"demo_circuits":demo_circuits}
    return render(request,"lattice_main/upload_circuit.html",context)

def view_compiled(request):
    """ url shortcut name: lattice_main-latticeview """
    # print(request.POST)
    if "localcircuit" in request.POST: # then select dropdown was used and therefore we have a local copy of the circuit in /assets/
        filename = request.POST['circuit']
        file_ext = filename.split('.')[-1]
        input_circuit_file = open(f"{PATH_TO_DEMO_CIRCUITS}/{filename}", "rb")
    else:
        file_ext = request.FILES['circuit'].name.split('.')[-1]
        # Save the file to a tmp dir so that pyzx can read it
        input_circuit_file = request.FILES['circuit']
    
    tmp_abs_path = os.path.abspath("./lattice_main/tmp/")
    circuit_tmp_save_location = os.path.join(tmp_abs_path,'%s.%s'%(uuid.uuid4(),file_ext))
    input_circuit_file.seek(0)

    with open(circuit_tmp_save_location, 'wb') as output_file:
        shutil.copyfileobj(input_circuit_file, output_file)

    apply_litinski_transform = True
    if "litinski" not in request.POST:
        apply_litinski_transform = False
    print(apply_litinski_transform)

    try:
        slices, compilation_text = lattice_surgery_compilation_pipeline.compile_file(circuit_tmp_save_location,apply_litinski_transform)
    finally:
        os.unlink(circuit_tmp_save_location)

    context = {
        'slices': slices,
        'patches': patches,
        'compilation_text' : compilation_text
    }
    return render(request,"lattice_main/lattice_view.html",context)

# def render_to_file(request) -> str:
#     # circuit_file_name: str, output_file_name: str, apply_litinski_transform: bool=True) -> str:
#     """ 
#     save output to file for debugging by calling the url /render_file/
#     hard-code desired circuit input name, make sure the file is in /web/ folder (appending assets dir isn't working)
#     outputs to /web/ directory with name given by output_file
#     """
#     print("current working directory: \n",os.getcwd())
#     #sys.path.append(PATH_TO_DEMO_CIRCUITS)
#     circuit_file_name = "nontrivial_state.qasm"
#     apply_litinski_transform = True
#     output_file_name = "saved.html"

#     slices, compilation_text = lattice_surgery_compilation_pipeline.compile_file(circuit_file_name,apply_litinski_transform)
#     context = {
#         'slices': slices,
#         'patches': patches,
#         'compilation_text' : compilation_text
#     }
#     rendered_page = render_to_string("lattice_main/lattice_view.html",context)
#     with open(output_file_name, 'w', encoding="UTF-8") as f:
#         f.write(rendered_page)

#     return redirect('/')

