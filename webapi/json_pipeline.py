import lattice_surgery_compilation_pipeline
import json
from typing import *
import visual_array_cell
import enum

class JsonResponse:
    def __init__(self, status: int, body: str):
        self.status = status
        self.body = body

class SliceArrayJSONEncoder(json.JSONEncoder):
    def __init__(self):
        super().__init__()
        self.indent = 2

    def default(self, obj):
        if isinstance(obj, enum.Enum):
            return obj.value
        elif isinstance(obj, visual_array_cell.VisualArrayCell):
            obj_with_good_keys =  obj.__dict__
            obj_with_good_keys['edges'] = dict([(k.value, v) for k, v in obj.edges.items()])
            print(obj_with_good_keys)
            return obj_with_good_keys
        elif(isinstance(obj,object)):
            return obj.__dict__
        return obj


def handle(json_request: str) -> JsonResponse:
    request_data = json.loads(json_request)

    if 'circuit' in request_data and request_data['circuit_source'] == 'str':
        apply_litinski_transform = request_data['apply_litinski_transform'] if 'apply_litinski_transform' in request_data else True

        slices, compilation_text = lattice_surgery_compilation_pipeline.compile_str(
            request_data['circuit'], apply_litinski_transform)
        respnse_body = {'slices':slices, 'compilation_text': compilation_text}

        return JsonResponse(200, SliceArrayJSONEncoder().encode(respnse_body))
    else:
        return JsonResponse(501, "Not implemented.\n Request was:\n%s\n"%json.dumps(request_data, indent=4, sort_keys=True))



