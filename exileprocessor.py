##exileprocessor.py
##Author: Benjamin Johnson
##CreatedOn: January 2014
##
## These functions are used to access the Path of Exile process and read its memory
## for experience and other player attributes.
##
## Note: This file uses spaces for indentation.
from ctypes import *
from ctypes.wintypes import *
from struct import *

#PSAPI.DLL
psapi = windll.psapi
#Kernel32.DLL
kernel = windll.kernel32

## Global Data
baseAddy = None
processHandle = None
pid = None

class MODULEINFO(Structure):
  _fields_ = [
          ('lpBaseOfDll', LPVOID),
          ('SizeOfImage', DWORD),
          ('EntryPoint', LPVOID)
  ]


def getProcessData():
  """
    Sets the base addy and pid
  """
  global pid
  global baseAddy

  ##print "getting process data..."

  arr = c_ulong * 256
  lpidProcess= arr()
  cb = sizeof(lpidProcess)
  cbNeeded = c_ulong()
  hModule = c_ulong()
  count = c_ulong()
  modname = c_buffer(30)
  lpmodinfo = MODULEINFO()
  PROCESS_QUERY_INFORMATION = 0x0400
  PROCESS_VM_READ = 0x0010
  
  #Call Enumprocesses to get hold of process id's
  psapi.EnumProcesses(byref(lpidProcess),
                      cb,
                      byref(cbNeeded))
  
  #Number of processes returned
  nReturned = cbNeeded.value/sizeof(c_ulong())
  
  pidProcess = [i for i in lpidProcess][:nReturned]
  
  for p in pidProcess:
      
    #Get handle to the process based on PID
    hProcess = kernel.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                                  False, p)
    if hProcess:
      psapi.EnumProcessModules(hProcess, byref(hModule), sizeof(hModule), byref(count))
      psapi.GetModuleBaseNameA(hProcess, hModule.value, modname, sizeof(modname))
      psapi.GetModuleInformation(hProcess, hModule.value, byref(lpmodinfo), byref(cbNeeded))
      processName = "".join([ i for i in modname if i != '\x00'])
      if processName == 'PathOfExileSteam.exe':
        ##print "process found"
        baseAddy = hex(lpmodinfo.lpBaseOfDll)
        ##print "process base address: " + baseAddy
        pid = p
      
      #-- Clean up
      for i in range(modname._length_):
        modname[i]='\x00'
      
      kernel.CloseHandle(hProcess)

def initializeProcessData():
  """
     Returns the process handle.
     TODO: return False in the case of failure
  """
  global baseAddy
  global pid
  global processHandle
  
  print "initializeing..."
  getProcessData()

  baseAddy = int(baseAddy, 16) + int('0x007D43FC', 16)
  ##print "base address: " + hex(baseAddy)
  ##print "pid: " + hex(pid)
  PAA = 0x1F0FFF # The windows PROCESS_ALL_ACCESS macro.

  #Get the connection to the game
  processHandle = kernel.OpenProcess(PAA,False,int(pid))


if __name__ == '__main__':
    readExperience()

def readExperience():
  """
     Returns an int that is the player experience.
     TODO: Return False if the read fails.
  """
  #make sure we have a handle
  global processHandle
  global baseAddy
  global pid

  ##print "reading exp..."
  if not processHandle:
    initializeProcessData()

  #calculate the address
  buff = c_ulong()
  bufferSize = (sizeof(buff))
  bytesRead = c_ulong(0)
  kernel.ReadProcessMemory(processHandle,baseAddy,byref(buff),bufferSize,byref(bytesRead))
  pointer1 = unpack('P',buff)[0] + int(0x50)
  ##print "pointer 1: " + hex(pointer1)
  kernel.ReadProcessMemory(processHandle,pointer1,byref(buff),bufferSize,byref(bytesRead))
  pointer2 = unpack('P',buff)[0] + int(0x980)
  ##print "pointer 2: " + hex(pointer2)
  kernel.ReadProcessMemory(processHandle,pointer2,byref(buff),bufferSize,byref(bytesRead))
  ##pointer3 = unpack('P',buff)[0] + int(0x4)
  ##print "pointer 3: " + hex(pointer3)
  ##kernel.ReadProcessMemory(processHandle,pointer3,byref(buff),bufferSize,byref(bytesRead))
  ##pointer4 = unpack('P',buff)[0] + int(0x980)
  ##print "pointer 4: " + hex(pointer4) ## This is the final address

  # Read the exp value
  ##kernel.ReadProcessMemory(processHandle,pointer4,byref(buff),bufferSize,byref(bytesRead))
  ##print "End result: " + str(unpack('I',buff)[0])
  return unpack('I',buff)[0]
