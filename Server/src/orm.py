from flask_sqlalchemy import SQLAlchemy
import datetime
import logging

db = SQLAlchemy()

class Frame(db.Model):
    """ Stores the frames """
    
    __tablename__ = 'frame'
    __table_args__ = {'sqlite_autoincrement':True}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    source = db.Column(db.String)
    frame_timestamp = db.Column(db.DateTime)
    uploading_timestamp = db.Column(db.DateTime)

    def dump(self):
        """ Return a db record as a dict """
        d = dict([(k,v) for k,v in self.__dict__.items() if k[0] != '_'])
        d["url"] = "/frames/"+str(d["id"])
        return d


def store_frame(source, timestamp):
    """ Store a new reservation 
    
    Return the frame record, otherwise
    Return None if a db error occured
    """
    try:
        frame = Frame()
        frame.source = source
        frame.frame_timestamp = timestamp
        frame.uploading_timestamp = datetime.datetime.now()
        db.session.add(frame)
        db.session.commit()
        return frame
    except Exception as e:
        logging.info(e)
        db.session.rollback()
        return None