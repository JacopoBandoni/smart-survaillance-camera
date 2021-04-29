import configparser
from datetime import datetime
import logging
import sys
import os
import glob

import connexion
from flask import config, current_app, Response

from orm import db, Frame, store_frame

from errors import Error400, Error404, Error500


"""
The default app configuration: 
in case a configuration is not found or 
some data is missing
"""
DEFAULT_CONFIGURATION = { 

    "IP": "0.0.0.0", # the app ip
    "PORT": 5000, # the app port
    "DEBUG":False, # set debug mode
    "FRAMES_DIR": "./frames",
    "DB_DROPALL": True,
    "SQLALCHEMY_DATABASE_URI": "frames.db", # the database path/name
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
}

ALLOWED_CONTENT_TYPE = {'image/jpeg'}

def stream(frames, directory):
    for frame in frames:
        with open(directory+"/"+str(frame.id)+".jpeg", "rb") as f:

            yield (b'--frame\r\n'
               b'Frame-ID: '+str.encode(str(frame.id))+b'\r\n'
               b'Frame-Source-ID: '+str.encode(str(frame.source))+b'\r\n'
               b'Frame-Timestamp: '+str.encode(str(frame.frame_timestamp))+b'\r\n'
               b'Frame-Uploading-Timestamp: '+str.encode(str(frame.uploading_timestamp))+b'\r\n'
               b'Frame-Size: '+str.encode(str(frame.size))+b'\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + f.read() + b'\r\n')
            

def get_frames(source, begin=None, end=None, metadata=False):
    """ Return a stream of frames of a given source in a given period.

    GET /frames?[source=S_ID&][begin=BEGING_DT&][end=END_DT&]
    
    It's possible to filter the frames thanks the query's parameters.
    The parameters can be overlapped in any way.
    Begin and End paramters are optional.

    - source: The id of the source of the stream
    - begin: All frames from a certain date onwards (format %Y-%m-%d %H:%M:%S.%f)
    - end: All frames up to a certain date onwards (format %Y-%m-%d %H:%M:%S.%f)
    - metadata: Return only the metadata of the frames
    
    If begin and not end is specified, all those starting from begin are taken. Same thing for end.
    Status Codes:
        200 - OK
        400 - Wrong datetime format
        404 - No Stream Found
    """

    q = db.session.query(Frame).filter_by(source=source)

    if begin is not None:
        try:
            begin = datetime.strptime(begin, '%Y-%m-%d %H:%M:%S.%f')
        except:
            return Error400("Begin Arguments is not a valid datetime").get()
        q = q.filter(Frame.frame_timestamp >= begin)

    if end is not None:
        try:
            end = datetime.strptime(end, '%Y-%m-%d %H:%M:%S.%f')
        except:
            return Error400("End Arguments is not a valid datetime").get()
        q = q.filter(Frame.frame_timestamp <= end)

    q = q.order_by(Frame.frame_timestamp.asc())

    if q.first() is None:
        return Error404("No Stream Found").get()
    
    if metadata:
        return [p.dump() for p in q], 200
    else:
        return Response(stream(q, current_app.config['FRAMES_DIR']),
                mimetype='multipart/x-mixed-replace; boundary=frame')


def new_frame():
    """ Store a frame.
    POST /frames
    
    Returns the frame metadata or returns an error message.
    Requires a some headers:
        - Frame-Source-ID: the identifier of the source
        - Frame-Timestamp: the timestamp of the frame
    Status Codes:
        201 - The frame has been stored
        400 - Bad request
        500 - Error in the database (try again)
    """
    request = connexion.request
    if request.content_type in ALLOWED_CONTENT_TYPE:
        source_id = connexion.request.headers['Frame-Source-ID']
        try:
            frame_timestamp = datetime.strptime(connexion.request.headers['Frame-Timestamp'], '%Y-%m-%d %H:%M:%S.%f')
        except:
            return Error400("Frame-Timestamp is not a valid datetime").get()
        
        frame = store_frame(source_id, frame_timestamp, sys.getsizeof(request.get_data()))

        if frame is None:
            return Error500().get()
        
        with open(current_app.config['FRAMES_DIR']+"/"+str(frame.id)+".jpeg", 'wb+') as f:
            f.write(request.get_data()) 

        return frame.dump(), 201

    return Error400("Content Type not allowed").get()

def get_frame(frame_id):
    """ Return a specific frame (request by id)
    GET /frames/{booking_id}
        Status Codes:
            200 - OK
            404 - Frame not found
    """
    frame = db.session.query(Frame).filter_by(id = frame_id).first()
    if frame is None:
        return Error404("Frame not found").get()
    
    try:
        with open(current_app.config['FRAMES_DIR']+"/"+str(frame.id)+".jpeg", "rb") as f:
            return Response(f.read(), 
                headers = {
                "Content-Type":"image/jpeg",
                "Frame-ID":frame.id,
                "Frame-Source-ID":frame.source,
                "Frame-Timestamp":frame.frame_timestamp,
                "Frame-Uploading-Timestamp": frame.uploading_timestamp,
                "Frame-Size": frame.size,
                })
    except:
        return Error404("Frame's data not found").get() 


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

            logging.info("- Server CONFIGURATION: %s",configuration)
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
        logging.info("- Server CONFIGURATION ERROR: %s",e)
        logging.info("- Server RUNNING: Default Configuration")
        return DEFAULT_CONFIGURATION

def setup(application, config):

    config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"+config["SQLALCHEMY_DATABASE_URI"]

    for k,v in config.items():
        application.config[k] = v # insert the requested configuration in the app configuration

    try:
        os.mkdir(config["FRAMES_DIR"])
    except OSError:
        pass
    
    db.init_app(application)

    if config["DB_DROPALL"]: #remove the data in the db
        logging.info("- Server Dropping All from Database...")
        db.drop_all(app=application)

        files = glob.glob(config["FRAMES_DIR"]+"/*")
        for f in files:
            os.remove(f)

    db.create_all(app=application)

def create_app(configuration=None):
    logging.basicConfig(level=logging.INFO)

    app = connexion.App(__name__)
    app.add_api('./swagger.yaml')
    # set the WSGI application callable to allow using uWSGI:
    # uwsgi --http :8080 -w app
    application = app.app

    conf = get_config(configuration)
    logging.info(conf)
    logging.info("- Server ONLINE @ ("+conf["IP"]+":"+str(conf["PORT"])+")")
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