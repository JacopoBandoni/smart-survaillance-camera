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

def reports(path):
    files = []
    analysis = {}
    data = {}
    for f in os.listdir(path):
        if "report" in f:
            files.append(f)
    files.sort()

    for f in files:
        label = ((f.split("."))[0]).replace("probe","Trial").replace("O", " Opt.").replace("Trial0","Control")
        analysis[label] = []
        with open(path+"/"+f,"r") as file:
            for l in file.readlines():
                analysis[label].append(json.loads(l))


    data = {}
    for a,ls in analysis.items():
        data[a] = {}
        for sample in ls:
            for attribute,field in sample.items():
                if attribute != "timestamp":
                    if attribute not in data[a]:
                        data[a][attribute] = {}
                    for k,v in field.items():
                        if k not in data[a][attribute]:
                            data[a][attribute][k] = []
                        (data[a][attribute][k]).append(v)

    values = {}
    for label,data in data.items():
        for attribute,field in data.items():
            if attribute not in values:
                values[attribute] = {}
            for k,v in field.items():
                if k not in values[attribute]:
                    values[attribute][k] = {}
                values[attribute][k][label] = v

    return values

if __name__ == "__main__":
    report = reports("experiments")
    
    for attribute,fields in report.items():
        for field,label in fields.items():
            if field != "total":# and field != "free":
                for l,v in label.items():
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
                    plt.plot(v[::12], label=l)

                plt.legend()
                plt.title(attribute+"-"+field)
                plt.tight_layout()
                plt.savefig("./results/c-"+attribute+"-"+field+".png", dpi=199)
                plt.show()

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
                plt.savefig("./results/h-"+attribute+"-"+field+".png", dpi=199)
                plt.show()

    with open(path+"/frames_size.txt","r") as f:
        data = f.readlines()

    sizes = []
    for d in data:
        sizes.append(float(d.replace("\n",""))/1024.0)

    newsizes = [sizes[i] for i in [1, 0, 3, 2, 5, 4]]
    #newsizes = sizes

    plt.bar(range(len(newlabels[1:])),newsizes,color=["#bc1142","#75a927"])
    plt.xticks(range(len(newlabels[1:])), newlabels[1:])
    plt.title("local frames-size")
    plt.ylabel("MB")
    plt.savefig("./results/local frames-size.png", dpi=199)
    plt.show()

    
    with open(path+"/network.txt","r") as f:
        data = json.loads(f.read())

    values = {}
    for trial in data:
        for k,v in data[trial].items():
            if k not in values:
                values[k] = []
            values[k].append(float(v)/1024.0/1024.0)

    for k,v in values.items():
        newv = [v[i] for i in [1, 0, 3, 2, 5, 4]]
        #newsizes = sizes

        plt.bar(range(len(newlabels[1:])),newv,color=["#bc1142","#75a927"])
        plt.xticks(range(len(newlabels[1:])), newlabels[1:])
        if k == "Total":
            plt.title("megabytes-sent")
            plt.ylabel("MB")
            plt.savefig("./results/megabytes-sent.png", dpi=199)
        else:
            plt.title(k.lower())
            plt.ylabel("MB/s")
            plt.savefig("./results/"+k.lower()+".png", dpi=199)
        plt.show()



    """
    plt.bar(range(len(labels)),d["cpu"]["percent"]["avg"])
    plt.xticks(range(len(labels)), labels)
    plt.show()
    """

    