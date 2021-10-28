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
    sd.default.channels = 1  #voce pode ter que alterar isso dependendo da sua placa
    # duration = #tempo em segundos que ira aquisitar o sinal acustico captado pelo mic


    # faca um print na tela dizendo que a captação começará em n segundos. e então 
    #use um time.sleep para a espera
    print("A captação começará em 4 segundos")
    sleep(2)
   
   #faça um print informando que a gravação foi inicializada
    print("A gravação foi inicializada")
   
   #declare uma variável "duração" com a duração em segundos da gravação. poucos segundos ... 
   #calcule o número de amostras "numAmostras" que serão feitas (número de aquisições)

    T = 2  #analise sua variavel "audio". pode ser um vetor com 1 ou 2 colunas, lista ...
    numAmostras = T*Fs #grave uma variavel com apenas a parte que interessa (dados)

    audio = sd.rec(int(numAmostras), Fs, channels=1)
    # audio = sd.rec(int(numAmostras))
    sd.wait()
    print("...     FIM")

    #loadsound()
    
    sd.playrec(audio)

    sleep(2)

    print("Passei")
    
    sd.wait()
    
    # x, y=signal.calcFFT(audio, Fs)
    
    # use a funcao linspace e crie o vetor tempo. Um instante correspondente a cada amostra!
    t = np.linspace(0,T,T*Fs)
    # t = np.linspace(-T/2,T/2,T*Fs)

    print("ESSE É O AUDIO:{0}".format(audio[0:10]))
    print(audio[10])
    arrayAudio = np.ndarray(shape=(88200,),dtype=np.float32)
    print("Olha aí o arrayAudio:{0}".format(arrayAudio[0:10]))

    for i in range(0,arrayAudio.shape[0]):
        arrayAudio[i] = audio[i][0]

    # plot do gravico  áudio vs tempo!
    plt.subplot(1,2,1)
    plt.plot(t[:400], arrayAudio[:400])
    plt.title("Som gravado")
    plt.autoscale(enable=True, axis='both', tight=True)
    plt.show()
    
    # y = audio[:300]
    ## Calcula e exibe o Fourier do sinal audio. como saida tem-se a amplitude e as frequencias
    print("Cheguei!")
    x, y = signal.calcFFT(arrayAudio, Fs)
    print(y)
    
    #esta funcao analisa o fourier e encontra os picos
    #voce deve aprender a usa-la. ha como ajustar a sensibilidade, ou seja, o que é um pico?
    #voce deve tambem evitar que dois picos proximos sejam identificados, pois pequenas variacoes na
    #frequencia do sinal podem gerar mais de um pico, e na verdade tempos apenas 1.
    # y_vamosver, x = signal.calcFFT(audio[:200], Fs)
    index = peakutils.indexes(y, thres=0.2, min_dist=10)
    # print(yf)
    # index=peakutils.indexes(yf, thres=0.2, min_dist=10)
    print(index)
    #printe os picos encontrados! 
    # print()

    frqObtidaLista = [[], []]
    for frequencia in x[index]:
        #Linha
        if int(frequencia) in range(640, 990):
            frqObtidaLista[0].append(int(frequencia))
        #Coluna
        elif int(frequencia) in range(1160, 1680):
            frqObtidaLista[1].append(int(frequencia))

    tabelaDTMF = {"1":[697, 1209], "2":[697, 1336], "3":[697, 1477], "A":[697, 1633], "4":[770, 1209], "5":[770, 1336], "6":[770, 1477], "B":[770, 1633], "7":[852, 1209], "8":[852, 1336], "9":[852, 1477], "C":[852, 1633], "X":[941, 1209], "0":[941, 1336], "#":[941, 1477], "D":[941, 1633]}

    character = "None"
    resolucao = 30
    for tecla, frequencias in tabelaDTMF.items():
        if frqObtidaLista[0][0] <= frequencias[0] + resolucao and frqObtidaLista[0][0] >= frequencias[0] - resolucao and frqObtidaLista[1][0] <= frequencias[1] + resolucao and frqObtidaLista[1][0] >= frequencias[1] - resolucao:
            character = tecla
    
    print(f"\n[+]---Tecla referente ao som gravado: {character}")

    
    #encontre na tabela duas frequencias proximas às frequencias de pico encontradas e descubra qual foi a tecla
    #print a tecla.
    plt.plot(x, y)
    plt.title('Transformada de Fourier do som gravado')
    plt.autoscale(enable=True, axis='both', tight=True)
    plt.show()        
  
    ## Exibe gráficos
    plt.show()

if __name__ == "__main__":
    main()
