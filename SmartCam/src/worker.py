import os
import time
import datetime
import requests
import psutil

from skimage.metrics import structural_similarity as ssim
import cv2

import numpy as np

MIN_KB = 1024.0
EPS = 0.1

def free_disk(frames_dir):
    try:
        available_kb = round(psutil.disk_usage('/').free/1024.0,1)
        if available_kb < MIN_KB:
            frames = [f for f in os.listdir(frames_dir) if os.path.isfile(os.path.join(frames_dir, f))]
            frames = list(map(lambda filename: 
                (filename,datetime.datetime.strptime((filename.split("."))[0],"%Y-%m-%d--%H-%M-%S-%f")),
                frames))
            frames.sort(key = lambda frame: frame[1], reverse=True)
            while available_kb < (MIN_KB + (MIN_KB*EPS)):
                try:
                    (file,_) = frames.pop()
                    os.remove(frames_dir+"/"+file)
                    available_kb = round(psutil.disk_usage('/').free/1024.0,1)
                except:
                    break
    except:
        pass

def compare(imgA, imgB):
    return ssim(imgA, imgB, multichannel=True)

from flask import current_app

def worker(app, frames_dir):
    #print("WORKER: Online")
    try:
        os.mkdir(frames_dir)
    except OSError:
        pass

    last_timer = datetime.datetime.now()
    cnt = 0

    with app.app.app_context():
        while True:
            current_app.config["CONTROLLER_LOCK"].acquire()
            cap_timer = current_app.config["CAP_TIMER"]
            current_app.config["CONTROLLER_LOCK"].release()
            
            if cap_timer != 0:
                time.sleep(cap_timer)

            current_app.config["CONTROLLER_LOCK"].acquire()
            camera = current_app.config["THIS_CAMERA"]
            server_url = current_app.config["SERVER_URL"]
            tdelta = datetime.timedelta(
                days=0,
                seconds=current_app.config["SERVER_TIMER"],
                microseconds=0
            )
            server_ratio = current_app.config["SERVER_RATIO"]
            threshold = current_app.config["THRESHOLD"]
            current_app.config["CONTROLLER_LOCK"].release()

            frame = camera.get_frame()
            #print("WORKER: Click!")


            difference = 0

            if threshold < 1:
                last = current_app.config["LAST_FRAME"]
                if last is not None:
                    last = cv2.imread(current_app.config["FRAMES_DIR"]+"/"+last)
                    new = cv2.imdecode(np.fromstring(frame, np.uint8), cv2.IMREAD_COLOR)
                    difference = compare(last, new)
                    #print("WORKER: Difference: "+str(difference))

            if difference <= threshold:
                
                now = datetime.datetime.now()
                cnt += 1
                
                current_app.config["CONTROLLER_LOCK"].acquire()
                current_app.config["LAST_CAP"] = str(now)
                old_last_sending = current_app.config["LAST_SENDING"]
                current_app.config["CONTROLLER_LOCK"].release()

                last_sending = old_last_sending

                if(now - last_timer >= tdelta or cnt >= server_ratio):
                    #print("WORKER: Sending...")
                    try:
                        requests.post(server_url, data=frame, headers={
                            "Content-Type":"image/jpeg",
                            "Frame-Source-ID":str(camera.get_id()),
                            "Frame-Timestamp":str(now)
                        })
                        last_sending = str(datetime.datetime.now())
                    except:
                        print("WORKER: Server "+str(server_url)+" N/A")
                        last_sending = old_last_sending
                    
                    last_timer = now
                    cnt = 0

                    current_app.config["CONTROLLER_LOCK"].acquire()
                    current_app.config["LAST_SENDING"] = last_sending
                    current_app.config["CONTROLLER_LOCK"].release()

                filename = str(now.strftime("%Y-%m-%d--%H-%M-%S-%f"))+".jpeg"

                with open(frames_dir+"/"+filename, 'wb+') as f:
                    f.write(frame) 

                free_disk(frames_dir)

                current_app.config["LAST_FRAME_LOCK"].acquire()
                current_app.config["LAST_FRAME"] = filename
                current_app.config["LAST_FRAME_LOCK"].release()

            else:
                #print("WORKER: Above the threshold ("+str(threshold)+")...")
                pass

if __name__ == "__main__":
    free_disk("./frames-raspberry")
