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
        print("Comunicação aberta com sucesso!\n")

        # -----------------------------------------------------------------------------------------------
        # HANDSHAKE
        
        TentarNovamente = True

        while TentarNovamente:
            print("-------------------------")
            print("         HANDSHAKE        ")
            print("-------------------------\n")
            print("Vamos estabelecer o Handshake com o Client")

            # os mesmos 2 bytes que foram enviados vão ser recebidos aqui: que são exatamente o tamanho total de byte

            txBufferHandshake, tRxHandshake = com2.getData(15)  
            EOP = b'\x00\x00\x00\x01'
            respostaServer = b'HEAD\x01/\x01\x00\x00\x00' + b'\x02' + EOP
            
            # de bytes transformando para decimal de novo, que é como iremos usar no resto da comunicação

            print("Agora servidor está enviando o Handshake de volta para o client")


            if txBufferHandshake[10:11] == b'\x01':
                time.sleep(1)
                com2.sendData(respostaServer)
                print("Respondi o Handshake e posso começar a transmissão")
                TentarNovamente = False


        print("Pronto para receber os pacotes\n")
        # com2.getData(10)
        #----------------------------------------------------------------------------------------------------

        # Receber os DATAGRAMASSS

        EnvioNaoCompleto = True

        nOldPackage = 0
        dataReceived = []

        print("------------------------------------------------")
        print("         INICIANDO RECEBIMENTO DE PACOTES      ")
        print("------------------------------------------------\n")

        forcarErro = False
        forcarErroNbytes = True


        while EnvioNaoCompleto:
            # time.sleep(2)

            print("Vamos estabelecer o recebimento dos datagramas com o Client!")

            # os mesmos 2 bytes que foram enviados vão ser recebidos aqui: que são exatamente o tamanho total de byte
            txPackSize, tRxNPackSize= com2.getData(2)  

            rxBufferResposta = int.from_bytes(txPackSize, byteorder ="big")

            print("Agora servidor está enviando o número de bytes do pacote a ser recebido")

            com2.sendData(np.asarray(txPackSize))

            print("Mandei de novo o número de bytes que irei receber\n")

            txPack, txnPack = com2.getData(rxBufferResposta)

            print("-----------------------------------")
            print("        ANALISANDO PACOTES...    ")
            print("-----------------------------------\n")
            print("Pacote recebido:{0}\n".format(txPack))

            if forcarErroNbytes:
                BytesErrados = txPack[0:10] + b'\x00\x01\x02\x00\x00\x00\x02' + txPack[11:rxBufferResposta]
                txPack = BytesErrados
                print("BYTES ERRADOS:{0}".format(BytesErrados))

            EOP = txPack[(rxBufferResposta-4):rxBufferResposta]
            print("Esse é o EOP:{0}\n".format(EOP))
            CurrentPack = txPack[4:5]

            print("-------------------------\n")
            print("Pacote atual:{0}".format(CurrentPack))
            nCurrentPack = int.from_bytes(CurrentPack, byteorder="big")
            print("Pacote atual em int:{0}\n".format(nCurrentPack))
            TotalPacks = txPack[6:7]
            nTotalPacks = int.from_bytes(TotalPacks, byteorder="big")
            print("-------------------------\n")

            print("Número total de pacotes :{0}\n".format(nTotalPacks))

            sinal_verde = b'HEAD\x01/\x01\x00\x00\x00' + b'\x0F'+ EOP

            if forcarErro:
                nCurrentPack -=1
                # forcarErro = False

            if nCurrentPack == (nOldPackage + 1) and EOP == b'\x00\x00\x00\x01':
                print("Pacote recebido está certo! Vou enviar o sinal verde: {0}".format(sinal_verde))
                dataReceived.append(txPack)
                com2.sendData(sinal_verde)
                nOldPackage+= 1
                if nCurrentPack == nTotalPacks and EOP == b'\x00\x00\x00\x01':
                    print("Recebi todos os pacotes!")
                    EnvioNaoCompleto = False

            # elif nCurrentPack != (nOldPackage + 1) or EOP != b'\x00\x00\x00\x01':
            else:
                if forcarErro:
                    print("Recebi o pacote errado!")
                    print("O Client vai ter que me enviar o mesmo pacote")
                    forcarErro = False
                    CurrentPackDatagrama = b'HEAD\x01/\x01\x00\x00\x00' + CurrentPack + EOP
                    print(CurrentPackDatagrama)
                    com2.sendData(CurrentPackDatagrama)
                elif forcarErroNbytes:
                    print("Recebi o número de bytes errado! O EOP está fora de ordem")
                    print("O client vai ter que me reenviar o pacote")
                    forcarErroNbytes = False
                    CurrentPackDatagrama = b'HEAD\x01/\x01\x00\x00\x00' + CurrentPack + b'\x00\x00\x00\x01'
                    print(CurrentPackDatagrama)
                    com2.sendData(CurrentPackDatagrama)


            # o server deve enviar uma mensagem para o cliente solicitando o reenvio do pacote, seja por
            # não ter o payload esperado, ou por não ser o pacote correto
        
        print("TODOS OS DADOS AQUI: {0}\n".format(dataReceived))

        organizedData = b''

        for j in range(len(dataReceived)):
            currentByteStr = dataReceived[j]
            lenCurrentByteStr = len(currentByteStr)
            payload = currentByteStr[10:(lenCurrentByteStr-4)]
            organizedData += payload

        print(organizedData)

        # encoding = 'utf-8'
        # Criou o arquivoooooooo YAAAAAAAAAY
        with open('receivedFile3.txt','wb') as f:
            f.write(organizedData)


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
