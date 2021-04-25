import requests
import datetime
with open('42.png', 'rb') as f:
    frame = f.read()
url = 'http://localhost:5000/frames'
now = datetime.datetime.now()
print(requests.post(url, data=frame, headers={
    "Content-Type":"image/png",
    "Frame-Source-ID":"helo",
    "Frame-Timestamp":str(now)
    }).json())
