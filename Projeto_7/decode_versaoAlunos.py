#Importe todas as bibliotecas

import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy import signal as window
from suaBibSignal import signalMeu
from time import sleep
import peakutils


#Função para transformar intenidade acústica em dB
def todB(s):
    sdB = 10*np.log10(s)
    return(sdB)

def main():
 
    #declare um objeto da classe da sua biblioteca de apoio (cedida)    
    signal = signalMeu()

    #declare uma variável com a frequência de amostragem, sendo 44100
    Fs = 44100
    
    #você importou a bilioteca sounddevice como, por exemplo, sd. então
    # os seguintes parametros devem ser setados:
    
    sd.default.samplerate = Fs #taxa de amostragem
    sd.default.channels = 2  #voce pode ter que alterar isso dependendo da sua placa
    # duration = #tempo em segundos que ira aquisitar o sinal acustico captado pelo mic


    # faca um print na tela dizendo que a captação começará em n segundos. e então 
    #use um time.sleep para a espera
    print("A captação começará em 2 segundos")
    sleep(2)
   
   #faça um print informando que a gravação foi inicializada
    print("A gravação foi inicializada")
   
   #declare uma variável "duração" com a duração em segundos da gravação. poucos segundos ... 
   #calcule o número de amostras "numAmostras" que serão feitas (número de aquisições)

    T = 3  #analise sua variavel "audio". pode ser um vetor com 1 ou 2 colunas, lista ...
    numAmostras = T*Fs #grave uma variavel com apenas a parte que interessa (dados)

    audio = sd.rec(int(numAmostras), Fs, channels=1)
    sd.wait()
    print("...     FIM")

    #loadsound()
    
    sd.playrec(audio)
    
    sd.wait()
    
    # x, y=signal.calcFFT(audio, Fs)
    
    # use a funcao linspace e crie o vetor tempo. Um instante correspondente a cada amostra!
    t = np.linspace(0,2*T,T*Fs)

    # plot do gravico  áudio vs tempo!
    plt.subplot(1,2,1)
    plt.plot(t[:200], audio[:200])
    plt.title("Som gravado")
    plt.autoscale(enable=True, axis='both', tight=True)
    
    y = audio[:200]
    ## Calcula e exibe o Fourier do sinal audio. como saida tem-se a amplitude e as frequencias
    xf, yf = signal.calcFFT(y, Fs)
    plt.subplot(1,2,2)
    plt.figure("F(y)")
    plt.plot(xf,yf)
    plt.grid()
    plt.title('Fourier audio')
    
    #esta funcao analisa o fourier e encontra os picos
    #voce deve aprender a usa-la. ha como ajustar a sensibilidade, ou seja, o que é um pico?
    #voce deve tambem evitar que dois picos proximos sejam identificados, pois pequenas variacoes na
    #frequencia do sinal podem gerar mais de um pico, e na verdade tempos apenas 1.
    y_vamosver, x = signal.calcFFT(audio[:200], Fs)
    index = peakutils.indexes(y_vamosver, thres=0.2, min_dist=10)
    # print(yf)
    # index=peakutils.indexes(yf, thres=0.2, min_dist=10)
    print(index)
    #printe os picos encontrados! 
    # print()
    
    #encontre na tabela duas frequencias proximas às frequencias de pico encontradas e descubra qual foi a tecla
    #print a tecla.
    
  
    ## Exibe gráficos
    plt.show()

if __name__ == "__main__":
    main()
