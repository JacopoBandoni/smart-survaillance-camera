# SmartCam

## Setup
```
$ ./run.sh setup
```

## Running the code

### Running in default mode
```
$ ./run.sh
```

### Running in production mode
```
$ ./run.sh PROD
```

### Running with custom configurations
```
$ ./run.sh MY_CONFIG
```

## Troubleshooting

* Make sure you have installed all the requirements via
```
$ ./run.sh setup
```

* If the following error occurs:
```
Traceback (most recent call last):
  File "src/app.py", line 14, in <module>
    from src.camera import *
  File "/home/pi/Desktop/MCPS/SmartCam/src/camera.py", line 2, in <module>
    import cv2
  File "/home/pi/.local/lib/python3.7/site-packages/cv2/__init__.py", line 5, in <module>
    from .cv2 import *
ImportError: libcblas.so.3: cannot open shared object file: No such file or directory
```
Then manually download the following dependencies
```
pip3 install opencv-python 
sudo apt-get install libcblas-dev
sudo apt-get install libhdf5-dev
sudo apt-get install libhdf5-serial-dev
sudo apt-get install libatlas-base-dev
sudo apt-get install libjasper-dev 
sudo apt-get install libqtgui4 
sudo apt-get install libqt4-test
```
or 
```
pip3 install opencv-contrib-python; sudo apt-get install -y libatlas-base-dev libhdf5-dev libhdf5-serial-dev libatlas-base-dev libjasper-dev  libqtgui4  libqt4-test
```
