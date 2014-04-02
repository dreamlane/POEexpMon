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

from time import sleep
from Tkinter import *
import datetime
import locale

from exileprocessor import *

#Change these values to configure the program (eventually read these from a config file)
UPDATERATE = .005 # Time in seconds between reading the exp value.
ALPHA = 0.8 #Set this to 1.0 for opaque, or 0.0 for transparent
FRAMELESS = 0 #set this to 1 to make a frameless window (not currently draggable)
CHARNAME = '' #This should be automatically found in the future. Currently Unused
SHORTTERMDURATION = 60 #number of seconds for the short term exp duration
LONGTERMDURATION = 600 #number of seconds for the long term exp duration
LEVELS = [0,525,1760,3781,7184,12186,19324,29377,43181,61693,85990,117506,
          157384,207736,269997,346462,439268,551295,685171,843709,1030734,
          1249629,1504995,1800847,2142652,2535122,2984677,3496798,4080655,
          4742836,5490247,6334393,7283446,8384398,9541110,10874351,12361842,
          14018289,15859432,17905634,20171471,22679999,25456123,28517857,31897771,
          35621447,39721017,44225461,49176560,54607467,60565335,67094245,74247659,
          82075627,90631041,99984974,110197515,121340161,133497202,146749362,161191120,
          176922628,194049893,212684946,232956711,255001620,278952403,304972236,
          333233648,363906163,397194041,433312945,472476370,514937180,560961898,
          610815862,664824416,723298169,786612664]

def trackXP(tracking,buttonsv):
    #flip the tracking state
    if not tracking['value']:
        print 'starting to track'
        buttonsv.set('Stop Tracking')
        tracking['value'] = True
        tracking['startTime'] = datetime.datetime.utcnow()
        print datetime.datetime.utcnow() #debugging
    else:
        print 'stopping tracking'
        tracking['value'] = False
        buttonsv.set('Start Tracking')
        tracking['endTime'] = datetime.datetime.utcnow()
        tracking['finishedTracking'] = True
        print tracking['endTime']-tracking['startTime'] #debugging

## Set up the window Tkinter window
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
totalexpgainedsv = StringVar()
totalexpgainedsv.set('Exp earned in the past hour: N/A')
totalexpgained = Label(root,textvariable=totalexpgainedsv)
totalexpgained.pack()
# The timer label
timersv = StringVar()
timersv.set('Press the button!')
timerLabel = Label(root, textvariable = timersv)
timerLabel.pack()
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


#set up the list of experience readings that will be added to each second
expList = []
lastupdate = datetime.datetime.utcnow()

#perform the initial read
lastexp = readExperience()
exp = lastexp
currentLevel = 0
while LEVELS[currentLevel] <= exp:
    currentLevel+=1

print currentLevel
#For the commas on numbers
locale.setlocale(locale.LC_ALL, '')
# This is the main loop of the program
while True:
    #Do this while the tracking is turned on
    while tracking['value']:
        #update the timer value
        s = (datetime.datetime.utcnow()-tracking['startTime']).seconds
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        timersv.set('%s:%s:%s' % (hours, minutes, seconds))
        
        exp = readExperience()
        if exp:
            #Set the lastkill label and update the lastexp value
            if lastexp != exp:
                if lastexp != 0:
                    lastkillsv.set("Last Kill: "+locale.format("%d",exp-lastexp,grouping=True))
                lastexp = exp
            #Update the current level
            currentLevel = 0
            while LEVELS[currentLevel] <= exp:
                currentLevel+=1
            expsv.set("exp: "+locale.format("%d",exp,grouping=True)+" Level: "+str(currentLevel))
            root.update()
            root.lift()

        else:
            ##TODO: Handle failure gracefully. To do this. Stop tracking and reset the UI.
            print "something died"
        
        #Check the time since last recorded exp value, if it's been more than 1 second, record.
        now = datetime.datetime.utcnow()
        deltatime = now-lastupdate
        if deltatime.seconds >= 5:
            expList.append((exp,now))
            lastupdate = now#+deltatime-datetime.timedelta(seconds=1)
            ##print lastupdate,now, deltatime
        #Check to see if there is enough information to give a short term xp rate
        if len(expList) > SHORTTERMDURATION/5:
            #calculate the xp per hour
            xpgain = expList[-1][0]-expList[-(SHORTTERMDURATION/5-1)][0]
            xpgainph = xpgain*(3600/SHORTTERMDURATION)
            xptillnext = LEVELS[currentLevel]-exp
            #Get the number of minutes until next level
            xpgainpm = xpgainph/60
            if xpgainpm != 0:
                minutes = xptillnext/xpgainpm
            else:
                minutes = "INF"
            shorttermexpsv.set('ShortTerm XPPH: '+locale.format("%d",xpgainph,grouping=True)+ " Mins to ding: "+str(minutes))
        else:
            shorttermexpsv.set('ShortTerm XPPH needs more time: '+str((SHORTTERMDURATION/5-len(expList))*5))
        #Check to see if there is enough information to give a long term xp rate
        if len(expList) > LONGTERMDURATION/5:
            #calculate the xp per hour
            xpgain = expList[-1][0]-expList[-(LONGTERMDURATION/5-1)][0]
            xpgainph = xpgain*(3600/LONGTERMDURATION)
            xptillnext = LEVELS[currentLevel]-exp
            #Get the number of minutes until next level
            xpgainpm = xpgainph/60
            if xpgainpm != 0:
                minutes = xptillnext/xpgainpm
            else:
                minutes = "INF"
            longtermexpsv.set('LongTerm XPPH: '+locale.format("%d",xpgainph,grouping=True)+" Mins to ding: "+str(minutes))
        else:
            longtermexpsv.set('LongTerm XPPH needs more time: '+str((LONGTERMDURATION/5-len(expList))*5))
        #Set the label for xp gained this session
        if len(expList) > 0:
            totalexpgainedsv.set('XP This Session: '+locale.format("%d",expList[-1][0]-expList[0][0],grouping=True))
        sleep(UPDATERATE)
    root.update()
    if tracking['finishedTracking']:
        # if we are ever finished tracking, let's write our data to file.
        print 'finished'
        print expList
        print len(expList)
        break #not exactly what we want to do here, but ok for now. Doesn't allow start-stop action
    sleep(.05)

