import configparser
import logging
import sys
import os
import psutil

from datetime import datetime

import threading

import connexion
from flask import current_app, Response

from src.camera import *

from src.worker import worker


ID = "raspberry"
THIS_CAMERA = None #IPCamera("192.168.1.6:8080")
SERVER_URL = "http://localhost:5000/frames"#"https://mcpserver.eu.pythonanywhere.com/frames"#
CAP_TIMER = 1
SERVER_TIMER = 5
SERVER_RATIO = 999
THRESHOLD = 1

FRAMES_DIR = None

"""
The default app configuration: 
in case a configuration is not found or 
some data is missing
"""
DEFAULT_CONFIGURATION = { 
    "IP": "0.0.0.0", # the app ip
    "PORT": 8080, # the app port
    "DEBUG":True, # set debug mode
    "ID": ID
}

def live_stream(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Frame-Timestamp: '+str.encode(str(datetime.now()))+b'\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def local_stream(frames_dir,begin=None, end=None):
    frames = [f for f in os.listdir(frames_dir) if os.path.isfile(os.path.join(frames_dir, f))]
    frames = list(map(lambda filename: 
        (filename,datetime.strptime((filename.split("."))[0],"%Y-%m-%d--%H-%M-%S-%f")),
        frames))
    frames.sort(key = lambda frame: frame[1])

    if begin is not None:
        try:
            begin = datetime.strptime(begin, '%Y-%m-%d %H:%M:%S.%f')
        except:
            pass

    if end is not None:
        try:
            end = datetime.strptime(end, '%Y-%m-%d %H:%M:%S.%f')
        except:
            pass

    for (filename,timestamp) in frames:
        if begin is None or timestamp >= begin:
            if end is not None and timestamp >= end:
                break
            with open(frames_dir+"/"+filename,"rb") as f:
                frame = f.read()
            yield (b'--frame\r\n'
                b'Frame-Timestamp: '+str.encode(str(datetime.now()))+b'\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def photo():
    frame = current_app.config["THIS_CAMERA"].get_frame()
    return Response((b'--frame\r\n'
               b'Frame-Timestamp: '+str.encode(str(datetime.now()))+b'\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def last():
    last_frame = current_app.config["LAST_FRAME"]
    if last_frame is None:
        frames = os.listdir(current_app.config["FRAMES_DIR"])
        if not frames:
           return '',404 
        else:
            paths = [os.path.join(current_app.config["FRAMES_DIR"], basename) for basename in frames]
            last_frame = ((max(paths, key=os.path.getctime)).split("/"))[-1]
            current_app.config["LAST_FRAME_LOCK"].acquire()
            current_app.config["LAST_FRAME"] = last_frame
            current_app.config["LAST_FRAME_LOCK"].release()
            
    
    with open(current_app.config["FRAMES_DIR"]+"/"+last_frame,"rb") as f:
        frame = f.read()
    return Response((b'--frame\r\n'
               b'Frame-Timestamp: '+str.encode((last_frame.split("."))[0])+b'\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def live():
   return Response(live_stream(current_app.config["THIS_CAMERA"]), mimetype='multipart/x-mixed-replace; boundary=frame')

def video(begin=None, end=None):
    return Response(local_stream(current_app.config["FRAMES_DIR"], begin, end), mimetype='multipart/x-mixed-replace; boundary=frame')

def get_controller():
    current_app.config["CONTROLLER_LOCK"].acquire()
    config = {
        "camera": current_app.config["THIS_CAMERA"].get_id(),
        "cap_timer": current_app.config["CAP_TIMER"],
        "server_url": current_app.config["SERVER_URL"],
        "server_timer": current_app.config["SERVER_TIMER"],
        "server_ratio": current_app.config["SERVER_RATIO"],
        "online_from": current_app.config["ONLINE_FROM"],
        "last_cap": current_app.config["LAST_CAP"],
        "last_sending": current_app.config["LAST_SENDING"],
        "threshold":current_app.config["THRESHOLD"]
    }
    
    current_app.config["CONTROLLER_LOCK"].release()
    return config

def post_controller():
    req = connexion.request.json
    current_app.config["CONTROLLER_LOCK"].acquire()

    if "cap_timer" in req and req["cap_timer"] is not None:
        current_app.config["CAP_TIMER"] = req["cap_timer"]

    if "server_url" in req:
        current_app.config["SERVER_URL"] = req["server_url"]

    if "server_timer" in req and req["server_timer"] is not None:
        current_app.config["SERVER_TIMER"] = req["server_timer"]

    if "server_ratio" in req and req["server_ratio"] is not None:
        current_app.config["SERVER_RATIO"] = req["server_ratio"]

    if "threshold" in req and req["threshold"] is not None:
        current_app.config["THRESHOLD"] = req["threshold"]

    current_app.config["CONTROLLER_LOCK"].release()

    return get_controller()

def get_cpu_temperature():
    try:
        return psutil.sensors_temperatures()['cpu_thermal'][0].current
    except:
        return None

def get_status():
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return {
        "timestamp": {
            "value":str(datetime.now()),
            "unit": "%Y-%m-%d %H:%M:%S.%f"
        },
        "cpu":{
            "percent": {
                "value": psutil.cpu_percent(0.1),
                "unit": "%"
            },
            "frequency": {
                "value": psutil.cpu_freq().current,
                "unit":"Mhz",
            },
	        "temperature": {
                "value": get_cpu_temperature(),
                "unit": "degrees Celsius"
            },
        },
        "memory":{
            "free": {
                "value": round(memory.available/1024.0/1024.0,1),
                "unit": "MB"
            },
            "total": {
                "value": round(memory.total/1024.0/1024.0,1),
                "unit": "MB"
            },
            "percent": {
                "value": memory.percent,
                "unit": "%"
            },
        },
        "disk":{
            "free": {
                "value": round(disk.free/1024.0/1024.0/1024.0,1),
                "unit": "GB"
            },
            "total": {
                "value": round(disk.total/1024.0/1024.0/1024.0,1),
                "unit": "GB"
            },
            "percent": {
                "value": disk.percent,
                "unit": "%"
            },
        }  
    }
    


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

    global THIS_CAMERA
    THIS_CAMERA = VirtualCamera(application.config["ID"],"./src/a.mp4")
    application.config["THIS_CAMERA"] = THIS_CAMERA
    application.config["SERVER_URL"] = SERVER_URL
    application.config["CAP_TIMER"] = CAP_TIMER
    application.config["SERVER_TIMER"] = SERVER_TIMER
    application.config["SERVER_RATIO"] = SERVER_RATIO
    application.config["LAST_FRAME"] = None
    application.config["LAST_FRAME_LOCK"] = threading.Lock()
    application.config["CONTROLLER_LOCK"] = threading.Lock()

    application.config["ONLINE_FROM"] = str(datetime.now())
    application.config["LAST_CAP"] = None
    application.config["LAST_SENDING"] = None

    global FRAMES_DIR
    FRAMES_DIR = "./frames-"+THIS_CAMERA.get_id()
    application.config["FRAMES_DIR"] = FRAMES_DIR

    application.config["THRESHOLD"] = THRESHOLD
    

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

    if (not app.app.config["DEBUG"]) or os.environ.get("WERKZEUG_RUN_MAIN") == "true": #execute only one time in debug mode (after the reload)            
        threading.Thread(target=worker, args=(app,FRAMES_DIR)).start()

    with app.app.app_context():
        app.run(
            host=current_app.config["IP"], 
            port=current_app.config["PORT"], 
            debug=current_app.config["DEBUG"]
            )