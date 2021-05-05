import psutil
import time
import psutil
import sys
import datetime
import math
import json
import statistics


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

def get_report(report_file):
    report = []

    with open(report_file, "r") as f:
        lines = f.readlines()

    for l in lines:
        report.append(json.loads(l))

    return report

def process_report(report, analysis_file):

    analysis = {}

    for record in report:
        for field,attributes in record.items():
            if field != "timestamp":
                if field not in analysis:
                    analysis[field] = {}
                for k,v in attributes.items():
                    if v is not None:
                        if k in analysis[field]:
                            (analysis[field][k]).append(v)
                        else:
                            analysis[field][k] = [v]

    for field,attributes in analysis.items():
        for k,a in attributes.items():
            if len(a) != 0:
                analysis[field][k] = {
                    "values": a,
                    "min": min(a),
                    "max": max(a),
                    "avg": statistics.fmean(a),
                    "stdev": statistics.stdev(a)
                }
    with open(analysis_file, "w+") as f:
        f.write(json.dumps(analysis))
    
    return analysis

if __name__ == "__main__":

    process_report(get_report("probe-report.txt"), "probe-analysis.txt")
    exit(0)

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
