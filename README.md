# Lattice Surgery Compiler
[![Unitary Fund](https://img.shields.io/badge/Supported%20By-UNITARY%20FUND-brightgreen.svg?style=for-the-badge)](http://unitary.fund)

<!-- start -->

Compile logical circuits to lattice surgery operations on a surface code lattice and visualize. [Project Status](
https://github.com/latticesurgery-com/general-issue-tracker/issues/3).

![image](https://user-images.githubusercontent.com/36427091/104856854-98ca5600-58c9-11eb-9599-286c1d5a4736.png)


## Overview
A compiler that takes a QASM circuit and turns it into abstract lattice surgery instructions.

Our long term vision is to have an end to end lattice surgery compiler. We want it to be able to take a manually programmed circuit and ouput a large error corrected circuit, that performs the same computation with many more qubits and a higher degree of accuracy.

### Features:
* Web-based patch visualizer that shows a computation happening on a surface code lattice (in picture). Try it at https://latticesurgery.com.
* HTTP Service to compile qasm circuits
* Data representation for Pauli rotations and abstract lattice surgery operations
* QASM to lattice surgery patch compiler 
* Remove stabilizer operations from the input circuit
* Simulation of patch computations

<!-- end -->

## Background 
A proposed solution to mitigate the occurrence of errors in quantum computers are the so-called quantum error correcting codes (QECC). Specifically we focus on the protocol of lattice surgery, which is based on the prominent methodology of surface codes. A natural question relates to how these techniques can be employed to systematically obtain fault tolerant logical qubits from less reliable ones. Recent work has focused on building compilers that translate a logical quantum circuit to a much larger error corrected one, with the output circuit performing the computation specified by the logical circuit with QECCs [[1]](#1)[[2]](#2). 

Surface codes are a family of QECCs that aims at improving computation fidelity by entangling many quantum mechanical entities in a two dimensional lattice. Our technique of choice for operating on this lattice is a protocol known as lattice surgery, which stores logical qubits in portions of the surface code's lattice *patches* and performs logical operations by merging and splitting patches [[3]](#3).

This program handles a portion of the logical to physical compilation. It takes a quantum circuit and translates it to a representation of lattice surgery operations, which are in direct correspondence with the physical error corrected circuit, up to code distance. The project comes with a visualizer tool (figure), that shows the state of the surface code lattice state in between surgery operations.

Part of our process is inspired by Litinski's Game of Surface Codes [[4]](#4). In particular, we leverage the idea of using Pauli rotations as an intermediate representation to get to abstract lattice surgery instructions and to remove stabilizer operations.

## Status
This project is under very active development. We hope to see in the very near future an operabe release. Currently we have visualization of lattice surgery operations and input circuit handling.

## Contributing and Development set up

Check out our [contribution guide](https://github.com/latticesurgery-com/lattice-surgery-compiler/blob/master/CONTRIBUTING.md).

If you just want to get an idea for what this compiler does, check out https://latticesurgery.com.


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

<a id="4">[4]</a> 
Daniel Litinski.
A Game of Surface Codes: Large-Scale Quantum Computing with Lattice Surgery
Quantum 3, 128 (2019)
