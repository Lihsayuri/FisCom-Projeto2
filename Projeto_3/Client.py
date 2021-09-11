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
from enlaceClient import *
from enlaceRxCLient import *
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

        # my_str = "helloworld"
        # my_str_as_bytes = str.encode(my_str)
        handshake_message = b'\x01'

        print("Primeira mensagem em bytes que será enviada para o server: {0}".format(handshake_message))
        print(len(handshake_message))

        # ------------------------------------------------------------------------------------------------------

        #Handshake a ser estabelecido entre Client e Server
        
        TentarNovamente = True

        while TentarNovamente:
            print("-------------------------")
            print("         HANDSHAKE        ")
            print("-------------------------\n")
            print("Handshake pelo client sendo enviado em alguns segundos... \n")

            com1.sendData(handshake_message)

            time.sleep(0.1)

            print("Enviou: {0}".format(handshake_message))
            print("Aguardando a confirmação do Server\n")

            print("Número de bytes enviados:{0}".format(com1.tx.transLen))

            rxBufferHandshake, rxnHandshake = com1.getData(1)
            
            print("Recebeu o Handshake: {0}\n".format(rxBufferHandshake))

            if rxBufferHandshake == b'\x02':
                print("Handshake feito com sucesso!")
                print("O server recebeu o byte: {0}".format(rxBufferHandshake))
                print("Vamos iniciar a transmissao do pacote\n")
                TentarNovamente = False
            # quando o server não responde, essa resposta é autogerada
            elif rxBufferHandshake == b'\xFF':
                resposta = input("Tentar novamente? S/N ")
                if resposta == "S":
                    TentarNovamente = True
                else: 
                    TentarNovamente = False
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

        datagramas = []
        for i in range(len(packageList)):
            lenPacks_bin = len(packageList).to_bytes(1, byteorder="big")
            currentPacks = (i+1).to_bytes(1, byteorder="big")
            Head = b'HEAD' + currentPacks + b'/' + lenPacks_bin + b'\x00\x00\x00'
            string_bytes_pack = Head+packageList[i]+EOP
            datagramas.append(string_bytes_pack)

        #-----------------------------------------------------------------------------------------------------

        #Comunicação para envio de datagramas

        EnvioNaoCompleto = True

        # while EnvioNaoCompleto:

        print("------------------------------------------")
        print("         INICIANDO ENVIO DE PACOTES      ")
        print("------------------------------------------\n")
        print("Pacote será enviado em alguns segundos... \n")
        

        for n in range(len(datagramas)):

            numeroBytesPack = (len(datagramas[n])).to_bytes(2, byteorder="big")
            com1.sendData(np.asarray(numeroBytesPack))

            print("------------------------------------------\n")
            print("Enviei o número de bytes a serem transmitidos\n")

            rxBufferPackSize, rxnPackSize = com1.getData(2)

            if rxBufferPackSize == numeroBytesPack:
                lenBytesPack = len(datagramas[n])
                print("Vamos transmitir: {0} bytes".format(lenBytesPack))

                print("Quero mandar esse pacote: {0}\n".format(datagramas[n]))

                com1.sendData(np.asarray(datagramas[n]))

                if n != len(datagramas):
                    rxNextPack, rxnNextPack = com1.getData(1)
                    if rxNextPack == b'\x0F':
                        print("O server deu o sinal verde, posso enviar o próximo pacote\n")
                    else:
                        print("Ops... Ocorreu um erro com os pacotes. Muito triste...")
                        nRxBytes, nRxNBytes = com1.getData(1)
                        print("Recebeu ")
                        n = int.from_bytes(nRxBytes, byteorder="big")

                else:
                    print("Transmissão encerrada!")
                
                
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
