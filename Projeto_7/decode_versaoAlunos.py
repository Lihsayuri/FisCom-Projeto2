#---------------- IMPORTANDO BIBLIOTECAS ----------------

import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy import signal as window
from suaBibSignal import signalMeu
from time import sleep
import peakutils

#---------------- IMPLEMENTANDO FUNÇÕES ----------------

# Função para transformar intenidade acústica em dB

def todB(s):
    sdB = 10*np.log10(s)
    return(sdB)

def achaTecla(index, x):
    freqObtained = [[], []]
    for frequencia in x[index]:
        # Frequências menores: Linha
        if int(frequencia) in range(640, 990):
            freqObtained[0].append(int(frequencia))
        # Frequências maiores: Coluna
        elif int(frequencia) in range(1160, 1680):
            freqObtained[1].append(int(frequencia))

    # Com esse for eu já filtro as frequências nos ranges que, potencialmente, podem ser as teclas
    dictFrequencies = {"1":[697, 1209], "2":[697, 1336], "3":[697, 1477], "A":[697, 1633], "4":[770, 1209], "5":[770, 1336], 
    "6":[770, 1477], "B":[770, 1633], "7":[852, 1209], "8":[852, 1336], "9":[852, 1477], "C":[852, 1633], "X":[941, 1209],
     "0":[941, 1336], "#":[941, 1477], "D":[941, 1633]}

    symbol = None
    erro = 30

    # Aqui tentamos identificar se pertence ao espectro de uma tecla ou não
    for tecla, frequencias in dictFrequencies.items():
        # Exemplo tecla 2, tenho 2 picos: [ 697.51581669 1335.53028413]. Quero que o primeiro esteja entre 667 <= x <= 727 e o segundo entre 1306 <= x <= 1366
        if (freqObtained[0][0] <= frequencias[0] + erro) and (freqObtained[0][0] >= frequencias[0] - erro) and (freqObtained[1][0] <= frequencias[1] + erro) and (freqObtained[1][0] >= frequencias[1] - erro):
            symbol = tecla
    
    print("\nTecla referente ao som gravado: {0}".format(symbol))

# Função principal
def main():
 
    # Declare um objeto da classe da sua biblioteca de apoio (cedida)    
    signal = signalMeu()

    # Declare uma variável com a frequência de amostragem, sendo 44100
    Fs = 44100
    
    # Você importou a bilioteca sounddevice como, por exemplo, sd, então
    # os seguintes parâmetros devem ser setados:
    
    sd.default.samplerate = Fs # Taxa de amostragem
    sd.default.channels = 1  # Você pode ter que alterar isso dependendo da sua placa

    # Faça um print na tela dizendo que a captação começará em n segundos, e então 
    # use um time.sleep para a espera
    print("A captação começará em 4 segundos")
    sleep(4)
   
   # Faça um print informando que a gravação foi inicializada
    print("A gravação foi inicializada")
   
   # Declare uma variável "duração" com a duração em segundos da gravação, poucos segundos ... 
   # Calcule o número de amostras "numAmostras" que serão feitas (número de aquisições)

    T = 2  
    numAmostras = T*Fs 

    # Grave uma variável com apenas a parte que interessa (dados)
    audio = sd.rec(int(numAmostras), Fs, channels=1)
    sd.wait()
    print("...     FIM")
    
    sd.playrec(audio)
    sleep(2)

    print("Áudio já gravado e re-tocado")
    
    sd.wait()
    
    # Analise sua variável "audio". Pode ser um vetor com 1 ou 2 colunas, lista ...
    # use a função linspace e crie o vetor tempo. Um instante correspondente a cada amostra!
    t = np.linspace(0,T,T*Fs)

    # print("ESSE É O AUDIO:{0}".format(audio[80000][0]))

    listaDoAudio = []  # Se eu pegar apenas audio[i], ele retorna o número dentro de uma lista. Eu quero apenas o número. 
    for i in range(0, numAmostras):
        listaDoAudio.append(audio[i][0])

    # print("ESSE É O TESTE {0}".format(teste))

    #---------------- PLOTANDO GRÁFICOS ----------------

    # Plot do gráfico áudio X tempo

    print("Será plotado o gráfico do áudio gravado")
    plt.plot(t, listaDoAudio)
    plt.grid(True)
    plt.title("Som gravado")
    plt.autoscale(enable=True, axis='both', tight=True)
    plt.show()
    
    # Calcula e exibe o Fourier do sinal audio. como saida tem-se a amplitude e as frequencias
    print("Agora será calculada a Transformada de Fourier!")
    x, y = signal.calcFFT(listaDoAudio, Fs)
    
    # Esta função analisa o Fourier e encontra os picos
    # Você deve aprender a usá-la. Há como ajustar a sensibilidade, ou seja, o que é um pico?
    # Você deve também evitar que dois picos próximos sejam identificados, pois pequenas variações na
    # frequência do sinal podem gerar mais de um pico, e na verdade temos apenas 1. 
    index = peakutils.indexes(y, thres=0.2, min_dist=10)

    # Printando picos encontrados

    print("Esses foram os picos encontrados: {0}".format(x[index]))

    print("Será plotado o gráfico da Transformada do Fourier com os picos encontrados!")
    plt.plot(x, y, label="transformada")
    plt.scatter(x[index], y[index], label= "picos", color= "green", marker= "o", s=30)
    plt.legend()
    plt.title('Transformada de Fourier do som gravado')
    plt.xlim([0,12000])
    plt.show()        
    
    # Encontre na tabela duas frequências próximas às frequências de pico encontradas e descubra qual foi a tecla
    
    # Printando tecla
    achaTecla(index, x)

    # Exibe gráficos
    plt.show()

if __name__ == "__main__":
    main()
