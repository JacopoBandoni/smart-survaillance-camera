import requests
import datetime
import cv2

url = 'https://mcpserver.eu.pythonanywhere.com/frames'

with open('42.jpeg', 'rb') as f:
    frame = f.read()
    print(requests.post(url, data=frame, headers={
        "Content-Type":"image/jpeg",
        "Frame-Source-ID":"D.Adams",
        "Frame-Timestamp":str(datetime.datetime.now())
        }).json())

cap = cv2.VideoCapture('a.mp4')
while(True):
    _, img = cap.read()
    _, frame = cv2.imencode('.jpeg', img)
    frame = frame.tobytes()

    print(requests.post(url, data=frame, headers={
    "Content-Type":"image/jpeg",
    "Frame-Source-ID":"video",
    "Frame-Timestamp":str(datetime.datetime.now())
    }).json())

