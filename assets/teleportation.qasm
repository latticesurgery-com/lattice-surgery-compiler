OPENQASM 2.0;
include "qelib1.inc";

OPENQASM 2.0;
include "qelib1.inc";

qreg q[3];
creg c_z[1];
creg c_x[1];
creg res[1];

h q[0];
t q[0];
h q[0];
barrier q[0],q[1],q[2];
h q[1];
cx q[1],q[2];
barrier q[0],q[1],q[2];
cx q[0],q[1];
h q[0];
measure q[0] -> c_z[0];
measure q[1] -> c_x[0];
if (c_x==1) x q[2];
if (c_z==1) z q[2];
measure q[2] -> res[0];


