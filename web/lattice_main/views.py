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

def contact(request):
    context = {}
    return render(request,"lattice_main/contact.html",context)

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