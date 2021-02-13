#!/bin/bash
echo "================ [`date`] running $0 ================ "
python3.8 -m venv env
env/bin/ac
env/bin/activate
source env/bin/activate
pip install pyzx  mako pyramid python-igraph
PYTHONPATH="..:$PYTHONPATH" python serve.py &
