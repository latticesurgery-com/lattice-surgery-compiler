# Lattice Surgery Compiler
[![Test](https://github.com/latticesurgery-com/lattice-surgery-compiler/actions/workflows/test.yml/badge.svg)](https://github.com/latticesurgery-com/lattice-surgery-compiler/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/latticesurgery-com/lattice-surgery-compiler/branch/dev/graph/badge.svg?token=7SSY2AY2QN)](https://codecov.io/gh/latticesurgery-com/lattice-surgery-compiler)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![arXiv](https://img.shields.io/badge/arXiv-2302.02459-b31b1b.svg)](https://arxiv.org/abs/2302.02459)
[![Unitary Fund](https://img.shields.io/badge/Supported%20By-Unitary%20Fund-FFFF00.svg)](https://unitary.fund)

<!-- start -->

[![LSC Logo](https://user-images.githubusercontent.com/46719079/150657000-8e83c649-84a8-431b-aab0-d44d847e5a24.png)](https://latticesurgery.com)

Compile logical quantum circuits to lattice surgery operations on a surface code lattice. Visualize how the lattice evolves between each step of surgery.

Currently in active development. See [Project Status](
https://github.com/latticesurgery-com/general-issue-tracker/issues/3).

## Overview
A compiler that translates QASM circuits into abstract lattice surgery instructions.

Lattice surgery instructions were chosen as the output since they are equivalent representations of QASM circuits, and they can be made fault-tolerant with more convenience.

Our long-term vision is to have an end-to-end lattice surgery compiler. It should be able to translate a manually programmed circuit into a larger, error corrected circuit that performs the same computation. The error corrected circuit is larger since it needs to use many more qubits to provide a higher degree of accuracy.

### Features:
* Web-based patch visualizer that shows a computation happening on a surface code lattice (in picture). Try it at [latticesurgery.com](https://latticesurgery.com).
* HTTP Service to compile QASM circuits.
* Data representation for Pauli rotations and abstract lattice surgery operations.
* QASM to lattice surgery patch compiler.
* Remove stabilizer operations from the input circuit.
* Simulation of patch computations.

<!-- end -->

<p align="center">
  <img alt="backers" height="70px" src="https://user-images.githubusercontent.com/36427091/150938385-b0099f77-fd7b-4666-95b6-a7610ec6c9de.png" />
</p>

## Background 
Quantum error correcting codes (QECC) have been proposed as a solution for reducing the occurence of errors in quantum computers. Surface codes are a family of QECCs that improve computation fidelity by entangling many quantum mechanical entities (systems, qubits) in a two dimensional lattice. A natural question relates to how these techniques can be employed to systematically obtain fault-tolerant logical qubits from less reliable ones. Recent work has focused on building compilers that translate a logical quantum circuit to a much larger error corrected one, with the output circuit performing the computation specified by the logical circuit with QECCs [[1]](#1)[[2]](#2). 

Specifically, our technique of choice for operating on this lattice is a protocol known as lattice surgery, which stores logical qubits in portions of the surface code's lattice *patches* and performs logical operations by merging and splitting patches [[3]](#3).

This program handles a portion of the logical to physical compilation. It takes a quantum circuit and translates it to a representation of lattice surgery operations, which are in direct correspondence with the physical error corrected circuit, up to code distance. The project comes with a visualizer tool that shows the state of the surface code lattice in between surgery operations.

Part of our process is inspired by Litinski's Game of Surface Codes [[4]](#4). In particular, we leverage the idea of using Pauli rotations as an intermediate representation to get to abstract lattice surgery instructions and to remove stabilizer operations.

## Status
The compiler is deployed in alpha at [latticesurgery.com](https://latticesurgery.com).

## Documentation
The latest documentation can be found [here](https://lattice-surgery-compiler.readthedocs.io/en/latest/).

With the compiler still being in alpha, most of the documentation doesn't exist yet or is subject to change. 

## Contributing and Development set up

Check out our [contribution guide](https://github.com/latticesurgery-com/lattice-surgery-compiler/blob/dev/CONTRIBUTING.md).

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
