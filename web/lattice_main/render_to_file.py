#### Stand-alone script version of render. (not yet sure why the CSS won't render)


from django.template.loader import render_to_string
import os, django, sys

sys.path.append("..")
os.environ.setdefault("DJANGO_SETTINGS_MODULE","lattice_surgery_web.settings")
django.setup()


sys.path.append("../../")
import patches # TODO remove the dependency on this import
import lattice_surgery_compilation_pipeline

sys.path.append("../assets/demo_circuits/")
# TODO restore this for debugging
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

c = "nontrivial_state.qasm"
render_to_file(c,'saved.html')