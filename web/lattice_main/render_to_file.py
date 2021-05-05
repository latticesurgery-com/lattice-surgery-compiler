"""
Stand-alone script version of render-to-html-file

Modify the hard-coded filename of the circuit you want to run at the bottom of this script, and update the path to the demo_circuit folder if it has changed. Html file saves in current directory and is git-ignored.
"""

from django.template.loader import render_to_string
from django.conf import settings
import os, django, sys

sys.path.append("..")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lattice_surgery_web.settings_render_to_file")
django.setup()

sys.path.append("../../")
import patches  # TODO remove the dependency on this import
import lattice_surgery_compilation_pipeline
import lattice_surgery_computation_composer
import compiler_options

from typing import *



def render_qasm_file_to_file(circuit_file_name: str, output_file_name: str, options : compiler_options.CompilerOptions) -> None:
    slices, compilation_text = lattice_surgery_compilation_pipeline.compile_file(circuit_file_name, options)
    render_slices_to_file(slices, output_file_name, compilation_text)


def render_slices_to_file(slices: List[lattice_surgery_compilation_pipeline.GUISlice],
                          output_file_name: str,
                          compilation_text : str = "") -> None:

    """ input"""
    context = {
        'slices': slices,
        'patches': patches,
        'compilation_text' : compilation_text
    }
    rendered_page = render_to_string("lattice_main/lattice_view.html",context)
    with open(output_file_name, 'w', encoding="UTF-8") as f:
        f.write(rendered_page)

if __name__ == '__main__':
    DEMO_CIRCUITS_DIR = "../../assets/demo_circuits/"

    circuit = "nontrivial_state.qasm"
    output_filename = "saved.html"

    render_qasm_file_to_file(DEMO_CIRCUITS_DIR + circuit, output_filename)