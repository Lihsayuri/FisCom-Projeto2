#---------------- IMPORTANDO BIBLIOTECAS ----------------

import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from os import sys
from logging import info
from suaBibSignal import signalMeu
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

def getfile(digit, yAudio, Fs):
    digit = str(digit)
    filename= "digit.wav"
    print(f'Salvando o arquivo de som em: {filename}')
    sf.write(filename, yAudio, Fs) 

def main():
    print("Inicializando encoder")
    
    # Declare um objeto da classe da sua biblioteca de apoio (cedida)    
    signal = signalMeu()


    # Printe a mensagem para o usuário teclar um número de 0 a 9. 
    # Não aceite outro valor de entrada.
    digit = input("Pressione alguma tecla de 0 a 9, A, B, C, D ou #: ")

    dictFrequencies = {"0": [941, 1336], "1":[697, 1209], "2":[697,1336], "3":[697, 1477], "4":[770, 1209], "5":[770, 1336], "6":[770, 1477], "7":[852, 1209], "8":[852,1336], "9":[852, 1477],
    "A": [697, 1633], "B":[770, 1633], "C":[852, 1633], "D":[941,1633], "#":[941,1477], "X":[941, 1209]}

    # Declare uma variável com a frequência de amostragem sendo 44100
    Fs = 44100
    
    # Você importou a bilioteca sounddevice como, por exemplo, sd, então
    # os seguintes parâmetros devem ser setados:

    sd.default.samplerate = Fs
    sd.default.channels = 1
 
    A = 1 # Amplitude 
    T = 2 # Tempo em que o seno será gerado (Período da amostra)/ tempo em segundos que irá emitir o sinal acústico
    t = np.linspace(0, 2*T, T*Fs) # Ex: 1000 bits por segundo, 1 segudo amostra 1000 vezes. Então 1 segundo amostra Fs vezes. 
    # t   = np.linspace(-T/2,T/2,T*Fs)


    # Construa o sinal a ser reproduzido. Não se esqueça de que é a soma das senoides

    freq1, freq2 = gerarSenoSinal(digit, dictFrequencies)    
    print("Essa é a frequência1: {0}".format(freq1))
    print("Essa é a frequência2: {0}".format(freq2))    
    x1, y1 = signal.generateSin(freq1, A, T, Fs)
    x2, y2 = signal.generateSin(freq2, A, T, Fs)

    y=y1+y2

    print("Gerando Tons base")

    info(f'Gerando tom referente ao símbolo: {digit} ')
    print("Gerando Tom referente ao símbolo : {}".format(digit))


    # Reproduz o som
    sd.play(y, Fs)

    # Aguarda fim do áudio
    sd.wait()
    

    # Relativo ao volume. Um ganho alto pode saturar sua placa... comece com .3    
    gainX  = 0.3
    gainY  = 0.3
    
    # Gere duas senoides para cada frequência da tabela DTMF! Canal X e canal Y 
    # Printe o gráfico no tempo do sinal a ser reproduzido
    # Use sua biblioteca (cedida) para isso 
    # Obtenha o vetor tempo tb.
    # Deixe tudo como array

    #---------------- PLOTANDO GRÁFICOS ----------------

    info('Plotando os gráficos')
    plt.figure()
    plt.plot(t[:300], y1[:300], 'b--', alpha=0.5, label= (f'{freq1}Hz'))
    plt.plot(t[:300], y2[:300], 'g--', alpha=0.5, label=(f'{freq2}Hz'))
    plt.plot(t[:300], y[:300], 'k', alpha=0.75, label=(f'Soma de {freq1}Hz e {freq2}Hz'))
    plt.legend()
    plt.title(f'Frequências do símbolo {digit}')
    plt.grid(True)
    plt.autoscale(enable=True, axis='both', tight=True)
    plt.show()


    # Exibe gráficos
    xFourier, yFourier = signal.calcFFT(y, Fs)
    info('Plotando o gráfico da Transformada de Fourier')
    plt.figure()
    plt.plot(xFourier,yFourier)
    plt.title(f'Transformada de Fourier do som gerado')
    plt.autoscale(enable=True, axis='both', tight=True)
    plt.xlim([0,5000])
    plt.show()



    getfile(digit, y, Fs)

if __name__ == "__main__":
    main()
