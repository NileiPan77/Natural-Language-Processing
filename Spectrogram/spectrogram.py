from cmath import inf
import wave
import nltk
import sys
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import itertools
from scipy.io import wavfile 
import re



class spectrogram:
    rescale = False
    debug = False
    millisecond_interval = 10
    framerate = 0

    argv = []
    sample_windows = []
    square_magnitude = []

    def __init__(self,argv):
        self.argv = argv
        if len(argv) == 1:
            print("Missing commandline arguments")
            print("Usage: python3 spectrogram.py .../xxx.wav [-r] [-g]")
            print("toggle -r for rescale magnitude to 0-255 window, works better in some situations")
            exit(1)
        if len(argv) > 1:
            if len(argv) > 2 and argv[2] == "-r":
                self.rescale = True
            if len(argv) > 3 and argv[3] == '-g':
                self.debug = True
            obj = wave.open(sys.argv[1],'r')

            if obj:
                signal = obj.readframes(-1)
                signal = np.frombuffer(signal, dtype=np.int16)

                self.framerate = obj.getframerate()
                step = int(self.millisecond_interval * self.framerate / 1000)
                for i in range(0, len(signal), step):
                    self.sample_windows.append(signal[i:i+step])
    
    def rescaling(self,x,xmin,xmax,ymin,ymax):
        return ymin + (ymax-ymin)*(x-xmin) / (xmax-xmin)

    def hamming(self,n,L):
        return 0.54 - 0.46 * np.cos(2 * np.pi * n / L)

    def square_magnitude_process(self):
        for i in range(len(self.sample_windows)):
            self.square_magnitude.append(np.absolute(np.fft.fft(self.sample_windows[i])))
    
        max = -inf
        min = inf
        for i in range(len(self.square_magnitude)):
            for j in range(len(self.square_magnitude[i])):
                self.square_magnitude[i][j] = np.log10(self.square_magnitude[i][j]) * 10
                self.square_magnitude[i][j] = self.square_magnitude[i][j] * self.hamming(i, len(self.square_magnitude))

                if max < self.square_magnitude[i][j]:
                    max = self.square_magnitude[i][j]
                if min > self.square_magnitude[i][j]:
                    min = self.square_magnitude[i][j]
        
        
    # rescale magnitude to fit rgb window 0-255
        if self.rescale:
            for i in range(len(self.square_magnitude)):
                for j in range(len(self.square_magnitude[i])):
                    self.square_magnitude[i][j] = self.rescaling(self.square_magnitude[i][j],min,max,0,255)
        return self.square_magnitude

    def image_array_create(self):
        image_array = []
        for i in range(len(self.square_magnitude)-1):
            image_array.append([])
            for j in range(len(self.square_magnitude[i])):
                image_array[i].append((self.square_magnitude[i][j],self.square_magnitude[i][j],self.square_magnitude[i][j]))


        array = np.array(list(zip(*image_array[::-1])),dtype=np.uint8)
        new_image = Image.fromarray(array)
        name = re.search(r'\b\w*\b(?=\.)',self.argv[1]).group(0)
        new_image.save(name + ".png")
        return 

    def debug_func(self):
        samplingFrequency, signalData = wavfile.read(self.argv[1])

        plt.subplot(211)
        plt.title('Spectrogram')
        plt.plot(signalData)
        plt.xlabel('Sample')
        plt.ylabel('Amplitude')

        plt.subplot(212)
        plt.specgram(signalData,Fs=samplingFrequency)
        plt.xlabel('Time')
        plt.ylabel('Frequency')
        plt.show()

    def run(self):
        self.square_magnitude_process()
        self.image_array_create()
        if self.debug:
            self.debug_func()

if __name__ == '__main__': 
    spm = spectrogram(sys.argv)
    spm.run()
        