#####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 
import random
import time

from numpy.core.fromnumeric import size
from enlace import *
import time
import numpy as np
from PIL import Image
import io
from enlaceRx import * 
# from Client import *

# txLen = ""
# voce deverá descomentar e configurar a porta com através da qual irá fazer comunicação
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)

serialName2 = "COM4"        #CABO AZUL

def main():
    try:
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com2 = enlace(serialName2)
    
        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com2.enable()

        #contabilizando o tempo inicial
        tempo_inicial = time.time()
        #limpar tudo antes de começar a receber, às vezes ficam alguns vestígios de bits perdidos
        com2.fisica.flush()
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        print("Comunicação aberta com sucesso!")

        # -----------------------------------------------------------------------------------------------
        # HANDSHAKE
        
        TentarNovamente = True

        while TentarNovamente:
            print("Vamos estabelecer o Handshake com o Client")

            # os mesmos 2 bytes que foram enviados vão ser recebidos aqui: que são exatamente o tamanho total de byte
            time.sleep(2)
            txBufferHandshake, tRxHandshake = com2.getData(10)  
            testeFalha = b'hello worlyd'

            # de bytes transformando para decimal de novo, que é como iremos usar no resto da comunicação
            print("Handshake recebidooo!")

            print("Agora servidor está enviando o Handshake de volta para o client")
            com2.sendData(np.asarray(txBufferHandshake))

            txYesBuffer, ntxYesBuffer = com2.getData(1)

            if txYesBuffer == b'S':
                time.sleep(1)
                TentarNovamente = True

            if txYesBuffer == b't':
                TentarNovamente = False
                print("Handshake feito!")
                print("Mensagem recebida do Client: {0}".format(txBufferHandshake))
            
            if txYesBuffer == b'N':
                TentarNovamente = False
                print("Ocorreu um erro e você não quis tentar novamente. Tente novamente depois então :/")
        
        #----------------------------------------------------------------------------------------------------

        # Receber os DATAGRAMASSS

        EnvioNaoCompleto = True

        while EnvioNaoCompleto:
            print("Vamos estabelecer o recebimento dos datagramas com o Client!")

            # os mesmos 2 bytes que foram enviados vão ser recebidos aqui: que são exatamente o tamanho total de byte
            time.sleep(2)
            txPackSize, tRxNPackSize= com2.getData(2)  

            rxBufferResposta = int.from_bytes(txPackSize, "big")

            print("Agora servidor está enviando o número de bytes do pacote a ser recebido")

            com2.sendData(np.asarray(txPackSize))

            print("Mandei de novo o número de bytes que irei receber")

            txPack, txnPack = com2.getData(rxBufferResposta)

            com2.sendData(txPack)

            print("Enviando o pacote recebido para o Client para conferir")


        time.sleep(5)

        tempo_final = time.time()
        tempo_total = tempo_final - tempo_inicial
        # velocidade = lenRx/ tempo_total

        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        # print("Velocidade: {0}".format(velocidade))
        com2.disable()
    
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com2.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
