from webapi import json_pipeline

from http.server import BaseHTTPRequestHandler, HTTPServer
import http.client
import json
import enum
import traceback
from typing import *


class Routes(enum.Enum):
    COMPILE = '/compile'


class _LocalCompilerApiServer(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        print("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n" % (
            str(self.path), str(self.headers), post_data.decode('utf-8')))
        if str(self.path) == Routes.COMPILE.value:
            try:
                response = json_pipeline.handle(post_data.decode('utf-8'))
                self.send_response(response.status)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(response.body.encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write("{}\n\nRequest was {}".format(traceback.format_exc(), post_data.decode('utf-8')).encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("POST Route not found: {}".format(self.path).encode('utf-8'))


SAMPLE_CIRCUIT = """
OPENQASM 2.0;
include "qelib1.inc";

qreg q[2];

h q[0];
cx q[0],q[1];
h q[0];
t q[1];
s q[0];
x q[0];
"""

JSON_POST_PARAMETERS = {
    'circuit_source': 'str',  # alternative would be 'file'
    'circuit': SAMPLE_CIRCUIT,
    'apply_litinski_transform': True
}


def probe(request_post_params: Optional[Dict] = None):
    if request_post_params is None:
        request_post_params = JSON_POST_PARAMETERS

    conn = http.client.HTTPConnection('localhost:9876')
    headers = {'Content-type': 'application/json'}

    conn.request('POST', '/compile', json.dumps(request_post_params), headers)

    response = conn.getresponse()
    print(response.read().decode())


if __name__ == "__main__":
    server_address = ('', 9876)
    httpd = HTTPServer(server_address, _LocalCompilerApiServer)
    httpd.serve_forever()
