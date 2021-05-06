import os
import json
import matplotlib.pyplot as plt
import numpy as np

def digest(path):
    files = []
    labels = []
    analysis = []
    data = {}
    for f in os.listdir(path):
        if "analysis" in f:
            files.append(f)
    files.sort()

    for f in files:
        with open(path+"/"+f,"r") as file:
            analysis.append(json.loads(file.read()))
        labels.append((f.split("."))[0])

    for a in analysis:
        for attribute,fields in a.items():
            if attribute not in data:
                    data[attribute] = {}
            for field,keys in fields.items():
                if field not in data[attribute]:
                    data[attribute][field] = {}
                for key,value in keys.items():
                    if key not in data[attribute][field]:
                        data[attribute][field][key] = []
                    data[attribute][field][key].append(float(value))

    return labels,data

def show(d, attribute, field, labels):
    X_axis = np.arange(len(labels))

    space = [-0.3,-0.1,0.1,0.3]
    i = 0
    for k in d[attribute][field]:
            plt.bar(X_axis+space[i], d[attribute][field][k], 0.2, label = k)
            i+=1
    
    plt.xticks(X_axis, labels)
    plt.title(attribute+"-"+field)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    path = "experiments/2"
    labels,d = digest(path)

    with open(path+"/digest.txt","w+") as f:
        json.dump(d,f)

    try:
        os.mkdir("./results")
    except:
        pass
    
    for attribute in d:
        for field in d[attribute]:
            if field != "total":# and field != "free":
                if field == "percent":
                    plt.ylabel("%")
                elif field == "frequency":
                    plt.ylabel("MHz")
                elif field == "temperature":
                    plt.ylabel("degrees Celsius")
                elif attribute == "disk":
                    plt.ylabel("GB")
                elif attribute == "memory":
                    plt.ylabel("MB")
                plt.bar(range(len(labels)),d[attribute][field]["avg"])
                plt.xticks(range(len(labels)), labels)
                plt.title(attribute+"-"+field)
                plt.savefig("./results/"+attribute+"-"+field+".png")
                plt.show()

    """
    plt.bar(range(len(labels)),d["cpu"]["percent"]["avg"])
    plt.xticks(range(len(labels)), labels)
    plt.show()
    """