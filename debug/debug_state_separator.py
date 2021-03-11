import sys
from typing import *

import lattice_surgery_computation_composer as ls
import logical_patch_state_simulation as lssim


import webgui.lattice_view
from fractions import Fraction

import qiskit.aqua.operators as qk
import qiskit.quantum_info as qkinfo

import math



if __name__ == "__main__":
    if len(sys.argv)>1 and sys.argv[1] == 'debug_trace':
        state = qk.DictStateFn({'10': 1 / math.sqrt(2), '00': 1 / math.sqrt(2)})
        l = [lssim.StateSeparator.trace_dict_state(state,[0]),lssim.StateSeparator.trace_dict_state(state,[1])]
        print(l[0])
        print(l[1])


    print("Separable qubits,")
    bell_pair = qk.DictStateFn({'11':1/math.sqrt(2),'00':1/math.sqrt(2)})
    print("of a Bell pair:",lssim.StateSeparator.get_separable_qubits(bell_pair))
    bell_pair_plus = qk.Plus^bell_pair
    bell_pair_plus = cast(qk.DictStateFn, bell_pair_plus.eval())
    print("of a Bell pair tensored with |+>:",lssim.StateSeparator.get_separable_qubits(bell_pair_plus))
    bell_pair_plus_surround = qk.Minus ^ bell_pair ^ qk.Plus
    bell_pair_plus_surround = cast(qk.DictStateFn, bell_pair_plus_surround.eval())
    print("of |+> otimes Bell pair otimes |->:")
    separated = lssim.StateSeparator.get_separable_qubits(bell_pair_plus_surround)
    print("0 :", separated[0])
    print("3 :", separated[3])
    print()

    print("More tests:")
    state = qk.DictStateFn({'10': 1 / math.sqrt(2), '00': 1 / math.sqrt(2)})
    print(lssim.StateSeparator.get_separable_qubits(state))

    state = qk.DictStateFn({'000':1/math.sqrt(4),'010':1/math.sqrt(4), '100':1/math.sqrt(4),'110':1/math.sqrt(4)})
    print(lssim.StateSeparator.get_separable_qubits(state))