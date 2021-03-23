OPENQASM 2.0;
include "qelib1.inc";

qreg q0[3];
creg c1[1];
creg c0[1];
h q0[1];
cx q0[1],q0[2];
barrier q0[0],q0[1],q0[2];
h q0[0];
t q0[0];
h q0[0];
barrier q0[0],q0[1],q0[2];
cx q0[0],q0[1];
h q0[0];
barrier q0[0],q0[1],q0[2];