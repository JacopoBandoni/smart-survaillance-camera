#!/bin/sh
export PYTHONPATH="."
case "$1" in
    "setup")
        pip3 install -r requirements.txt
        ;;
    "exp")
        sleep 300
        
        python3 probe.py 0.25 1200 f experiments/probe0.report.txt experiments/probe0.analysis.txt
        sleep 300

        python3 src/app1.py &
        sleep 5
        python3 probe.py 0.25 1200 f experiments/probe1.report.txt experiments/probe1.analysis.txt
        pkill -f "python3"
        rm -r ./frames-raspberry
        sleep 300

        python3 src/app1O.py &
        sleep 5
        python3 probe.py 0.25 1200 f experiments/probe1O.report.txt experiments/probe1O.analysis.txt
        pkill -f "python3"
        rm -r ./frames-raspberry
        sleep 300

        python3 src/app2.py &
        sleep 5
        python3 probe.py 0.25 1200 f experiments/probe2.report.txt experiments/probe2.analysis.txt
        pkill -f "python3"
        rm -r ./frames-raspberry
        sleep 300

        python3 src/app2O.py &
        sleep 5
        python3 probe.py 0.25 1200 f experiments/probe2O.report.txt experiments/probe2O.analysis.txt
        pkill -f "python3"
        rm -r ./frames-raspberry
        sleep 300

        python3 src/app3.py &
        sleep 5
        python3 probe.py 0.25 1200 f experiments/probe3.report.txt experiments/probe3.analysis.txt
        pkill -f "python3"
        rm -r ./frames-raspberry
        sleep 300

        python3 src/app3O.py &
        sleep 5
        python3 probe.py 0.25 1200 f experiments/probe3O.report.txt experiments/probe3O.analysis.txt
        pkill -f "python3"
        rm -r ./frames-raspberry
        
        ;;
    "")
        python3 src/app.py
        ;;
    *)
        python3 src/app.py "$1"
        ;;
esac