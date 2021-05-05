from os import stat
import psutil
import time
import psutil
import sys
import datetime
import math
import json
import statistics

SAMPLE_TIME = 0.1


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
            "percent": psutil.cpu_percent(SAMPLE_TIME),
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

def process_report(report):

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
                    #"values": a,
                    "min": min(a),
                    "max": max(a),
                    "avg": statistics.fmean(a),
                    "stdev": statistics.stdev(a)
                }
    
    return analysis

if __name__ == "__main__":

    delta = 1
    end = 60
    verbose = False
    report_file = "probe-report.txt"
    analysis_file = "probe-analysis.txt"

    try:
        delta = float(sys.argv[1])
    except:
        pass

    try:
        t =sys.argv[2]
        if t == "inf":
            end = math.inf
        else:
            end = int(t)
    except:
        pass

    try:
        if sys.argv[3] == "t":
            verbose = True
    except:
        pass

    try:
        report_file = sys.argv[4]
    except:
        pass

    try:
        analysis_file = sys.argv[5]
    except:
        pass

    with open(report_file, "w+") as f:
        pass

    if delta > SAMPLE_TIME:
        delta -= SAMPLE_TIME
    else:
        delta = 0

    print("*** Starting probing...")
    print(f"*** Sampling {end} times")
    print(f"*** Waiting {delta}s (sample time {SAMPLE_TIME}s - total {delta+SAMPLE_TIME}s)")
    print(f"*** Reporting on {report_file}")
    print(f"*** Analysis on {analysis_file}")
    print(f"*** Verbose: {verbose}")
    print()

    i = 0
    while i < end:
        time.sleep(delta)
        status = get_status()
        if verbose:
            print(status)
        with open(report_file, "a+") as f:
            f.write(json.dumps(status))
            f.write("\n")
        i+=1
        #print(psutil.net_io_counters())

    analysis = process_report(get_report(report_file))
    
    with open(analysis_file, "w+") as f:
        f.write(json.dumps(analysis))

    print(analysis)
