from nomic import AtlasDataset
from nomic import embed
import numpy as np
import spacy
nlp = spacy.load('en_core_web_md') 


dataset = AtlasDataset('linkedindescription')
map = dataset.maps[0]

originaldata = (np.array(map.data.df)).tolist()
topicarray = (np.array(map.topics.df)).tolist()

xvector = map.embeddings.df.at[0, 'x']
yvector = map.embeddings.df.at[0, 'y']

uniquewords = np.unique(topicarray)

#for word in uniquewords:
 #   if not word.isnumeric():
  #      print(word)

jobindexes = []

#print(originaldata)

for entry in originaldata:
    if entry[6] == "Internship":
        jobindexes.append(originaldata.index(entry))
        #print(entry[6])

workingdata = []

#print(originaldata)

for jobid in jobindexes:
    workingdata.append([[jobid], [(originaldata[jobid][27] + " " + topicarray[jobid][1] + " " + topicarray[jobid][2]).split(" ")][0]])

scores = []

def pullsimilar(searchkey):
    jobstoreturn = []
    for entry in workingdata:
        i = 0
        result = 0
        for word in entry[1]:
            #print(word)
            tokens = nlp(searchkey + " " + word)
            if len(tokens) == 2:
                token1, token2 = tokens[0], tokens[1] 
                similarity = token1.similarity(token2)
                result += similarity
                i += 1
        result = result / i
        scores.append([int(entry[0][0]), result])
    scoresnp = np.array(scores)
    scoresnp_sorted = scoresnp[scoresnp[:, 1].argsort()[::-1]]
    scores_sorted = scoresnp_sorted.tolist()[0:10]

    for entry in scores_sorted:
        jobstoreturn.append(originaldata[int(entry[0])][27])
    
    return(jobstoreturn)

print(pullsimilar("education"))