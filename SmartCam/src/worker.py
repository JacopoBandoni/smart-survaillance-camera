import os
import time
import datetime
import requests

from flask import current_app

def worker(app):
    print("WORKER: Online")
    try:
        os.mkdir("./frames")
    except OSError:
        pass

    last_timer = datetime.datetime.now()
    cnt = 0

    with app.app.app_context():
        while True:
            time.sleep(current_app.config["CAP_TIMER"])

            camera = current_app.config["THIS_CAMERA"]
            server_url = current_app.config["SERVER_URL"]

            frame = camera.get_frame()
            print("WORKER: Click!")
            now = datetime.datetime.now()
            cnt += 1
            tdelta = datetime.timedelta(
                days=0,
                seconds=current_app.config["SERVER_TIMER"],
                microseconds=0
            )
            if(now - last_timer >= tdelta or cnt >= current_app.config["SERVER_RATIO"]):
                print("WORKER: Sending...")
                try:
                    requests.post(server_url, data=frame, headers={
                        "Content-Type":"image/png",
                        "Frame-Source-ID":str(camera.get_id()),
                        "Frame-Timestamp":str(now)
                    })
                except:
                    print("WORKER: Server "+str(server_url)+" N/A")
                last_timer = now
                cnt = 0

            with open("./frames/"+str(now.strftime("%Y-%m-%d--%H-%M-%S-%f"))+".png", 'wb+') as f:
                f.write(frame) 

if __name__ == "__main__":
    from camera import IPCamera, VirtualCamera
    worker(VirtualCamera("./src/a.mp4"),None,5,10,4) #"https://mcpserver.eu.pythonanywhere.com/frames"
