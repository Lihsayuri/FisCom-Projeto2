#---------------- IMPORTANDO BIBLIOTECAS ----------------

from math import pi
import numpy as np
from scipy.signal.ltisys import freqresp
import sounddevice as sd
import matplotlib.pyplot as plt
from os import sys
from logging import info
from suaBibSignal import signalMeu
import soundfile as sf
from time import sleep
import peakutils
from filtro import *
import math
import soundfile as sf


#---------------- IMPLEMENTANDO FUNÇÕES ----------------

def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)

# Converte intensidade em Db
def todB(s):
    sdB = 10*np.log10(s)
    return(sdB)

def gerarSenoSinal(digit, dictFrequencias):
    if digit in dictFrequencias:
        return dictFrequencias[digit][0], dictFrequencias[digit][1]
    else:
        print("Ops, o termo teclado não existe!")

def getfile(yAudio, Fs, nome):
    filename= nome+".wav"
    print(f'Salvando o arquivo de som em: {filename}')
    sf.write(filename, yAudio, Fs) 

def main():
    print("Inicializando encoder")
    
    signal = signalMeu()

    Fs = 44100
    
    sd.default.samplerate = Fs # Taxa de amostragem
    sd.default.channels = 1  # Você pode ter que alterar isso dependendo da sua placa

    print("A captação começará em 4 segundos")
    sleep(4)
   
    print("A gravação foi inicializada")

    A = 1
    T = 3  
    numAmostras = T*Fs 
    t = np.linspace(0, 2*T, T*Fs) # Ex: 1000 bits por segundo, 1 segudo amostra 1000 vezes. Então 1 segundo amostra Fs vezes. 

    audio = sd.rec(int(numAmostras), Fs, channels=1)
    sd.wait()
    print("...     FIM")
    
    sd.playrec(audio)
    sleep(2)

    print("Áudio já gravado e re-tocado")

    getfile(audio, Fs, "audio-saudacao")

    # Gráfico do aúdio gravado pelo tempo 
    plt.figure()
    plt.plot(t, audio, 'b--', alpha=0.5)
    plt.title(f'Áudio gravado')
    plt.show()

    #---------------------------------------------------------------------------

    # Começamos apenas transformando o formato do áudio para uma lista normal, já que é uma lista de listas originalmente
    listaDoAudio = []  # Se eu pegar apenas audio[i], ele retorna o número dentro de uma lista. Eu quero apenas o número. 
    for i in range(0, numAmostras):
        listaDoAudio.append(audio[i][0])

    
    xOriginal, yOriginal = signal.calcFFT(listaDoAudio, Fs)
    plt.figure()
    plt.plot(xOriginal, yOriginal, 'b--', alpha=0.5)
    plt.title(f'FOURIER Sinal de áudio original (x: frequências, y: amplitude)')
    plt.show()


    yfiltro = LPF(listaDoAudio, 4000, Fs)
    sd.play(yfiltro)
    # sd.wait()

    xfiltrado, yfiltrado = signal.calcFFT(yfiltro, Fs)
    plt.figure()
    plt.plot(xfiltrado, yfiltrado, 'b--', alpha=0.5)
    plt.title(f'FOURIER Sinal de áudio filtrado (x: frequências, y: amplitude)')
    plt.show()

    # # Agora vamos tentar normalizar o sinal
    # # Com o Fourier do sinal filtrado já feito, achar os picos

    index = peakutils.indexes(yfiltrado, thres=0.3, min_dist=10)

#     # E encontrar os picos de frequência do áudio 
    print("Esses foram os picos encontrados: {0}".format(xfiltrado[index]))

#     # Quando acharmos a maior frequência, iremos dividir o sinal para que a frequência fique entre [1 -1]
    maior_frequencia = 0
    for i in range(len(xfiltrado[index])):
        if xfiltrado[index][i] > maior_frequencia:
            maior_frequencia = xfiltrado[index][i]
    
    print("Essa foi a maior frequência encontrada: ", maior_frequencia)
    

    # AudioNormalizado = yfiltro/maior_frequencia
    AudioNormalizado = normalizeAudio(yfiltro)

    print(f"\nTocando o audio normalizado\n")
    sd.play(AudioNormalizado, Fs)

    plt.figure()
    plt.plot(t, AudioNormalizado, 'b--', alpha=0.5)
    plt.title(f'Sinal de áudio normalizado')
    plt.show()

    
# #------------------------------------------------------------------------------------------

# #Module esse sinal de áudio em AM com portadora de 14 kHz. (Essa portadora deve ser uma senoide começando em zero)


    print(f"\nModulando o sinal por AM de 20 MHz\n")
    t = np.linspace(0, 2*T, numAmostras)

    freqPortadora = 14000
    xPortadora, yPortadora = generateSin(freqPortadora, A, T, Fs)
    plt.figure("portadora")
    plt.title('Portadora')
    plt.plot(xPortadora[0:500], yPortadora[0:500])
    plt.grid()
    plt.show()
    # xPortadora, yPortadora =  generateSin(14000, A, T, Fs )
    # portadora = 1*np.cos(2*pi*14000*t)

    audioModulado = AudioNormalizado * yPortadora
    plt.figure("AM")
    plt.title('AM')
    plt.plot(audioModulado[0:500])
    plt.grid()

    
    print(f"\nTocando o audio modulado (não é audível)\n")
    sd.play(audioModulado)
    sd.wait()


#     #------------------------------ DEMODULARIZAR -----------------------------------------


    xModulado, yModulado = calcFFT(audioModulado, Fs)
    plt.plot(xModulado, np.abs(yModulado), label="Áudio do amigo", color="black")
    plt.title("Fourier do áudio do amigo")
    # plt.savefig("FourierAudiodoAmigo.jpg")
    plt.show()

    ## Demodulando
    print(f"\nDemodulando o áudio\n")
    audioDemod = yPortadora*audioModulado

#     ## Filtrando freqûencias superiores a 4kHz
    print(f"\nFiltrando frequências superiores a 4kHz\n")
    audioDemodFiltered = LPF(audioDemod, 4000, Fs)
    # audioDemodFiltered = filtro(audioDemod, Fs, 4000)
    # audioDemodFiltered = low_pass_filter(Fs, 4000, audioDemod)

    ## Executando o áudio e vendo que é audível
    print(f"\nTocando áudio demodularizado e filtrado\n")
    sd.play(audioDemodFiltered)
    sd.wait()


if __name__ == "__main__":
    main()
