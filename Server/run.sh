#!/bin/sh
export PYTHONPATH="."
case "$1" in
    "setup")
        pip3 install -r requirements.txt
        ;;
    "docker-build")
        docker build . -t server
        ;;
    "-d")
        python3 src/app.py
        ;;
    "docker")
        if [ -z "$2" ] 
        then
            docker run -it -p 8080:8080 server 
        else
            docker run -it -p 8080:8080 -e "CONFIG=$2" server
        fi
        ;;
    *)
        python3 src/app.py "$1"
        ;;
esac