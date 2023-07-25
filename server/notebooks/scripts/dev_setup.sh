#!/bin/bash
virtualenv env
source env/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
