import psutil
import time
import psutil
import sys
import datetime
import math
import json


def get_cpu_temperature():
    """
    from subprocess import PIPE, Popen
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
    output, _ = process.communicate()
    return output
    """
    try:
        return psutil.sensors_temperatures()['cpu_thermal'][0].current
    except:
        return None

def get_status():
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return {
        "timestamp": str(datetime.datetime.now()),
        "cpu":{
            "percent": psutil.cpu_percent(0.1),
            "frequency": psutil.cpu_freq().current,
	        "temperature": get_cpu_temperature(),
        },
        "memory":{
            "free": round(memory.available/1024.0/1024.0,1),
            "total": round(memory.total/1024.0/1024.0,1),
            "percent": memory.percent
        },
        "disk":{
            "free":round(disk.free/1024.0/1024.0/1024.0,1),
            "total": round(disk.total/1024.0/1024.0/1024.0,1),
            "percent": disk.percent
        }  
    }

def get_report():
    report = []
    report_file = "probe-report.txt"

    with open(report_file, "r") as f:
        lines = f.readlines()

    for l in lines:
        report.append(json.loads(l))

    return report

if __name__ == "__main__":

    report = "probe-report.txt"
    delta = 1
    end = math.inf
    try:
        delta = float(sys.argv[1])
    except:
        pass
    try:
        end = int(sys.argv[2])
    except:
        pass

    with open(report, "w+") as f:
        pass

    i = 0
    while i < end:
        time.sleep(delta)
        with open(report, "a+") as f:
            f.write(json.dumps(get_status()))
            f.write("\n")
        i+=1

        #print(psutil.net_io_counters())

    #print(get_report())
