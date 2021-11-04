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
    A = 1
    T = 3  
    numAmostras = T*Fs 
    t = np.linspace(0, 2*T, T*Fs) # Ex: 1000 bits por segundo, 1 segudo amostra 1000 vezes. Então 1 segundo amostra Fs vezes. 


    print("A captação começará em 4 segundos")
    sleep(4)
   
    print("A gravação foi inicializada")


    audio = sd.rec(int(numAmostras), Fs, channels=1)
    sd.wait()
    print("...     FIM DA GRAVAÇÃO")
    
    sd.playrec(audio)
    sleep(2)

    print("Áudio já gravado e re-tocado")


    print("Salvando o audio gravado no file audio-saudacao")
    getfile(audio, Fs, "audio-saudacao")

    # Gráfico do aúdio gravado pelo tempo 
    plt.figure()
    plt.plot(t, audio, 'b--', alpha=0.5)
    plt.title(f'Áudio original gravado no tempo')
    plt.grid(True)
    plt.show()

    #---------------------------------------------------------------------------

    # Começamos apenas transformando o formato do áudio para uma lista normal, já que é uma lista de listas originalmente
    listaDoAudio = []  # Se eu pegar apenas audio[i], ele retorna o número dentro de uma lista. Eu quero apenas o número. 
    for i in range(0, numAmostras):
        listaDoAudio.append(audio[i][0])

    
    # FOURIER do sinal original, apenas para ver as frequências gravadas
    xOriginal, yOriginal = signal.calcFFT(listaDoAudio, Fs)
    plt.figure()
    plt.plot(xOriginal, yOriginal, 'b--', alpha=0.5)
    plt.title(f'FOURIER Sinal de áudio original (x: frequências, y: amplitude)')
    plt.show()


    # AudioNormalizado = yfiltro/maior_frequencia
    AudioNormalizado = normalizeAudio(audio)

    print(f"\nTocando o audio normalizado\n")
    sd.play(AudioNormalizado, Fs)

    # O audio normalizado provém do áudio que o formato é diferente do formato que precisa para usar nas funçõe de Fourier e no filtro,
    #  então por isso esse "for"
    listaDoAudioNormalizado = []  
    for i in range(0, numAmostras):
        listaDoAudioNormalizado.append(AudioNormalizado[i][0])

    #Gráfico 1: Sinal de áudio original normalizado – domínio do tempo. 
    plt.figure()
    plt.plot(t, AudioNormalizado, 'b--', alpha=0.5, color= "purple")
    plt.title(f'Gráfico 1: Áudio original normalizado no tempo.')
    plt.savefig("Audio_Original_Normalizado_No_Tempo.jpg")
    plt.show()

    # FOURIER do sinal original, apenas para ver as frequências gravadas
    xNormal, yNormal = signal.calcFFT(listaDoAudioNormalizado, Fs)
    plt.figure()
    plt.plot(xOriginal, yOriginal, 'b--', alpha=0.5)
    plt.title(f'FOURIER do sinal de áudio original normalizado (x: frequências, y: amplitude)')
    plt.show()

    # Filtrando o áudio acima de 4KHz
    yfiltro = LPF(listaDoAudioNormalizado, 4000, Fs)
    sd.play(yfiltro)
    # sd.wait()

    #Gráfico 2: Sinal de áudio filtrado – domínio do tempo. (repare que não se nota diferença). 
    plt.figure()
    plt.plot(t, yfiltro, 'b--', alpha=0.5, color= "purple")
    plt.title(f'Gráfico 2: Áudio filtrado (já normalizado) no tempo')
    plt.savefig("Audio_Filtrado_E_Normalizado_No_Tempo.jpg")
    plt.show()

    #Gráfico 3: Sinal de áudio normalizado filtrado – domínio da frequência (x: frequências, y: amplitude). 
    xfiltrado, yfiltrado = signal.calcFFT(yfiltro, Fs)
    plt.figure()
    plt.plot(xfiltrado, yfiltrado, 'b--', alpha=0.5, color= "purple")
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
    plt.plot(xPortadora[0:500], yPortadora[0:500])
    plt.grid()
    plt.show()
    # portadora = 1*np.cos(2*pi*14000*t)

    #Gráfico 4: sinal de áudio modulado – domínio do tempo (mais uma vez, não se nota diferença)
    audioModulado = yfiltro * yPortadora
    plt.figure("AM")
    plt.title('Gráfico 4: Áudio modulado no tempo')
    plt.plot(t[0:500], audioModulado[0:500], color= "purple")
    plt.grid()
    plt.savefig("Audio_Modulado_No_Tempo.jpg")
    plt.show()

    
    print(f"\nTocando o audio modulado (não é audível)\n")
    sd.play(audioModulado)
    sd.wait()

    # Gráfico 5: sinal de áudio modulado – domínio da frequência. (entre 10kHz e 18kHz)
    xModulado, yModulado = calcFFT(audioModulado, Fs)
    plt.plot(xModulado, np.abs(yModulado), label="Áudio modulado", color="black")
    plt.title("Gráfico 5: Áudio modulado – domínio da frequência (entre 10kHz e 18kHz)")
    plt.grid()
    plt.savefig("Audio_Modulado_Dominio_Da_Frequencia.jpg")
    plt.show()

#------------------------------ DEMODULARIZAR -----------------------------------------


    ## Demodulando
    print(f"\nDemodulando o áudio\n")
    audioDemod = yPortadora*audioModulado

    # Gráfico 6: sinal de áudio demodulado – domínio do tempo
    plt.plot(t, audioDemod, color="purple")
    plt.title("Gráfico 6: Áudio demodulado no tempo")
    plt.grid()
    plt.savefig("Audio_Demodulado_No_Tempo.jpg")
    plt.show()


    # Gráfico 7: sinal de áudio demodulado – domínio da frequência. (verifique que reobteve as baixas frequências)
    xDemod, yDemod = calcFFT(audioDemod, Fs)
    plt.plot(xDemod, np.abs(yDemod), color="black")
    plt.title("Gráfico 7: Áudio demodulado – domínio da frequência.")
    plt.grid()
    plt.savefig("Audio_Demodulado_Dominio_Da_Frequencia.jpg")
    plt.show()

    ## Filtrando freqûencias superiores a 4kHz
    print(f"\nFiltrando frequências superiores a 4kHz\n")
    audioDemodFiltered = LPF(audioDemod, 4000, Fs)

    # Gráfico 8: sinal de áudio demodulado e filtrado – domínio da frequência.
    xDemodFiltrado, yDemodFiltrado = calcFFT(audioDemodFiltered, Fs)
    plt.plot(xDemodFiltrado, np.abs(yDemodFiltrado), color="black")
    plt.title("Gráfico 8: Áudio demodulado e filtrado – domínio da frequência.")
    plt.grid()
    plt.savefig("Audio_Demodulado_E_Filtrado_Dominio_Da_Frequencia.jpg")
    plt.show()


    ## Executando o áudio e vendo que é audível
    print(f"\nTocando áudio demodularizado e filtrado\n")
    sd.play(audioDemodFiltered)
    sd.wait()


if __name__ == "__main__":
    main()
