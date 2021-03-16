from typing import *
import qiskit.aqua.operators as qk


def nice_print_dict_of_dict_states(ds : Dict[int,qk.DictStateFn]) -> str:
    out = "{"
    for k ,v in ds.items():
        out += "\n\t" + str(k) + " : "
        out +=        str(v.primitive) + " ,"
    return out + "}"
