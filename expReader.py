##expReader.py
##Author: Benjamin Johnson
##CreatedOn: March 10 2013
##
## This is a simple python application that takes in the pid of Path of Exile,
##    and the memory location of your character's experience. It displays a small
##    window with some interesting information about your rate of experience gain.
##    hopefully in the future it will log your experience gain, for charting purposes.
##
## Please note that the use of this script is probably a Path of Exile ToS violation
## I am not responsible if you get banned, suspended, scolded, or made fun of.
##
## Note: This file uses tabs for indentation.

from ctypes import *
from ctypes.wintypes import *
from time import sleep
from datetime import datetime
from Tkinter import *
from struct import *

#Change these values to configure the program (eventually read these from a config file)
UPDATERATE = .005 #
ALPHA = 0.8 #Set this to 1.0 for opaque, or 0.0 for transparent
FRAMELESS = 0 #set this to 1 to make a frameless window (not currently draggable)
CHARNAME = 'DreamBowXVI' #This should be automatically found in the future
SHORTTERMDURATION = 60 #number of seconds for the short term exp duration
LONGTERMDURATION = 600 #number of seconds for the long term exp duration

def outputDebugData(buff,datadummy,bytesRead):
    print unpack('I',datadummy)
    print datadummy
    print buff
    print bytesRead.value
    print '-----'

def trackXP(tracking,buttonsv):
    #flip the tracking state
    if not tracking['value']:
        print 'starting to track'
        buttonsv.set('Stop Tracking')
        tracking['value'] = True
        tracking['startTime'] = datetime.utcnow()
        print datetime.utcnow() #debugging
    else:
        print 'stopping tracking'
        tracking['value'] = False
        buttonsv.set('Start Tracking')
        tracking['endTime'] = datetime.utcnow()
        tracking['finishedTracking'] = True
        print tracking['endTime']-tracking['startTime'] #debugging
    
        
pid = 3532
op = windll.kernel32.OpenProcess
rpm = windll.kernel32.ReadProcessMemory
ch = windll.kernel32.CloseHandle
PAA = 0x1F0FFF
addy = 0x60EDCB98

#set up the window
root = Tk()
# The experience label
expsv = StringVar()
expsv.set('hello, go kill some stuff')
currentExp = Label(root, textvariable = expsv)
currentExp.pack()
# The lastkill label
lastkillsv = StringVar()
lastkillsv.set('lastkill: N/A')
lastKill = Label(root,textvariable = lastkillsv)
lastKill.pack()
# The Short term experience per hour label
shorttermexpsv = StringVar()
shorttermexpsv.set('ShortTerm XPPH: N/A')
shorttermexp = Label(root,textvariable = shorttermexpsv)
shorttermexp.pack()
# The long term experience per hour label
longtermexpsv = StringVar()
longtermexpsv.set('LongTerm XPPH: N/A')
longtermexp = Label(root,textvariable = longtermexpsv)
longtermexp.pack()
# XP earned in the past hour
pasthourexpsv = StringVar()
pasthourexpsv.set('Exp earned in the past hour: N/A')
pasthourexp = Label(root,textvariable=pasthourexpsv)
pasthourexp.pack()
# The start button
#This is used as an on/off switch for xp tracking
tracking = {'value':False,'startTime':None, 'endTime':None, 'finishedTracking':False}
buttonsv = StringVar()
buttonsv.set('Start Tracking')
startb = Button(root,textvariable=buttonsv,command=lambda: trackXP(tracking, buttonsv))
startb.pack()
#main window attributes and configuration
root.attributes('-topmost',True)
root.attributes('-alpha', ALPHA)
#root.configure(background='white')
root.overrideredirect(FRAMELESS)
#Show it for the first time
root.update()
#Get the connection to the game
ph = op(PAA,False,int(pid))

#set up the list of experience readings that will be added to each second
expList = []
lastupdate = datetime.now()

#perform the initial read
datadummy = b'.'*4
buff = c_char_p(datadummy)
bufferSize = (len(buff.value))
bytesRead = c_ulong(0)
rpm(ph,addy,buff,bufferSize,byref(bytesRead))
lastexp = unpack('I',datadummy)[0]
exp = lastexp

# This is the main loop of the program
while True:
    while tracking['value']:
        datadummy = b'.'*4
        buff = c_char_p(datadummy)
        bufferSize = (len(buff.value))
        bytesRead = c_ulong(0)

        if rpm(ph,addy,buff,bufferSize,byref(bytesRead)):
            exp = unpack('I',datadummy)[0]

            #Set the lastkill label and update the lastexp value
            if lastexp != exp:
                if lastexp != 0:
                    lastkillsv.set("Last Kill: "+str(exp-lastexp))
                outputDebugData(buff,datadummy,bytesRead)
                lastexp = exp
            expsv.set("exp: "+str(exp))
            previous = buff.value
            root.update()
            root.lift()
        #Check the time since last recorded exp value, if it's been more than 1 second, record.
        now = datetime.now()
        timedelta = now-lastupdate
        if timedelta.seconds >= 1:
            expList.append(exp)
            lastupdate = now
        #Check to see if there is enough information to give a short term xp rate
        if len(expList) > SHORTTERMDURATION:
            #calculate the xp per hour
            xpgain = expList[-1]-expList[-(SHORTTERMDURATION-1)]
            xpgainph = xpgain*(3600/SHORTTERMDURATION)
            shorttermexpsv.set('ShortTerm XPPH: '+str(xpgainph))
        else:
            shorttermexpsv.set('ShortTerm XPPH needs more time: '+str(SHORTTERMDURATION-len(expList)))
        if len(expList) > LONGTERMDURATION:
            #calculate the xp per hour
            xpgain = expList[-1]-expList[-(LONGTERMDURATION-1)]
            xpgainph = xpgain*(3600/LONGTERMDURATION)
            longtermexpsv.set('LongTerm XPPH: '+str(xpgainph))
        else:
            longtermexpsv.set('LongTerm XPPH needs more time: '+str(LONGTERMDURATION-len(expList)))
        sleep(UPDATERATE)
    root.update()
    if tracking['finishedTracking']:
        # if we are ever finished tracking, let's write our data to file.
        print 'finished'
        print expList
        print len(expList)
        break #not exactly what we want to do here, but ok for now. Doesn't allow start-stop action
    sleep(.05)

