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
        labels.append(((f.split("."))[0]).replace("probe","Trial").replace("O", " Opt.").replace("Trial0","Control"))

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
    path = "experiments"

    try:
        os.mkdir("./results")
    except:
        pass

    labels,d = digest(path)
    newlabels = [labels[i] for i in [0, 2, 1, 4, 3, 6, 5]]
    #newlabels = labels

    with open(path+"/digest.txt","w+") as f:
        json.dump(d,f)

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

                data = [d[attribute][field]["avg"][i] for i in [0, 2, 1, 4, 3, 6, 5]]
                #data = d[attribute][field]["avg"]
                plt.bar(range(len(newlabels)),data, color=["#75a927","#bc1142"])
                plt.xticks(range(len(newlabels)), newlabels)
                plt.title(attribute+"-"+field)
                plt.tight_layout()
                plt.savefig("./results/"+attribute+"-"+field+".png", dpi=199)
                plt.show()

    with open(path+"/frames_size.txt","r") as f:
        data = f.readlines()

    sizes = []
    for d in data:
        sizes.append(float(d.replace("\n",""))/1024.0)

    newsizes = [sizes[i] for i in [1, 0, 3, 2, 5, 4]]
    #newsizes = sizes

    plt.bar(range(len(newlabels[1:])),newsizes,color=["#75a927","#bc1142"])
    plt.xticks(range(len(newlabels[1:])), newlabels[1:])
    plt.title("local frames-size")
    plt.ylabel("MB")
    plt.savefig("./results/local frames-size.png")
    plt.show()

    """
    plt.bar(range(len(labels)),d["cpu"]["percent"]["avg"])
    plt.xticks(range(len(labels)), labels)
    plt.show()
    """

    