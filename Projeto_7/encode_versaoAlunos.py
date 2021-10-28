#importe as bibliotecas
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from os import sys
from logging import info
from suaBibSignal import signalMeu
import soundfile as sf

def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)

#converte intensidade em Db, caso queiram ...
def todB(s):
    sdB = 10*np.log10(s)
    return(sdB)

def main():
    print("Inicializando encoder")
    
    #declare um objeto da classe da sua biblioteca de apoio (cedida)    
    signal = signalMeu()


    digit = input("Pressione alguma tecla de 0 a 9, A, B, C, D ou #: ")

    dict_frequencies = {"0": [941, 1336], "1":[697, 1209], "2":[697,1336], "3":[697, 1477], "4":[770, 1209], "5":[770, 1336], "6":[770, 1477], "7":[852, 1209], "8":[852,1336], "9":[852, 1477],
    "A": [697, 1633], "B":[770, 1633], "C":[852, 1633], "D":[941,1633], "#":[941,1477], "X":[941, 1209]}

    #declare uma variavel com a frequencia de amostragem, sendo 44100
    Fs = 44100
    #voce importou a bilioteca sounddevice como, por exemplo, sd. entao
    # os seguintes parametros devem ser setados:
    sd.default.samplerate = Fs
    sd.default.channels = 1

    # fs  = 200   # pontos por segundo (frequência de amostragem)
    # A   = 1.5   # Amplitude
    # F   = 1     # Hz
    # T   = 4     # Tempo em que o seno será gerado
    # t   = np.linspace(-T/2,T/2,T*fs)

    # F = 440 #Hz
    A = 1 #amplitude
    T = 2 # tempo em que o seno será gerado
    t = np.linspace(0, 2*T, T*Fs) #Ex: 1000 bits por segundo, 1 segudo amostra 1000 vezes. Então 1segundo amostra Fs vezes. 
    
    # duration = 
    #tempo em segundos que ira emitir o sinal acustico

    def gerarSenoSinal(digit):
        # for i in range(len(dict_frequencies)):
            if digit in dict_frequencies:
                return dict_frequencies[digit][0], dict_frequencies[digit][1]
            else:
                print("Ops, o termo teclado não existe!")

    freq1, freq2 = gerarSenoSinal(digit)    
    print("Essa é a frequência1: {0}".format(freq1))
    print("Essa é a frequência2: {0}".format(freq2))    
    x1, y1 = signal.generateSin(freq1, A, T, Fs)
    x2, y2 = signal.generateSin(freq2, A, T, Fs)

    y=y1+y2
    

    print("Gerando Tons base")

    info(f'Gerando tom referente ao símbolo: {digit} ')
    print("Gerando Tom referente ao símbolo : {}".format(digit))

    sd.play(y, Fs)

    #relativo ao volume. Um ganho alto pode saturar sua placa... comece com .3    
    gainX  = 0.3
    gainY  = 0.3
    
    #gere duas senoides para cada frequencia da tabela DTMF ! Canal x e canal y 
    #use para isso sua biblioteca (cedida)
    #obtenha o vetor tempo tb.
    #deixe tudo como array

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
    
    sd.wait()

    #printe a mensagem para o usuario teclar um numero de 0 a 9. 
    #nao aceite outro valor de entrada.
    
    
    #construa o sunal a ser reproduzido. nao se esqueca de que é a soma das senoides
    
    #printe o grafico no tempo do sinal a ser reproduzido
    # reproduz o som
    # sd.play(sine, Fs)
    #  Exibe gráficos
    print('Plotando os gráficos')
    plt.figure()
    plt.plot(t[:300], y[:300], '.-')
    plt.show()
    # aguarda fim do audio
    sd.wait()


    # print('Plotando gráfico Fourier')
    # plt.figure()
    # plt.plot(t, y, '.-')
    # plt.show()

    def getfile(digit):
        digit = str(digit)
        filename= "digit.wav"
        return filename
    
    filename=getfile(digit)
    print(f'Salvando o arquivo de som em: {filename}')
    sf.write(filename, y, Fs) 


if __name__ == "__main__":
    main()
