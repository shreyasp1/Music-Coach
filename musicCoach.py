## Music Coach: takes the recording and graphs the differences
# between the user and original pitches
# Author: Shreya Prakash

# imports 
import pyaudio
import wave
import scipy.io.wavfile as wavfile
import numpy as np
import matplotlib

# matplotlib specifications
# want to be able to use matplotlib along with tkinter
# window
matplotlib.use('TkAgg')


import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as mpatches
from matplotlib import style

# for the threading
import math
import time

# for uploading files
from contextlib import closing
# for UI
import random

# GUI
from tkinter import *
from tkinter.filedialog import askopenfilename

# Import Recorder class from file
from recorder import Recorder

from testSound import AudioFile

# Use ggplot style
style.use('ggplot')

### GLOBAL VARIABLE INITIALIZATION ###
DATA_INDEX = 1
userPitches = []
origPitches = []
userTime = []
root = Tk()

# setting up the matplotlib figure and it's subplots
f = plt.figure(figsize=(7 , 10), dpi=100)
a = f.add_subplot(211)
a_diff = f.add_subplot(212)


# used this format from mode dispatcher in cs notes
####################################
# init
####################################

# initializes all shared variables
def init(data):

    # for all modes:
    data.uploadIconx0 = data.width//2
    data.uploadIcony0 = data.height//2+35

    data.startIconx0 = data.width//2
    data.startIcony0 = data.height//2+75

    data.graphIconx0 = data.width//2
    data.graphIcony0 = data.height//2+115

    data.quitIconx0 = data.width//2
    data.quitIcony0 = data.height//2+165

    data.splashpageIconsxDiff = 70
    data.splashpageIconsyDiff = 15


    # for splashScreen
    data.mode = "splashScreen"
    data.origFileName = "C.wav"
    data.duration = None
    data.upload = False

    # recording mode
    data.done = False
    data.recording = False
    data.userFileName = ""
    data.userRecording = ""

    # result mode
    data.origPitches = []
    data.userPitches = []
    data.userTime = None
    data.origTime = None
    data.diffTimes = None
    data.stepsDiff = None
    
    # Threading
    data.song = ""
    data.songPlayed = False
    
    # for calculating percentage
    data.totalDiff = 0
    data.totalPitches = 0
    data.percentage = None
    data.resultCalculated = False

    ## UI animations
    # used in splashScreen and recording
    data.dots = 40
    dots = 40
    data.dotsx = [random.randint(1, data.width-1) for i in range(dots)]
    data.dotsy = [random.randint(1, data.height-1) for i in range(dots)]
    data.dotsr = [random.randint(5, 20) for i in range(dots)]
    colors = ["blue", "green", "orange", "violet red", "purple"]
    data.dotsColor = [random.choice(colors) for i in range(dots)]

    # used in help screen
    data.colors = ["blue", "gold", "violet red", "purple"]

    # used in result
    data.r = 0
    data.x, data.y = data.width//2, data.height//2


####################################
# Mode dispatcher
####################################

def mousePressed(event, data):
    if (data.mode == "splashScreen"): splashScreenMousePressed(event, data)
    elif (data.mode == "recording"):  recordingMousePressed(event, data)
    elif (data.mode == "result"):     resultMousePressed(event, data)
    elif (data.mode == "help"):     helpMousePressed(event, data)

def keyPressed(event, data):
    if (data.mode == "splashScreen"): splashScreenKeyPressed(event, data)
    elif (data.mode == "recording"):  recordingKeyPressed(event, data)
    elif (data.mode == "result"):     resultKeyPressed(event, data)
    elif (data.mode == "help"):     helpKeyPressed(event, data)

def timerFired(data):
    if (data.mode == "splashScreen"): splashScreenTimerFired(data)
    elif (data.mode == "recording"):  recordingTimerFired(data)
    elif (data.mode == "result"):     resultTimerFired(data)
    elif (data.mode == "help"):     helpTimerFired(data)

def redrawAll(canvas, data):
    if (data.mode == "splashScreen"): splashScreenRedrawAll(canvas, data)
    elif (data.mode == "recording"):  recordingRedrawAll(canvas, data)
    elif (data.mode == "result"):     resultRedrawAll(canvas, data)
    elif (data.mode == "help"):     helpRedrawAll(canvas, data)


####################################
# splashScreen mode
####################################

def splashScreenMousePressed(event, data):
    (x,y) = (event.x, event.y)

    # checks if rectangle is clicked
    if (x>=data.uploadIconx0-data.splashpageIconsxDiff and 
        x<=data.uploadIconx0+data.splashpageIconsxDiff and
        y>=data.uploadIcony0-data.splashpageIconsyDiff and
        y<=data.uploadIcony0+data.splashpageIconsyDiff):

        # will upload the file
        fname = askopenfilename(filetypes=(("Wav Files", "*.wav"),
                                             ("All files", "*.*") ))
        data.origFileName = fname
        data.duration = findDuration(data)
        data.upload = True

    # will check if file uploaded and rectangle clicked before starting
    elif (x>=data.startIconx0-data.splashpageIconsxDiff and 
        x<=data.startIconx0+data.splashpageIconsxDiff and
        y>=data.startIcony0-data.splashpageIconsyDiff and
        y<=data.startIcony0+data.splashpageIconsyDiff and
        data.upload):

        data.mode = "recording"

    # will go to help screen
    elif (x>=data.graphIconx0-data.splashpageIconsxDiff and 
        x<=data.graphIconx0+data.splashpageIconsxDiff and
        y>=data.graphIcony0-data.splashpageIconsyDiff and
        y<=data.graphIcony0+data.splashpageIconsyDiff):

        data.mode = "help"

def splashScreenKeyPressed(event, data):
    pass

def findDuration(data):
    # used some of this code to get duration
    # http://stackoverflow.com/questions/7833807/
    # get-wav-file-length-or-duration

    # making it a shorter variable name by renaming as audio
    with closing(wave.open(data.origFileName,'r')) as audio:
        # gets the frames of the recording
        frames = audio.getnframes()
        # gets the rate
        rate = audio.getframerate()
        # duration is frames/rate
        duration = frames / float(rate)
        # want the user to have a little more time than the recording
        # so will ceil the the duration
        return(math.ceil(duration))

# for UI, moving dots
def splashScreenTimerFired(data):
    for dot in range(data.dots):
        if data.dotsy[dot] == data.height:
            data.dotsy[dot] = 0
        data.dotsy[dot] += 1


def splashScreenRedrawAll(canvas, data):
    # background
    canvas.create_rectangle(0,0, data.width, data.height, 
        fill = "light sky blue")

    # draws dots
    for dot in range(data.dots):
        canvas.create_oval(data.dotsx[dot]-data.dotsr[dot],
            data.dotsy[dot]-data.dotsr[dot], 
            data.dotsx[dot]+data.dotsr[dot],
            data.dotsy[dot]+data.dotsr[dot], fill = data.dotsColor[dot])

    # title
    canvas.create_text(data.width/2, data.height/2-20,
                       text="Welcome to the Music Coach!", font="Arial 26 bold")
    
    # draws upload button
    canvas.create_rectangle(data.uploadIconx0-data.splashpageIconsxDiff, 
        data.uploadIcony0+data.splashpageIconsyDiff, 
        data.uploadIconx0+data.splashpageIconsxDiff , 
        data.uploadIcony0-data.splashpageIconsyDiff, fill = "lavender") 

    canvas.create_text(data.uploadIconx0, data.uploadIcony0,
        text="Upload File")

    # draws start button
    canvas.create_rectangle(data.startIconx0-data.splashpageIconsxDiff, 
        data.startIcony0+data.splashpageIconsyDiff, 
        data.startIconx0+data.splashpageIconsxDiff , 
        data.startIcony0-data.splashpageIconsyDiff, fill = "lavender") 

    canvas.create_text(data.startIconx0, data.startIcony0,
        text="Start")

    # draws help button
    canvas.create_rectangle(data.graphIconx0-data.splashpageIconsxDiff, 
        data.graphIcony0+data.splashpageIconsyDiff, 
        data.graphIconx0+data.splashpageIconsxDiff , 
        data.graphIcony0-data.splashpageIconsyDiff, fill = "lavender") 

    canvas.create_text(data.graphIconx0, data.graphIcony0,
        text="Help")

    # will tell if file uploaded successfully
    if data.upload:
        canvas.create_text(data.width//2, 
                            data.startIcony0 + data.splashpageIconsxDiff,
                           text="""File Uploaded Successfully""", 
                           font="Arial 20") 


####################################
# help mode
####################################

def helpMousePressed(event, data):
    (x,y) = (event.x, event.y)

    # goes back to home button
    if (x>=data.graphIconx0-data.splashpageIconsxDiff and 
        x<=data.graphIconx0+data.splashpageIconsxDiff and
        y>=data.graphIcony0-data.splashpageIconsyDiff and
        y<=data.graphIcony0+data.splashpageIconsyDiff):

        data.mode = "splashScreen"

def helpKeyPressed(event, data):
    pass

def helpTimerFired(data):
    pass

def helpRedrawAll(canvas, data):
    # background
    canvas.create_rectangle(0,0, data.width, data.height, 
        fill = "SeaGreen1")

    ## used for drawing the colored question marks
    # left to right diagonal
    colorIndex = 0

    for i in range(100, data.width, 100):
        if (i < data.width//2+100 and i > data.width//2-100 and 
            i<data.height//2+200 and i>data.height//2-200):
            continue
        canvas.create_text(i, i-10, text="?", font="Arial %d"%(12+i//10), 
            fill = data.colors[colorIndex%(len(data.colors))])
        colorIndex+=1

    # right to left diagonal
    colorIndex = 0

    for i in range(100, data.width, 100):
        if (i < data.width//2+100 and i > data.width//2-100 and 
            i<data.height//2+100 and i>data.height//2-100):
            continue
        canvas.create_text(data.width -i, i-10, text="?", 
            font="Arial %d"%(12+i//10), 
            fill = data.colors[colorIndex%(len(data.colors))])
        colorIndex+=1

    # instructions
    canvas.create_text(data.width/2, data.height/2-40,
                       text="You asked for help?", font="Arial 26 bold")
    canvas.create_text(data.width/2, data.height/2-10,
                       text="What to do:", font="Arial 20")
    canvas.create_text(data.width/2-40, data.height/2+40,
                       text="""
                       Upload the original version of what you are
                       practicing and record your version of it. 
                       Then the Music Coach will show you where 
                       you differed compared to the recording!
                       """, 
                       font="Arial 15")

    # draws back to home button
    canvas.create_rectangle(data.graphIconx0-data.splashpageIconsxDiff, 
        data.graphIcony0+data.splashpageIconsyDiff, 
        data.graphIconx0+data.splashpageIconsxDiff , 
        data.graphIcony0-data.splashpageIconsyDiff, fill = "lavender") 

    canvas.create_text(data.graphIconx0, data.graphIcony0,
        text="Back to Home")


####################################
# recording mode
####################################

def recordingMousePressed(event, data):
    (x,y) = (event.x, event.y)

    # checks if pressed record button
    if (x>=data.uploadIconx0-data.splashpageIconsxDiff and 
        x<=data.uploadIconx0+data.splashpageIconsxDiff and
        y>=data.uploadIcony0-data.splashpageIconsyDiff and
        y<=data.uploadIcony0+data.splashpageIconsyDiff):

        data.done = False
        data.recording = True
        # creates instance of recording class
        data.userRecording = Recorder(data.duration)
        # calls the record method
        (data.userFileName) = data.userRecording.record()
        # done recording
        data.recording = False
        data.done = True

    # checks if done recording and will go to next page
    elif (x>=data.startIconx0-data.splashpageIconsxDiff and 
        x<=data.startIconx0+data.splashpageIconsxDiff and
        y>=data.startIcony0-data.splashpageIconsyDiff and
        y<=data.startIcony0+data.splashpageIconsyDiff and
        data.done):

        data.mode = "result"


def recordingKeyPressed(event, data):
    pass

# the dots UI
def recordingTimerFired(data):
    for dot in range(data.dots):
        if data.dotsr[dot] == 25:
            data.dotsr[dot] = 0
        data.dotsr[dot] += 1

def recordingRedrawAll(canvas, data):
    # draws background
    canvas.create_rectangle(0,0, data.width, data.height, 
        fill = "firebrick3")

    # dots UI
    for dot in range(data.dots):
        canvas.create_oval(data.dotsx[dot]-data.dotsr[dot],
            data.dotsy[dot]-data.dotsr[dot], 
            data.dotsx[dot]+data.dotsr[dot],
            data.dotsy[dot]+data.dotsr[dot], fill = data.dotsColor[dot])

    # title
    canvas.create_text(data.width/2, data.height/2-20,
                       text="Record Your Version!", font="Arial 26 bold")

    # record button
    canvas.create_rectangle(data.uploadIconx0-data.splashpageIconsxDiff, 
        data.uploadIcony0+data.splashpageIconsyDiff, 
        data.uploadIconx0+data.splashpageIconsxDiff , 
        data.uploadIcony0-data.splashpageIconsyDiff, fill = "lavender") 

    canvas.create_text(data.uploadIconx0, data.uploadIcony0,
        text="Record")

    # result page button will show up is recording is done
    if data.done:
        canvas.create_rectangle(data.startIconx0-data.splashpageIconsxDiff, 
        data.startIcony0+data.splashpageIconsyDiff, 
        data.startIconx0+data.splashpageIconsxDiff , 
        data.startIcony0-data.splashpageIconsyDiff, fill = "lavender") 

        canvas.create_text(data.startIconx0, data.startIcony0,
            text="Results Page")

        canvas.create_text(data.startIconx0, 
            data.height//2+2*100, text= "Done Recording", 
            font="Arial 18 bold")



####################################
# result mode
####################################

# will reset the recording so can play back
def resetIndex():
    global DATA_INDEX
    DATA_INDEX = 1
            
# will play the audio 
def playAudio(data):
    # creates an instance of audioFile class
    # then start audio file
    data.song = AudioFile(data.userFileName)
    data.song.start()
    resetIndex()

# will stop the audio
def stopAudio(data):
    data.song.stop()

# followed tutorial from
# https://pythonprogramming.net/embedding-live-matplotlib-graph-tkinter-gui/
# for animation

# cannot pass in data because called seperately from the tkinter GUI
def animate(i):
    # using the global that were initialized
    global DATA_INDEX
    global userTime
    global userPitches
    global origPitches

    # for the y-axis
    ylabels = ["silence", "C", "C#", "D", "D#", "E", "F", 
    "F#", "G", "G#", "A", "A#", "B"]

    # will show only a section of the data
    xList = userTime[:DATA_INDEX]
    yList = userPitches[:DATA_INDEX]
    y1List = origPitches[:DATA_INDEX]
    DATA_INDEX += 1

    # will stop incrementing data index
    if DATA_INDEX >= len(userPitches):
        DATA_INDEX = len(userPitches)-1 

    # initialize the plot labels
    a.set_xlabel("Times (s)")
    a.set_ylabel("Pitches (notes)")
    a.set_yticks(np.arange(13))
    a.set_yticklabels(ylabels)
    a.set_ylim(-1,15)
    red_patch = mpatches.Patch(color='red', label='Your notes')
    blue_patch = mpatches.Patch(color='blue', label='Original notes')
    a.legend(handles= [red_patch, blue_patch], prop={'size':8})
    a.set_title("Your Pitches and the Original Pitches")
    f.tight_layout()

    # it is so can redraw the graph everytime it is called
    a.clear()

    # to set the labels again after plot is cleared
    a.set_xlabel("Times (s)")
    a.set_ylabel("Pitches (notes)")
    a.set_yticks(np.arange(13))
    a.set_yticklabels(ylabels)
    a.set_ylim(-1,15)
    red_patch = mpatches.Patch(color='red', label='Your notes')
    blue_patch = mpatches.Patch(color='blue', label='Original notes')
    a.legend(handles= [red_patch, blue_patch], prop={'size':8})
    a.set_title("Your Pitches and the Original Pitches")
    f.tight_layout()
    
    # plotting
    a.plot(xList, y1List, "bs", xList, yList, "ro")

def resultMousePressed(event, data):

    (x,y) = (event.x, event.y)

    # will modify globals so can use them in animate
    global userTime
    global userPitches
    global origPitches

    # will use find frequencies method, in midi freq
    (data.userTime, data.userPitches) = (data.userRecording.findFrequencies(data.userFileName,data.duration))
    (data.origTime, data.origPitches) = (data.userRecording.findFrequencies(data.origFileName,data.duration))

    # will find differences in frequencies
    data.diffTimes, data.stepsDiff = data.userRecording.findDifference(data.origTime, 
    data.userTime, data.origPitches, data.userPitches)

    # getting the note values
    data.origPitches = data.userRecording.getNotes(data.origPitches)
    data.userPitches = data.userRecording.getNotes(data.userPitches)

    # need to do this since data.userTime is a np array
    for i in range(len(data.userTime)):
        userTime.append(data.userTime[i])
    
    # setting the globals
    userPitches = data.userPitches
    origPitches = data.origPitches

    ## calculating accuracy
    # calculating the number of differences
    for diff in data.stepsDiff:
        if math.isnan(diff):
            continue
        if int(diff) != 0:
            data.totalDiff += 1

    # the total pitches
    data.totalPitches = len(data.userPitches)
    
    # calculating the percentage
    data.percentage = int(((data.totalPitches-data.totalDiff)/data.totalPitches)*100)
    data.resultCalculated = True

    # checks if the live graph button is clicked
    if (x>=data.uploadIconx0-data.splashpageIconsxDiff and 
        x<=data.uploadIconx0+data.splashpageIconsxDiff and
        y>=data.uploadIcony0-data.splashpageIconsyDiff and
        y<=data.uploadIcony0+data.splashpageIconsyDiff):

        # making the bar graph
        global a_diff

        bar_width = 0.10
        a_diff.bar(data.diffTimes, data.stepsDiff, bar_width, color='b')
        a_diff.set_xlabel("Times (s)")
        a_diff.set_ylabel("Note Differences (1/2 step notes)")
        a_diff.set_xlim(-0.25,data.duration + 0.25)
        a_diff.set_ylim(0,15)
        a_diff.set_yticks(np.arange(13))
        
        a_diff.set_title("Differences in User and Original Pitches")
            
        # don't want to block so can quit plot
        plt.show(block=False)

    # so plays at same time when button is clicked, using same dimensions
    if (x>=data.uploadIconx0-data.splashpageIconsxDiff and 
        x<=data.uploadIconx0+data.splashpageIconsxDiff and
        y>=data.uploadIcony0-data.splashpageIconsyDiff and
        y<=data.uploadIcony0+data.splashpageIconsyDiff):

        playAudio(data) 
        data.songPlayed = True

    # quit button
    elif (x>=data.startIconx0-data.splashpageIconsxDiff and 
        x<=data.startIconx0+data.splashpageIconsxDiff and
        y>=data.startIcony0-data.splashpageIconsyDiff and
        y<=data.startIcony0+data.splashpageIconsyDiff):

        # will close threads gracefully
        stopAudio(data)
        plt.close("all")
        global root
        root.quit()

    # restart button
    elif (x>=data.graphIconx0-data.splashpageIconsxDiff and 
        x<=data.graphIconx0+data.splashpageIconsxDiff and
        y>=data.graphIcony0-data.splashpageIconsyDiff and
        y<=data.graphIcony0+data.splashpageIconsyDiff):

        # will close audio thread and plots and go back to start
        stopAudio(data)
        plt.close("all")
        init(data)

def resultKeyPressed(event, data):
    pass

# UI square
def resultTimerFired(data):
    if data.r == data.width//2 or data.r == data.height//2:
        data.r = 0

    increaseSize = 5
    data.r += increaseSize

def resultRedrawAll(canvas, data):
    margin = 50
    # background
    canvas.create_rectangle(0,0, data.width, data.height, 
        fill = "DarkOrchid4")

    canvas.create_rectangle(data.x-data.r, data.y-data.r, data.x+data.r,
        data.y+data.r, fill = "turquoise")

    # title
    canvas.create_text(data.width//2, 10*2,
                       text="Here is how you did!", font="Arial 26 bold")

    # will show accuracy if it is calculated
    if data.resultCalculated:
        canvas.create_text(data.width//2, 
                    data.height-margin,
                    text="Your Accuracy: %d%%" % (data.percentage), 
                   font="Arial 18 bold")

    # see live results button
    canvas.create_rectangle(data.uploadIconx0-data.splashpageIconsxDiff, 
        data.uploadIcony0+data.splashpageIconsyDiff, 
        data.uploadIconx0+data.splashpageIconsxDiff , 
        data.uploadIcony0-data.splashpageIconsyDiff, fill = "lavender") 

    canvas.create_text(data.uploadIconx0, data.uploadIcony0,
        text="See Live Results")

    # quit button
    canvas.create_rectangle(data.startIconx0-data.splashpageIconsxDiff, 
        data.startIcony0+data.splashpageIconsyDiff, 
        data.startIconx0+data.splashpageIconsxDiff , 
        data.startIcony0-data.splashpageIconsyDiff, fill = "lavender") 

    canvas.create_text(data.startIconx0, data.startIcony0,
        text="Quit")

    # restart button
    canvas.create_rectangle(data.graphIconx0-data.splashpageIconsxDiff, 
        data.graphIcony0+data.splashpageIconsyDiff, 
        data.graphIconx0+data.splashpageIconsxDiff , 
        data.graphIcony0-data.splashpageIconsyDiff, fill = "lavender") 

    canvas.create_text(data.graphIconx0, data.graphIcony0,
        text="Restart")

    
####################################
# run function
####################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)

    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    init(data)
    # create the root and the canvas
    global root
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    ani = animation.FuncAnimation(f, animate, repeat=False, interval=90)
    root.mainloop()  # blocks until window is closed



run(600, 600)

