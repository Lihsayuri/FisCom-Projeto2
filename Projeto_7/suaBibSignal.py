
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy import signal as window


class signalMeu:
    def __init__(self):
        self.init = 0

    def __init__(self):
        self.init = 0

    def generateSin(self, freq, amplitude, time, fs):
        n = time*fs
        x = np.linspace(0.0, time, n)
        s = amplitude*np.sin(freq*x*2*np.pi)
        return (x, s)

    def calcFFT(self, signal, fs):
        # x frequencia e y amplitudes
        # https://docs.scipy.org/doc/scipy/reference/tutorial/fftpack.html
        N  = len(signal)
        print(N)
        T  = 1/fs
        # print("Esse é o período de amostragem:{0}".format(T))
        W = window.hamming(N)
        # print(W)
        # print("ESSE É O W:".format(W))
        xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
        yf = fft(signal*W)
        # print(yf)
        return(xf, np.abs(yf[0:N//2]))

    def plotFFT(self, signal, fs):
        #plotar o FFT
        x,y = self.calcFFT(signal, fs)
        plt.figure()
        plt.plot(x, np.abs(y))
        plt.title('Fourier')
