from ctypes import *
from ctypes.wintypes import *
from time import sleep
from Tkinter import *


pid = 4920
op = windll.kernel32.OpenProcess
rpm = windll.kernel32.ReadProcessMemory
ch = windll.kernel32.CloseHandle
PAA = 0x1F0FFF
addy = 0x5F8A8440

#set up the window
root = Tk()
expsv = StringVar()
expsv.set('hello, go kill some stuff')
lastkillsv = StringVar()
lastkillsv.set('lastkill: N/A')

currentExp = Label(root, textvariable = expsv)
lastKill = Label(root,textvariable = lastkillsv)
currentExp.pack()
lastKill.pack()
root.attributes('-topmost',True)
root.attributes('-alpha', 0.3)
root.overrideredirect(1)
ph = op(PAA,False,int(pid))
previous = b'.'*2000
lastexp = 0
while True:
    datadummy = b'.'*2000
    buffer = c_char_p(datadummy)
    bufferSize = (len(buffer.value))
    bytesRead = c_ulong(0)

    if rpm(ph,addy,buffer,bufferSize,byref(bytesRead)) and previous != buffer.value:
        #parse the line
        exp = 0
        for i in range(len(buffer.value)-1,-1,-1):
            multiplier = i*2
            hexrep = hex(ord(buffer.value[i]))
            exp += int(hexrep[-1],16)*pow(16,multiplier)
            if hexrep[-2] != 'x':
                exp += int(hexrep[-2],16)*pow(16,multiplier+1)
        
        lastkillsv.set("Last Kill: "+str(exp-lastexp))
        lastexp = exp
        expsv.set("exp: "+str(exp))
        previous = buffer.value
        root.update()
        root.lift()

    sleep(.01)
