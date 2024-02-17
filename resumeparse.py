import json
 
# Opening JSON file
f = open('resumei.json')
 
# returns JSON object as 
# a dictionary
data = json.load(f)

skilllist = " "

for i in range(len(data[0]['data']['skills'])):
    skilllist += data[0]['data']['skills'][i]['name'] + " "
 
print(skilllist)
# Iterating through the json
# list

 
# Closing file
f.close()