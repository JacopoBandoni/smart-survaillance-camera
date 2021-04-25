import requests
import datetime
import cv2

url = 'http://localhost:5000/frames'

with open('42.png', 'rb') as f:
    frame = f.read()
    print(requests.post(url, data=frame, headers={
        "Content-Type":"image/png",
        "Frame-Source-ID":"helo",
        "Frame-Timestamp":str(datetime.datetime.now())
        }).json())


cap = cv2.VideoCapture('a.mp4')
while(True):
    _, img = cap.read()
    _, frame = cv2.imencode('.png', img)
    frame = frame.tobytes()

    print(requests.post(url, data=frame, headers={
    "Content-Type":"image/png",
    "Frame-Source-ID":"video",
    "Frame-Timestamp":str(datetime.datetime.now())
    }).json())
