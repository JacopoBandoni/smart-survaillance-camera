import psutil
import time
from subprocess import PIPE, Popen
import psutil


def get_cpu_temperature():
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
    output, _ = process.communicate()
    return float(output[output.index('=') + 1:output.rindex("'")])

def get_stats():
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    # Divide from Bytes -> KB -> MB
    return {
        "cpu":{
            "percent":psutil.cpu_percent(0.1),
            "frequency":psutil.cpu_freq().current,
            #"temperature": get_cpu_temperature()
        },
        "memory":{
            "available": round(memory.available/1024.0/1024.0,1),
            "total": round(memory.total/1024.0/1024.0,1),
            "percent": memory.percent
        },
        "disk":{
            "free":round(disk.free/1024.0/1024.0/1024.0,1),
            "total": round(disk.total/1024.0/1024.0/1024.0,1),
            "percent": disk.percent
        }
        

    }

while True:
    time.sleep(0.25)
    print(get_stats())

    print(psutil.net_io_counters())
    #print(psutil.sensors_temperatures())
