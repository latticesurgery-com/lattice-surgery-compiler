# Lattice Surgery Compiler

Compile logical circuits to lattice surgery operations on a surface code lattice and visualize.

![image](https://user-images.githubusercontent.com/36427091/104856854-98ca5600-58c9-11eb-9599-286c1d5a4736.png)

## Overview 
A proposed solution to mitigate the occurrence of errors in quantum computers are the so-called quantum error correcting codes (QECC). Specifically we focus on the protocol of lattice surgery, which is based on the prominent methodology of surface codes. A natural question relates to how these techniques can be employed to systematically obtain fault tolerant logical qubits from less reliable ones. Recent work has focused on building compilers that translate a logical quantum circuit to a much larger error corrected one, with the output circuit performing the computation specified by the logical circuit with QECCs [[1]](#1)[[2]](#2). 

Surface codes are a family of QECCs that aims at improving computation fidelity by entangling many quantum mechanical entities in a two dimensional lattice. Our technique of choice for operating on this lattice is a protocol known as lattice surgery, which stores logical qubits in portions of the surface code's lattice *patches* and performs logical operations by merging and splitting patches [[3]](#3).

This program handles a portion of the logical to physical compilation. It takes a quantum circuit and translates it to a representation of lattice surgery operations, which are in direct correspondence with the physical error corrected circuit, up to code distance. The project comes with a visualizer tool (figure), that shows the state of the surface code lattice state in between surgery operations.


## Status
This project is under very active development. We hope to see in the very near future an operabe release. Currently we have visualization of lattice surgery operations and input circuit handling.

## References
<a id="1">[1]</a> 
Alexandru Paler and Austin G Fowler. 
Opensurgery for topological assemblies.
arXivpreprint arXiv:1906.07994, 2019

<a id="2">[2]</a> 
Xiaosi Xu, Simon C Benjamin, and Xiao Yuan.
Variational circuit compiler for quan-tum error correction.
arXiv preprint arXiv:1911.05759, 2019.

<a id="3">[3]</a> 
Clare Horsman, Austin G Fowler, Simon Devitt, and Rodney Van Meter.
Surface codequantum computing by lattice surgery.
New Journal of Physics, 14(12):123011, 2012
