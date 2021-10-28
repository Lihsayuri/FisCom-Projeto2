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

def achaTecla(index, x):
    frqObtidaLista = [[], []]
    for frequencia in x[index]:
        #frequências menores: Linha
        if int(frequencia) in range(640, 990):
            frqObtidaLista[0].append(int(frequencia))
        #frequências maiores: Coluna
        elif int(frequencia) in range(1160, 1680):
            frqObtidaLista[1].append(int(frequencia))

    tabelaDeFrequencias = {"1":[697, 1209], "2":[697, 1336], "3":[697, 1477], "A":[697, 1633], "4":[770, 1209], "5":[770, 1336], "6":[770, 1477], "B":[770, 1633], "7":[852, 1209], "8":[852, 1336], "9":[852, 1477], "C":[852, 1633], "X":[941, 1209], "0":[941, 1336], "#":[941, 1477], "D":[941, 1633]}

    character = "None"
    resolucao = 30
    for tecla, frequencias in tabelaDeFrequencias.items():
        #exemplo tecla 2, tenho 2 picos: [ 697.51581669 1335.53028413]. Quero que o primeiro esteja entre 667 <= x <= 727 e o segundo entre 1306 <= x <= 1366
        if (frqObtidaLista[0][0] <= frequencias[0] + resolucao) and (frqObtidaLista[0][0] >= frequencias[0] - resolucao) and (frqObtidaLista[1][0] <= frequencias[1] + resolucao) and (frqObtidaLista[1][0] >= frequencias[1] - resolucao):
            character = tecla
    
    print("\nTecla referente ao som gravado: {0}".format(character))



def main():
 
    #declare um objeto da classe da sua biblioteca de apoio (cedida)    
    signal = signalMeu()

    #declare uma variável com a frequência de amostragem, sendo 44100
    Fs = 44100
    
    #você importou a bilioteca sounddevice como, por exemplo, sd. então
    # os seguintes parametros devem ser setados:
    
    sd.default.samplerate = Fs #taxa de amostragem
    sd.default.channels = 1  #voce pode ter que alterar isso dependendo da sua placa

    # faca um print na tela dizendo que a captação começará em n segundos. e então 
    #use um time.sleep para a espera
    print("A captação começará em 4 segundos")
    sleep(4)
   
   #faça um print informando que a gravação foi inicializada
    print("A gravação foi inicializada")
   
   #declare uma variável "duração" com a duração em segundos da gravação. poucos segundos ... 
   #calcule o número de amostras "numAmostras" que serão feitas (número de aquisições)

    T = 2  
    numAmostras = T*Fs 


    #grave uma variavel com apenas a parte que interessa (dados)
    audio = sd.rec(int(numAmostras), Fs, channels=1)
    sd.wait()
    print("...     FIM")

    
    sd.playrec(audio)
    sleep(2)

    print("Áudio já gravado e re-tocado")
    
    sd.wait()
    
    #analise sua variavel "audio". pode ser um vetor com 1 ou 2 colunas, lista ...
    # use a funcao linspace e crie o vetor tempo. Um instante correspondente a cada amostra!
    t = np.linspace(0,T,T*Fs)
    # t = np.linspace(-T/2,T/2,T*Fs)

    # print("ESSE É O AUDIO:{0}".format(audio[80000]))
    # print(audio[10])
    arrayAudio = np.ndarray(shape=(88200,),dtype=np.float32)
    print("Olha aí o arrayAudio:{0}".format(arrayAudio[0:10]))

    for i in range(0,arrayAudio.shape[0]):
        arrayAudio[i] = audio[i][0]

    teste = []
    for i in range(0,88200):
        teste.append(audio[i][0])

    # print("ESSE É O TESTE {0}".format(teste))

    # plot do gráfico áudio vs tempo!
    print("Será plotado o gráfico do áudio gravado")
    plt.plot(t[:400], teste[:400])
    plt.title("Som gravado")
    plt.autoscale(enable=True, axis='both', tight=True)
    plt.show()
    
    # y = audio[:300]
    ## Calcula e exibe o Fourier do sinal audio. como saida tem-se a amplitude e as frequencias
    print("Agora será calculada a Transformada de Fourier!")
    x, y = signal.calcFFT(teste, Fs)
    # print(y)
    
    #esta funcao analisa o fourier e encontra os picos
    #voce deve aprender a usa-la. ha como ajustar a sensibilidade, ou seja, o que é um pico?
    #voce deve tambem evitar que dois picos proximos sejam identificados, pois pequenas variacoes na
    #frequencia do sinal podem gerar mais de um pico, e na verdade tempos apenas 1.
    index = peakutils.indexes(y, thres=0.2, min_dist=10)
    # index=peakutils.indexes(yf, thres=0.2, min_dist=10)

    #printe os picos encontrados! 
    print("Esses foram os picos encontrados: {0}".format(x[index]))

    print("Será plotado o gráfico da Transformada do Fourier com os picos encontrados!")
    plt.plot(x, y, label="transformada")
    plt.scatter(x[index], y[index], label= "picos", color= "green", marker= "o", s=30)
    plt.title('Transformada de Fourier do som gravado')
    plt.autoscale(enable=True, axis='both', tight=True)
    plt.show()        
    
    #encontre na tabela duas frequencias proximas às frequencias de pico encontradas e descubra qual foi a tecla
    #print a tecla.
    achaTecla(index, x)


    ## Exibe gráficos
    plt.show()

if __name__ == "__main__":
    main()
