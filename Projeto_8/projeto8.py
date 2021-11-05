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


def main():
    print("Inicializando encoder")
    
    signal = signalMeu()

    Fs = 44100
    sd.default.samplerate = Fs # Taxa de amostragem
    sd.default.channels = 1  # Você pode ter que alterar isso dependendo da sua placa
    A = 1
    T = 3  
    numAmostras = T*Fs 
    t = np.linspace(0, 2*T, T*Fs) # Ex: 1000 bits por segundo, 1 segudo amostra 1000 vezes. Então 1 segundo amostra Fs vezes. 

    print(f"\nO áudio que faremos a análise já foi gravado com o Fs de 44100Hz!\n")
    print(f"\nÉ um áudio de saudação de um colega para o outro.\n")
    print(f"\nA mensagem gravada é: Oi Henrique!\n")
    print(f"\nOBS: gravei o áudio para passar os 4kHz e poder ver o filtro funcionando")
    audio, samplerate = sf.read('audio-saudacao.wav')

    sd.playrec(audio)
    sleep(2)

    print("Tocando o áudio já gravado para conferir")

    # Gráfico do aúdio gravado pelo tempo 
    plt.figure()
    plt.plot(t, audio, alpha=0.5, color="darkorange")
    plt.title(f'Áudio original gravado no tempo')
    plt.grid(True)
    plt.show()

    #---------------------------------------------------------------------------
    
    # Com o áudio original fizemos o FOURIER do sinal, apenas para ver as frequências gravadas
    xOriginal, yOriginal = signal.calcFFT(audio, Fs)
    plt.figure()
    plt.plot(xOriginal, yOriginal, alpha=0.5, color="darkorange")
    plt.title(f'FOURIER Sinal de áudio original (x: frequências, y: amplitude)')
    plt.show()


    # Normalizamos o áudio com uma função 
    AudioNormalizado = normalizeAudio(audio)

    print(f"\nTocando o audio normalizado\n")
    sd.play(AudioNormalizado, Fs)

    #Gráfico 1: Sinal de áudio original normalizado – domínio do tempo. 
    plt.figure()
    plt.plot(t, AudioNormalizado, alpha=0.5, color= "darkorange")
    plt.title(f'Gráfico 1: Áudio original normalizado no tempo.')
    plt.savefig("Audio_Original_Normalizado_No_Tempo.jpg")
    plt.show()

    # FOURIER do sinal original, apenas para ver as frequências gravadas
    xNormal, yNormal = signal.calcFFT(AudioNormalizado, Fs)
    plt.figure()
    plt.plot(xOriginal, yOriginal, alpha=0.5, color="darkorange")
    plt.title(f'FOURIER do sinal de áudio original normalizado (x: frequências, y: amplitude)')
    plt.show()

    # Filtrando o áudio acima de 4KHz
    yfiltro = LPF(AudioNormalizado, 4000, Fs)
    sd.play(yfiltro)
    # sd.wait()

    #Gráfico 2: Sinal de áudio filtrado – domínio do tempo. (repare que não se nota diferença). 
    plt.figure()
    plt.plot(t, yfiltro, alpha=0.5, color= "darkorange")
    plt.title(f'Gráfico 2: Áudio filtrado (já normalizado) no tempo')
    plt.savefig("Audio_Filtrado_E_Normalizado_No_Tempo.jpg")
    plt.show()

    #Gráfico 3: Sinal de áudio normalizado filtrado – domínio da frequência (x: frequências, y: amplitude). 
    xfiltrado, yfiltrado = signal.calcFFT(yfiltro, Fs)
    plt.figure()
    plt.plot(xfiltrado, yfiltrado, alpha=0.5, color= "darkorange")
    plt.title(f'Gráfico 3: Áudio filtrado (já normalizado) – domínio da frequência')
    plt.savefig("Audio_Filtrado_E_Normalizado_Dominio_Da_Frequencia.jpg")
    plt.show()

    
# #------------------------------------------------------------------------------------------

# #Module esse sinal de áudio em AM com portadora de 14 kHz. (Essa portadora deve ser uma senoide começando em zero)


    print(f"\nModulando o sinal por AM com portadora de 14KHz\n")

    freqPortadora = 14000
    xPortadora, yPortadora = generateSin(freqPortadora, A, T, Fs)
    plt.figure()
    plt.title('Seno da portadora de 14KHz')
    plt.plot(xPortadora[0:500], yPortadora[0:500], color="darkorange")
    plt.grid()
    plt.show()
    # portadora = 1*np.cos(2*pi*14000*t)

    #Gráfico 4: sinal de áudio modulado – domínio do tempo (mais uma vez, não se nota diferença)
    audioModulado = yfiltro * yPortadora
    plt.figure("AM")
    plt.title('Gráfico 4: Áudio modulado no tempo')
    plt.plot(t[0:500], audioModulado[0:500], color= "darkorange")
    plt.grid()
    plt.savefig("Audio_Modulado_No_Tempo.jpg")
    plt.show()

    
    print(f"\nTocando o audio modulado (não é audível)\n")
    sd.play(audioModulado)
    sd.wait()

    # Gráfico 5: sinal de áudio modulado – domínio da frequência. (entre 10kHz e 18kHz)
    xModulado, yModulado = calcFFT(audioModulado, Fs)
    plt.plot(xModulado, np.abs(yModulado), color="darkorange")
    plt.title("Gráfico 5: Áudio modulado – domínio da frequência (entre 10kHz e 18kHz)")
    plt.grid()
    plt.savefig("Audio_Modulado_Dominio_Da_Frequencia.jpg")
    plt.show()

#------------------------------ DEMODULARIZAR -----------------------------------------


    ## Demodulando
    print(f"\nDemodulando o áudio\n")
    audioDemod = yPortadora*audioModulado

    # Gráfico do sinal de áudio demodulado – domínio do tempo
    plt.plot(t, audioDemod, color="darkorange")
    plt.title("Áudio demodulado no tempo")
    plt.grid()
    plt.show()


    # Gráfico 6: sinal de áudio demodulado – domínio da frequência. (verifique que reobteve as baixas frequências)
    xDemod, yDemod = calcFFT(audioDemod, Fs)
    plt.plot(xDemod, np.abs(yDemod), color="darkorange")
    plt.title("Gráfico 6: Áudio demodulado – domínio da frequência.")
    plt.grid()
    plt.savefig("Audio_Demodulado_Dominio_Da_Frequencia.jpg")
    plt.show()

    ## Filtrando freqûencias superiores a 4kHz
    print(f"\nFiltrando frequências superiores a 4kHz\n")
    audioDemodFiltered = LPF(audioDemod, 4000, Fs)

    # Gráfico 8: sinal de áudio demodulado e filtrado – domínio da frequência.
    xDemodFiltrado, yDemodFiltrado = calcFFT(audioDemodFiltered, Fs)
    plt.plot(xDemodFiltrado, np.abs(yDemodFiltrado), color="darkorange")
    plt.title("Gráfico 7: Áudio demodulado e filtrado – domínio da frequência.")
    plt.grid()
    plt.savefig("Audio_Demodulado_E_Filtrado_Dominio_Da_Frequencia.jpg")
    plt.show()


    ## Executando o áudio e vendo que é audível
    print(f"\nTocando áudio demodularizado e filtrado\n")
    sd.play(audioDemodFiltered)
    sd.wait()


if __name__ == "__main__":
    main()
