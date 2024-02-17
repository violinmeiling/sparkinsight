import numpy as np
import spacy
nlp = spacy.load('en_core_web_md') 
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure, show
import requests
from resumeparse import skilllist
import json
from tkinter import *
import pyautogui

  
# import messagebox from tkinter module 
import tkinter.messagebox 
#location - 29
#remote - 9
#min salary - 4
#max salary - 2
#worktype - 6
#title - 27
#jobid - 1
#description - 28
#url - 30

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
                #print(event.button)

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
    
import ctypes  # An included library with Python install.
def Mbox(title, text, style):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)


def plot(rawlist):
    x = []
    y = []
    n = []

    xavg = 0
    yavg = 0

    for i in range(len(rawlist)-1):
        #print(rawlist[i])
        n.append(rawlist[i][0])
        x.append(float(rawlist[i][1]))
        y.append(float(rawlist[i][2]))
        xavg += ((len(rawlist) - i)/len(rawlist)) * float(rawlist[i][1])
        yavg += ((len(rawlist) - i)/len(rawlist)) * float(rawlist[i][2])

    xavg = xavg / len(rawlist)
    yavg = yavg / len(rawlist)

    fig = figure()

    ax = fig.add_subplot(111, xlim=(-50,50), ylim=(-50,50), autoscale_on=False)

    
    
    ax.scatter(x,y, picker=True)
    ax.plot(xavg, yavg, 'ro')
    ax.text(xavg, yavg, "You")
    for i, txt in enumerate(n):
        ax.text(x[i], y[i], txt)
    scale = 1.1
    zp = ZoomPan()
    figZoom = zp.zoom_factory(ax, base_scale = scale)
    figPan = zp.pan_factory(ax)

    def onpick3(event):
        index = event.ind
        ind = int(index)
        message = str('Job title: ' + str(rawlist[ind][0]) + '\n' + 'Company ID: ' + str(rawlist[ind][3]) + '\n' + 'Description: ' + str(rawlist[ind][4]) + '\n' + 'Linkedin URL: ' + str(rawlist[ind][5]) + '\n\n' + '----------------------------------------------------------' + '\n')
        print(message)

    fig.canvas.mpl_connect('pick_event', onpick3)

    show()

f = open('joblist.json')
 
# returns JSON object as 
# a dictionary
data = json.load(f)
plot(data)