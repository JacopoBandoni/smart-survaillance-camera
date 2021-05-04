#!/bin/sh
export PYTHONPATH="."
case "$1" in
    "setup")
        pip3 install -r requirements.txt
        ;;
    "")
        python3 src/app.py
        ;;
    *)
        python3 src/app.py "$1"
        ;;
esac