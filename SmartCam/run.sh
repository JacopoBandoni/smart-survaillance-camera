#!/bin/sh
export PYTHONPATH="."
case "$1" in
    "setup")
        pip3 install -r requirements.txt
        ;;
    "exp")
        python3 src/app.py &
        sleep 5
        python3 probe.py 0.25 12 f probe-report.txt probe.analysis.txt
        pkill -f "python3"
        ;;
    "")
        python3 src/app.py
        ;;
    *)
        python3 src/app.py "$1"
        ;;
esac