#!/bin/bash

echo "================ [`date`] running deploy.sh ================ "

if [ ! -d "env" ]
then
  python3.8 -m venv env
fi
source env/bin/activate
pip install pyzx mako pyramid python-igraph qiskit
PYTHONPATH="..:$PYTHONPATH" python serve.py &
