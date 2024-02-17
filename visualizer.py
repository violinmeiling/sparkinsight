from nomic import AtlasDataset
from nomic import embed
import numpy as np
import spacy
nlp = spacy.load('en_core_web_md') 
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure, show

#location - 29
#remote - 9
#min salary - 4
#max salary - 2
#worktype - 6
#title - 27

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
        xvector = map.embeddings.df.at[entry[0], 'x']
        yvector = map.embeddings.df.at[entry[0], 'y']
        jobstoreturn.append([originaldata[int(entry[0])][27], xvector, yvector])
    return(jobstoreturn)

class ZoomPan:
    def __init__(self):
        self.press = None
        self.cur_xlim = None
        self.cur_ylim = None
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.xpress = None
        self.ypress = None


    def zoom_factory(self, ax, base_scale = 2.):
        def zoom(event):
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()

            xdata = event.xdata # get event x location
            ydata = event.ydata # get event y location

            if event.button == 'down':
                # deal with zoom in
                scale_factor = 1 / base_scale
            elif event.button == 'up':
                # deal with zoom out
                scale_factor = base_scale
            else:
                # deal with something that should never happen
                scale_factor = 1
                print(event.button)

            new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

            relx = (cur_xlim[1] - xdata)/(cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata)/(cur_ylim[1] - cur_ylim[0])

            ax.set_xlim([xdata - new_width * (1-relx), xdata + new_width * (relx)])
            ax.set_ylim([ydata - new_height * (1-rely), ydata + new_height * (rely)])
            ax.figure.canvas.draw()

        fig = ax.get_figure() # get the figure of interest
        fig.canvas.mpl_connect('scroll_event', zoom)

        return zoom

    def pan_factory(self, ax):
        def onPress(event):
            if event.inaxes != ax: return
            self.cur_xlim = ax.get_xlim()
            self.cur_ylim = ax.get_ylim()
            self.press = self.x0, self.y0, event.xdata, event.ydata
            self.x0, self.y0, self.xpress, self.ypress = self.press

        def onRelease(event):
            self.press = None
            ax.figure.canvas.draw()

        def onMotion(event):
            if self.press is None: return
            if event.inaxes != ax: return
            dx = event.xdata - self.xpress
            dy = event.ydata - self.ypress
            self.cur_xlim -= dx
            self.cur_ylim -= dy
            ax.set_xlim(self.cur_xlim)
            ax.set_ylim(self.cur_ylim)

            ax.figure.canvas.draw()

        fig = ax.get_figure() # get the figure of interest

        # attach the call back
        fig.canvas.mpl_connect('button_press_event',onPress)
        fig.canvas.mpl_connect('button_release_event',onRelease)
        fig.canvas.mpl_connect('motion_notify_event',onMotion)

        #return the function
        return onMotion

def plot(rawlist):
    x = []
    y = []
    n = []

    for item in rawlist:
        n.append(item[0])
        x.append(item[1])
        y.append(item[2])

    fig = figure()

    ax = fig.add_subplot(111, xlim=(-50,50), ylim=(-50,50), autoscale_on=False)
    
    ax.scatter(x,y)
    for i, txt in enumerate(n):
        ax.text(x[i], y[i], txt)
    scale = 1.1
    zp = ZoomPan()
    figZoom = zp.zoom_factory(ax, base_scale = scale)
    figPan = zp.pan_factory(ax)
    show()

applyfilters(True, "MN", -1, -1, False)
if len(jobindexes) == 0:
    print("no jobs found :(")
else:
    plot(pullsimilar("education"))

