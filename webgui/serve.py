import circuit
import segmented_qasm_parser

from pauli_rotations_to_lattice_surgery import pauli_rotation_to_lattice_surgery_computation
import webgui.lattice_view

from wsgiref.simple_server import make_server
import mako.template
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.request import Request

import os
import uuid
import shutil



@view_config(route_name='upload_circuit')
def upload_circuit(request):
    page = mako.template.Template(filename="templates/upload_circuit.mak")
    return Response(page.render(request=request))


@view_config(route_name='lattice_view')
def view_compiled(request : Request):

    # Save the file to a tmp dir so that pyzx can read it
    file_ext = request.POST['circuit'].filename.split('.')[-1]
    circuit_tmp_save_location = os.path.join('/tmp','%s.%s'%(uuid.uuid4(),file_ext))
    intput_circuit_file = request.POST['circuit'].file
    intput_circuit_file.seek(0)
    with open(circuit_tmp_save_location, 'wb') as output_file:
        shutil.copyfileobj(intput_circuit_file, output_file)

    input_circuit = segmented_qasm_parser.parse_file(circuit_tmp_save_location)
    print(input_circuit.render_ascii())
    os.unlink(circuit_tmp_save_location)

    # TODO refactor the process of getting slices into circuit
    lsc = pauli_rotation_to_lattice_surgery_computation(input_circuit)
    return Response(webgui.lattice_view.render_html(lsc.composer.getSlices()))


if __name__ == '__main__':
    with Configurator() as config:
        config.add_route('upload_circuit', '/')
        config.add_route('lattice_view', '/lattice_view')
        config.add_route('static', '/static')
        config.add_static_view(name='static', path='static')
        config.scan()
        app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 6543, app)
    server.serve_forever()