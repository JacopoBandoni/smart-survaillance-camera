import configparser
import logging
import sys
import os

from datetime import date, datetime, timedelta

import threading

from werkzeug.utils import append_slash_redirect

import connexion
from flask import current_app, Response

from src.camera import IPCamera, VirtualCamera

from src.worker import worker

import requests
import time

THIS_CAMERA = VirtualCamera("./src/a.mp4")#IPCamera("192.168.1.6:8080")
SERVER_URL = None #"https://mcpserver.eu.pythonanywhere.com/frames" 
CAP_TIMER = 5
SERVER_TIMER = 10  
SERVER_RATIO = 4

"""
The default app configuration: 
in case a configuration is not found or 
some data is missing
"""
DEFAULT_CONFIGURATION = { 
    "IP": "0.0.0.0", # the app ip
    "PORT": 8080, # the app port
    "DEBUG":True, # set debug mode
}

def live_stream():
    while True:
        frame = THIS_CAMERA.get_frame()
        yield (b'--frame\r\n'
               b'Frame-Timestamp: '+str.encode(str(datetime.now()))+b'\r\n'
               b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')

def local_stream():
    frames = [f for f in os.listdir("./frames") if os.path.isfile(os.path.join("./frames", f))]
    frames.sort()
    for filename in frames:
        with open("./frames/"+filename,"rb") as f:
            frame = f.read()
        yield (b'--frame\r\n'
               b'Frame-Timestamp: '+str.encode(str(datetime.now()))+b'\r\n'
               b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')

def photo():
    frame = THIS_CAMERA.get_frame()
    return Response((b'--frame\r\n'
               b'Frame-Timestamp: '+str.encode(str(datetime.now()))+b'\r\n'
               b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def live():
   return Response(live_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

def video():
    return Response(local_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

def get_config(configuration=None):
    """ Returns a json file containing the configuration to use in the app

    The configuration to be used can be passed as a parameter, 
    otherwise the one indicated by default in config.ini is chosen

    ------------------------------------
    [CONFIG]
    CONFIG = The_default_configuration
    ------------------------------------

    Params:
        - configuration: if it is a string it indicates the configuration to choose in config.ini
    """
    try:
        parser = configparser.ConfigParser()
        if parser.read('config.ini') != []:
            
            if type(configuration) != str: # if it's not a string, take the default one
                configuration = parser["CONFIG"]["CONFIG"]

            logging.info("- SmartCam CONFIGURATION: %s",configuration)
            configuration = parser._sections[configuration] # get the configuration data

            parsed_configuration = {}
            for k,v in configuration.items(): # Capitalize keys and translate strings (when possible) to their relative number or boolean
                k = k.upper()
                parsed_configuration[k] = v
                try:
                    parsed_configuration[k] = int(v)
                except:
                    try:
                        parsed_configuration[k] = float(v)
                    except:
                        if v == "true":
                            parsed_configuration[k] = True
                        elif v == "false":
                            parsed_configuration[k] = False

            for k,v in DEFAULT_CONFIGURATION.items():
                if not k in parsed_configuration: # if some data are missing enter the default ones
                    parsed_configuration[k] = v

            return parsed_configuration
        else:
            return DEFAULT_CONFIGURATION
    except Exception as e:
        logging.info("- SmartCam CONFIGURATION ERROR: %s",e)
        logging.info("- SmartCam RUNNING: Default Configuration")
        return DEFAULT_CONFIGURATION

def setup(application, config):

    for k,v in config.items():
        application.config[k] = v # insert the requested configuration in the app configuration

    application.config["THIS_CAMERA"] = THIS_CAMERA
    application.config["SERVER_URL"] = SERVER_URL
    application.config["CAP_TIMER"] = CAP_TIMER
    application.config["SERVER_TIMER"] = SERVER_TIMER
    application.config["SERVER_RATIO"] = SERVER_RATIO
    

def create_app(configuration=None):
    logging.basicConfig(level=logging.INFO)

    app = connexion.App(__name__)
    app.add_api('./swagger.yaml')
    # set the WSGI application callable to allow using uWSGI:
    # uwsgi --http :8080 -w app
    application = app.app

    conf = get_config(configuration)
    logging.info(conf)
    logging.info("- SmartCam ONLINE @ ("+conf["IP"]+":"+str(conf["PORT"])+")")
    with application.app_context():
        setup(application, conf)

    return app

if __name__ == '__main__':

    c = None
    if len(sys.argv) > 1: # if it is inserted
        c = sys.argv[1] # get the configuration name from the arguments

    app = create_app(c)

    if os.environ.get("WERKZEUG_RUN_MAIN") == "true": #execute only one time in debug mode (after the reload)            
        threading.Thread(target=worker, args=(app,)).start()

        def f(app):
            time.sleep(15)
            with app.app.app_context():
                current_app.config["CAP_TIMER"] = 2
            print("hello")
        threading.Thread(target=f, args=(app,)).start()

    with app.app.app_context():
        app.run(
            host=current_app.config["IP"], 
            port=current_app.config["PORT"], 
            debug=current_app.config["DEBUG"]
            )