from flask import current_app, send_file, Response
import configparser
import logging
import sys
import time
import numpy as np
import cv2

from datetime import date, datetime


import connexion


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

def time():
    return datetime.now()

def test_photo():
    return send_file("42.png",mimetype="image/png")

def photo():
    frame = IPCamera("192.168.0.101:8081").get_frame()
    return Response((b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
def gen(camera):
    start = 0
    end = 0
    avg = 0
    cnt = 0
    while True:
        
        frame =  camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def video():
   return Response(gen(IPCamera("192.168.1.6:8080")),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def gen2():
    cap = cv2.VideoCapture('a.mp4')
    while(True):
        _, img = cap.read()
        _, frame = cv2.imencode('.jpeg', img)
        frame = frame.tostring()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
               
def video_feed():
   return Response(gen2(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
                    
def motion():
    return send_file("a.mjpeg",mimetype="image/png")

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
    with app.app.app_context():
        setup(application, conf)

    return app

if __name__ == '__main__':

    c = None
    if len(sys.argv) > 1: # if it is inserted
        c = sys.argv[1] # get the configuration name from the arguments

    app = create_app(c)

    with app.app.app_context():
        app.run(
            host=current_app.config["IP"], 
            port=current_app.config["PORT"], 
            debug=current_app.config["DEBUG"]
            )
