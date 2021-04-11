import requests
import shutil

class IPCamera:
    def __init__(self, ip):
        self._ip = ip

    def get_frame(self):
        frame = requests.get("http://"+self._ip+"/shot.jpg")
        return frame.content


if __name__ == "__main__":
    IPCamera("192.168.1.6:8080").get_frame()
