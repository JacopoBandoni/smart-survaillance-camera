import requests
import cv2

class IPCamera:
    def __init__(self, id, ip):
        self._id = id
        self._ip = ip

    def get_id(self):
        return self._id

    def get_frame(self):
        frame = requests.get("http://"+self._ip+"/shot.jpg")
        return frame.content

class VirtualCamera:
    def __init__(self, id, video):
        self._id = id
        self._video = video
        self._cap = cv2.VideoCapture(video)

    def get_id(self):
        return self._id

    def get_frame(self):
        _, img = self._cap.read()
        if img is None:
            self._cap = cv2.VideoCapture(self._video)
            _, img = self._cap.read()
        _, frame = cv2.imencode('.jpeg', img)
        return frame.tobytes()
