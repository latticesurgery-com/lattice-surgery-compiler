#### Stand-alone script version of render. (not yet sure why the CSS won't render)

from django.template.loader import render_to_string
from django.conf import settings
import os, django, sys

sys.path.append("..")
os.environ.setdefault("DJANGO_SETTINGS_MODULE","lattice_surgery_web.settings_template_test")
django.setup()

sys.path.append("../../")
import patches # TODO remove the dependency on this import
import lattice_surgery_compilation_pipeline

def render_to_file(circuit_file_name: str, output_file_name: str, apply_litinski_transform: bool=True) -> str:
    """ input"""
    slices, compilation_text = lattice_surgery_compilation_pipeline.compile_file(circuit_file_name,apply_litinski_transform)
    context = {
        'slices': slices,
        'patches': patches,
        'compilation_text' : compilation_text
    }
    rendered_page = render_to_string("lattice_main/lattice_view.html",context)
    with open(output_file_name, 'w', encoding="UTF-8") as f:
        f.write(rendered_page)

DEMO_CIRCUITS_DIR = "../../assets/demo_circuits/"

circuit = "nontrivial_state.qasm"
output_filename = "saved.html"

render_to_file(DEMO_CIRCUITS_DIR + circuit, output_filename)