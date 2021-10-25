import enum
import json
from logical_lattice_ops import VisualArrayCell

import lattice_surgery_compilation_pipeline


class JsonResponse:
    def __init__(self, status: int, body: str):
        self.status = status
        self.body = body


class _SliceArrayJSONEncoder(json.JSONEncoder):
    """Used to encode slices (Array[Array[Array[VisualArrayCell]]]) as JSON.
    Necessary to work around the fact that slices contain types that don't convert directly to JSON
    """

    def __init__(self):
        super().__init__()
        self.indent = 2

    def default(self, obj):
        if isinstance(obj, enum.Enum):
            return obj.value
        elif isinstance(obj, VisualArrayCell):
            obj_with_good_keys = obj.__dict__
            obj_with_good_keys['edges'] = dict([(k.value, v) for k, v in obj.edges.items()])
            print(obj_with_good_keys)
            return obj_with_good_keys
        elif (isinstance(obj, object)):
            return obj.__dict__
        return obj


def handle(json_request: str) -> JsonResponse:
    """
    @param json_request:
    Accepts a string containing request for compilation in JSON format. Currently the only supported parameters are:
    {
       circuit : "A string containing a QASM circuit",
       circuit_source : "str", // in the future this will support "file"
       apply_litinski_transform : true | false.
    }

    @return:
    a json containing the following JSON
    {
        slices : Array[Array[Array[VisualArrayCellAsJSON]]]
        compilation_text : "A string containing information about how the compilation process went"
    }
    """
    request_data = json.loads(json_request)

    if 'circuit' in request_data and request_data['circuit_source'] == 'str':
        apply_litinski_transform = request_data[
            'apply_litinski_transform'] if 'apply_litinski_transform' in request_data else True

        slices, compilation_text = lattice_surgery_compilation_pipeline.compile_str(
            request_data['circuit'], apply_litinski_transform)
        respnse_body = {'slices': slices, 'compilation_text': compilation_text}

        return JsonResponse(200, _SliceArrayJSONEncoder().encode(respnse_body))
    else:
        return JsonResponse(501, "Not implemented.\n Request was:\n%s\n" % json.dumps(request_data, indent=4,
                                                                                      sort_keys=True))
