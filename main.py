

# -*- coding: utf8 -*-
from __future__ import division
import numpy as np
import numpy.fft as FFT
#import matplotlib.pyplot as plt
from scipy import signal
from scipy.fft import fft
import wave
from tkinter import *
import tkinter as tk
from tkinter import filedialog

# globale Variablen
CHUNKSIZE = 1024 	# 
CHANNELS = 1		#
RATE = 44100 		#
DAUER = 5			# Dauer, wie lange aufgenommen wird
FINGERPRINT_CUT = 20 # bestimmt wie lang fingerprint maximal ist
PAIR_VAL = 15 	# bestimmt zu welchem Grad ein Peak mit benachbartem Peak für einen fingerprint gepaart werden kann
				# je höher, desto mehr fingerprints
MIN_HASH_TIME_DELTA = 0
MAX_HASH_TIME_DELTA = 50
fullMatchFiles=[]
fullMatchNums=[]
matchWhales=[]
data = wave.open("data.wav","r")
CompData = wave.open("data.wav","r")
# empfange Audiosignale und schreibe sie in ein Numpy-Array 
def getCompAudio(filename):
    CompData = wave.open(filename, 'r')
    CompData.rewind()
    framesByte = CompData.readframes(-1)
    numpydata = np.frombuffer(framesByte, dtype="int16")
    return numpydata
def getAudio(filename):
    data = wave.open(filename, 'r')
    data.rewind()
    framesByte = data.readframes(-1)
    numpydata = np.frombuffer(framesByte, dtype="int16")
    return numpydata
# Short-Time Fourier Transform 
def stft(x, fs, framesz, hop):
	x=np.concatenate((x,np.zeros(1)))
	halfwindow = int(np.round(framesz*fs/2))
	framesamp=2*halfwindow+1
	hopsamp = int(np.round(hop*fs))
	w = signal.windows.hann(framesamp)
	X = np.array([fft(w*x[i-halfwindow:i+halfwindow+1])
	for i in range(halfwindow, len(x)-halfwindow, hopsamp)])
	#print X.shape             
	return X
def findPeakGrid(arr):
    result = []
    row = len(arr)
    column = len(arr[0])

    for i in range(row):
        for j in range(column):

            # checking with top element
            if i > 0:
                if arr[i][j] < arr[i-1][j]:
                    continue
            # checking with right element
            if j < column-1:
                if arr[i][j] < arr[i][j+1]:
                    continue
            # checking with bottom element
            if i < row-1:
                if arr[i][j] < arr[i+1][j]:
                    continue
            # checking with left element
            if j > 0:
                if arr[i][j] < arr[i][j-1]:
                    continue

            result.append(i)
            result.append(j)
            break

    return result
# berechne Spektrum
def spect(filename):
 
    fensterdauer=0.1
    fensterueberlappung=0.025   # jeweils in Sekunden
 
    sig = getAudio(filename) # Daten aus Audiostream
    A=stft(sig,RATE,fensterdauer,fensterueberlappung)
    A = A[:,0:800]
 
    eps=1e-8   # Offset, um logarithmieren zu koennen
 
    r,s=A.shape
    #print r
    #print s					# Größe des transformierten Arrays
    # 
    yl=np.linspace(0,DAUER, r)
    xl=np.linspace(0,4000,round(s/2))
    X,Y=np.meshgrid(xl,yl)
    #plt.figure(1)
    #plt.pcolormesh(Y,X,np.log10(np.absolute(A[:,:s//2]+eps)))
    #plt.xlabel(filename)
    #plt.show()
    return findPeakGrid(A)
def spectComp(filename):
 
    fensterdauer=0.1
    fensterueberlappung=0.025   # jeweils in Sekunden
 
    sig = getCompAudio(filename) # Daten aus Audiostream
    A=stft(sig,RATE,fensterdauer,fensterueberlappung)
    A = A[:,0:800]
 
    eps=1e-8   # Offset, um logarithmieren zu koennen
 
    r,s=A.shape
    #print r
    #print s					# Größe des transformierten Arrays
    # 
    yl=np.linspace(0,DAUER, r)
    xl=np.linspace(0,4000,round(s/2))
    X,Y=np.meshgrid(xl,yl)
    #plt.figure(1)
    #plt.pcolormesh(Y,X,np.log10(np.absolute(A[:,:s//2]+eps)))
    #plt.xlabel(filename)
    #plt.show()
    return findPeakGrid(A)
# Vergleiche die eingefügte Datei mit der Datenbank
root = Tk() 
root.title('WHALEZAM (Not trademarked)')
root.geometry("1920x1080") 
bg = PhotoImage(file = "background.png") 
label1 = Label( root, image = bg) 
label1.place(x = 0, y = 0) 
w = Label(root, text="WHALEZAM(not trademarked)")
w.pack(pady=(50,0))
def UploadAction(event=None):
    filename = filedialog.askopenfilename()
    t3.config(text="Selected: "+ filename)
    getlowestRest(filename)
    print('Selected:', filename)
    
fn = tk.Button(root, text='Datei Öffnen', command=UploadAction, width=50)
t3 = Label(text="Selected: None", width=50)
fn.pack(pady=(50,0))
t2 = Label(text="", width=60)
def compPeaks(filesToComp, fileToComp):
     t2 = Label(text="", width=60)
     matchWhales.clear()
     fullMatchNums.clear()
     fullMatchFiles.clear()
     compFile=spectComp(fileToComp)
     #print("Overall peaks in "+fileToComp+": "+str(len(compFile)))
     for i in range(len(filesToComp)):
          fileData=spect(filesToComp[i])
          counter = 0
          duplicateMatches = 0
          alreadyChecked=list({})
          for j in range(len(fileData)):
               for k in range(len(compFile)):
                   if fileData[j] == compFile[k]:
                        if fileData[j] in alreadyChecked:
                            duplicateMatches+=1
                        else:
                            counter+=1
                            alreadyChecked.append(fileData[j])
          if counter==len(compFile)/2:
            #print(str(counter) + " matches in "+filesToComp[i]+"("+str(duplicateMatches)+" duplicate matches)(rest: "+str(duplicateMatches%len(compFile)/2)+")")
            fullMatchNums.append(duplicateMatches%len(compFile)/2)
            fullMatchFiles.append(filesToComp[i])
            matchWhales.append(whales[i])
            print(matchWhales)
          #else:
            #print(str(counter) + " matches in "+filesToComp[i]+"("+str(duplicateMatches)+" duplicate matches)")
     return fullMatchFiles
def getlowestRest(filename):
    compPeaks(arr,filename)
    lowest=7000000
    lowestIndex=0
    for i in range (len(fullMatchNums)):
        if fullMatchNums[i]<lowest:
            lowest=fullMatchNums[i]
            lowestIndex=i
    if lowest==7000000:
        print("No full matches!!!")
    else:
        #print(lowest)
        #print(fullMatchFiles)
        #print(matchWhales)
        #print("")
        #print("")
        #print("")
        #print(matchWhales)
        t2.config(text="Am wahrscheinlichsten ist dies die Aufnahme eines "+ matchWhales[lowestIndex])
        t2.pack()
arr = ["belugaseq.wav","pottwal1.wav","common.wav","tursi3er.wav"]
whales = ["Beluga","Pottwal","Gemeinen Delfins","Tümmler"]

#TKINTER
def check():
    if(fn.get()!=""):
        getlowestRest(fn.get())
    else:
        t2.config(text="Error: nothing to check")
t1 = Label(text="Ergebniss:", width=60)
t3.pack()
t1.pack(pady=(40,0))
t2.pack()
exit = tk.Button(root, text='Fenster Schließen', width=25, command=root.destroy)
exit.pack(pady=(50,0))

root.mainloop()