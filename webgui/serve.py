from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config


# Lattice view imports
import webgui.lattice_view
import mako.template as mako


@view_config(route_name='upload_circuit')
def upload_circuit(request):
    page = mako.Template(filename="templates/upload_circuit.mak")
    return Response(page.render(request=request))


@view_config(route_name='lattice_view')
def view_compiled(request):
    return Response('View Compiled')


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