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
from typing import Text
from math import ceil  #arredonda uma número para cima

from numpy.core.fromnumeric import size
from enlace import *
import time
import numpy as np
from PIL import Image
import io
import math

# voce deverá descomentar e configurar a porta com através da qual irá fazer comunicação
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName1 = "COM5"       #MEU CABO           # Windows(variacao de)

def main():
    try:
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName1)

        #Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com1.enable()

        print("Comunicação aberta com sucesso!")

        # Contabilizando o tempo inicial
        cronometro_client = time.time()

        my_str = "helloworld"
        my_str_as_bytes = str.encode(my_str)
        handshake_message = my_str_as_bytes

        print("Primeira mensagem em bytes que será enviada para o server: {0}".format(handshake_message))
        print(len(handshake_message))

        # ------------------------------------------------------------------------------------------------------

        #Handshake a ser estabelecido entre Client e Server
        
        TentarNovamente = True

        while TentarNovamente:
            print("Handshake pelo client sendo enviado em alguns segundos... \n")

            com1.sendData(np.asarray(handshake_message))

            print("Aguardando a confirmação do Server")

            rxBufferHandshake, rxnHandshake = com1.getData(10)

            time.sleep(5)

            if handshake_message == rxBufferHandshake:
                print("Handshake feito com sucesso!")
                print("O server recebeu o mesmo que foi enviado pelo client: {0}".format(rxBufferHandshake))
                com1.sendData(b't')

                TentarNovamente = False
            else:
                print("Servidor inativo")
                resposta = input("Tentar novamente? S/N ")
                if resposta == "S":
                    com1.sendData(b'S')
                    TentarNovamente = True
                else: 
                    TentarNovamente = False
                    com1.sendData(b'N')
                    print("Ocorreu um erro e você não quis tentar novamente. Tente novamente depois então :/")


        #------------------------------------------------------------------------------------

        # DATAGRAMA

        Head = b'HEAD/Sayti'
        print(Head) 
        EOP = b'\x00\x00\x00\x01'
        print(EOP)

        #------- Definindo Payload ---------

        # Payload = "Uns, com os olhos postos no passado, Veem o que nao veem; outros, fitos Os mesmos olhos no futuro, veem O que nao se pode ver. Porque tao longe ir por o que esta perto A seguranca nossa Este e o dia, Esta e a hora, este o momento, isto E quem somos, e e tudo. Perene flui a interminavel hora Que nos confessa nulos. No mesmo hausto Em que vivemos, morreremos. Colhe O dia, porque es ele."
        filepath = "./payload.txt"
        sizePayload = 114 

        packageList = []
        with open(filepath, "rb") as file:
            binRead = file.read()
            binArray = bytearray(binRead)
            lenPacks = (len(binArray)/sizePayload)
            for i in range(0, int(ceil(lenPacks))):
                packageList.append(binArray[:sizePayload])
                del(binArray[:sizePayload])
                #lê, apenda e tira!
                
        print(packageList)

        datagramas = []
        for i in range(len(packageList)):
            lenPacks_bin = len(packageList).to_bytes(1, byteorder="big")
            currentPacks = (i+1).to_bytes(1, byteorder="big")
            Head = b'HEAD' + currentPacks + b'/' + lenPacks_bin + b'\x00\x00\x00'
            string_bytes_pack = Head+packageList[i]+EOP
            datagramas.append(string_bytes_pack)
        
        print(datagramas)

        #-----------------------------------------------------------------------------------------------------

        #Comunicação para envio de datagramas

        EnvioNaoCompleto = True

        while EnvioNaoCompleto:

            print("Pacote será enviado em alguns segundos... \n")

            for n in range(len(datagramas)):

                numeroBytesPack = len(datagramas[n]).to_bytes(2, byteorder="big")
                com1.sendData(np.asarray(numeroBytesPack))

                rxBufferPackSize, rxnPackSize = com1.getData(2)

                if rxBufferPackSize == numeroBytesPack:
                    lenBytesPack = len(datagramas[n])
                    print("Vamos transmitir {0} bytes".format(lenBytesPack))

                    com1.sendData(np.asarray(datagramas[n]))

                    rxBufferPack, rxnBufferPack = com1.getData(lenBytesPack)

                    if rxBufferPack == datagramas[n]:
                        print("pacotes iguais")

                  





 
        tempo_final = time.time()
        tempo_total = tempo_final - cronometro_client
        # velocidade = len(txBuffer)/tempo_total

        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")

        com1.disable()
    

    #Separando o número de pacotes

    # frac, whole = math.modf(len(payload_as_bytes)/sizePayload)
    
    # if frac > 0:
    #     numPacks = round(whole + 1)
    # else:
    #     numPacks = round(whole)

    # lista_packs = []
    # for i in range(numPacks):
    #     pack = b''
    #     for j in range(0,sizePayload):
    #         print(payload_as_bytes[j])
    #         pack += payload_as_bytes[j]
    #     datagrama = Head + pack + EOP
    #     lista_packs.append(datagrama)
            
    # print(lista_packs)

    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
