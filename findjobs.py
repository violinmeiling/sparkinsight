from nomic import AtlasDataset
from nomic import embed
import numpy as np
import json
from resumeparse import skilllist
import spacy
import spacy
nlp = spacy.load('en_core_web_md') 
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure, show
import requests
from resumeparse import skilllist

dataset = AtlasDataset('linkedindescription')
map = dataset.maps[0]
originaldata = (np.array(map.data.df)).tolist()
topicarray = (np.array(map.topics.df)).tolist()

jobindexes = []
workingdata = []

def applyfilters(internship, state, min, max, remote):
    filters = []
    if (internship):
        filters.append(lambda x: x[6] == "Internship")
    if (state != ''):
        filters.append(lambda x: str(x[29][len(x[29])-2:len(x[29])]) == state)
    if (min != -1):
        filters.append(lambda x: x[4] > 10)
    if (max != -1):
        filters.append(lambda x: x[2] < 40000)
    if (remote):
        filters.append(lambda x: x[9] == 1)
    
    for entry in originaldata:
        #print(entry)
        addentry = True
        for i in range(len(filters)-1):
            if not filters[i](entry):
                addentry = False
        if (addentry):
            jobindexes.append(originaldata.index(entry))

    for jobid in jobindexes:
        workingdata.append([[jobid], [(originaldata[jobid][27] + " " + topicarray[jobid][1] + " " + topicarray[jobid][2]).split(" ")][0]])

def pullsimilar(searchkey):
    scores = []
    jobstoreturn = []
    for entry in workingdata:
        entrywords = ""
        for word in entry[1]:
            entrywords += word + " "
        tokens = nlp(searchkey + " " + entrywords)
        similarity = 0
        count = 0
        for firstword in tokens:
            for secondword in tokens:
                similarity += firstword.similarity(secondword)
                count += 1
        result = similarity / count
        scores.append([int(entry[0][0]), result])
    scoresnp = np.array(scores)
    scoresnp_sorted = scoresnp[scoresnp[:, 1].argsort()[::-1]]
    scores_sorted = scoresnp_sorted.tolist()[0:20]

    for entry in scores_sorted:
        xvector = map.embeddings.df.at[entry[0], 'x']
        yvector = map.embeddings.df.at[entry[0], 'y']
        jobstoreturn.append([str(originaldata[int(entry[0])][27]), str(xvector), str(yvector), str(originaldata[int(entry[0])][1]), str(originaldata[int(entry[0])][28]), str(originaldata[int(entry[0])][30])])
    return(jobstoreturn)

applyfilters(True, "MN", -1, -1, False)
if len(workingdata) == 0:
    print("no jobs found :(")
else:
    json_object = json.dumps(pullsimilar(skilllist))
    # Writing to sample.json
    with open("joblist.json", "w") as outfile:
        outfile.write(json_object)